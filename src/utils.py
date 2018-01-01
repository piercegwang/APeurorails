import json
from board import Board

def load_files(city_db_path, board_path, harbor_path):
    """
    Loads JSON database of Eurorails and ASCII map of board.

    :param city_db_path: path to city/load database
    :param board_path: path to ASCII board text file
    :return: database as a dictionary
    """
    board = []
    harbors = {}

    # load city/load database
    with open(city_db_path, 'r') as f:
        city_db = json.load(f)

    # construct reverse city database
    city_db["points"] = {}
    for city in city_db["cities"]:
        city_db["cities"][city]["coords"] = tuple(city_db["cities"][city]["coords"])
        city_db["points"][city_db["cities"][city]["coords"]] = city

    # load ascii path
    board_raw = open(board_path).read().split('\n')
    min_x, max_x = map(int, board_raw[0].split(' '))
    min_y, max_y = map(int, board_raw[1].split(' '))

    # fill ends of rows with spaces
    for row in board_raw[2:]:
        board.append([c for c in row])
        if len(board[-1]) < 2 * (min_x + max_x + 1):
            board[-1].extend([' ' for _ in range(abs(min_x) + abs(max_x) + 1 - len(board[-1]))])

    # load harbors
    harbors_raw = open(harbor_path).read().split('\n')
    for line in harbors_raw:
        expand = line.split(' ')
        harbors[(int(expand[1]), int(expand[2]))] = ((int(expand[4]), int(expand[5])), int(expand[6]))
        harbors[(int(expand[4]), int(expand[5]))] = ((int(expand[1]), int(expand[2])), int(expand[6]))

    board = Board(board, harbors, min_x, max_x, min_y, max_y)

    return city_db, board

