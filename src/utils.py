from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
import json

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
        elif (dx, dy) not in ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)):
            raise ValueError("board.compute_cost() called on non-adjacent points.")    
        else:
            dest = self(p2_x, p2_y)
            
            if dest == "." or dest == "L":
                cost = 1
            elif dest == "m":
                cost = 2
            elif dest == "a":
                cost = 5
            elif dest == "S" or dest == "M":
                cost = 3
            elif dest == "h":
                other_harbor, cost = self.harbors[(p2_x, p2_y)]
                if self(other_harbor[0], other_harbor[1]) == "H":
                    cost += 3
            elif dest == "H":
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


class BuiltTrack:
    def __init__(self, board):
        self.min_x = board.min_x
        self.max_x = board.max_x
        self.min_y = board.min_y
        self.max_y = board.max_y
        self.board = [[0 for _ in range(2 * (abs(self.min_x) + abs(self.max_x) + 1))] for _ in range(2 * (abs(self.min_y) + abs(self.max_y) + 1))]
        self.queued_track = []
        self.has_track = False

    def claim_point(self, x, y):
        x_index = 2 * (x - self.min_x)
        y_index = 2 * (self.max_y - y)
        if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
            self.board[y_index][x_index] = 1
        self.has_track = True

    def claim_track(self, x, y, dx, dy):
        x_index = 2 * (x - self.min_x) + dx
        y_index = 2 * (self.max_y - y) - dy
        if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
            self.board[y_index][x_index] = 1

    def add_track(self, sequence):
        for i in range(len(sequence)):
            x, y = sequence[i]
            self.claim_point(x, y)
            if i < len(sequence) - 1:
                dx = sequence[i + 1][0] - x
                dy = sequence[i + 1][1] - y
                if (dx, dy) in ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)):
                    self.claim_track(x, y, dx, dy)

    def __contains__(self, pt):
        x_index = 2 * (pt[0] - self.min_x)
        y_index = 2 * (self.max_y - pt[1])
        if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
            return self.board[y_index][x_index]

    def clean(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                self.board[r][c] = 0
        self.empty_queued_track()
        self.has_track = False
    
    def queue_track(self, path):
        self.queued_track.append(path)
    
    def save_queued_track(self):
        for path in self.queued_track:
            self.add_track(path)
        self.empty_queued_track()
    
    def empty_queued_track(self):
        self.queued_track = []

class Visual:
    LINE_THICKNESS = 2
    CIRCLE_THICKNESS = 2
    RADIUS = 6
    references = {(0, 0): (505, 402), # Paris
                  (-9, -19): (210, 669), # Madrid
                  (15, -13): (645, 583), # Milano
                  (26, -8): (860, 513), # Wien
                  (17, 5): (820, 330), # Berlin
                  (10, 20): (827, 117), # Goteburg
                  (-10, 16): (468, 177), # Manchester
                  (7, 4): (650, 344), # Ruhr
                  (-21, -17): (32, 637), # Lisboa
                  (-14, -25): (81, 749), # Sevilla
                  (1, -14): (410, 598), # Toulouse
                  (21, -15): (722, 611), # Venezia
                  (25, -25): (705, 749), # Roma
                  (39, -19): (983, 665), # Beograd
                  (35, -22): (895, 708), # Sarajevo
                  (28, -15): (836, 611), # Zagreb
                  (-21, 17): (304, 163), # Cork
                  (27, 2): (958, 373), # Lodz
                  (8, 9): (705, 274), # Bremen
                  (-18, 19): (363, 135), # Dublin
                  (-17, 22): (402, 93), # Belfast
                  }
    X_CONST = (16.21, -0.1)
    Y_CONST = (8.0645, 14.03)

    def __init__(self, board_file):
        self.filepath = board_file
        self.board = Image.open(self.filepath)
        self.board = self.board.resize((4096//4, 3281//4), Image.ANTIALIAS)
        self.draw = ImageDraw.Draw(self.board)

        # Create tkinter window
        self.window = tk.Tk()
        self.tk_img = ImageTk.PhotoImage(self.board)
        self.panel = tk.Label(self.window, image=self.tk_img)
        self.panel.pack(side="bottom", fill="both", expand="yes")

    def draw_path(self, points, color=0):
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            p1 = self.coordinates_to_pixels(p1)
            p2 = self.coordinates_to_pixels(p2)
            self.draw.line([p1, p2], fill=color, width=Visual.LINE_THICKNESS)
                

    def mark_city(self, city_loc, color=0):
        city_loc = self.coordinates_to_pixels(city_loc)
        for i in range(Visual.RADIUS, Visual.RADIUS + Visual.CIRCLE_THICKNESS):
            self.draw.ellipse((city_loc[0] - i, city_loc[1] - i, city_loc[0] + (i - 1), city_loc[1] + (i - 1)),
                              outline=color)
            self.draw.ellipse((city_loc[0] - (i - 1), city_loc[1] - (i - 1), city_loc[0] + (i - 1), city_loc[1] + (i - 1)),
                              outline = color)
            self.draw.ellipse((city_loc[0] - i, city_loc[1] - i, city_loc[0] + i, city_loc[1] + i),
                              outline=color)

    def clean(self):
        self.board = Image.open(self.filepath)
        self.board = self.board.resize((4096//4, 3281//4), Image.ANTIALIAS)
        self.draw = ImageDraw.Draw(self.board)

    def update(self):
        self.tk_img = ImageTk.PhotoImage(self.board)
        self.panel.configure(image=self.tk_img)
        self.window.update()

    def quit(self):
        self.window.quit()
        
    def coordinates_to_pixels(self, coords):
        def get_closest_reference(coords):
            def distance(p1, p2):
                return abs(p2[1] - p1[1]) + abs(p2[0] - p1[0])
            closest_reference = None
            for r in Visual.references:
                if closest_reference is None or distance(coords, r) < distance(coords, closest_reference):
                    closest_reference = r
            return closest_reference
        
        
        ref = get_closest_reference(coords)
        pixel = list(Visual.references[ref])
        
        delta = (coords[0] - ref[0], coords[1] - ref[1])
            
        pixel[0] += round(Visual.X_CONST[0] * (delta[0] + 0.5 * delta[1])) + round(Visual.X_CONST[1] * delta[1])
        pixel[1] -= round(Visual.Y_CONST[1] * delta[1])
        # print(ref, pixel)
        return tuple(pixel)

def load_files(city_db_path, board_path, harbor_path):
    """
    Loads JSON database of Eurorails and ASCII map of board.

    :param city_db_path: path to city/load database
    :param board_path: path to ASCII board text file
    :return: database as a dictionary
    """
    board = []
    harbors = {}
    with open(city_db_path, 'r') as f:
        city_db = json.load(f)

    city_db["points"] = {}
    
    for city in city_db["cities"]:
        city_db["cities"][city]["coords"] = tuple(city_db["cities"][city]["coords"])
        city_db["points"][city_db["cities"][city]["coords"]] = city

    board_raw = open(board_path).read().split('\n')
    min_x, max_x = map(int, board_raw[0].split(' '))
    min_y, max_y = map(int, board_raw[1].split(' '))

    for row in board_raw[2:]:
        board.append([c for c in row])
        if len(board[-1]) < 2 * (min_x + max_x + 1):
            board[-1].extend([' ' for _ in range(abs(min_x) + abs(max_x) + 1 - len(board[-1]))])

    harbors_raw = open(harbor_path).read().split('\n')
    for line in harbors_raw:
        expand = line.split(' ')
        harbors[(int(expand[1]), int(expand[2]))] = ((int(expand[4]), int(expand[5])), int(expand[6]))
        harbors[(int(expand[4]), int(expand[5]))] = ((int(expand[1]), int(expand[2])), int(expand[6]))

    board = Board(board, harbors, min_x, max_x, min_y, max_y)

    return city_db, board

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
        def __init__(self, point, parent=None, cost = 0):
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
