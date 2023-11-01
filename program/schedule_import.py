import collections
import datetime
import re
from dataclasses import dataclass
from typing import Any, Iterable

import openpyxl
from django.utils import timezone
from django.utils.text import slugify
from openpyxl.worksheet.merge import MergedCellRange

from program import models, views

ROOM_CAPACITY_SUFFIX = r"\s+\d+$"
PRETALX_CODE_PATTERN = r"^[A-Z0-9]{6}$"


class ScheduleImporter:
    def import_xlsx(
        self, file_path: str
    ) -> list[models.Room | models.Utility | models.Slot]:
        """
        Read the active sheet from the given XLSX file and creates a schedule.
        Missing rooms and utilities are created, new slots are saved to the database.

        Each slot in the file can contain either a 6-alphanum code of talk/workshop
        in pretalx, or any text - it will be added as a utility.

        The sheet can contain a schedule for multiple days - each day must contain
        a name of the day in the top-left column (e.g., Friday/Saturday), and the left
        column must contain only times (e.g., 10:00).

        The file must be formatted - this command uses information about merged cells
        to determine the length of slots and detect events that take place
        in multiple rooms.

        :param file_path: Path to XLSX file with schedule.
        :return: List of all objects that were created.
        """
        workbook: openpyxl.Workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        all_values = trim_trailing_dimensions(sheet.values)
        sheet_merges = [
            SheetMerge.from_openpyxl(cell_merge) for cell_merge in sheet.merged_cells
        ]

        batch = ImportBatch()
        for schedule_for_day in self._split_to_daily_tables(all_values, sheet_merges):
            self._import_schedule_for_day(schedule_for_day, batch)

        # Save slots to the database. Rooms and utilities were saved when created,
        # because they are immediately referenced by the slot.
        batch.bulk_create_slots()
        return batch.get_new_objects()

    def _import_schedule_for_day(
        self, schedule_day: "ScheduleDay", batch: "ImportBatch"
    ):
        batch.create_missing_rooms(schedule_day.room_names)

        for event in schedule_day.iterate_events():
            for room_name in event.rooms:
                slot = models.Slot(
                    start=event.start_time,
                    end=event.end_time,
                    room=batch.get_room(room_name),
                )

                self._assign_slot_event(batch, event, slot)
                batch.add_slot(slot)

    def _assign_slot_event(
        self, batch: "ImportBatch", event: "ScheduleEvent", slot: models.Slot
    ) -> None:
        if is_pretalx_code(event.name):
            if talk := batch.get_talk(event.name):
                slot.talk = talk
                return
            if workshop := batch.get_workshop(event.name):
                slot.workshop = workshop
                return

        slot.utility = batch.get_or_create_utility(event.name)

    def _split_to_daily_tables(
        self, values: list[list[str | None]], merges: list["SheetMerge"]
    ) -> Iterable["ScheduleDay"]:
        header_row = values[0]

        # Scan the header row and find columns that belong to each conference day.
        index = 0
        while index < len(header_row):
            # Check if the value in the current header cell matched a conference day.
            conference_day = parse_conference_day_title(header_row[index])
            if not conference_day:
                index += 1
                continue

            # Try to find an end of the schedule table - either start of another
            # conference day, or end of the entire table.
            start_index = index
            index += 1
            while index < len(header_row):
                if parse_conference_day_title(header_row[index]) is not None:
                    break
                index += 1

            # Extract only columns for the current conference day.
            day_range = slice(start_index, index)
            yield ScheduleDay(
                date=conference_day,
                values=slice_columns(values, day_range),
                merges=slice_merges(merges, day_range),
            )


