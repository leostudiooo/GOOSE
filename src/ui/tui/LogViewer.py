import logging
import time
from collections import deque
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Button, Label, Static, Header
from textual.reactive import reactive

class LogHandler(logging.Handler):
    """自定义日志处理器，用于存储最近的日志记录"""

    def __init__(self, max_entries=1000):
        super().__init__()
        self.logs = deque(maxlen=max_entries)
        self.formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    
    def emit(self, record):
        log_entry = self.formatter.format(record)
        self.logs.append(log_entry)

# 创建全局日志处理器实例
log_handler = LogHandler()
logging.getLogger().addHandler(log_handler)

class LogViewer(Container):
    """日志查看器组件"""
    
    DEFAULT_CSS = """
    LogViewer {
        background: $surface-darken-1;
        padding: 1;
        border: solid $primary;
    }
    
    #log_header {
        dock: top;
        height: 3;
        padding: 0 1;
        background: $primary;
        color: $text;
    }
    
    #log_title {
        color: $text;
        text-style: bold;
        content-align: center middle;
    }
    
    #close_button {
        dock: right;
    }
    
    #log_container {
        height: 1fr;
        overflow-y: auto;
        margin: 1 0;
    }
    
    #log_content {
        width: 100%;
        height: auto;
        color: $text;
        overflow: hidden;
    }
    
    #refresh_button {
        dock: bottom;
        width: 100%;
    }
    """
    
    is_visible = reactive(False)
    
    def __init__(self, id="log_viewer"):
        super().__init__(id=id)
        
    def compose(self) -> ComposeResult:
        """创建日志查看器的布局"""
        with Container(id="log_header"):
            yield Label("日志查看器", id="log_title")
            yield Button("关闭", id="close_button", variant="error")
        
        with ScrollableContainer(id="log_container"):
            yield Static("", id="log_content")
        
        yield Button("刷新日志", id="refresh_button", variant="primary")
    
    def on_mount(self) -> None:
        """组件挂载时刷新日志"""
        self.refresh_logs()
    
    def toggle(self) -> None:
        """切换日志查看器的可见性"""
        self.is_visible = not self.is_visible
        if self.is_visible:
            self.add_class("visible")
            self.refresh_logs()
        else:
            self.remove_class("visible")
    
    def refresh_logs(self) -> None:
        """刷新日志内容"""
        log_content = self.query_one("#log_content")
        log_container = self.query_one("#log_container")
        
        # 合并所有日志条目并显示
        log_text = "\n".join(log_handler.logs)
        log_content.update(log_text if log_text else "暂无日志记录")
        
        # 自动滚动到最新日志
        log_container.scroll_end()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        button_id = event.button.id
        
        if button_id == "close_button":
            self.toggle()
        elif button_id == "refresh_button":
            self.refresh_logs()