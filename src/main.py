from utils import *
from mytrack import *
from visual import *
from board import *
from optparse import OptionParser
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

def handle_query(database, board, my_track, visual, query):
    tokenized = query.split(' ')
    keyword = tokenized[0]
    tokenized = tokenized[1:]
    output = ""
    color = (random.randrange(0, 150), random.randrange(0, 150), random.randrange(0, 150))
    
    # QUERY = clear board
    if keyword == "clean":
        visual.clean()
        if len(tokenized) >= 2 and tokenized[1] == "all":
            my_track.clean()
        else:
            for track in my_track:
                visual.draw_path(track, color)

    elif keyword == "save":
        my_track.save_queued_track()
        
    else:
        my_track.empty_queued_track()

        # QUERY = city
        if keyword == "city":
            for city in tokenized:
                if city in database["cities"]:
                    visual.mark_city(database["cities"][city]["coords"], color)
                    output += print_city(database, tokenized[0])
    
        # QUERY = load
        elif keyword == "load":
            for load in tokenized:
                if load in database["loads"]:
                    entry = database["loads"][tokenized[0]]
                    for city in entry:
                        visual.mark_city(database["cities"][city]["coords"], color)
                        output += print_city(database, city)
            
        # QUERY = two cities
        elif (keyword == "path" or keyword == "path*") and len(tokenized) == 2:
            # TODO: expand to accommodate more than two cities
            start_city = tokenized[0]
            end_city = tokenized[1]
            
            if start_city in database["cities"] and end_city in database["cities"]:
                start_city_loc = database["cities"][start_city]["coords"]
                end_city_loc = database["cities"][end_city]["coords"]
        
                visual.mark_city(start_city_loc, color)
                visual.mark_city(end_city_loc, color)
                output += print_city(database, start_city)
                output += print_city(database, end_city)
                
                path, cost = find_path(start_city_loc, board, lambda p: p == end_city_loc)
                my_track.append_to_queue(path)
                output += print_path(path, cost)
                visual.draw_path(path, color)
                
            elif start_city not in database["cities"]:
                raise ValueError(start_city + " is not a city in the database.")
            elif end_city not in database["cities"]:
                raise ValueError(end_city + " is not a city in the database.")
    
        # QUERY = destination city and load
        elif (keyword == "mission" or keyword == "mission*") and len(tokenized) >= 2:
            load = tokenized[0]
            end_city = tokenized[1]
            if end_city in database["cities"] and load in database["loads"]:
                start_cities = database["loads"][load][:]
                if len(tokenized) >= 3:
                    mode = tokenized[2]
                else:
                    mode = "all"
        
                if mode == "best": # find best path from load to city
                    load_city_locs = [database["cities"][sc]["coords"] for sc in start_cities]
                    end_city_loc = database["cities"][end_city]["coords"]
                    path, cost = find_path(end_city_loc, board, lambda p: p in load_city_locs)
                    my_track.append_to_queue(path)
                    best_load_city = database["points"][path[-1]]
        
                    visual.mark_city(database["cities"][best_load_city]["coords"], color)
                    output += print_city(database, best_load_city)
                    visual.mark_city(database["cities"][end_city]["coords"], color)
                    output += print_city(database, end_city)
                    
                    output += print_path(path, cost, best_load_city)
                    visual.draw_path(path, color)
                
                else: # default option -> mode == "all"; find all paths from load to city
                    for sc in start_cities:
                        visual.mark_city(database["cities"][sc]["coords"], color)
                        output += print_city(database, sc)
                    visual.mark_city(database["cities"][end_city]["coords"], color)
                    output += print_city(database, end_city)
    
                    for sc in start_cities:
                        start_city_loc = database["cities"][sc]["coords"]
                        end_city_loc = database["cities"][end_city]["coords"]
                        
                        path, cost = find_path(start_city_loc, board, lambda p: p == end_city_loc)
                        my_track.append_to_queue(path)
                        output += print_path(path, cost, sc)
                        visual.draw_path(path, color)
            
            elif end_city not in database["cities"]:
                raise ValueError(end_city + " is not a city in the database.")
            elif load not in database["loads"]:
                raise ValueError(load + " is not a valid load in the database.")
        
        # QUERY = connect cities to existing track
        elif keyword == "add" or keyword == "add*" or keyword == "addcity" or keyword == "addcity*":
            
            if not my_track.has_track:
                raise Exception("No track currently owned.")
    
            for q in tokenized:
                if q in database["cities"]:
                    city = q
                    city_loc = database["cities"][city]["coords"]
                    visual.mark_city(city_loc, color)
                    output += print_city(database, city)
                    path, cost = find_path(city_loc, board, lambda p: p == p in my_track)
                    my_track.append_to_queue(path)
                    
                    visual.draw_path(path, color)
                    output += "Optimal Cost Path: cost " + str(cost) + ", length " + str(len(path))

        # QUERY = connect loads to existing track
        elif keyword == "addload" or keyword == "addload*":
        
            if not my_track.has_track:
                raise Exception("No track currently owned.")
        
            for q in tokenized:
                if q in database["loads"]:
                    load_cities = database["loads"][q][:]
                    for sc in load_cities:
                        visual.mark_city(database["cities"][sc]["coords"], color)
                        output += print_city(database, sc)
        
                    opt_path = None
                    opt_cost = None
                    opt_city = None
                    for sc in load_cities:
                        load_city_loc = database["cities"][sc]["coords"]
        
                        path, cost = find_path(load_city_loc, board, lambda p: p in my_track)
        
                        if opt_cost is None or cost < opt_cost or (
                                cost == opt_cost and len(path) < len(opt_path)):
                            opt_path = path
                            opt_cost = cost
                            opt_city = sc
        
                        output += print_path(path, cost, sc)
        
                    output += "Best: " + opt_city + "\n    "
                    my_track.append_to_queue(opt_path)
                    visual.draw_path(opt_path, color)
        
        elif keyword == "draw" or keyword == "draw*":
            path = []
            for loc in tokenized:
                if loc in database["cities"]: # city
                    path.append(database["cities"][loc]["coords"])
                elif type(loc) == tuple and len(loc) == 2: # loc
                    path.append(loc)
                elif len(path) >= 1:
                    if loc == "r":
                        path.append((path[-1][0] + 1, path[-1][1]))
                    elif loc == "l":
                        path.append((path[-1][0] - 1, path[-1][1]))
                    elif loc == "ur":
                        path.append((path[-1][0], path[-1][1] + 1))
                    elif loc == "ul":
                        path.append((path[-1][0] - 1, path[-1][1] + 1))
                    elif loc == "dl":
                        path.append((path[-1][0], path[-1][1] - 1))
                    elif loc == "dr":
                        path.append((path[-1][0] + 1, path[-1][1] - 1))
            visual.draw_path(path, color)
        
        elif len(query.strip()) > 0:
            raise ValueError("Query could not be processed.")

    if keyword[-1] == '*':
        my_track.save_queued_track()

    return output
    

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--database", dest="db_path", default=str(DEFAULT_DB_PATH))
    parser.add_option("--board", dest="board_path", default=str(DEFAULT_BOARD_PATH))
    parser.add_option("--harbors", dest="harbor_path", default=str(DEFAULT_HARBOR_PATH))
    opts, args = parser.parse_args()

    database, board = load_files(opts.db_path, opts.board_path, opts.harbor_path)
    visual = Visual(DEFAULT_IMG_PATH)
    my_track = MyTrack(board)

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
                output = handle_query(database, board, my_track, visual, raw_expression)
                if len(output) > 0:
                    print("  >", output)
            except Exception as error:
                import traceback
                traceback.print_exc()
                print("  > ERROR:", str(error))
        i += 1