class ImportBatch:
    def __init__(self):
        self._talks = models.Talk.objects.filter(pretalx_code__isnull=False).in_bulk(
            field_name="pretalx_code"
        )
        self._workshops = models.Workshop.objects.filter(
            pretalx_code__isnull=False
        ).in_bulk(field_name="pretalx_code")
        self._existing_rooms = {room.label: room for room in models.Room.objects.all()}
        self._new_rooms = {}
        self._all_rooms = collections.ChainMap(self._new_rooms, self._existing_rooms)

        self._existing_utilities = {
            utility.title: utility for utility in models.Utility.objects.all()
        }
        self._new_utilities = {}
        self._all_utilities = collections.ChainMap(
            self._new_utilities, self._existing_utilities
        )
        self._slots = []

    def create_missing_rooms(self, room_names: list[str]):
        for order, room_name in enumerate(room_names, start=1):
            if room_name in self._all_rooms:
                continue
            room = models.Room(
                label=room_name,
                slug=slugify(room_name),
                order=10 * order,
            )
            room.save()
            self._new_rooms[room.label] = room

    def get_talk(self, pretalx_code: str) -> models.Talk | None:
        return self._talks.get(pretalx_code)

    def get_workshop(self, pretalx_code: str) -> models.Workshop | None:
        return self._workshops.get(pretalx_code)

    def get_room(self, label: str) -> models.Room:
        return self._all_rooms[label]

    def get_or_create_utility(self, title: str) -> models.Utility:
        utility = self._all_utilities.get(title)
        if utility is None:
            utility = models.Utility(
                title=title,
                slug=slugify(title),
            )
            utility.save()
            self._new_utilities[title] = utility

        return utility

    def add_slot(self, slot: models.Slot) -> None:
        self._slots.append(slot)

    def bulk_create_slots(self) -> None:
        models.Slot.objects.bulk_create(self._slots)

    def get_new_objects(self) -> list[models.Room | models.Utility | models.Slot]:
        return [
            *self._new_rooms.values(),
            *self._new_utilities.values(),
            *self._slots,
        ]


class ScheduleDay:
    def __init__(
        self, date: datetime.date, values: list[list[Any]], merges: list["SheetMerge"]
    ):
        self.date = date
        self._values = values
        self._merges = self._prepare_merges(merges)
        self._timeline = self._prepare_times()
        self._room_names = self._prepare_rooms()

    @property
    def room_names(self) -> list[str]:
        """
        Get room names extracted from the table header.
        """
        return list(filter(None, self._room_names))

    def iterate_events(self) -> Iterable["ScheduleEvent"]:
        """
        Iterate through events in the schedule table. This function uses cell merges
        to determine the length of the event and rooms in which the event takes place.
        """
        for row_index, row in enumerate(self._values[1:], start=1):
            for col_index, value in enumerate(row[1:], start=1):
                if value is None:
                    continue
                value = value.strip()
                if not value:
                    continue

                start_time = self._timeline[row_index]
                merge = self._merges.get(
                    (row_index, col_index),
                    # Use fake single-column merge when no merge is found.
                    SheetMerge(row_index, row_index + 1, col_index, col_index + 1),
                )
                end_time = self._timeline[merge.end_row]
                yield ScheduleEvent(
                    name=value,
                    rooms=self._room_names[col_index : merge.end_column],
                    start_time=start_time,
                    end_time=end_time,
                )

    def _prepare_merges(
        self, merges: list["SheetMerge"]
    ) -> dict[tuple[int, int], "SheetMerge"]:
        return {
            (cell_merge.start_row, cell_merge.start_column): cell_merge
            for cell_merge in merges
        }

    def _prepare_times(self) -> list[datetime.datetime | None]:
        tz = timezone.get_current_timezone()
        result = []
        for row in self._values:
            try:
                if isinstance(row[0], str):
                    parsed_time = datetime.datetime.strptime(row[0], "%H:%M")
                    local_time = parsed_time.time()
                elif isinstance(row[0], datetime.time):
                    local_time = row[0]
                else:
                    raise TypeError(f"Unsupported type for time: {type(row[0])}")

                timestamp = datetime.datetime.combine(
                    date=self.date,
                    time=local_time,
                    tzinfo=tz,
                )
                result.append(timestamp)
            except ValueError:
                result.append(None)

        # Add one more entry 10 mins after the last one
        last_time = max(filter(None, result))
        result.append(last_time + datetime.timedelta(minutes=10))

        return result

    def _prepare_rooms(self):
        # First cell contains name of the day, keep it empty to
        return [
            None,
            *map(
                # Some room names in the sheet contain capacity as their suffix,
                # e.g., Lustrový sál 144 - remove it.
                lambda room_name: re.sub(ROOM_CAPACITY_SUFFIX, "", room_name.strip()),
                self._values[0][1:],
            ),
        ]


