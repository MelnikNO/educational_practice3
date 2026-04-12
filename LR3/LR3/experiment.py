import time
import matplotlib.pyplot as plt
from rip_router import RIPRouter
from ospf_router import OSPFRouter


def run_convergence_test(RouterClass, name_prefix, topology, failure_link):
    """
    Запускает тест сходимости после отказа линка
    """
    routers = {}
    for r in topology['routers']:
        routers[r] = RouterClass(r)

    # Добавляем линки
    for a, b, cost in topology['links']:
        routers[a].add_link(b, cost)
        routers[b].add_link(a, cost)

    # Даём время на инициализацию
    time.sleep(2)

    # Фиксируем момент отказа
    start_time = time.time()
    r1, r2 = failure_link
    routers[r1].set_link_down(r2)
    routers[r2].set_link_down(r1)

    # Ждём появления маршрута между двумя удалёнными узлами
    convergence_detected = False
    check_interval = 0.1
    max_wait = 60

    waited = 0
    while not convergence_detected and waited < max_wait:
        time.sleep(check_interval)
        waited += check_interval

        table = routers['A'].get_routes()
        if 'E' in table and table['E'][1] < 100:
            convergence_detected = True

    convergence_time = (time.time() - start_time) * 1000

    total_logs = sum(len(r.logs) for r in routers.values())

    return convergence_time, total_logs


def main():
    topology = {
        'routers': ['A', 'B', 'C', 'D', 'E'],
        'links': [
            ('A', 'B', 1),
            ('B', 'C', 1),
            ('C', 'D', 1),
            ('D', 'E', 1),
            ('E', 'A', 5),
        ]
    }

    print("=== Пилотный эксперимент (Windows, Python) ===")
    print("Тестируем отказ линка B-C...")

    rip_time, rip_logs = run_convergence_test(RIPRouter, "RIP", topology, ('B', 'C'))
    ospf_time, ospf_logs = run_convergence_test(OSPFRouter, "OSPF", topology, ('B', 'C'))

    print(f"\nРезультаты:")
    print(f"RIP:  сходимость = {rip_time:.1f} ms, сообщений = {rip_logs}")
    print(f"OSPF: сходимость = {ospf_time:.1f} ms, сообщений = {ospf_logs}")

    labels = ['RIP', 'OSPF']
    times = [rip_time, ospf_time]

    plt.bar(labels, times, color=['red', 'green'])
    plt.ylabel('Convergence time (ms)')
    plt.title('Convergence after link failure')
    for i, v in enumerate(times):
        plt.text(i, v + 100, f"{v:.0f} ms", ha='center')

    plt.savefig('results/convergence.png')
    plt.show()

    print("\nГрафик сохранён в results/convergence.png")


if __name__ == "__main__":
    main()