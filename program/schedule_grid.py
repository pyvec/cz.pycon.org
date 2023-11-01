import dataclasses
import datetime
from typing import Iterable

from program import models

# Number of header rows: 1st row contains names of the rooms.
HEADER_ROWS = 0
# Number of header columns: 1st colum contains the timeline.
HEADER_COLS = 0


@dataclasses.dataclass()
class ScheduleGrid:
    columns: list["ScheduleColumn"]
    rows: list["ScheduleRow"] = dataclasses.field(default_factory=list)

    @classmethod
    def create_from_slots(cls, slots: Iterable[models.Slot]) -> "ScheduleGrid":
        """
        Create a schedule grid from slots. The slots MUST be sorted
        by ``start`` and ``room__order``.
        """

        # Create a set with unique rooms from the list of slots,
        # convert it to list and sort the list by room order.
        rooms = list({slot.room for slot in slots})
        rooms.sort(key=lambda room: room.order)

        # Calculate room offsets. The first column is reserved for time,
        # start counting at 2.
        room_offsets = {
            room: offset for offset, room in enumerate(rooms, start=HEADER_COLS + 1)
        }

        grid = ScheduleGrid(
            columns=[
                ScheduleColumn(offset=room_offsets[room], room=room) for room in rooms
            ]
        )

        # Create a dictionary of all rows and compute their offsets.
        rows = {}
        offset = HEADER_ROWS
        for slot in slots:
            if slot.start in rows:
                continue
            offset += 1
            rows[slot.start] = ScheduleRow(
                offset=offset,
                time=slot.start,
            )

        # Populate the rows with items.
        last_item: ScheduleItem | None = None
        last_row_time = max(rows.keys()) if rows else None
        for slot in slots:
            # If the last item was the same event, but in a different room,
            # expand the previous slot to the current room.
            if last_item and slot.is_same_for_different_room(last_item.slot):
                last_item.column_end = room_offsets[slot.room] + 1

                if last_item.is_talk:
                    last_item.is_streamed = True

                continue

            item_row = rows[slot.start]

            if last_row_time and slot.end > last_row_time:
                end_row = rows.get(last_row_time)
                grid_row_end = end_row.offset + 1
            else:
                end_row = rows.get(slot.end)
                grid_row_end = (
                    end_row.offset if end_row is not None else item_row.offset + 1
                )

            item = ScheduleItem(
                row_start=item_row.offset,
                row_end=grid_row_end,
                column_start=room_offsets[slot.room],
                column_end=room_offsets[slot.room] + 1,
                slot=slot,
            )
            if item.is_utility and item.slot.event.is_streamed:
                item.is_streamed = True

            item_row.items.append(item)
            last_item = item

        # Assign rows to the grid
        grid.rows = list(rows.values())

        return grid

    def pop_row(self, index: int = 0) -> "ScheduleRow":
        result = self.rows.pop(index)
        # Shift offset of all following rows
        for row in self.rows[index:]:
            row.offset -= 1
            for item in row.items:
                item.row_start -= 1
                item.row_end -= 1

        return result


@dataclasses.dataclass()
class ScheduleColumn:
    offset: int
    room: models.Room

    @property
    def grid_area(self):
        return f"1 / {self.offset} / 2 / {self.offset + 1}"


@dataclasses.dataclass()
class ScheduleRow:
    offset: int
    time: datetime.datetime
    items: list["ScheduleItem"] = dataclasses.field(default_factory=list)

    def contains_only_non_streamed_utilities(self):
        return all(item.is_utility and not item.is_streamed for item in self.items)


@dataclasses.dataclass()
class ScheduleItem:
    row_start: int
    row_end: int
    column_start: int
    column_end: int
    slot: models.Slot
    is_streamed: bool = False

    @property
    def grid_area(self):
        return (
            f"{self.row_start} / {self.column_start} / "
            f"{self.row_end} / {self.column_end}"
        )

    @property
    def is_talk(self):
        return isinstance(self.slot.event, models.Talk)

    @property
    def is_workshop(self):
        return isinstance(self.slot.event, models.Workshop)

    @property
    def is_utility(self):
        return isinstance(self.slot.event, models.Utility)

    @property
    def is_multi_room(self):
        return (self.column_end - self.column_start) > 1

    @property
    def type(self):
        event = self.slot.event
        if isinstance(event, models.Talk) and event.is_keynote:
            return "keynote"
        if isinstance(event, (models.Talk, models.Workshop)):
            return event.type
        return "utility"
