from PIL import Image, ImageDraw
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

def draw_line(point1, point2, rgbcode, boardfile=None):
    if boardfile == None:
        board = Image.open("../database/board.jpg")
        draw  = ImageDraw.Draw(board)
    else:
        draw = ImageDraw.Draw(boardfile)
    draw.line([point1, point2], fill=rgbcode, width=14)
    if boardfile == None:
        return board
    else:
        return boardfile
#paris is 2021, 1608

def draw_ellipse(point, rgbcode, boardfile=None):
    if boardfile == None:
        board = Image.open("../database/board.jpg")
        draw  = ImageDraw.Draw(board)
    else:
        draw = ImageDraw.Draw(boardfile)
    r=64
    width = 16
    for i in range(r, r+width):
        draw.ellipse((point[0] - i, point[1] - i, point[0] + (i - 1), point[1] + (i - 1)), outline=rgbcode)
        draw.ellipse((point[0] - (i-1), point[1] - (i-1), point[0] + (i - 1), point[1] + (i - 1)), outline=rgbcode)
        draw.ellipse((point[0] - i, point[1] - i, point[0] + i, point[1] + i), outline=rgbcode)
    if boardfile == None:
        return board
    else:
        return boardfile

draw_line((0,0),(2021,1608),(0,0,0,0),draw_ellipse((2021,1608),(0,0,0,0))).show()