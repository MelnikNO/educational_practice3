from router import Router
import threading
import time
import heapq


class OSPFRouter(Router):
    def __init__(self, name: str, hello_interval: int = 5):
        super().__init__(name)
        self.hello_interval = hello_interval
        self.running = True
        self._start_hello()

    def _start_hello(self):
        def discover():
            time.sleep(1)
            while self.running:
                self._run_dijkstra()
                time.sleep(self.hello_interval)

        threading.Thread(target=discover, daemon=True).start()

    def _build_graph(self):
        """Строит граф топологии на основе известных связей"""
        graph = {self.name: {}}

        for neighbor, link in self.links.items():
            if link.is_up:
                graph[self.name][neighbor] = link.cost
                if neighbor not in graph:
                    graph[neighbor] = {}
                graph[neighbor][self.name] = link.cost

        return graph

    def _run_dijkstra(self):
        """Упрощённый Дейкстра на основе известной топологии"""
        graph = self._build_graph()

        if len(graph) <= 1:
            return

        distances = {node: float('inf') for node in graph}
        distances[self.name] = 0
        previous = {node: None for node in graph}
        pq = [(0, self.name)]

        while pq:
            dist, node = heapq.heappop(pq)
            if dist > distances[node]:
                continue
            for neighbor, cost in graph.get(node, {}).items():
                new_dist = dist + cost
                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                    previous[neighbor] = node
                    heapq.heappush(pq, (new_dist, neighbor))

        new_table = {}
        for dest in graph:
            if dest == self.name:
                continue
            if distances[dest] != float('inf'):
                hop = dest
                while previous.get(hop) != self.name and previous.get(hop) is not None:
                    hop = previous[hop]
                next_hop = hop if previous.get(hop) == self.name else dest
                new_table[dest] = (next_hop, int(distances[dest]))

        self.routing_table = new_table
        if new_table:
            self.log(f"Routes updated: {len(new_table)} destinations")

    def trigger_update(self):
        self._run_dijkstra()