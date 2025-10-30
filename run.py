import sys
import heapq

def solve(lines: list[str]) -> int:
    """
    Решение задачи о сортировке в лабиринте

    Args:
        lines: список строк, представляющих лабиринт

    Returns:
        минимальная энергия для достижения целевой конфигурации
    """
    cost_multiply= {'A': 1, 'B': 10, 'C': 100, 'D': 1000} # цена передвижения
    priority_of_rooms = {'A': 0, 'B': 1, 'C': 2, 'D': 3} # приоритет комнат
    room_positions = [2, 4, 6, 8] # позиции комнат
    corridor_positions = [0, 1, 3, 5, 7, 9, 10] # позиции коридора которые можно использовать не транзитом

    depth = len(lines) - 3 # края и коридор (2 или 4)
    rooms = [[] for i in range(4)] # сами комнаты
    for i in range(depth): # заполняем из наших вводных данных
        line = lines[2 + i]
        rooms[0].append(line[3])
        rooms[1].append(line[5])
        rooms[2].append(line[7])
        rooms[3].append(line[9])

    initial_corridor = tuple(['.'] * 11) # пустой коридор
    initial_rooms = tuple(tuple(room) for room in rooms)
    goal_rooms = ( # нужное состояние комнат для нас
        tuple(['A'] * depth),
        tuple(['B'] * depth),
        tuple(['C'] * depth),
        tuple(['D'] * depth)
    )
    # проверка коридора на возможность пройти
    def is_path_free(corridor, start, end, exclude=None):
        low = min(start, end)
        high = max(start, end)
        for k in range(low, high + 1):
            if k == exclude:
                continue
            if corridor[k] != '.':
                return False
        return True

    heap = []
    heapq.heappush(heap, (0, initial_corridor, initial_rooms))
    visited = {}

    while heap:
        cost, corridor, rooms = heapq.heappop(heap)
        state = (corridor, rooms)
        if state in visited and visited[state] <= cost:
            continue
        visited[state] = cost

        if rooms == goal_rooms:
            return cost
        # движение из комнаты в коридор
        for i in range(4):
            room = rooms[i] # рассматриваем по очереди комнаты
            for d in range(depth):
                if room[d] != '.': # проверяем есть ли что-то в нашей комнаты не глубине d
                    # проверка есть ли буквы над той, которую мы рассматриваем
                    if any(room[k] != '.' for k in range(d)):
                        continue

                    type_char = room[d] # тип буквы которую хотим переместить
                    # если уже на нужном месте(ура нам повезло) то не двигаем
                    if i == priority_of_rooms[type_char]:
                        if all(c == '.' or c == type_char for c in room[d + 1:]):
                            continue

                    for j in corridor_positions: # свободен ли проход до места в коридоре
                        if not is_path_free(corridor, room_positions[i], j):
                            continue
                        # новое состояние коридора
                        new_corridor = list(corridor)
                        new_corridor[j] = type_char
                        new_corridor = tuple(new_corridor)
                        # новое состояние комнат
                        new_rooms = list(rooms)
                        new_room_i = list(room)
                        new_room_i[d] = '.'
                        new_rooms[i] = tuple(new_room_i)
                        new_rooms = tuple(new_rooms)
                        # считаем цену
                        steps = d + 1 + abs(room_positions[i] - j)
                        new_cost = cost + steps * cost_multiply[type_char]
                        new_state = (new_corridor, new_rooms)

                        if new_state in visited and visited[new_state] <= new_cost:
                            continue
                        heapq.heappush(heap, (new_cost, new_corridor, new_rooms))
                    break
        # перемещение из коридора в комнаты
        for j in range(11):
            # пропуск пустых позиций
            if corridor[j] == '.':
                continue
            # тип буквы и куда ее отправить
            type_char = corridor[j]
            i_target = priority_of_rooms[type_char]
            room = rooms[i_target]

            if any(c != '.' and c != type_char for c in room):
                continue # если в комнате другие буквы нам туда нельзя и надо пропустить
            # ищем место куда будем ставить букву
            d = depth - 1
            while d >= 0 and room[d] != '.':
                d -= 1
            if d < 0:
                continue
            # проверяем свободен ли путь игнорируя позицию в которой находится буква
            if not is_path_free(corridor, j, room_positions[i_target], exclude=j):
                continue
            # новое состояние коридора
            new_corridor = list(corridor)
            new_corridor[j] = '.'
            new_corridor = tuple(new_corridor)
            # новое состояние комнат
            new_rooms = list(rooms)
            new_room_i = list(room)
            new_room_i[d] = type_char
            new_rooms[i_target] = tuple(new_room_i)
            new_rooms = tuple(new_rooms)
            # считаем цену
            steps = abs(j - room_positions[i_target]) + (d + 1)
            new_cost = cost + steps * cost_multiply[type_char]
            new_state = (new_corridor, new_rooms)

            if new_state in visited and visited[new_state] <= new_cost:
                continue # если есть лучше - пропускаем
            heapq.heappush(heap, (new_cost, new_corridor, new_rooms))

    return -1


def main():
    # Чтение входных данных
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))

    result = solve(lines)
    print(result)


if __name__ == "__main__":
    main()

# проверка webhook :)