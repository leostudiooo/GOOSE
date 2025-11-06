from datetime import datetime, timedelta
from pydantic import BaseModel

from src.infrastructure.constants import CALORIE_PER_KM
from src.model.track import Track


class Exercise(BaseModel):
    """
    运动记录模型
    
    包含一次完整运动的所有数据，包括轨迹、时间、距离、卡路里等。
    """
    track_str: str  # 轨迹数据的JSON字符串
    record_date: str  # 记录日期 (YYYY-MM-DD)
    start_time: str  # 开始时间 (HH:MM:SS)
    end_time: str  # 结束时间 (HH:MM:SS)
    duration_sec: int  # 持续时间（秒）
    distance_km: str  # 距离（公里）
    calorie: str  # 消耗卡路里
    pace: str  # 配速 (分'秒'')
    time_text: str  # 时间文本 (HH:MM:SS)

    @classmethod
    def get_from(cls, date_time: datetime, track: Track) -> "Exercise":
        """
        从时间和轨迹数据创建运动记录
        
        根据提供的开始时间和轨迹数据，计算所有运动指标。
        
        Args:
            date_time: 运动开始时间
            track: 运动轨迹数据
            
        Returns:
            完整的Exercise对象
        """
        distance_km = track.get_distance_km()
        duration_sec = track.get_duration_sec()
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
            calorie=f"{CALORIE_PER_KM * distance_km:.0f}",
            pace="0'00''" if pace_sec == 0 else pace,
            time_text=f"{duration_sec // 3600:02d}:{duration_sec // 60 % 60:02d}:{duration_sec % 60:02d}",
        )
