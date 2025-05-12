from pydantic import BaseModel

from src.infrastructure.exceptions import RouteNotFoundError
from src.model.route import Route


class RouteGroup(BaseModel):
    routes: list[Route]

    def get_route(self, route_name: str):
        for route in self.routes:
            if route.route_name == route_name:
                return route
        raise RouteNotFoundError(route_name, self.get_route_names())

    def get_route_names(self) -> list[str]:
        return [route.route_name for route in self.routes]
