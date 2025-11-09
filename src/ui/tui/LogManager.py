from collections import deque
import logging
from typing import List, Optional, Deque



class LogStore:
    """
    日志存储器，用于存储应用程序日志
    提供添加和获取日志的接口
    """
    
    def __init__(self, max_entries: int = 1000):
        """
        初始化日志存储
        
        参数:
            max_entries: 最大存储的日志条数
        """
        self.logs: Deque[str] = deque(maxlen=max_entries)
        
    def add_log(self, message: str) -> None:
        """
        添加一条日志
        
        参数:
            message: 日志消息
        """
        self.logs.append(message)
        
    def get_logs(self) -> List[str]:
        """获取所有存储的日志"""
        return list(self.logs)
        
    def clear(self) -> None:
        """清空所有日志"""
        self.logs.clear()


class LogHandler(logging.Handler):
    """
    日志处理器，将日志记录到 LogStore
    """
    
    def __init__(self, log_store: LogStore):
        """
        初始化日志处理器
        
        参数:
            log_store: 日志存储实例
        """
        super().__init__()
        self.log_store = log_store
        self.formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def emit(self, record: logging.LogRecord) -> None:
        """
        处理日志记录
        
        参数:
            record: 日志记录
        """
        log_entry = self.formatter.format(record)
        self.log_store.add_log(log_entry)


def setup_logging(log_store: Optional[LogStore] = None, 
                  notification_handler: Optional[logging.Handler] = None,
                  console: bool = False,
                  level: int = logging.INFO) -> LogStore:
    """
    设置应用日志系统
    
    参数:
        log_store: 日志存储实例，如果为None则创建新实例
        notification_handler: 通知处理器
        console: 是否添加控制台输出
        level: 日志级别
        
    返回:
        日志存储实例
    """
    # 如果未提供日志存储，则创建一个
    if log_store is None:
        log_store = LogStore()
        
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除已有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加日志存储处理器
    log_handler = LogHandler(log_store)
    root_logger.addHandler(log_handler)
    
    # 添加通知处理器(如果提供)
    if notification_handler is not None:
        root_logger.addHandler(notification_handler)
    
    # 添加控制台处理器(如果需要)
    if console:
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
    return log_store