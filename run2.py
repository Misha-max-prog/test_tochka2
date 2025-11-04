import sys
from collections import deque

# вебхук сработай пж да да
def is_gateway(node):
    return node.isupper()

def choose_gateway(current, graph):
    distances = {}
    queue = deque([current])
    distances[current] = 0
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)
    gateways = []
    for node in distances:
        if is_gateway(node):
            gateways.append((node, distances[node]))
    gateways.sort(key=lambda g: (g[1], g[0]))
    return gateways

def solve(edges: list[tuple[str, str]]) -> list[str]:
    result = []
    graph = {}
    for u, v in edges:
        if u not in graph:
            graph[u] = set()
        if v not in graph:
            graph[v] = set()
        graph[u].add(v)
        graph[v].add(u)
    current='a'
    gateways = choose_gateway(current, graph)
    print(gateways)
    for i in range(len(gateways)):
        remember2 = gateways[i][0]
        nodes = list(graph[remember2])
        sorted_nodes = sorted(nodes)
        for j in range(len(sorted_nodes)):
            remember1 = list(graph[remember2])[j]
            res = remember2 + '-' + remember1
            result.append(res)
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


if __name__ == "__main__":
    main()