from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
import json

class Board:
    def __init__(self, board, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.board = board
        
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
    
    def compute_cost(self, p1, p2):
        def get_travel_cost(x, y, dx, dy):
            x_index = 2 * (x - self.min_x) + dx
            y_index = 2 * (self.max_y - y) + dy
            if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
                cost = self.board[y_index][x_index]
            else:
                raise ValueError("Point out of range.")
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
                raise NotImplementedError("Harbors not implemented.")
            elif dest == "H":
                raise NotImplementedError("Harbors not implemented.")
            else:
                raise ValueError("Board contains invalid character.")
            
            cost += get_travel_cost(p1_x, p1_y, dx, dy)
            return cost

class Visual:
    DEFAULT_BOARD_IMG_PATH = "../database/board.jpg"
    LINE_THICKNESS = 10
    CIRCLE_THICKNESS = 100
    RADIUS = 64

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

    def draw_path(self, p1, p2, color="black"):
        self.draw.line([p1, p2], fill=color, width=Visual.LINE_THICKNESS)

    def mark_city(self, city_loc, color=0):
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

    def update(self):
        self.tk_img = ImageTk.PhotoImage(self.board)
        self.panel.configure(image=self.tk_img)
        self.window.update()

    def quit(self):
        self.window.quit()

def load_files(city_db_path, board_path):
    """
    Loads JSON database of Eurorails and ASCII map of board.

    :param city_db_path: path to city/load database
    :param board_path: path to ASCII board text file
    :return: database as a dictionary
    """
    board = []
    with open(city_db_path, 'r') as f:
        city_db = json.load(f)

    raw = open(board_path).read().split('\n')
    min_x, max_x = map(int, raw[0].split(' '))
    min_y, max_y = map(int, raw[1].split(' '))

    for row in raw[2:]:
        board.append([c for c in row])
        if len(board[-1]) < 2 * (min_x + max_x + 1):
            board[-1].extend([' ' for _ in range(abs(min_x) + abs(max_x) + 1 - len(board[-1]))])

    board = Board(board, min_x, max_x, min_y, max_y)

    return city_db, board

def find_path(p1, p2, board):
    def get_path(initial, point):
        path = []
        while point != initial:
            path.append(point.coord)
            point = point.parent
        path.append(initial.coord)
        return list(reversed(path))
    
    def get_neighbors(point):
        neighbors = []
        for dx, dy in ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)):
            if board.is_valid(point.x + dx, point.y + dy):
                neighbors.append(Point((point.x + dx, point.y + dy),
                                       point,
                                       point.cost + board.compute_cost(point.coord, (point.x + dx, point.y + dy))))
                if board.is_harbor(point.x + dx, point.y + dy):
                    raise NotImplementedError("Harbors not implemented for neighbors.")
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
    
    p1 = Point(p1)
    p2 = Point(p2)
    visited = set()
    agenda = LinkedList(p1)
    while agenda.size() > 0:
        current_point, agenda = agenda.pop_min(value=Point.get_cost)
        if current_point not in visited:
            visited.add(current_point)
            print("Examining", current_point)
            if current_point == p2:
                return get_path(p1, current_point)
            else:
                neighbors = get_neighbors(current_point)
                for n in neighbors:
                    if n not in visited:
                        agenda.append(n)
    
    return None

if __name__ == '__main__':
    DEFAULT_DB_PATH = "../database/eurorails.json"
    DEFAULT_BOARD_PATH = "../database/board_ascii.txt"
    db, board = load_files(DEFAULT_DB_PATH, DEFAULT_BOARD_PATH)
    path = find_path((15, -13), (18, -7), board)
    # path = find_path((0, 0), (1, 1), board)
    print(path)