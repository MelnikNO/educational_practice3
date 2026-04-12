import time
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class Link:
    to: str
    cost: int
    is_up: bool = True


class Router:
    def __init__(self, name: str):
        self.name = name
        self.links: Dict[str, Link] = {}
        self.routing_table: Dict[str, Tuple[str, int]] = {}
        self.logs = []

    def add_link(self, neighbor: str, cost: int):
        self.links[neighbor] = Link(to=neighbor, cost=cost)

    def set_link_down(self, neighbor: str):
        if neighbor in self.links:
            self.links[neighbor].is_up = False
            self.log(f"Link to {neighbor} is DOWN")
            self.trigger_update()

    def set_link_up(self, neighbor: str):
        if neighbor in self.links:
            self.links[neighbor].is_up = True
            self.log(f"Link to {neighbor} is UP")
            self.trigger_update()

    def log(self, msg: str):
        timestamp = time.time()
        self.logs.append((timestamp, msg))
        print(f"[{self.name}] {msg}")

    def trigger_update(self):
        """Вызывается при изменении топологии"""
        pass

    def get_routes(self) -> Dict[str, Tuple[str, int]]:
        return self.routing_table.copy()