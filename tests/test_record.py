import base64
import json
import unittest
from datetime import datetime

from src.model import Track
from src.model.record import Record
from src.model.route import Route
from src.model.track import TrackMetadata
from src.model.user import CustomTrack, User


class MockTrack(Track):
    def __init__(self):
        track = []
        metadata = TrackMetadata.model_validate(
            {
                "createdAt": datetime(2020, 1, 1),
                "formattedDistance": "1.23 公里",
                "formattedTime": "8 分 48 秒",
                "pointCount": 67,
                "sampleTimeInterval": 8,
                "totalDistance": 1232.3390303256608,
                "totalTime": 528,
            }
        )
        super().__init__(track=track, metadata=metadata)

    def get_distance_km(self) -> float:
        return 1.0

    def get_track_str(self) -> str:
        return "[Track]"

    def get_duration_sec(self) -> int:
        return 600


class TestRecord(unittest.TestCase):
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
    payload = base64.b64encode(json.dumps({"userid": "123"}).encode()).decode().rstrip("=")
    user = User(
        token=f"header.{payload}.sign",
        date_time=datetime(2025, 1, 1, 19, 0),
        finish_image="",
        route="",
        start_image="",
        custom_track=CustomTrack(),
    )
    record = Record(route=route, track=MockTrack(), user=user)
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
        start_record = self.record.get_start_record("A.jpg")
        start_record = json.dumps(start_record, ensure_ascii=False)
        self.assertEqual(self.start_record_expected, start_record)

    def test_get_finish_record(self):
        start_record = self.record.get_start_record("A.jpg")
        finish_record = self.record.get_finish_record(start_record, "B.jpg", "123")
        finish_record = json.dumps(finish_record, ensure_ascii=False)
        self.assertEqual(self.finish_record_expected, finish_record)


if __name__ == "__main__":
    unittest.main()
