import logging
import shutil
from datetime import datetime
from pathlib import Path

from src.infrastructure import (
    APIClient,
    FileHandler,
    JSONModelStorage,
    YAMLModelStorage,
)
from src.infrastructure.exceptions import AppError
from src.model import Exercise, Headers, Track, User, RouteGroup
from src.service.record_service import RecordService

logger = logging.getLogger(__name__)


class Service:
    """此类包含了各种供 CLI 和 GUI 使用的业务方法"""

    def __init__(self, config_dir: Path, default_tracks_dir: Path):
        sys_config_path = config_dir / "system.yaml"
        user_config_path = config_dir / "user.yaml"
        route_info_path = config_dir / "route_info.yaml"

        self.default_tracks_dir = default_tracks_dir
        self.route_group_storage = YAMLModelStorage(route_info_path, RouteGroup)
        self.headers_storage = YAMLModelStorage(sys_config_path, Headers)
        self.user_storage = YAMLModelStorage(user_config_path, User)

    def get_headers(self) -> Headers:
        """从系统配置文件读取请求头信息"""
        return self.headers_storage.load()

    def save_headers(self, headers: Headers):
        """保存请求头信息到系统配置文件"""
        self.headers_storage.save(headers)

    def get_user(self, use_default: bool = True) -> User:
        """从用户配置文件读取用户信息"""
        try:
            return self.user_storage.load()
        except Exception:
            if use_default:
                return User.get_default()
            raise

    def save_user(self, user: User):
        """保存用户信息到用户配置文件"""
        self.user_storage.save(user)

    def get_route_names(self) -> list[str]:
        """获取所有路线组中路线名称列表"""
        route_group = self.route_group_storage.load()
        return route_group.get_route_names()

    def validate(self):
        """
        验证系统配置文件和用户配置文件，并确保所有相关资源路径有效且数据合法, 同时验证 tenant 和 token.

        任一环节验证失败将会抛出 AppError 的子异常.
        """
        user, headers, _, _ = self._make_models()

        FileHandler(Path(user.start_image)).check_path()
        FileHandler(Path(user.finish_image)).check_path()

        client = self._make_client(user, headers)
        client.check_tenant()
        client.check_token()

    def upload(self):
        """
        加载并验证各种模型, 执行上传操作. 上传出现错误时将抛出 AppError 的子异常
        """
        user, headers, route, track = self._make_models()
        exercise = Exercise.get_from(user.date_time, track)

        client = self._make_client(user, headers)
        record_service = RecordService(client, exercise, route, user)
        record_service.upload()

    @staticmethod
    def _make_client(user: User, headers: Headers):
        return APIClient(
            headers.user_agent,
            headers.miniapp_version,
            str(headers.referer),
            headers.tenant,
            user.token,
        )

    def _make_models(self):
        user = self.user_storage.load()
        headers = self.headers_storage.load()
        route_group = self.route_group_storage.load()

        route = route_group.get_route(user.route)

        if user.custom_track_path == "":
            track_path = self.default_tracks_dir / f"{route.route_name}.json"
            logger.warning(f"未启用自定义轨迹, 将使用默认的轨迹文件 '{track_path}'")
        else:
            track_path = Path(user.custom_track_path)
        track = JSONModelStorage(track_path, Track).load()

        user.validate_token()

        return user, headers, route, track
