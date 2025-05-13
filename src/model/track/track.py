import json

from pydantic import BaseModel

from src.model.track.track_metadata import TrackMetadata
from src.model.track.track_point import TrackPoint


class Track(BaseModel):
    """轨迹数据的封装类"""

    track: list[TrackPoint]
    metadata: TrackMetadata

    def get_distance_km(self) -> float:
        distance = 0.0
        for p1, p2 in zip(self.track[:-1], self.track[1:]):
            distance += p1.distance_with(p2)

        return distance

    def get_track_str(self) -> str:
        return json.dumps(self.model_dump()["track"])

    def get_duration_sec(self) -> int:
        return self.metadata.totalTime
