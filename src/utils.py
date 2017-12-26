from PIL import Image, ImageDraw
import json

DEFAULT_BOARD_IMG_PATH = "../database/board.jpg"
LINE_THICKNESS = 14
CIRCLE_THICKNESS = 16
RADIUS = 64

class Board:
    def __init__(self, board, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.board = board
    def __call__(self, x, y):
        return self.board[MAX_Y - y][x - MIN_X]

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
            board[-1].extend([' ' for _ in range(min_x + max_x + 1 - len(board[-1]))])

    board = Board(board, min_x, max_x, min_y, max_y)

    return city_db, board

def draw_line(point1, point2, rgbcode, boardfile=None):
    draw = ImageDraw.Draw(boardfile)
    draw.line([point1, point2], fill=rgbcode, width=LINE_THICKNESS)
    return boardfile
#paris is 2021, 1608

def draw_ellipse(point, rgbcode, boardfile=Image.open(DEFAULT_BOARD_IMG_PATH)):
    draw = ImageDraw.Draw(boardfile)
    for i in range(RADIUS, RADIUS + CIRCLE_THICKNESS):
        draw.ellipse((point[0] - i, point[1] - i, point[0] + (i - 1), point[1] + (i - 1)), outline=rgbcode)
        draw.ellipse((point[0] - (i-1), point[1] - (i-1), point[0] + (i - 1), point[1] + (i - 1)), outline=rgbcode)
        draw.ellipse((point[0] - i, point[1] - i, point[0] + i, point[1] + i), outline=rgbcode)
    return boardfile
