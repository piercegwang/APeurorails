from random import choice
from random import sample
from mytrack import Track

REG_HARBOR_PENALTY = 12
HIGH_HARBOR_PENALTY = 10000
STEP_PENALTY = 0.2

MAJOR_CITIES = ["madrid", "london", "paris", "berlin", "ruhr", "wien", "holland", "milano"]

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
        self.harbor_penalty = REG_HARBOR_PENALTY
        self.step_penalty = STEP_PENALTY

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

    def compute_cost(self, p1, p2, my_track):
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

            if p2 in my_track:
                if p1 in my_track:
                    return 0
                else:
                    cost = 0
            elif self(p1_x, p1_y) == 'L' and dest == 'L':
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

    def compute_point_cost(self, pt, my_track):

        x, y = pt

        if not self.is_valid(x, y):
            raise ValueError("Point", pt, "is not a valid point on the board")
        else:
            dest = self(x, y)

            if pt in my_track:
                cost = 0
            elif dest == "." or dest == "L":
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

    def cycle_harbor_penalty(self):
        if self.harbor_penalty == REG_HARBOR_PENALTY:
            self.harbor_penalty = HIGH_HARBOR_PENALTY
        else:
            self.harbor_penalty = REG_HARBOR_PENALTY


def find_path(start_city, board, my_track, reached_goal, reverse=True):
    """
    Finds path from end city to some goal (e.g. start city, load, existing track).
    """

    def get_path(point, reverse):
        path = []
        while point.parent is not None:
            path.append(point.coord)
            point = point.parent
        path.append(point.coord)
        if reverse:
            return list(reversed(path))
        else:
            return path

    def get_neighbors(point):
        neighbors = []
        for dx, dy in ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)):
            if board.is_valid(point.x + dx, point.y + dy):
                if not board.is_harbor(point.x, point.y) or \
                        board.is_harbor(point.x, point.y) and not board.is_harbor(point.x + dx, point.y + dy):
                    c = board.compute_cost(point.coord, (point.x + dx, point.y + dy), my_track)
                    neighbors.append(Point((point.x + dx, point.y + dy), point, point.build_cost + c, point.penalty + board.step_penalty))
        if board.is_harbor(point.x, point.y):
            neighbors.append(Point(board.get_other_harbor(point.x, point.y), point, point.build_cost, point.penalty + board.harbor_penalty))

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
            min_nodes = []
            for node in self:
                if min_nodes == [] or value(min_nodes[0].item) == value(node.item):
                    min_nodes.append(node)
                elif value(min_nodes[0].item) > value(node.item):
                    min_nodes = [node]
            min_node = choice(min_nodes)
            if min_node is self:
                new_first_node = min_node.next
            else:
                new_first_node = self
            return min_node.pop(), new_first_node

        def size(self):
            return len([node for node in self])

        def __str__(self):
            return str(self.item)

        # def __eq__(self, other):
        #     return self.item == other.item

        def __iter__(self):
            if self.item is not None:
                yield self
            node = self.next
            while node is not self:
                if node.item is not None:
                    yield node
                node = node.next

    class Point:
        def __init__(self, point, parent=None, cost=0, penalty=0):
            self.x, self.y = point
            self.parent = parent
            self.build_cost = cost
            self.penalty = penalty

        @property
        def coord(self):
            return (self.x, self.y)

        def get_cost(self):
            return self.build_cost + self.penalty

        def __str__(self):
            return "(" + str(self.x) + ", " + str(self.y) + ")"

        def __hash__(self):
            return hash((self.x, self.y))

        def __eq__(self, other):
            return other is not None and self.x == other.x and self.y == other.y

    agenda = LinkedList()
    if type(start_city) == set or type(start_city) == list:
        for ec in start_city:
            # agenda.append(Point(ec, cost=board.compute_point_cost(ec, my_track)))
            agenda.append(Point(ec, cost=0))
    else:
        # agenda.append(Point(start_city, cost=board.compute_point_cost(start_city, my_track)))
        agenda.append(Point(start_city, cost=0))
    visited = set()
    while agenda.size() > 0:
        current_point, agenda = agenda.pop_min(value=Point.get_cost)
        if current_point not in visited:
            visited.add(current_point)
            if reached_goal((current_point.x, current_point.y)):
                return get_path(current_point, reverse), current_point.build_cost
            else:
                neighbors = get_neighbors(current_point)
                for n in neighbors:
                    if n not in visited:
                        # if reached_goal((n.x, n.y)) and not reverse:
                        #     c = board.compute_point_cost((n.x, n.y), my_track)
                        #     n.build_cost -= c # correction for path calculation from end city to beginning city
                        agenda.append(n)

    print("No path found")
    return None, None
    # TODO: implement A* search
    # TODO: balance between cost and distance


def connect_cities(board, my_track, cities, number_tries=1):
    def contained(tracks):
        def __contained(point):
            for t in tracks:
                if point in t:
                    return True
            return False

        return __contained

    tracks = []
    if my_track is not None and my_track.has_track:
        tracks.append(my_track)
    for group in cities:
        t = Track(board)
        for c in group:
            t.add_representative(c[0], c[1])
        tracks.append(t)

    opt_paths = None
    opt_cost = None
    actual_number_tries = number_tries if number_tries <= len(tracks) else len(tracks)
    order = sample(range(len(tracks)), actual_number_tries)
    for i in range(actual_number_tries):
        tracks_cp = [t.copy() for t in tracks]
        home = tracks_cp.pop(order[i])
        all_paths = []
        total_cost = 0

        while len(tracks_cp) > 0:
            p, c = find_path(home.representatives, board, home, reached_goal=contained(tracks_cp), reverse=True)
            home.add_track(p)
            i = 0
            while i < len(tracks_cp):
                t = tracks_cp[i]
                if p[-1] in t:
                    home.union(t)
                    tracks_cp.pop(i)
                else:
                    i += 1
            home.remove_unconnected(p[0])
            all_paths.append(p)
            total_cost += c

        if opt_cost is None or opt_cost > total_cost:
            opt_paths = all_paths
            opt_cost = total_cost

    return opt_paths, opt_cost