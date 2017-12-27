from utils import *
from optparse import OptionParser

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

    return output

def handle_query(database, board, visual, query):
    tokenized = query.split(' ')
    output = None
    
    # QUERY = clear board
    if tokenized[0] == "clean":
        visual.clean()

    # QUERY = city
    elif len(tokenized) == 1 and tokenized[0] in database["cities"]:
        output = ""
        visual.mark_city(database["cities"][tokenized[0]]["coords"], 0)
        output += print_city(database, tokenized[0])
        output += "\n    "

    # QUERY = load
    elif len(tokenized) == 1 and tokenized[0] in database["loads"]:
        entry = database["loads"][tokenized[0]]
        output = ""
        for city in entry:
            visual.mark_city(database["cities"][city]["coords"], 0)
            output += print_city(database, city) + "\n    "

    # QUERY = two cities
    elif len(tokenized) == 2 and tokenized[0] in database["cities"] and tokenized[1] in database["cities"]:
        start_city = tokenized[0]
        end_city = tokenized[1]
        output = ""

        visual.mark_city(database["cities"][start_city]["coords"], 0)
        visual.mark_city(database["cities"][end_city]["coords"], 0)
        output += print_city(database, start_city) + "\n    "
        output += print_city(database, end_city) + "\n    "
        
        city_loc_1 = database["cities"][start_city]["coords"]
        city_loc_2 = database["cities"][end_city]["coords"]
        path, cost = find_path(city_loc_1, board, lambda p: p == city_loc_2)
        output += "Optimal Cost Path: cost " + str(cost) + ", length " + str(len(path))
        # for pt in path:
        #     output += str(pt) + " "
        output += "\n    "
        visual.draw_path(path, 0)

    # QUERY = destination city and load
    elif len(tokenized) >= 2 and tokenized[0] in database["cities"] and tokenized[1] in database["loads"]:
        end_city = tokenized[0]
        start_cities = database["loads"][tokenized[1]]
        if len(tokenized) >= 3:
            mode = tokenized[2]
        else:
            mode = "all"
        output = ""

        if mode == "best":
            load_city_locs = [database["cities"][sc]["coords"] for sc in start_cities]
            end_city_loc = database["cities"][end_city]["coords"]
            path, cost = find_path(end_city_loc, board, lambda p: p in load_city_locs)
            best_load_city = database["points"][path[-1]]

            visual.mark_city(database["cities"][best_load_city]["coords"], "black")
            output += print_city(database, best_load_city) + "\n    "
            visual.mark_city(database["cities"][end_city]["coords"], "black")
            output += print_city(database, end_city) + "\n    "
            
            output += "Optimal Cost Path: " + best_load_city + ", cost " + str(cost) + ", length " + str(len(path))
            output += "\n    "
            visual.draw_path(path, 0)
        else:
            i = 1
            for sc in start_cities:
                visual.mark_city(database["cities"][sc]["coords"], "black")
                output += print_city(database, sc) + "\n    "
            visual.mark_city(database["cities"][end_city]["coords"], "black")
            output += print_city(database, end_city) + "\n    "
            
            for sc in start_cities:
                city_loc_1 = database["cities"][sc]["coords"]
                city_loc_2 = database["cities"][end_city]["coords"]
                path, cost = find_path(city_loc_1, board, lambda p: p == city_loc_2)
                output += "Optimal Cost Path " + str(i) + ": " + sc + ", cost " + str(cost) + ", length " + str(len(path))
                output += "\n    "
                i += 1
                visual.draw_path(path, 0)
        
    elif len(query.strip()) > 0:
        raise ValueError("Query could not be processed.")

    return output
    

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--database", dest="db_path", default=str(DEFAULT_DB_PATH))
    parser.add_option("--board", dest="board_path", default=str(DEFAULT_BOARD_PATH))
    parser.add_option("--harbors", dest="harbor_path", default=str(DEFAULT_HARBOR_PATH))
    opts, args = parser.parse_args()

    database, board = load_files(opts.db_path, opts.board_path, opts.harbor_path)
    visual = Visual(DEFAULT_IMG_PATH)

    i = 1
    while True:
        visual.update()
        raw_expression = input(str(i) + ": ")
        if raw_expression == "reload":
            database, board = load_files(opts.db_path, opts.board_path, opts.harbor_path)
        elif raw_expression == "exit":
            visual.quit()
            break
        else:
            try:
                output = handle_query(database, board, visual, raw_expression)
                if output is not None:
                    print("  >", output)
            except Exception as error:
                print("  > ERROR:", str(error))
        i += 1