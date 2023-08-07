import urllib.parse
from enum import Enum
from typing import Iterable, Any

import requests
from django.conf import settings
from requests.auth import AuthBase

DEFAULT_API_BASE_URL = "https://pretalx.com/api/"
DEFAULT_LIMIT = 50


def create_pretalx_client() -> "PretalxClient":
    return PretalxClient(
        event_slug=settings.PRETALX_EVENT_SLUG,
        token=settings.PRETALX_TOKEN,
    )


class AnswersCollection:
    def __init__(self, answers: list[dict[str, Any]]) -> None:
        self.answers = self._preprocess_answers(answers)

    def get_answer(self, question_text: str) -> str:
        return self.answers.get(question_text.casefold(), "")

    def get_mapped_answer(self, question_text: str, value_map: dict[str, str]) -> str:
        value = self.get_answer(question_text)
        return value_map.get(value.casefold(), "")

    def _preprocess_answers(self, answers: list[dict[str, Any]]) -> dict[str, str]:
        result = {}
        for answer in answers:
            question_text: str = answer["question"]["question"]["en"]
            result[question_text.casefold()] = answer["answer"]
        return result


class SubmissionState(Enum):
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CONFIRMED = "confirmed"


class PretalxTokenAuth(AuthBase):
    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("pretalx token cannot be empty.")
        self.token = token

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.headers["Authorization"] = f"Token {self.token}"
        return request


class PretalxClient:
    def __init__(
        self,
        event_slug: str,
        token: str,
        api_base_url: str = DEFAULT_API_BASE_URL,
    ):
        self.event_slug = event_slug
        self._auth = PretalxTokenAuth(token)
        self.api_base_url = api_base_url.rstrip(
            "/"
        )  # ensure there is no trailing slash

    def list_submissions(
        self,
        questions: list[str | int] | None = None,
        states: list[SubmissionState] | None = None,
        limit: int = DEFAULT_LIMIT,
    ) -> Iterable[dict[str, Any]]:
        params = {}
        if states:
            params["state"] = [state.value for state in states]
        if questions:
            params["questions"] = ",".join(str(question) for question in questions)

        return self._paginate_results(
            endpoint="submissions/",
            query_params=params,
            limit=limit,
        )

    def get_submission(
        self, code: str, questions: list[str | int] | None = None
    ) -> dict[str, Any]:
        params = {}
        if questions:
            params["questions"] = ",".join(str(question) for question in questions)

        return self._call_endpoint(
            method="GET",
            endpoint=f"submissions/{urllib.parse.quote(code)}",
            query_params=params,
        )

    def list_speakers(
        self,
        questions: list[str | int] | None = None,
        limit: int = DEFAULT_LIMIT,
    ):
        params = {}
        if questions:
            params["questions"] = ",".join(str(question) for question in questions)

        return self._paginate_results(
            endpoint="speakers/",
            query_params=params,
            limit=limit,
        )

    def get_speaker(
        self, code: str, questions: list[str | int] | None = None
    ) -> dict[str, Any]:
        params = {}
        if questions:
            params["questions"] = ",".join(str(question) for question in questions)

        return self._call_endpoint(
            method="GET",
            endpoint=f"speakers/{urllib.parse.quote(code)}",
            query_params=params,
        )

    def _paginate_results(
        self,
        endpoint: str,
        query_params: dict[str, Any] | None = None,
        limit: int = DEFAULT_LIMIT,
    ) -> Iterable[dict[str, Any]]:
        next_page_url = self._format_endpoint_url(endpoint)
        next_query_params = query_params if query_params is not None else {}
        next_query_params["limit"] = limit

        while next_page_url is not None:
            with self._do_request(
                method="GET",
                url=next_page_url,
                query_params=next_query_params,
            ) as response:
                response.raise_for_status()

                response_data = response.json()
                yield from response_data["results"]

                next_page_url = response_data["next"]
                # The URL of the next page already includes query parameters, do not send them.
                next_query_params = None

    def _call_endpoint(
        self, method: str, endpoint: str, query_params: dict[str, Any] | None = None
    ):
        with self._do_request(
            method=method,
            url=self._format_endpoint_url(endpoint),
            query_params=query_params,
        ) as response:
            response.raise_for_status()
            return response.json()

    def _format_endpoint_url(self, endpoint: str) -> str:
        return f"{self.api_base_url}/events/{urllib.parse.quote(self.event_slug)}/{endpoint}"

    def _do_request(
        self,
        method: str,
        url: str,
        query_params: dict[str, Any] | None = None,
    ):
        return requests.request(
            method=method,
            url=url,
            params=query_params,
            headers={
                "Accept": "application/json",
            },
            auth=self._auth,
            timeout=60,
        )
