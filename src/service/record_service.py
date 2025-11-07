from typing import Any

from src.infrastructure import APIClient
from src.infrastructure.constants import RECORD_STATUS_FINISHED
from src.model import Exercise, Route, User


class RecordService:
    def __init__(self, api_client: APIClient, exercise: Exercise, route: Route, user: User):
        self._client = api_client
        self._exercise = exercise
        self._route = route
        self._user = user

    def get_start_record(self, start_image_url: str) -> dict[str, Any]:
        return {
            "routeName": self._route.route_name,
            "ruleId": self._route.rule_id,
            "planId": self._route.plan_id,
            "recordTime": self._exercise.record_date,
            "startTime": self._exercise.start_time,
            "startImage": start_image_url,
            "endTime": "",
            "exerciseTimes": "",
            "routeKilometre": "",
            "endImage": "",
            "strLatitudeLongitude": [],
            "routeRule": self._route.route_rule,
            "maxTime": self._route.max_time,
            "minTime": self._route.min_time,
            "orouteKilometre": self._route.route_distance_km,
            "ruleEndTime": self._route.rule_end_time,
            "ruleStartTime": self._route.rule_start_time,
            "calorie": 0,
            "speed": "0'00''",
            "dispTimeText": 0,
            "studentId": self._user.student_id,
        }

    def get_finish_record(self, start_image_url: str, finish_image_url: str, record_id: str) -> dict[str, Any]:
        record = self.get_start_record(start_image_url)
        record_remaining = {
            "endTime": self._exercise.end_time,
            "exerciseTimes": self._exercise.duration_sec,
            "routeKilometre": self._exercise.distance_km,
            "endImage": finish_image_url,
            "strLatitudeLongitude": self._exercise.track_str,
            "calorie": self._exercise.calorie,
            "speed": self._exercise.pace,
            "dispTimeText": self._exercise.time_text,
            "id": record_id,
            "nowStatus": RECORD_STATUS_FINISHED,
        }
        record.update(record_remaining)

        return record

    def upload(self) -> None:
        self._client.check_tenant()
        self._client.check_token()

        with open(self._user.start_image, "rb") as f:
            start_image_url = self._client.upload_start_image(f)

        start_record = self.get_start_record(start_image_url)
        record_id = self._client.upload_start_record(start_record)

        with open(self._user.finish_image, "rb") as f:
            finish_image_url = self._client.upload_finish_image(f)

        finish_record = self.get_finish_record(start_image_url, finish_image_url, record_id)
        self._client.upload_finish_record(finish_record)
