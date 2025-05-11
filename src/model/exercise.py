from datetime import datetime, timedelta
from pydantic import BaseModel

from src.model.track import Track


class Exercise(BaseModel):
    track_str: str
    record_date: str
    start_time: str
    end_time: str
    duration_sec: int
    distance_km: str
    calorie: str
    pace: str
    time_text: str

    @classmethod
    def get_from(
        cls, date_time: datetime, duration_sec: int, track: Track
    ) -> "Exercise":
        distance_km = track.get_distance_km()
        duration = timedelta(seconds=duration_sec)
        pace_sec = 0 if distance_km == 0 else int(round(duration_sec / distance_km))
        pace = f"{pace_sec // 60}'{pace_sec % 60}''"
        return cls(
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
