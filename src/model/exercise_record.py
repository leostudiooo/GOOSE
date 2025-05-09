from dataclasses import dataclass
from datetime import timedelta
from typing import Any, ClassVar, Optional

from src.model.user_config import UserConfig
from src.model.route_info import RouteInfo
from src.model.track import Track


@dataclass
class ExerciseRecord:
    """ 运动记录的封装类, 这些数据将被发送到服务器 """
    route_info: RouteInfo
    user_config: UserConfig
    track: Track
    start_image: str
    end_image: str
    id: Optional[str] = None

    def _get_params(self):
        start_datetime = self.user_config.date_time
        duration_sec = self.user_config.duration
        duration = timedelta(seconds=duration_sec)
        distance_km = self.track.distance_km
        speed_sec = 0 if distance_km == 0 else int(round(duration_sec / distance_km))
        speed = f"{speed_sec // 60}'{speed_sec % 60}''"
        return {
            "strLatitudeLongitude": self.track.dump_json(),
            "recordTime": start_datetime.strftime("%Y-%m-%d"),
            "startTime": start_datetime.strftime("%H:%M:%S"),
            "endTime": (start_datetime + duration).strftime("%H:%M:%S"),
            "exerciseTimes": duration_sec,
            "routeKilometre": f"{distance_km:.2f}",
            "calorie": f"{62 * distance_km:.0f}",
            "speed": "0'00''" if speed_sec == 0 else speed,
            "dispTimeText": f"{duration_sec // 3600:02d}:{duration_sec // 60 % 60:02d}:{duration_sec % 60:02d}",
        }

    def _dump(self):
        record = self.route_info.model_dump(by_alias=True)
        record.update(self._get_params())
        record.update(
            {
                "studentId": self.user_config.student_id,
                "startImage": self.start_image,
                "endImage": self.end_image,
            }
        )

        return record

    def set_id(self, record_id: str):
        self.id = record_id

    def get_start_record(self) -> dict[str, Any]:
        record = self._dump()
        record.update(
            {
                "endTime": "",
                "exerciseTimes": "",
                "routeKilometre": "",
                "endImage": "",
                "strLatitudeLongitude": [],
                "calorie": 0,
                "speed": "0'00''",
                "dispTimeText": 0,
            }
        )
        record = {k: record[k] for k in self.key_order}
        assert all(v is not None for v in record.values()), "Parameters incomplete"
        return record

    def get_finish_record(self) -> dict[str, Any]:
        record = self._dump()
        record = {k: record[k] for k in self.key_order}
        record.update({"id": self.id, "nowStatus": 2})
        assert all(v is not None for v in record.values()), "Parameters incomplete"
        return record

    key_order: ClassVar = [
        "routeName",
        "ruleId",
        "planId",
        "recordTime",
        "startTime",
        "startImage",
        "endTime",
        "exerciseTimes",
        "routeKilometre",
        "endImage",
        "strLatitudeLongitude",
        "routeRule",
        "maxTime",
        "minTime",
        "orouteKilometre",
        "ruleEndTime",
        "ruleStartTime",
        "calorie",
        "speed",
        "dispTimeText",
        "studentId",
    ]
