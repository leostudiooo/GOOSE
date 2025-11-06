from pydantic import BaseModel

from src.infrastructure.exceptions import RouteNotFoundError
from src.model.route import Route


class RouteGroup(BaseModel):
    """
    路线组模型
    
    管理多个运动路线，提供路线查询和验证功能。
    """
    routes: list[Route]

    def get_route(self, route_name: str) -> Route:
        """
        根据路线名称获取路线对象
        
        Args:
            route_name: 路线名称
            
        Returns:
            匹配的Route对象
            
        Raises:
            RouteNotFoundError: 当找不到指定名称的路线时
        """
        for route in self.routes:
            if route.route_name == route_name:
                return route
        raise RouteNotFoundError(route_name, self.get_route_names())

    def get_route_names(self) -> list[str]:
        """
        获取所有路线的名称列表
        
        Returns:
            路线名称列表
        """
        return [route.route_name for route in self.routes]
