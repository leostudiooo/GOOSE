from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from src.infrastructure.constants import CALORIE_PER_KM, RECORD_STATUS_FINISHED
from src.model.route import Route
from src.model.track import Track
from src.model.user import User


@dataclass(frozen=True)
class Record:
    route: Route
    track: Track
    user: User

    def get_start_record(self, start_image_url: str) -> dict[str, Any]:
        return {
            "routeName": self.route.route_name,
            "ruleId": self.route.rule_id,
            "planId": self.route.plan_id,
            "recordTime": self.user.date_time.strftime("%Y-%m-%d"),
            "startTime": self.user.date_time.strftime("%H:%M:%S"),
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

    def get_finish_record(self, start_record: dict[str, Any], finish_image_url: str, record_id: str) -> dict[str, Any]:
        distance_km = self.track.get_distance_km()
        duration_sec = self.track.get_duration_sec()
        pace_sec = 0 if distance_km == 0 else int(round(duration_sec / distance_km))

        record = start_record.copy()
        record_remaining = {
            "endTime": (self.user.date_time + timedelta(seconds=duration_sec)).strftime("%H:%M:%S"),
            "exerciseTimes": duration_sec,
            "routeKilometre": f"{distance_km:.2f}",
            "endImage": finish_image_url,
            "strLatitudeLongitude": self.track.get_track_str(),
            "calorie": f"{CALORIE_PER_KM * distance_km:.0f}",
            "speed": "0'00''" if pace_sec == 0 else f"{pace_sec // 60}'{pace_sec % 60}''",
            "dispTimeText": f"{duration_sec // 3600:02d}:{duration_sec // 60 % 60:02d}:{duration_sec % 60:02d}",
            "id": record_id,
            "nowStatus": RECORD_STATUS_FINISHED,
        }
        record.update(record_remaining)

        return record
