"""
Open SEU Exercise CLI: 东南大学体育锻炼助手命令行版本
Copyright (c) 2025 Leo Li

This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging

from rich.logging import RichHandler

from src.core.exceptions import AppError
from src.service.service import Service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    handlers=[RichHandler(omit_repeated_times=False, rich_tracebacks=True)],
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        service = Service()
        service.do_upload()
    except AppError as e:
        logger.exception(e.explain())
    except Exception as e:
        logger.exception("出现未处理的异常")
