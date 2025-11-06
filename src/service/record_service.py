from pathlib import Path
from typing import Any

from src.infrastructure import APIClient, FileHandler
from src.infrastructure.constants import RECORD_STATUS_FINISHED
from src.model import Exercise, Route, User


class RecordService:
    """
    运动记录上传服务
    
    负责协调运动记录的上传流程，包括图片上传和记录数据的提交。
    """
    
    def __init__(
        self, api_client: APIClient, exercise: Exercise, route: Route, user: User
    ):
        """
        初始化记录服务
        
        Args:
            api_client: API客户端实例
            exercise: 运动记录数据
            route: 运动路线信息
            user: 用户信息
        """
        self.client = api_client
        self.exercise = exercise
        self.route = route
        self.user = user

    def get_start_record(self, start_image_url: str) -> dict[str, Any]:
        """
        构建开始运动记录的数据
        
        Args:
            start_image_url: 开始运动的图片URL
            
        Returns:
            包含开始记录所有必需字段的字典
        """
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

    def get_finish_record(
        self, start_image_url: str, finish_image_url: str, record_id: str
    ) -> dict[str, Any]:
        """
        构建完成运动记录的数据
        
        Args:
            start_image_url: 开始运动的图片URL
            finish_image_url: 结束运动的图片URL
            record_id: 服务器返回的记录ID
            
        Returns:
            包含完整运动记录所有字段的字典
        """
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
            "nowStatus": RECORD_STATUS_FINISHED,
        }
        record.update(record_remaining)

        return record

    def upload(self) -> None:
        """
        执行完整的运动记录上传流程
        
        流程包括：
        1. 验证tenant和token
        2. 上传开始图片
        3. 提交开始记录
        4. 上传结束图片
        5. 提交完成记录
        
        Raises:
            APIClientError: 当API请求失败时
            FileHandlerError: 当图片文件无法读取时
            APIResponseError: 当服务器返回错误响应时
        """
        self.client.check_tenant()
        self.client.check_token()

        with FileHandler(Path(self.user.start_image), "rb", None) as f:
            start_image_url = self.client.upload_start_image(f)

        start_record = self.get_start_record(start_image_url)
        record_id = self.client.upload_start_record(start_record)

        with FileHandler(Path(self.user.finish_image), "rb", None) as f:
            finish_image_url = self.client.upload_finish_image(f)

        finish_record = self.get_finish_record(
            start_image_url, finish_image_url, record_id
        )
        self.client.upload_finish_record(finish_record)
