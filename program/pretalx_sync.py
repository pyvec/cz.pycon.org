from collections import ChainMap
from collections.abc import Collection
from typing import MutableMapping, Any

from program import models
from program import pretalx


class PretalxSync:
    def __init__(self, pretalx_client: pretalx.PretalxClient) -> None:
        self.client = pretalx_client
        # Used for assigning unique order numbers to new talks/workshops
        self._talks_order = 0
        self._workshops_order = 0
        # Used assigning speakers when updating individual submissions
        self._existing_speakers: dict[str, models.Speaker] | None = None

    def update_speakers(self, speakers: Collection[models.Speaker]) -> None:
        """
        Fetches updated data for the given list of speakers and updates the database
        models.

        Note: this method currently performs 1 API call per speaker, therefore
        updating many speakers might take a long time and might cause the HTTP
        request to time-out.
        """
        for speaker in speakers:
            speaker_data = self.client.get_speaker(
                code=speaker.pretalx_code,
                questions=["all"],
            )
            speaker.update_from_pretalx(speaker_data)

        models.Speaker.objects.bulk_update(
            objs=speakers,
            fields=models.Speaker.PRETALX_FIELDS,
        )

    def update_talks(self, talks: Collection[models.Talk]) -> None:
        """
        Fetches updated data for the given list of talks and updates the database
        models.

        Note: this method currently performs 1 API call per talk, therefore
        updating many talks might take a long time and might cause the HTTP
        request to time-out.
        """
        for talk in talks:
            submission_data = self.client.get_submission(
                code=talk.pretalx_code,
                questions=["all"],
            )
            talk.update_from_pretalx(submission_data)
            talk.talk_speakers.set(
                [
                    self._get_or_fetch_speaker(speaker_data["code"])
                    for speaker_data in submission_data["speakers"]
                ]
            )

        models.Talk.objects.bulk_update(
            objs=talks,
            fields=models.Talk.PRETALX_FIELDS,
        )

    def update_workshops(self, workshops: Collection[models.Workshop]) -> None:
        """
        Fetches updated data for the given list of workshops and updates the database
        models.

        Note: this method currently performs 1 API call per workshop, therefore
        updating many workshops might take a long time and might cause the HTTP
        request to time-out.
        """
        for workshop in workshops:
            submission_data = self.client.get_submission(
                code=workshop.pretalx_code,
                questions=["all"],
            )
            workshop.update_from_pretalx(submission_data)
            workshop.workshop_speakers.set(
                [
                    self._get_or_fetch_speaker(speaker_data["code"])
                    for speaker_data in submission_data["speakers"]
                ]
            )

        models.Workshop.objects.bulk_update(
            objs=workshops,
            fields=models.Workshop.PRETALX_FIELDS,
        )

    def full_sync(self):
        """
        Performs full synchronization of speakers, talks and workshops. New entries
        are created when required, existing entries will be updated.

        This operation currently creates or updates only speakers with at least
        one confirmed submission.
        """
        submissions = self._fetch_submissions()
        confirmed_speaker_codes = self._extract_confirmed_speaker_codes(submissions)
        speakers = self._fetch_speakers_by_code(confirmed_speaker_codes)

        all_speakers = self._sync_speakers(speakers)
        self._sync_submissions(submissions, all_speakers)

    def _fetch_submissions(self) -> list[dict[str, Any]]:
        # `list_submissions` returns an iterable that can be iterated only once.
        # We want to use the list of confirmed submissions to filter speakers to update/create,
        # therefore we need to convert it to a list
        submissions = self.client.list_submissions(
            questions=["all"], states=[pretalx.SubmissionState.CONFIRMED]
        )
        submissions = list(submissions)
        return submissions

    def _extract_confirmed_speaker_codes(
        self, submissions: list[dict[str, Any]]
    ) -> set[str]:
        result = set()
        for submission in submissions:
            for speaker in submission["speakers"]:
                result.add(speaker["code"])
        return result

    def _fetch_speakers_by_code(self, speaker_codes) -> list[dict[str, Any]]:
        speakers = self.client.list_speakers(
            questions=["all"],
        )
        speakers = filter(
            lambda speaker_data: speaker_data["code"] in speaker_codes, speakers
        )
        return list(speakers)

    def _sync_speakers(self, speakers) -> dict[str, models.Speaker]:
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

    def _sync_submissions(
        self, submissions: list[dict[str, Any]], speakers: dict[str, models.Speaker]
    ):
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

        self._sync_talks(talks, speakers)
        self._sync_workshops(workshops, speakers)

    def _sync_talks(
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
            self._update_talk(all_talks, submission_data)

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

    def _sync_workshops(
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
            self._update_workshop(all_workshops, submission_data)

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

    def _update_talk(
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

    def _update_workshop(
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

    def _get_or_fetch_speaker(self, pretalx_code: str) -> models.Speaker:
        if self._existing_speakers is None:
            self._existing_speakers = models.Speaker.objects.filter(
                pretalx_code__isnull=False,
            ).in_bulk(field_name="pretalx_code")

        speaker = self._existing_speakers.get(pretalx_code)
        if speaker is None:
            speaker_data = self.client.get_speaker(
                code=pretalx_code,
                questions=["all"],
            )
            speaker = models.Speaker(
                is_public=False,
                pretalx_code=pretalx_code,
            )
            speaker.update_from_pretalx(speaker_data)
            speaker.save()
            self._existing_speakers[pretalx_code] = speaker

        return speaker
