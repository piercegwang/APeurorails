from utils import *
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
    output = ""
    color = (random.randrange(0, 150), random.randrange(0, 150), random.randrange(0, 150))
    
    # QUERY = clear board
    if tokenized[0] == "clean":
        visual.clean()
        # TODO: redraw my track
        if len(tokenized) >= 2 and tokenized[1] == "all":
            my_track.clean()

    elif tokenized[0] == "save":
        my_track.save_queued_track()
        
    else:
        my_track.empty_queued_track()

        # QUERY = city
        if len(tokenized) == 1 and tokenized[0] in database["cities"]:
            visual.mark_city(database["cities"][tokenized[0]]["coords"], color)
            output += print_city(database, tokenized[0])
    
        # QUERY = load
        elif len(tokenized) == 1 and tokenized[0] in database["loads"]:
            entry = database["loads"][tokenized[0]]
            for city in entry:
                visual.mark_city(database["cities"][city]["coords"], color)
                output += print_city(database, city)
    
        # QUERY = two cities
        elif len(tokenized) == 2 and tokenized[0] in database["cities"] and tokenized[1] in database["cities"]:
            start_city = tokenized[0]
            end_city = tokenized[1]
            start_city_loc = database["cities"][start_city]["coords"]
            end_city_loc = database["cities"][end_city]["coords"]
    
            visual.mark_city(start_city_loc, color)
            visual.mark_city(end_city_loc, color)
            output += print_city(database, start_city)
            output += print_city(database, end_city)
            
            path, cost = find_path(start_city_loc, board, lambda p: p == end_city_loc)
            my_track.queue_track(path)
            output += print_path(path, cost)
            visual.draw_path(path, color)
    
        # QUERY = destination city and load
        elif len(tokenized) >= 2 and tokenized[0] in database["cities"] and tokenized[1] in database["loads"]:
            end_city = tokenized[0]
            start_cities = database["loads"][tokenized[1]][:]
            if len(tokenized) >= 3:
                mode = tokenized[2]
            else:
                mode = "all"
    
            if mode == "best":
                load_city_locs = [database["cities"][sc]["coords"] for sc in start_cities]
                end_city_loc = database["cities"][end_city]["coords"]
                path, cost = find_path(end_city_loc, board, lambda p: p in load_city_locs)
                my_track.queue_track(path)
                best_load_city = database["points"][path[-1]]
    
                visual.mark_city(database["cities"][best_load_city]["coords"], color)
                output += print_city(database, best_load_city)
                visual.mark_city(database["cities"][end_city]["coords"], color)
                output += print_city(database, end_city)
                
                output += print_path(path, cost, best_load_city)
                visual.draw_path(path, color)
            else: # mode == "all"
                for sc in start_cities:
                    visual.mark_city(database["cities"][sc]["coords"], color)
                    output += print_city(database, sc)
                visual.mark_city(database["cities"][end_city]["coords"], color)
                output += print_city(database, end_city)
                
                for sc in start_cities:
                    start_city_loc = database["cities"][sc]["coords"]
                    end_city_loc = database["cities"][end_city]["coords"]
                    
                    path, cost = find_path(start_city_loc, board, lambda p: p == end_city_loc)
                    my_track.queue_track(path)
                    output += print_path(path, cost, sc)
                    visual.draw_path(path, color)
        
        # QUERY = connect cities/loads to existing track
        elif tokenized[0] == "add" or tokenized[0] == "add*":
            queries = tokenized[1:]
            
            if not my_track.has_track:
                raise Exception("No track currently owned.")
    
            for q in queries:
                if q in database["cities"]:
                    city = q
                    city_loc = database["cities"][city]["coords"]
                    visual.mark_city(city_loc, color)
                    output += print_city(database, city)
                    path, cost = find_path(city_loc, board, lambda p: p == p in my_track)
                    my_track.queue_track(path)
                    
                    visual.draw_path(path, color)
                    output += "Optimal Cost Path: cost " + str(cost) + ", length " + str(len(path))
                    
                elif q in database["loads"]:
                    load_cities = database["loads"][q][:]
                    for sc in load_cities:
                        visual.mark_city(database["cities"][sc]["coords"], color)
                        output += print_city(database, sc)
    
                    for sc in load_cities:
                        load_city_loc = database["cities"][sc]["coords"]
    
                        path, cost = find_path(load_city_loc, board, lambda p: p in my_track)
                        my_track.queue_track(path)
                        visual.draw_path(path, color)
                        output += print_path(path, cost, sc)
            
            if tokenized[0] == "add*":
                my_track.save_queued_track()
        
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
    my_track = BuiltTrack(board)

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
                # import traceback
                # traceback.print_exc()
                print("  > ERROR:", repr(error))
        i += 1