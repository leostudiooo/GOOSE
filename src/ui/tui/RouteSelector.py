from textual.widgets import Select, Label
from textual.app import ComposeResult
from textual.containers import Vertical
from pathlib import Path

import logging

# 直接引入Service类
from src.service.main_service import Service

class RouteSelector(Vertical):
    """路线选择组件容器"""

    DEFAULT_CSS = """
    RouteSelector {
        margin: 1;
        height: auto;
    }
    
    RouteSelector Label {
        width: auto;
        margin: 1 0;
        text-style: bold;
    }
    """
    
    def __init__(self, id="route_container"):
        super().__init__(id=id)
        self._routes = []
        # 直接创建Service实例，不依赖app
        self._service = Service(Path("config/"), Path("resources/default_tracks/"))

    def compose(self) -> ComposeResult:
        """创建组件"""
        yield Label("选择路线", id="route_label")
        yield Select(id="route_select", options=[])
    
    def on_mount(self):
        """组件挂载时加载路线选项"""
        self.load_routes()
    
    def load_routes(self):
        """从服务加载可用的路线列表"""
        try:
            route_names = self._service.route_group_storage.load().get_route_names()
            self._routes = route_names
            route_options = [(name, name) for name in route_names]
            self.query_one(Select).set_options(route_options)
            
        except Exception as e:
            logging.error(f"加载路线列表失败: {e}")
            # 错误处理
            if hasattr(self.app, 'notify'):
                self.app.notify(f"加载路线列表失败: {e}", severity="error")
            else:
                print(f"加载路线列表失败: {e}")
    
    def get_route_info(self, route_name):
        """获取特定路线的信息"""
        if route_name in self._routes:
            return self._routes[route_name]
        return None