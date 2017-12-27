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
        return self.board[self.max_y - y][x - self.min_x]

class Visual:
    DEFAULT_BOARD_IMG_PATH = "../database/board.jpg"
    LINE_THICKNESS = 14
    CIRCLE_THICKNESS = 100
    RADIUS = 64

    def __init__(self, board_file):
        self.filepath = board_file
        self.board = Image.open(self.filepath)
        self.board = self.board.resize((4096//4, 3281//4), Image.ANTIALIAS)
        self.draw = ImageDraw.Draw(self.board)
        self.window = tk.Tk()
        self.canvas = tk.Canvas(self.window, width=4096//4, height=3281//4)
        self.canvas.pack()
        self.show()

    def draw_path(self, p1, p2, color=0):
        print("test")
        i = self.canvas.create_line(0, 820, 1024, 0, fill="black")


    def mark_city(self, city_loc, color=0):
        #self.canvas.create_oval(x0, y0, x1, y1, option, ...)
        pass

    def clean(self):
        self.board = Image.open(self.filepath)
        self.board = self.board.resize((4096//4, 3281//4), Image.ANTIALIAS)
        tkimage = ImageTk.PhotoImage(self.board)
        self.window.update()

    def show(self):
        self.tkimage = ImageTk.PhotoImage(self.board)
        tk.Label(self.window, image=self.tkimage).pack()
        self.window.update()

    def update(self):
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
        if len(board[-1]) < min_x + max_x + 1:
            board[-1].extend([' ' for _ in range(abs(min_x) + abs(max_x) + 1 - len(board[-1]))])

    board = Board(board, min_x, max_x, min_y, max_y)

    return city_db, board