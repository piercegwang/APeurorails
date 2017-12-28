from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
import json

def load_database(filename):
    """
    Loads JSON database of Eurorails.

    :param filename: path to database
    :return: database as a dictionary
    """
    with open(filename, 'r') as f:
        database = json.load(f)
    return database


class Visual:
    LINE_THICKNESS = 2
    CIRCLE_THICKNESS = 3
    RADIUS = 6
    references = {(0, 0): (505, 402),  # Paris
                  (-9, -19): (210, 669),  # Madrid
                  (15, -13): (645, 583),  # Milano
                  (26, -8): (860, 513),  # Wien
                  (17, 5): (820, 330),  # Berlin
                  (10, 20): (827, 117),  # Goteburg
                  (-10, 16): (468, 177),  # Manchester
                  (7, 4): (650, 344),  # Ruhr
                  (-21, -17): (32, 637),  # Lisboa
                  (-14, -25): (81, 749),  # Sevilla
                  (1, -14): (410, 598),  # Toulouse
                  (21, -15): (722, 611),  # Venezia
                  (25, -25): (705, 749),  # Roma
                  (39, -19): (983, 665),  # Beograd
                  (35, -22): (895, 708),  # Sarajevo
                  (28, -15): (836, 611),  # Zagreb
                  (-21, 17): (304, 163),  # Cork
                  (27, 2): (958, 373),  # Lodz
                  (8, 9): (705, 274),  # Bremen
                  (-18, 19): (363, 135),  # Dublin
                  (-17, 22): (402, 93),  # Belfast
                  }
    X_CONST = (16.21, -0.1)
    Y_CONST = (8.0645, 14.03)

    def __init__(self, board_file):
        self.filepath = board_file
        self.board = Image.open(self.filepath)
        self.board = self.board.resize((4096 // 4, 3281 // 4), Image.ANTIALIAS)
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
            self.draw.ellipse(
                (city_loc[0] - (i - 1), city_loc[1] - (i - 1), city_loc[0] + (i - 1), city_loc[1] + (i - 1)),
                outline=color)
            self.draw.ellipse((city_loc[0] - i, city_loc[1] - i, city_loc[0] + i, city_loc[1] + i),
                              outline=color)

    def clean(self):
        self.board = Image.open(self.filepath)
        self.board = self.board.resize((4096 // 4, 3281 // 4), Image.ANTIALIAS)
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
        self.board = [[0 for _ in range(2 * (abs(self.min_x) + abs(self.max_x) + 1))] for _ in
                      range(2 * (abs(self.min_y) + abs(self.max_y) + 1))]
        self.queued_track = []
        self.has_track = False

    def clean(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                self.board[r][c] = 0
        self.empty_queued_track()
        self.has_track = False


def load_files(city_db_path, board_path):
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

    board = Board(board, harbors, min_x, max_x, min_y, max_y)
    return city_db, board