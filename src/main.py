from utils import *
import random

DEFAULT_DB_PATH = "../database/eurorails.json"
DEFAULT_BOARD_PATH = "../database/board_ascii.txt"
DEFAULT_IMG_PATH = "../database/board.jpg"
DEFAULT_HARBOR_PATH = "../database/harbors.txt"


def print_city(database, city):
    entry = database["cities"][city]
    output = city + ":\n"
    output += "      Location: (" + str(entry["coords"][0]) + ", " + str(entry["coords"][1]) + ")\n"
    output += "      Load: "
    if len(entry["loads"]) > 0:
        for l in entry["loads"]:
            output += l + " "
    else:
        output += "none"
    output += "\n"
    output += "      Land: " + entry["island"] + "\n"
    output += "      City Type: " + entry["type"]
    output += "\n    "

    return output


def print_path(path, cost, start_city=None):
    if start_city is None:
        return "Optimal Cost Path: cost " + str(cost) + ", length " + str(len(path)) + "\n    "
    else:
        return "Optimal Cost Path: " + start_city + ", cost " + str(cost) + ", length " + str(len(path)) + "\n    "


def handle_query(database, board, visual, query):
    tokenized = query.split(' ')
    keyword = tokenized[0]
    tokenized = tokenized[1:]
    output = ""
    color = (random.randrange(0, 150), random.randrange(0, 150), random.randrange(0, 150))

    # QUERY = clear board
    if keyword == "clean":
        visual.clean()

    # QUERY = city
    elif keyword == "city":
        for city in tokenized:
            if city in database["cities"]:
                visual.mark_city(database["cities"][city]["coords"], (124, 255, 75))
                print(tokenized[0])
                print(city)
                output += print_city(database, tokenized[0])

    # QUERY = load
    elif keyword == "load":
        for load in tokenized:
            if load in database["loads"]:
                entry = database["loads"][tokenized[0]]
                for city in entry:
                    visual.mark_city(database["cities"][city]["coords"], color)
                    output += print_city(database, city)

    return output


if __name__ == '__main__':
    visual = Visual(DEFAULT_IMG_PATH)

    database, board = load_files(DEFAULT_DB_PATH, DEFAULT_BOARD_PATH)
    i = 1
    while True:
        visual.update()
        raw_expression = input(str(i) + ": ")
        if raw_expression == "exit":
            visual.quit()
            break
        else:
            try:
                output = handle_query(database, board, visual, raw_expression)
                if len(output) > 0:
                    print("  >", output)
            except Exception as error:
                import traceback
                traceback.print_exc()
                print("  > ERROR:", str(error))
        i += 1