import logging
from pathlib import Path

from rich.logging import RichHandler

from src.infrastructure.exceptions import AppError
from src.service.main_service import Service

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
        service = Service(Path("config/"), Path("resources/default_tracks/"))
        service.upload()
    except AppError as e:
        logger.error(e.explain())
    except Exception as e:
        logger.error(f"出现未处理的异常: {e}")
