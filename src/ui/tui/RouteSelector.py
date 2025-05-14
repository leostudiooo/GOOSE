from textual.widgets import Select
from textual import on
from pathlib import Path

# 直接引入Service类
from src.service.main_service import Service

class RouteSelector(Select):
    """路线选择组件"""
    
    def __init__(self, id="route"):
        super().__init__(id=id, options=[])
        self._routes = []
        # 直接创建Service实例，不依赖app
        self._service = Service(Path("config/"), Path("resources/default_tracks/"))
    
    def on_mount(self) -> None:
        """组件挂载时加载路线选项"""
        self.load_routes()
    
    def load_routes(self) -> None:
        """从服务加载可用的路线列表"""
        try:
            route_names = self._service.route_group_storage.load().get_route_names()
            self._routes = route_names
            route_options = [(name, name) for name in route_names]
            self.set_options(route_options)
            
        except Exception as e:
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