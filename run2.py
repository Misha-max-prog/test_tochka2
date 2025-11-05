from collections import deque
import sys
import copy

# проверка на шлюз
def is_gateway(node):
    return node.isupper()

# строим граф
def build_graph(edges):
    graph = {}
    for u, v in edges:
        if u not in graph:
            graph[u] = set()
        if v not in graph:
            graph[v] = set()
        graph[u].add(v)
        graph[v].add(u)
    return graph

# бфс от состояния до шлюзов
def bfs_distances(start, graph):
    distances = {start: 0}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for neighbor in graph.get(current, set()):
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)

    return distances

# следующий шлюз куда идет вирус
def find_target_gateway(virus_pos, graph):
    distances = bfs_distances(virus_pos, graph)
    gateways = [node for node in graph if is_gateway(node)]

    reachable_gateways = []
    for gateway in gateways:
        if gateway in distances:
            reachable_gateways.append((distances[gateway], gateway))

    if not reachable_gateways:
        return None

    reachable_gateways.sort()
    return reachable_gateways[0][1]

# следующий шаг вируса
def predict_virus_move(virus_pos, graph):
    #  move - движение и следующий ход
    # stuck - вирус застрял - победа
    # reach - вирус достиг шлюза и это тильт
    target_gateway = find_target_gateway(virus_pos, graph)
    if target_gateway is None:
        return 'stuck', None

    gateway_distances = bfs_distances(target_gateway, graph)
    # вирус застрял
    if virus_pos not in gateway_distances:
        return 'stuck', None
    # вирус достигнет шлюза
    if gateway_distances[virus_pos] == 1:
        return 'reach', target_gateway

    next_moves = []
    for neighbor in sorted(graph[virus_pos]):
        if neighbor in gateway_distances and gateway_distances[neighbor] == gateway_distances[virus_pos] - 1:
            next_moves.append(neighbor)

    if not next_moves:
        return 'stuck', None
    # возвращаем след ход
    return 'move', next_moves[0]

# ищем все возможные отключения шлюз узел
def get_possible_cuts(graph):
    cuts = []
    for node in graph:
        if is_gateway(node):
            for neighbor in sorted(graph[node]):
                if not is_gateway(neighbor):
                    cuts.append((node, neighbor))
    cuts.sort()
    return cuts

# удаляем ребро между двумя узлами
def cut_edge(graph, node1, node2):
    new_graph = copy.deepcopy(graph)
    if node2 in new_graph[node1]:
        new_graph[node1].remove(node2)
    if node1 in new_graph[node2]:
        new_graph[node2].remove(node1)
    return new_graph


def find_winning_plan(graph, virus_pos, memo):
    state_key = (virus_pos, tuple(sorted(
        (min(u, v), max(u, v))
        for u in graph
        for v in graph[u]
        if u < v
    ))) # создаем ключ для кэша

    if state_key in memo:
        return memo[state_key]

    # если вирус уже изолирован возвращаем пустой план
    target_gateway = find_target_gateway(virus_pos, graph)
    if target_gateway is None:
        memo[state_key] = []
        return []

    # ищем шлюзы соседние с вирусом
    adjacent_gateways = []
    for neighbor in sorted(graph.get(virus_pos, set())):
        if is_gateway(neighbor):
            adjacent_gateways.append(neighbor)
    # если нашли
    if adjacent_gateways:
        # отрезаем первый лексикографический и проверяем куда пойдет вирус
        gateway_to_cut = adjacent_gateways[0]
        new_graph = cut_edge(graph, gateway_to_cut, virus_pos)
        move_type, next_pos = predict_virus_move(virus_pos, new_graph)
        # если вирус достигает шлюза - отключение плохое
        if move_type == 'reach':
            memo[state_key] = None
            return None
        # если вирус застрял возвращаем один ход
        if move_type == 'stuck':
            memo[state_key] = [f"{gateway_to_cut}-{virus_pos}"]
            return [f"{gateway_to_cut}-{virus_pos}"]
        # рекурсивно ищем новую позицию
        sub_plan = find_winning_plan(new_graph, next_pos, memo)
        if sub_plan is not None:
            result = [f"{gateway_to_cut}-{virus_pos}"] + sub_plan
            memo[state_key] = result
            return result
        # если не нашли запоминаем это и возвращаем
        memo[state_key] = None
        return None

    # проверяем все возможные отключения шлюзов
    possible_cuts = get_possible_cuts(graph)

    for gateway, node in possible_cuts:
        new_graph = cut_edge(graph, gateway, node)
        move_type, next_pos = predict_virus_move(virus_pos, new_graph)
        # пропускаем проигрышные ходы
        if move_type == 'reach':
            continue
        # опять рекурсивно ищем
        sub_plan = find_winning_plan(new_graph, next_pos, memo) if move_type == 'move' else []

        if sub_plan is not None:
            result = [f"{gateway}-{node}"] + (sub_plan if move_type == 'move' else [])
            memo[state_key] = result
            return result
    # запоминаем неудачу
    memo[state_key] = None
    return None


def solve(edges: list[tuple[str, str]]) -> list[str]:
    graph = build_graph(edges)
    virus_start = "a"
    memo = {}

    result  = find_winning_plan(graph, virus_start, memo)
    return result


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)

def test1(): # тестовая функция
    edges = [('a', 'b'), ('b', 'c'), ('c', 'G'), ('b', 'f'), ('f', 'g'), ('g', 'h'),
             ('b', 'd'), ('d', 'e'), ('e', 'C'), ('e', 'D'), ('e', 'E'), ('e', 'F'),
             ('h', 'A'), ('h', 'B'), ('e', 'H')]
    result = solve(edges)
    for edge in result:
        print(edge)

def test2():  # тестовая функция
    edges = [('a', 'b'), ('b', 'c'), ('c', 'G'), ('b', 'f'), ('f', 'g'),
             ('b', 'd'), ('d', 'e'), ('e', 'C'), ('e', 'D'), ('e', 'E'), ('e', 'F'),
             ('g', 'A'), ('g', 'B'), ('e', 'H')]
    result = solve(edges)
    for edge in result:
        print(edge)

if __name__ == "__main__":
    main()