@dataclass
class ScheduleEvent:
    name: str
    rooms: list[str]
    start_time: datetime.datetime
    end_time: datetime.datetime


@dataclass
class SheetMerge:
    start_row: int
    end_row: int
    start_column: int
    end_column: int

    @classmethod
    def from_google_sheets(cls, merge: dict[str, int]) -> "SheetMerge":
        # Google Sheets uses 0-based numbering for rows/cols,
        # the end of the range is exclusive.
        return cls(
            start_row=merge["startRowIndex"],
            end_row=merge["endRowIndex"],
            start_column=merge["startColumnIndex"],
            end_column=merge["endColumnIndex"],
        )

    @classmethod
    def from_openpyxl(cls, cell_merge: MergedCellRange) -> "SheetMerge":
        # Openpyxl uses 1-based numbering for rows/cols,
        # the end of the range is inclusive.
        return cls(
            start_row=cell_merge.min_row - 1,
            end_row=cell_merge.max_row,
            start_column=cell_merge.min_col - 1,
            end_column=cell_merge.max_col,
        )


def is_pretalx_code(value: str) -> bool:
    """
    Check if the given value matches 6-alphanum code of a pretalx submission.
    """
    return re.match(PRETALX_CODE_PATTERN, value) is not None


def parse_conference_day_title(value: str) -> datetime.date | None:
    """
    Try to match the first word from the given string with a name of a conference day.
    Returns date of the day or ``None`` if the string could not be matched.

    Examples:

        >>> parse_conference_day_title("Friday Talks")
        datetime.date(2023, 9, 15)
        >>> parse_conference_day_title("Ball Room")
        None
    """
    value_lower = value.lower()
    for conference_day, date in views.CONFERENCE_DAYS.items():
        if value_lower.startswith(conference_day):
            return date
    return None


def trim_trailing_dimensions(values: Iterable[tuple[Any, ...]]) -> list[list[Any]]:
    """
    Removes empty rows and columns from the end of the table.

    This function is required because the ``openpyxl`` library returns all rows
    and columns in the sheet data, including empty rows exported from Google Sheets.
    """
    result = list(values).copy()
    # Trim empty trailing rows
    while result:
        if any(cell is not None for cell in result[-1]):
            break

        result.pop()

    # Convert row tuples to lists
    result = [list(row) for row in result]

    # Get the last non-empty index for each row
    def last_index_to_trim(row: list) -> int:
        last_index = len(row) - 1
        while row[last_index] is None:
            last_index -= 1
        return last_index + 1

    last_non_empty_column = max(last_index_to_trim(row) for row in result)

    # Trim empty trialing columns from each remaining row
    for index in range(len(result)):
        result[index] = result[index][:last_non_empty_column]

    return result


def slice_columns(values: list[list[Any]], column_slice: slice) -> list[list[Any]]:
    """
    Slice columns from the given table.
    """
    result = []
    for row in values:
        row_slice = row[column_slice]
        # End the table when the first column is empty
        if not row_slice[0]:
            break
        result.append(row_slice)
    return result


def slice_merges(merges: list[SheetMerge], column_slice: slice) -> list[SheetMerge]:
    """
    Slice merges for the given columns. The merges are transposed to match
    the indices returned by the ``slice_columns`` function.
    """
    result = []
    for cell_merge in merges:
        if (
            cell_merge.start_column < column_slice.start
            or cell_merge.start_column >= column_slice.stop
        ):
            continue
        result.append(
            SheetMerge(
                start_row=cell_merge.start_row,
                end_row=cell_merge.end_row,
                start_column=cell_merge.start_column - column_slice.start,
                end_column=cell_merge.end_column - column_slice.start,
            )
        )
    return result
