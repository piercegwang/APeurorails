def is_one_step(dx, dy):
    return (dx, dy) in ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))


class Board:
    def __init__(self, board, harbors, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.board = board
        self.harbors = harbors

    def __call__(self, x, y):
        x_index = 2 * (x - self.min_x)
        y_index = 2 * (self.max_y - y)
        if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
            return self.board[y_index][x_index]
        else:
            return None

    def is_valid(self, x, y):
        return self(x, y) is not None and self(x, y) != " "

    def is_harbor(self, x, y):
        return self(x, y) == "h" or self(x, y) == "H"

    def get_other_harbor(self, x, y):
        if self.is_harbor(x, y):
            harbor, _ = self.harbors[(x, y)]
            return harbor

    def compute_cost(self, p1, p2):
        def get_travel_cost(x, y, dx, dy):
            x_index = 2 * (x - self.min_x) + dx
            y_index = 2 * (self.max_y - y) - dy
            if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
                cost = self.board[y_index][x_index]
            else:
                raise ValueError("Point " + str((x, y, dx, dy)) + " out of range.")
            if cost == ' ':
                return 0
            else:
                return int(cost)

        p1_x, p1_y = p1
        p2_x, p2_y = p2
        dx, dy = p2_x - p1_x, p2_y - p1_y

        if not self.is_valid(p1_x, p1_y):
            raise ValueError("Point 1 is not a valid point on the board")
        elif not self.is_valid(p2_x, p2_y):
            raise ValueError("Point 2 is not a valid point on the board")
        elif not is_one_step(dx, dy):
            raise ValueError("board.compute_cost() called on non-adjacent points.")
        else:
            dest = self(p2_x, p2_y)

            if self(p1_x, p1_y) == 'L' and dest == 'L':
                return 0
            elif dest == '.' or dest == 'L':
                cost = 1
            elif dest == 'm':
                cost = 2
            elif dest == 'a':
                cost = 5
            elif dest == 'S' or dest == 'M':
                cost = 3
            elif dest == 'h':
                other_harbor, cost = self.harbors[(p2_x, p2_y)]
                if self(other_harbor[0], other_harbor[1]) == 'H':
                    cost += 3
            elif dest == 'H':
                _, cost = self.harbors[(p2_x, p2_y)]
                cost += 3
            else:
                raise ValueError("Board contains invalid character.")

            cost += get_travel_cost(p1_x, p1_y, dx, dy)
            return cost

    def compute_point_cost(self, pt):

        x, y = pt

        if not self.is_valid(x, y):
            raise ValueError("Point", pt, "is not a valid point on the board")
        else:
            dest = self(x, y)

            if dest == "." or dest == "L":
                cost = 1
            elif dest == "m":
                cost = 2
            elif dest == "a":
                cost = 5
            elif dest == "S" or dest == "M":
                cost = 3
            elif dest == "h":
                other_harbor, cost = self.harbors[(x, y)]
                if self(other_harbor[0], other_harbor[1]) == "H":
                    cost += 3
            elif dest == "H":
                _, cost = self.harbors[(x, y)]
                cost += 3
            else:
                raise ValueError("Board contains invalid character.")

            return cost


def find_path(end_city, board, reached_goal):
    """
    Finds path from end city to some goal (e.g. start city, load, existing track).
    """

    def get_path(end, point):
        path = []
        while point != end:
            path.append(point.coord)
            point = point.parent
        path.append(end.coord)
        return path

    def get_neighbors(point):
        neighbors = []
        for dx, dy in ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)):
            if board.is_valid(point.x + dx, point.y + dy):
                if not board.is_harbor(point.x, point.y) or \
                        board.is_harbor(point.x, point.y) and not board.is_harbor(point.x + dx, point.y + dy):
                    neighbors.append(Point((point.x + dx, point.y + dy),
                                           point,
                                           point.cost + board.compute_cost(point.coord, (point.x + dx, point.y + dy))))
        if board.is_harbor(point.x, point.y):
            neighbors.append(Point(board.get_other_harbor(point.x, point.y),
                                   point,
                                   point.cost))

        return neighbors

    class LinkedList:
        def __init__(self, obj=None):
            self.item = obj
            self.next = self
            self.prev = self

        def append(self, obj):
            if self.item is None:
                self.item = obj
            else:
                new_item = LinkedList(obj)
                new_item.prev = self.prev
                new_item.next = self

                self.prev.next = new_item
                self.prev = new_item

        def insert(self, obj):
            if self.item is None:
                self.item = obj
            else:
                new_item = LinkedList(obj)
                new_item.prev = self
                new_item.next = self.next

                self.next.prev = new_item
                self.next = new_item

        def pop(self):
            item = self.item
            if self.prev == self and self.next == self:
                self.item = None

            self.prev.next = self.next
            self.next.prev = self.prev
            return item

        def pop_min(self, value=lambda x: x):
            min_node = None
            for node in self:
                if min_node is None:
                    min_node = node
                elif value(min_node.item) > value(node.item):
                    min_node = node
            if min_node == self:
                new_first_node = min_node.next
            else:
                new_first_node = self
            return min_node.pop(), new_first_node

        def size(self):
            return len([node for node in self])

        def __str__(self):
            return str(self.item)

        def __eq__(self, other):
            return self.item == other.item

        def __iter__(self):
            if self.item is not None:
                yield self
            node = self.next
            while node != self:
                if node.item is not None:
                    yield node
                node = node.next

    class Point:
        def __init__(self, point, parent=None, cost=0):
            self.x, self.y = point
            self.parent = parent
            self.cost = cost
            self.next = None

        @property
        def coord(self):
            return (self.x, self.y)

        def get_cost(self):
            return self.cost

        def __str__(self):
            return "(" + str(self.x) + ", " + str(self.y) + ")"

        def __hash__(self):
            return hash((self.x, self.y))

        def __eq__(self, other):
            return other is not None and self.x == other.x and self.y == other.y

    end_city = Point(end_city, cost=board.compute_point_cost(end_city))
    visited = set()
    agenda = LinkedList(end_city)
    while agenda.size() > 0:
        current_point, agenda = agenda.pop_min(value=Point.get_cost)
        if current_point not in visited:
            visited.add(current_point)
            if reached_goal((current_point.x, current_point.y)):
                return get_path(end_city, current_point), current_point.get_cost()
            else:
                neighbors = get_neighbors(current_point)
                for n in neighbors:
                    if n not in visited:
                        if reached_goal((n.x, n.y)):
                            n.cost -= board.compute_point_cost((n.x, n.y))
                        agenda.append(n)

    return None, None
    # TODO: implement A* search
    # TODO: balance between cost and distance