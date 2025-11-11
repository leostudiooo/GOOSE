import asyncio
import functools
import json
import logging
import random
import time
from io import BytesIO
from typing import Any, Callable

import aiohttp
import urllib3

from src.infrastructure.constants import (
    API_BASE_URL,
    API_CHECK_TENANT_PATH,
    API_CHECK_TOKEN_PATH,
    API_LIST_ROUTE_PATH,
    API_SAVE_RECORD_PATH,
    API_SAVE_START_RECORD_PATH,
    API_SUCCESS_CODE,
    API_UPLOAD_FINISH_IMAGE_PATH,
    API_UPLOAD_START_IMAGE_PATH,
    HEADER_ACCEPT,
    HEADER_ACCEPT_ENCODING,
    HEADER_ACCEPT_LANGUAGE,
    HEADER_CONTENT_TYPE_JSON,
    HEADER_CONTENT_TYPE_JSON_SIMPLE,
    HEADER_SEC_FETCH_DEST,
    HEADER_SEC_FETCH_MODE,
    HEADER_SEC_FETCH_SITE,
    HEADER_TOKEN_PREFIX,
    HEADER_XWEB_XHR,
    IMAGE_FILENAME,
    IMAGE_MIME_TYPE,
    REQUEST_MAX_DELAY_SEC,
    REQUEST_MIN_DELAY_SEC,
)
from src.infrastructure.exceptions import APIClientError, APIResponseError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 忽略SSL警告
urllib3.disable_warnings(UserWarning)  # 忽略用户警告


def api_wrapper(desc: str):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logging.info(f"正在{desc}")
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise APIClientError(desc) from e

        return wrapper

    return decorator


class APIClient:
    def __init__(self, ua: str, app_ver: str, referer: str, tenant: str, token: str):
        self._base_url = API_BASE_URL
        self._session = aiohttp.ClientSession()
        self._tenant = tenant
        self._headers = {
            "token": f"{HEADER_TOKEN_PREFIX}{token}",
            "miniappversion": app_ver,
            "User-Agent": ua,
            "tenant": self._tenant,
            "Referer": referer,
            "xweb_xhr": HEADER_XWEB_XHR,
            "Accept": HEADER_ACCEPT,
            "Sec-Fetch-Site": HEADER_SEC_FETCH_SITE,
            "Sec-Fetch-Mode": HEADER_SEC_FETCH_MODE,
            "Sec-Fetch-Dest": HEADER_SEC_FETCH_DEST,
            "Accept-Encoding": HEADER_ACCEPT_ENCODING,
            "Accept-Language": HEADER_ACCEPT_LANGUAGE,
        }

    @api_wrapper("检查tenant")
    async def check_tenant(self):
        """检查tenant是否有效"""
        url = f"{API_CHECK_TENANT_PATH}?tenantCode={self._tenant}"
        headers = self._headers.copy()
        headers.pop("tenant", "")
        headers.pop("token", "")
        headers["Content-Type"] = HEADER_CONTENT_TYPE_JSON

        await self._request(url, method="POST", headers=headers, json={})

    @api_wrapper("检查token")
    async def check_token(self):
        """检查token是否有效"""
        await self._request(
            url=API_CHECK_TOKEN_PATH,
            method="GET",
            headers=self._headers | {"Content-Type": HEADER_CONTENT_TYPE_JSON_SIMPLE},
            params={"para": "undefined"},
        )

    @api_wrapper("上传开始记录")
    async def upload_start_record(self, record: dict[str, Any]) -> str:
        """上传开始记录并返回记录ID"""
        result = await self._upload_record(record, API_SAVE_START_RECORD_PATH)
        return result.get("data", "")

    @api_wrapper("上传结束记录")
    async def upload_finish_record(self, record: dict[str, Any]) -> bool:
        """上传结束记录并返回一个布尔值, 表示是否上传成功"""
        result = await self._upload_record(record, API_SAVE_RECORD_PATH)
        return result.get("data", False)

    async def _upload_record(self, record: dict[str, Any], api_path: str) -> dict[str, Any]:
        response = await self._request(
            url=api_path,
            method="POST",
            headers=self._headers | {"Content-Type": HEADER_CONTENT_TYPE_JSON},
            data=json.dumps(record, ensure_ascii=False),
        )
        return await response.json()

    @api_wrapper("上传运动开始图片")
    async def upload_start_image(self, image_buffer: BytesIO) -> str:
        """上传运动开始图片并返回图片URL"""
        result = await self._upload_image(image_buffer, API_UPLOAD_START_IMAGE_PATH)
        return result.get("data", "")

    @api_wrapper("上传运动结束图片")
    async def upload_finish_image(self, image_buffer: BytesIO) -> str:
        """上传运动结束图片并返回图片URL"""
        result = await self._upload_image(image_buffer, API_UPLOAD_FINISH_IMAGE_PATH)
        return result.get("data", "")

    async def _upload_image(self, image_buffer: BytesIO, api_path: str) -> dict[str, Any]:
        response = await self._request(
            url=api_path,
            method="POST",
            headers=self._headers,
            files={"file": (IMAGE_FILENAME, image_buffer, IMAGE_MIME_TYPE)},
        )

        return await response.json()

    @api_wrapper("获取路线信息")
    async def get_all_route_info(self) -> dict[str, dict[str, Any]]:
        """获取所有路线信息, 返回一个字典, 格式为 {路线名: {路线信息}}"""
        response = await self._request(
            url=API_LIST_ROUTE_PATH,
            method="GET",
            headers=self._headers | {"Content-Type": HEADER_CONTENT_TYPE_JSON_SIMPLE},
        )
        data: list[dict] = (await response.json()).get("data", [])
        if len(data) == 0:
            raise ValueError("没有获取到可用路线")

        return {
            plan["routeName"]: {
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
            for rule in data
            for plan in rule["plans"]
        }

    async def _request(self, url: str, method: str = "POST", **kwargs):
        full_url = f"{self._base_url}{url}"
        logging.debug(f"正在向 '{full_url}' 发送 {method} 请求")

        await asyncio.sleep(
            random.uniform(REQUEST_MIN_DELAY_SEC, REQUEST_MAX_DELAY_SEC)
        )  # 添加随机延迟, 避免发送请求过快

        async with self._session.request(method, full_url, **kwargs) as response:
            logging.debug(f"来自 '{full_url}' 的响应状态码为 {response.status}")
            response_json = await response.json()
            code: int = response_json.get("code", 1 - (1 << 31))
            if code != API_SUCCESS_CODE:
                raise APIResponseError(str(response.url), code, response_json.get("msg", ""))

            logging.debug(f"来自 '{response.url}' 的响应: {response_json}")
            response.raise_for_status()

            return response
