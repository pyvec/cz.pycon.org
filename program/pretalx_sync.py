from collections import ChainMap
from typing import MutableMapping, Any

from program import models
from program import pretalx


class PretalxSync:
    def __init__(self, pretalx_client: pretalx.PretalxClient) -> None:
        self.client = pretalx_client
        # Used for assigning unique order numbers to new talks/workshops
        self._talks_order = 0
        self._workshops_order = 0

    def full_sync(self):
        all_speakers = self.sync_speakers()
        self.sync_submissions(all_speakers)

    def sync_speakers(self) -> dict[str, models.Speaker]:
        speakers = self.client.list_speakers(
            questions=["all"],
        )

        existing_speakers = models.Speaker.objects.filter(
            pretalx_code__isnull=False,
        ).in_bulk(field_name="pretalx_code")
        new_speakers: dict[str, models.Speaker] = {}
        all_speakers = ChainMap(new_speakers, existing_speakers)

        for speaker_data in speakers:
            speaker_code = speaker_data["code"]
            speaker = all_speakers.get(speaker_code)
            if speaker is None:
                speaker = models.Speaker(
                    is_public=False,
                    pretalx_code=speaker_code,
                )
                all_speakers[speaker_code] = speaker
            speaker.update_from_pretalx(speaker_data)

        # Update existing speakers
        models.Speaker.objects.bulk_update(
            objs=existing_speakers.values(),
            fields=models.Speaker.PRETALX_FIELDS,
        )
        # Create new speakers
        models.Speaker.objects.bulk_create(new_speakers.values())

        return dict(all_speakers)

    def sync_submissions(self, speakers: dict[str, models.Speaker]):
        submissions = self.client.list_submissions(
            questions=["all"], states=[pretalx.SubmissionState.CONFIRMED]
        )
        talks: list[dict[str, Any]] = []
        workshops: list[dict[str, Any]] = []
        for submission in submissions:
            type_ = models.Session.get_pretalx_submission_type(
                submission["submission_type"]
            )
            if type_ == "talk":
                talks.append(submission)
            else:
                workshops.append(submission)

        self.sync_talks(talks, speakers)
        self.sync_workshops(workshops, speakers)

    def sync_talks(
        self, submissions: list[dict[str, Any]], speakers: dict[str, models.Speaker]
    ) -> None:
        existing_talks = models.Talk.objects.filter(
            pretalx_code__isnull=False,
        ).in_bulk(field_name="pretalx_code")
        self._talks_order = max(
            (talk.order for talk in existing_talks.values()), default=0
        )
        new_talks: dict[str, models.Talk] = {}
        all_talks: MutableMapping[str, models.Talk] = ChainMap(
            new_talks, existing_talks
        )

        for submission_data in submissions:
            self.update_talk(all_talks, submission_data)

        models.Talk.objects.bulk_update(
            objs=existing_talks.values(),
            fields=models.Talk.PRETALX_FIELDS,
        )
        models.Talk.objects.bulk_create(new_talks.values())

        for submission_data in submissions:
            all_talks[submission_data["code"]].talk_speakers.set(
                [
                    speakers[speaker_data["code"]]
                    for speaker_data in submission_data["speakers"]
                ]
            )

    def sync_workshops(
        self, submissions: list[dict[str, Any]], speakers: dict[str, models.Speaker]
    ) -> None:
        existing_workshops = models.Workshop.objects.filter(
            pretalx_code__isnull=False,
        ).in_bulk(field_name="pretalx_code")
        self._workshops_order = max(
            (workshop.order for workshop in existing_workshops.values()), default=0
        )
        new_workshops: dict[str, models.Workshop] = {}
        all_workshops: MutableMapping[str, models.Workshop] = ChainMap(
            new_workshops, existing_workshops
        )

        for submission_data in submissions:
            self.update_workshop(all_workshops, submission_data)

        models.Workshop.objects.bulk_update(
            objs=existing_workshops.values(),
            fields=models.Workshop.PRETALX_FIELDS,
        )
        models.Workshop.objects.bulk_create(new_workshops.values())

        for submission_data in submissions:
            all_workshops[submission_data["code"]].workshop_speakers.set(
                [
                    speakers[speaker_data["code"]]
                    for speaker_data in submission_data["speakers"]
                ]
            )

    def update_talk(
        self,
        all_talks: MutableMapping[str, models.Talk],
        submission_data: dict[str, Any],
    ):
        code = submission_data["code"]
        talk = all_talks.get(code)

        if talk is None:
            self._talks_order += 10
            talk = models.Talk(
                is_public=False,
                is_backup=False,
                pretalx_code=code,
                order=self._talks_order,
            )
            all_talks[code] = talk

        talk.update_from_pretalx(submission_data)

    def update_workshop(
        self,
        all_workshops: MutableMapping[str, models.Workshop],
        submission_data: dict[str, Any],
    ):
        code = submission_data["code"]
        workshop = all_workshops.get(code)

        if workshop is None:
            self._workshops_order += 10
            workshop = models.Workshop(
                is_public=False,
                is_backup=False,
                pretalx_code=code,
                order=self._workshops_order,
            )
            all_workshops[code] = workshop

        workshop.update_from_pretalx(submission_data)