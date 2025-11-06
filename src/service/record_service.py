from pathlib import Path
from typing import Any

from src.infrastructure import APIClient
from src.model import Exercise, Route, User


class RecordService:
    def __init__(self, api_client: APIClient, exercise: Exercise, route: Route, user: User):
        self.client = api_client
        self.exercise = exercise
        self.route = route
        self.user = user

    def get_start_record(self, start_image_url: str) -> dict[str, Any]:
        return {
            "routeName": self.route.route_name,
            "ruleId": self.route.rule_id,
            "planId": self.route.plan_id,
            "recordTime": self.exercise.record_date,
            "startTime": self.exercise.start_time,
            "startImage": start_image_url,
            "endTime": "",
            "exerciseTimes": "",
            "routeKilometre": "",
            "endImage": "",
            "strLatitudeLongitude": [],
            "routeRule": self.route.route_rule,
            "maxTime": self.route.max_time,
            "minTime": self.route.min_time,
            "orouteKilometre": self.route.route_distance_km,
            "ruleEndTime": self.route.rule_end_time,
            "ruleStartTime": self.route.rule_start_time,
            "calorie": 0,
            "speed": "0'00''",
            "dispTimeText": 0,
            "studentId": self.user.student_id,
        }

    def get_finish_record(self, start_image_url: str, finish_image_url: str, record_id: str) -> dict[str, Any]:
        record = self.get_start_record(start_image_url)
        record_remaining = {
            "endTime": self.exercise.end_time,
            "exerciseTimes": self.exercise.duration_sec,
            "routeKilometre": self.exercise.distance_km,
            "endImage": finish_image_url,
            "strLatitudeLongitude": self.exercise.track_str,
            "calorie": self.exercise.calorie,
            "speed": self.exercise.pace,
            "dispTimeText": self.exercise.time_text,
            "id": record_id,
            "nowStatus": 2,
        }
        record.update(record_remaining)

        return record

    def upload(self) -> None:
        self.client.check_tenant()
        self.client.check_token()

        with open(self.user.start_image, "rb") as f:
            start_image_url = self.client.upload_start_image(f)

        start_record = self.get_start_record(start_image_url)
        record_id = self.client.upload_start_record(start_record)

        with open(self.user.finish_image, "rb") as f:
            finish_image_url = self.client.upload_finish_image(f)

        finish_record = self.get_finish_record(start_image_url, finish_image_url, record_id)
        self.client.upload_finish_record(finish_record)
