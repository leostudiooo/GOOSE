import json
import unittest
from datetime import datetime

from src.model import Track, Route
from src.model.track import TrackMetadata
from src.model.user import User, CustomTrack
from src.service.record_service import RecordService


class MockTrack(Track):
    def __init__(self, distance_km: float, duration_sec: int, track_str: str):
        super().__init__(
            track=[],
            metadata=TrackMetadata(
                totalDistance=0,
                formattedDistance="",
                totalTime=0,
                formattedTime="",
                sampleTimeInterval=0,
                pointCount=0,
                createdAt=datetime(2017, 1, 1),
            ),
        )
        self._distance_km = distance_km
        self._duration_sec = duration_sec
        self._track_str = track_str

    def get_distance_km(self) -> float:
        return self._distance_km

    def get_track_str(self) -> str:
        return self._track_str

    def get_duration_sec(self) -> int:
        return self._duration_sec


class TestRecordService(unittest.TestCase):
    track = MockTrack(distance_km=1, duration_sec=600, track_str="[Track]")
    route = Route(
        route_name="Test田径场",
        rule_id="25",
        plan_id="10",
        route_rule="Test校区",
        max_time=12,
        min_time=4,
        route_distance_km=1.2,
        rule_end_time="22:00",
        rule_start_time="06:00",
    )
    user = User(
        token="a.eyJ1c2VyaWQiOiAiMTIzIn0.a",
        date_time=datetime(2025, 1, 1, 19, 0, 0),
        finish_image="",
        route="",
        start_image="",
        custom_track=CustomTrack(enable=False, file_path=""),
    )
    service = RecordService(None, track, route, user)
    start_record_expected = (
        '{"routeName": "Test田径场", "ruleId": "25", "planId": "10", "recordTime": "2025-01-01",'
        ' "startTime": "19:00:00", "startImage": "A.jpg", "endTime": "", "exerciseTimes": "",'
        ' "routeKilometre": "", "endImage": "", "strLatitudeLongitude": [], "routeRule": "Test校区",'
        ' "maxTime": 12, "minTime": 4, "orouteKilometre": 1.2, "ruleEndTime": "22:00",'
        ' "ruleStartTime": "06:00", "calorie": 0, "speed": "0\'00\'\'", "dispTimeText": 0, "studentId": "123"}'
    )
    finish_record_expected = (
        '{"routeName": "Test田径场", "ruleId": "25", "planId": "10", '
        '"recordTime": "2025-01-01", "startTime": "19:00:00", "startImage": "A.jpg", '
        '"endTime": "19:10:00", "exerciseTimes": 600, "routeKilometre": "1.00", '
        '"endImage": "B.jpg", "strLatitudeLongitude": "[Track]", "routeRule": "Test校区", '
        '"maxTime": 12, "minTime": 4, "orouteKilometre": 1.2, "ruleEndTime": "22:00", '
        '"ruleStartTime": "06:00", "calorie": "62", "speed": "10\'0\'\'", '
        '"dispTimeText": "00:10:00", "studentId": "123", "id": "123", "nowStatus": 2}'
    )

    def test_get_start_record(self):
        start_record = self.service._get_start_record("A.jpg")
        start_record = json.dumps(start_record, ensure_ascii=False)
        self.assertEqual(self.start_record_expected, start_record)

    def test_get_finish_record(self):
        finish_record = self.service._get_finish_record("A.jpg", "B.jpg", "123")
        finish_record = json.dumps(finish_record, ensure_ascii=False)
        self.assertEqual(self.finish_record_expected, finish_record)


if __name__ == "__main__":
    unittest.main()
