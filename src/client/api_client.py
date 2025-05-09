import functools
import json
import logging
import os
import random
import time
from typing import Any, Callable

import requests
import urllib3

from src.core.exceptions import (
    APIClientError,
    AppError,
    APIResponseError,
)
from src.core.file_tools import validate_jpg
from src.model.route_info import RouteInfo
from src.model.system_config import SystemConfig

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 忽略SSL警告
urllib3.disable_warnings(UserWarning)  # 忽略用户警告

logger = logging.getLogger(__name__)


def api_wrapper(desc: str):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"正在{desc}")
            try:
                return func(*args, **kwargs)
            except AppError:
                raise
            except Exception as e:
                raise APIClientError(desc) from e

        return wrapper

    return decorator


class APIClient:
    def __init__(self, sys_config: SystemConfig, token: str):
        self._base_url = f"https://tyxsjpt.seu.edu.cn"
        self._session = requests.Session()
        self._session.verify = False

        self._tenant = sys_config.tenant
        self._headers = {
            "token": f"Bearer {token}",
            "miniappversion": sys_config.miniapp_version,
            "User-Agent": sys_config.user_agent,
            "tenant": self._tenant,
            "Referer": f"https://{sys_config.referer}",
            "xweb_xhr": "1",
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

    def set_token(self, token: str):
        self._headers["token"] = f"Bearer {token}"

    @api_wrapper("检查tenant")
    def check_tenant(self):
        """检查tenant是否有效"""
        url = f"/api/miniapp/anno/checkTenant?tenantCode={self._tenant}"
        headers = self._headers.copy()
        headers.pop("tenant", "")
        headers.pop("token", "")
        headers["Content-Type"] = "application/json;charset=UTF-8"

        self._request(url, method="POST", headers=headers, json={})

    @api_wrapper("检查token")
    def check_token(self):
        """检查token是否有效"""
        self._request(
            url="/api/miniapp/student/checkToken",
            method="GET",
            headers=self._headers | {"Content-Type": "application/json"},
            params={"para": "undefined"},
        )

    @api_wrapper("上传开始记录")
    def upload_start_record(self, record: dict[str, Any]) -> str:
        """上传开始记录并返回记录ID"""
        return self._upload_record(record, "saveStartRecord").get("data", "")

    @api_wrapper("上传结束记录")
    def upload_finish_record(self, record: dict[str, Any]) -> bool:
        """上传结束记录并返回一个布尔值, 表示是否上传成功"""
        return self._upload_record(record, "saveRecord").get("data", False)

    @api_wrapper("上传运动开始图片")
    def upload_start_image(self, image_path: str) -> str:
        """上传运动开始图片并返回图片URL"""
        return self._upload_image(image_path, "uploadRecordImage")

    @api_wrapper("上传运动结束图片")
    def upload_finish_image(self, image_path: str) -> str:
        """上传运动结束图片并返回图片URL"""
        return self._upload_image(image_path, "uploadRecordImage2")

    @api_wrapper("获取路线信息")
    def get_all_route_info(self) -> dict[str, RouteInfo]:
        """获取所有路线信息, 返回一个字典, 格式为 {路线名: 路线信息}"""
        response = self._request(
            url="/api/miniapp/exercise/listRule",
            method="GET",
            headers=self._headers | {"Content-Type": "application/json"},
        )
        data: list[dict] = response.json().get("data", [])
        if len(data) == 0:
            raise ValueError("没有获取到可用路线")

        return {
            plan["routeName"]: RouteInfo.model_validate(
                {
                    "route_name": plan["routeName"],
                    "rule_id": rule["ruleId"],
                    "plan_id": plan["planId"],
                    "route_rule": rule["routeRule"],
                    "max_time": plan["maxTime"],
                    "min_time": plan["minTime"],
                    "route_distance_km": plan["routeKilometre"],
                    "rule_end_time": rule["ruleEndTime"],
                    "rule_start_time": rule["ruleStartTime"],
                }
            )
            for rule in data
            for plan in rule["plans"]
        }

    def _upload_record(self, record: dict[str, Any], api_name: str) -> dict[str, Any]:
        response = self._request(
            url=f"/api/exercise/exerciseRecord/{api_name}",
            method="POST",
            headers=self._headers | {"Content-Type": "application/json;charset=UTF-8"},
            data=json.dumps(record, ensure_ascii=False),
        )
        return response.json()

    def _upload_image(self, image_path: str, api_name: str) -> str:
        validate_jpg(image_path)
        with open(image_path, "rb") as file:
            response = self._request(
                url=f"/api/miniapp/exercise/{api_name}",
                method="POST",
                headers=self._headers,
                files={"file": (os.path.basename(image_path), file, "image/jpeg")},
            )

        return response.json().get("data", "")

    def _request(self, url: str, method: str = "POST", **kwargs):
        full_url = f"{self._base_url}{url}"
        logger.debug(f"正在向 '{full_url}' 发送 {method} 请求")

        time.sleep(random.uniform(1.5, 3.5))  # 添加随机延迟, 避免发送请求过快
        response = self._session.request(method, full_url, **kwargs)

        logger.debug(f"来自 '{full_url}' 的响应状态码为 {response.status_code}")
        response_json = response.json()
        code: int = response_json.get("code", 1 - (1 << 31))

        if code != 0:
            raise APIResponseError(response.url, code, response_json.get("msg", ""))
        logger.debug(f"来自 '{response.url}' 的响应: {response_json}")
        response.raise_for_status()

        return response
