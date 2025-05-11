import logging
from pathlib import Path

from src.infrastructure.file_handler import FileHandler
from src.infrastructure.api_client import APIClient
from src.infrastructure.model_handler import (
    dump_model_to_yaml,
    load_model_from_json,
    load_model_from_yaml,
)
from src.model.exercise import Exercise
from src.model.headers import Headers
from src.model.route import Route
from src.model.track import Track
from src.model.user import User
from src.service.record_service import RecordService

logger = logging.getLogger(__name__)


class Service:
    """此类包含了各种供 CLI 和 GUI 使用的业务方法"""

    def __init__(self):
        self.root_path = Path(__file__).parent.parent.parent
        self.sys_config_path = self.root_path / "config/system.yaml"
        self.user_config_path = self.root_path / "config/user.yaml"
        self.route_file_dir = self.root_path / "resources/route_info"

    def get_headers(self) -> Headers:
        """从系统配置文件读取请求头信息"""
        return load_model_from_yaml(self.sys_config_path, Headers)

    def save_headers(self, headers: Headers):
        """保存请求头信息到系统配置文件"""
        dump_model_to_yaml(self.sys_config_path, headers)

    def get_user(self) -> User:
        """从用户配置文件读取用户信息"""
        return load_model_from_yaml(self.user_config_path, User)

    def save_user(self, user: User):
        """保存用户信息到用户配置文件"""
        dump_model_to_yaml(self.user_config_path, user)

    def validate(self):
        """
        验证系统配置文件和用户配置文件，并确保所有相关资源路径有效且数据合法, 同时验证 tenant 和 token.

        任一环节验证失败将会抛出异常.
        """
        user = load_model_from_yaml(self.user_config_path, User)
        headers = load_model_from_yaml(self.sys_config_path, Headers)
        route_file_path = self.route_file_dir / f"{user.route}.json"
        load_model_from_json(route_file_path, Route)
        load_model_from_json(Path(user.custom_track), Track)

        FileHandler(Path(user.start_image)).check_path()
        FileHandler(Path(user.finish_image)).check_path()

        client = APIClient(headers, user.token)
        client.check_tenant()
        client.check_token()

    def upload(self):
        """
        加载并验证各种模型, 执行上传操作. 上传出现错误时将抛出异常
        """
        user = load_model_from_yaml(self.user_config_path, User)
        headers = load_model_from_yaml(self.sys_config_path, Headers)
        track = load_model_from_json(Path(user.custom_track), Track)

        route_file_path = self.route_file_dir / f"{user.route}.json"

        route = load_model_from_json(route_file_path, Route)
        exercise = Exercise.get_from(user.date_time, user.duration, track)

        client = APIClient(headers, user.token)
        record_service = RecordService(client, exercise, route, user)
        record_service.upload()
