from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, NamedTuple

from src.infrastructure import APIClient, FileHandler
from src.model import Route, User, Track


class Exercise(NamedTuple):
    track_str: str
    record_date: str
    start_time: str
    end_time: str
    duration_sec: int
    distance_km: str
    calorie: str
    pace: str
    time_text: str


class RecordService:
    def __init__(self, api_client: APIClient, track: Track, route: Route, user: User):
        self._client = api_client
        self._route = route
        self._user = user
        self._exercise = self._get_exercise_info(user.date_time, track)

    @staticmethod
    def _get_exercise_info(date_time: datetime, track: Track) -> Exercise:
        distance_km = track.get_distance_km()
        duration_sec = track.get_duration_sec()
        duration = timedelta(seconds=duration_sec)
        pace_sec = 0 if distance_km == 0 else int(round(duration_sec / distance_km))
        pace = f"{pace_sec // 60}'{pace_sec % 60}''"
        return Exercise(
            track_str=track.get_track_str(),
            record_date=date_time.strftime("%Y-%m-%d"),
            start_time=date_time.strftime("%H:%M:%S"),
            end_time=(date_time + duration).strftime("%H:%M:%S"),
            duration_sec=duration_sec,
            distance_km=f"{distance_km:.2f}",
            calorie=f"{62 * distance_km:.0f}",
            pace="0'00''" if pace_sec == 0 else pace,
            time_text=f"{duration_sec // 3600:02d}:{duration_sec // 60 % 60:02d}:{duration_sec % 60:02d}",
        )

    def _get_start_record(self, start_image_url: str) -> dict[str, Any]:
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

    def _get_finish_record(
        self, start_image_url: str, finish_image_url: str, record_id: str
    ) -> dict[str, Any]:
        record = self._get_start_record(start_image_url)
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
            "nowStatus": 2,
        }
        record.update(record_remaining)

        return record

    def upload(self) -> None:
        self._client.check_tenant()
        self._client.check_token()

        with FileHandler(Path(self._user.start_image), "rb", None) as f:
            start_image_url = self._client.upload_start_image(f)

        start_record = self._get_start_record(start_image_url)
        record_id = self._client.upload_start_record(start_record)

        with FileHandler(Path(self._user.finish_image), "rb", None) as f:
            finish_image_url = self._client.upload_finish_image(f)

        finish_record = self._get_finish_record(
            start_image_url, finish_image_url, record_id
        )
        self._client.upload_finish_record(finish_record)
