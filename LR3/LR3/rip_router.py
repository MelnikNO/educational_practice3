from router import Router
import threading
import time
from typing import Dict


class RIPRouter(Router):
    def __init__(self, name: str, update_interval: int = 30, invalid_timer: int = 180):
        super().__init__(name)
        self.update_interval = update_interval
        self.invalid_timer = invalid_timer
        self.neighbor_last_heard: Dict[str, float] = {}
        self.running = True
        self._start_timers()

    def _start_timers(self):
        def periodic_updates():
            while self.running:
                time.sleep(self.update_interval)
                self._send_routing_table()

        def check_neighbors():
            while self.running:
                time.sleep(5)
                now = time.time()
                for neighbor, last in list(self.neighbor_last_heard.items()):
                    if now - last > self.invalid_timer:
                        self.log(f"Neighbor {neighbor} timed out")
                        if neighbor in self.links:
                            self.links[neighbor].is_up = False
                            self._remove_routes_via(neighbor)

        threading.Thread(target=periodic_updates, daemon=True).start()
        threading.Thread(target=check_neighbors, daemon=True).start()

    def _send_routing_table(self):
        """Отправляет таблицу маршрутизации всем соседям"""
        for neighbor, link in self.links.items():
            if not link.is_up:
                continue
            # Симуляция отправки: обновляем метку времени
            self.neighbor_last_heard[neighbor] = time.time()

    def _remove_routes_via(self, neighbor: str):
        """Удаляет маршруты, которые идут через упавшего соседа"""
        to_remove = []
        for dest, (next_hop, _) in self.routing_table.items():
            if next_hop == neighbor:
                to_remove.append(dest)
        for dest in to_remove:
            del self.routing_table[dest]

    def trigger_update(self):
        """При изменении топологии отправляем update немедленно"""
        self._send_routing_table()

    def receive_update(self, from_neighbor: str, routes: dict):
        """Получение обновления от соседа"""
        if from_neighbor not in self.links:
            self.log(f"Ignoring update from unknown neighbor {from_neighbor}")
            return

        if not self.links[from_neighbor].is_up:
            self.log(f"Ignoring update from {from_neighbor} (link is down)")
            return

        self.neighbor_last_heard[from_neighbor] = time.time()

        for dest, cost in routes.items():
            new_cost = cost + self.links[from_neighbor].cost
            current = self.routing_table.get(dest)

            if dest not in self.routing_table or new_cost < current[1]:
                self.routing_table[dest] = (from_neighbor, new_cost)
                self.log(f"Route to {dest} updated: via {from_neighbor}, cost {new_cost}")