import asyncio
import functools
import logging
from pathlib import Path
from typing import Callable, Optional

from src.infrastructure import APIClient, JSONModelStorage, YAMLModelStorage
from src.infrastructure.exceptions import AppError, ServiceError
from src.model import Headers, RouteGroup, Track, User
from src.model.record import Record
from src.model.route import Route


def service_wrapper(desc: str):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logging.info(f"正在{desc}")
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise ServiceError(desc) from e

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logging.info(f"正在{desc}")
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise ServiceError(desc) from e

        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper

    return decorator


class Service:
    """此类包含了各种供 CLI 和 GUI 使用的业务方法"""

    def __init__(
        self,
        route_group_storage: Optional[YAMLModelStorage[RouteGroup]] = None,
        headers_storage: Optional[YAMLModelStorage[Headers]] = None,
        user_storage: Optional[YAMLModelStorage[User]] = None,
        track_storage: Optional[JSONModelStorage[Track]] = None,
    ):
        self._route_group_storage = route_group_storage or YAMLModelStorage(
            Path("config/"), RouteGroup
        )
        self._headers_storage = headers_storage or YAMLModelStorage(Path("config/"), Headers)
        self._user_storage = user_storage or YAMLModelStorage(Path("config/"), User)
        self._track_storage = track_storage or JSONModelStorage(
            Path("resources/default_tracks/"), Track
        )

    @service_wrapper("加载用户配置")
    def get_user(self, default: Optional[User] = None) -> User:
        """从用户配置文件读取用户信息"""
        try:
            return self._user_storage.load("user")
        except AppError:
            if default is None:
                raise
            logging.warning("无法加载用户配置, 将使用默认的用户配置")
            return default

    @service_wrapper("保存用户配置")
    def save_user(self, user: User):
        """保存用户信息到用户配置文件"""
        self._user_storage.save("user", user)

    @service_wrapper("加载路线名称列表")
    def get_route_names(self) -> list[str]:
        """获取所有路线组中路线名称列表"""
        route_group = self._route_group_storage.load("route_group")
        return route_group.get_route_names()

    @service_wrapper("验证系统配置和用户配置")
    async def validate(self) -> tuple[User, Headers, Route, Track]:
        """
        验证系统配置文件和用户配置文件，并确保所有相关资源路径有效且数据合法, 同时验证 tenant 和 token.
        验证后返回用户信息和 APIClient 实例
        任何一个环节验证失败将会抛出 AppError 的子异常.
        """
        user = self._user_storage.load("user")
        headers = self._headers_storage.load("headers")

        user.decode_token()

        open(user.start_image, "rb").close()
        open(user.finish_image, "rb").close()

        route = self._route_group_storage.load("route_group").get_route(user.route)
        track = self._get_track(route.route_name, user.custom_track_path)

        async with self._construct_client(user, headers) as client:
            await client.check_tenant()
            await client.check_token()

        return user, headers, route, track

    @service_wrapper("上传运动记录")
    async def upload(self):
        """
        加载并验证各种模型, 执行上传操作. 上传出现错误时将抛出 AppError 的子异常
        """
        user, headers, route, track = await self.validate()
        record = Record(route, track, user)

        async with self._construct_client(user, headers) as client:
            with open(user.start_image, "rb") as f:
                start_image_url = await client.upload_start_image(f)
            start_record = record.get_start_record(start_image_url)
            record_id = await client.upload_start_record(start_record)

            with open(user.finish_image, "rb") as f:
                finish_image_url = await client.upload_finish_image(f)
            finish_record = record.get_finish_record(start_record, finish_image_url, record_id)
            await client.upload_finish_record(finish_record)

    def _get_track(self, route_name: str, custom_track_path: str) -> Track:
        if custom_track_path == "":
            logging.warning("未启用自定义轨迹, 将使用默认的轨迹文件")
            track = self._track_storage.load(route_name)
        else:
            track_path = Path(custom_track_path)
            track = self._track_storage.with_file_dir(track_path.parent).load(track_path.stem)
        return track

    @staticmethod
    def _construct_client(user: User, headers: Headers):
        return APIClient(
            headers.user_agent, headers.miniapp_version, headers.referer, headers.tenant, user.token
        )
