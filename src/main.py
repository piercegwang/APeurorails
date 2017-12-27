from utils import *
from optparse import OptionParser

DEFAULT_DB_PATH = "../database/eurorails.json"
DEFAULT_BOARD_PATH = "../database/board_ascii.txt"
DEFAULT_IMG_PATH = "../database/board.jpg"

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

    return output

def handle_query(database, visual, query):
    # QUERY = clear board
    if query == "clear":
        visual.clear()
        return "string string string string board cleared string string"

    # QUERY = city
    elif query in database["cities"]:
        return print_city(database, query)

    # QUERY = load
    elif query in database["loads"]:
        entry = database["loads"][query]
        output = ""
        for city in entry:
            output += print_city(database, city) + "\n    "
        return output

    else:
        visual.draw_path((0, 0), (100, 100))
        raise ValueError("Query could not be processed.")

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--database", dest="db_path", default=str(DEFAULT_DB_PATH))
    parser.add_option("--board", dest="board_path", default=str(DEFAULT_BOARD_PATH))
    opts, args = parser.parse_args()

    database, board = load_files(opts.db_path, opts.board_path)
    visual = Visual(DEFAULT_IMG_PATH)

    i = 1
    while True:
        visual.update()
        raw_expression = input(str(i) + ": ")
        if raw_expression == "exit":
            visual.quit()
            break
        else:
            try:
                output = handle_query(database, visual, raw_expression)
                if output is not None:
                    print("  >", output)
            except Exception as error:
                print("  > ERROR:", str(error))
        i += 1