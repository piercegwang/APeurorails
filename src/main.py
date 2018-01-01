from utils import *
from mytrack import *
from visual import *
from board import *
from log import *
from collections import deque
from optparse import OptionParser
import random

DEFAULT_DB_PATH = "../database/eurorails.json"
DEFAULT_BOARD_PATH = "../database/board_ascii.txt"
DEFAULT_IMG_PATH = "../database/board.jpg"
DEFAULT_HARBOR_PATH = "../database/harbors.txt"
DEFAULT_RESULTS_PATH = "../results/"
INDENT_1 = "    "
INDENT_2 = INDENT_1 + "  "

def print_city(database, city):
    """
    Produces console output text for a city

    :param database: city database
    :param city: string containing name of city
    :return: string containing console output, with indents
    """
    entry = database["cities"][city]
    output = city + ":\n"
    output += INDENT_2 + "Location: (" + str(entry["coords"][0]) + ", " + str(entry["coords"][1]) + ")\n"
    output += INDENT_2 + "Load: "
    if len(entry["loads"]) > 0:
        for l in entry["loads"]:
            output += l + " "
    else:
        output += "none"
    output += "\n"
    output += INDENT_2 + "Land: " + entry["island"] + "\n"
    output += INDENT_2 + "City Type: " + entry["type"] + "\n"
    output += INDENT_1

    return output

def print_path(path, cost, start_city=None):
    """
    Produces console output text for a path.

    :param path: list of points in path.
    :param cost: integer containing Cost to build path.
    :param start_city: string containing name of city associated with path, or None if no city exists.
    :return: string containing console output
    """
    if start_city is None:
        return "Optimal Cost Path: cost " + str(cost) + ", length " + str(len(path)) + "\n" + INDENT_1
    else:
        return "Optimal Cost Path: " + start_city + ", cost " + str(cost) + ", length " + str(len(path)) + "\n" + INDENT_1

def clear_extra(my_track, log, visual):
    """
    Clear extra tracks which don't belong to my_track from visual.

    :param my_track: MyTrack object containing currently owned track.
    :param log: Log object containing a history of all saved actions.
    :param visual: Visual object containing the GUI
    :return: None   TODO: return True if successful
    """
    my_track.clean() # clears track and empties queue
    my_track.add_from_log(log) # takes each saved action from log and adds it to my_track
    visual.redraw() # redraw visual

def undo(my_track, log, visual):
    """
    Undo last recorded query in log.
    
    :param my_track: MyTrack object containing currently owned track.
    :param log: Log object containing a history of all saved actions.
    :param visual: Visual object containing the GUI
    :return: None   TODO: return True if successful
    """
    my_track.clean()
    log.pop() # undo last action in log
    my_track.add_from_log(log)  # takes each saved action from log and adds it to my_track
    visual.redraw()

def handle_query(database, board, my_track, log, visual, results_path, query):
    """
    Query handler for program.
    
    :param database: dictionary containing Eurorails database (cities, loads).
    :param board: Board object containing ASCII map of board.
    :param my_track: MyTrack object containing currently owned track.
    :param log: Log object containing a history of all saved actions.
    :param visual: Visual object containing the GUI.
    :param query: string containing the user's query. Unprocessed when passed to query handler. See README API for keywords.
    :return: string containing console output of query.
    """
    tokenized = query.split(' ')
    keyword = tokenized[0]
    tokenized = tokenized[1:] # remove keyword from tokenized
    output = ""
    color = (random.randrange(0, 150), random.randrange(0, 150), random.randrange(0, 150))
    save = len(keyword) > 0 and keyword[-1] == "*" # check if save character is at the end of the keyword
    if save:
        keyword = keyword[:-1]
    
    # QUERY = clear board
    if keyword == "clean":
        if len(tokenized) >= 2 and tokenized[1] == "all": # remove everything
            visual.clean()
            log.clean()
            my_track.clean()
        else:
            clear_extra(my_track, log, visual)
        

    # QUERY = save last command to real track
    elif keyword == "save":
        my_track.save_queued_track(log, True)

    # QUERY = undo
    elif keyword == "undo":
        undo(my_track, log, visual)
        
    # QUERY = print
    elif keyword == "print":
        sec_keyword = tokenized[0]
        
        # QUERY = print log
        if sec_keyword == "log":
            output += log.print()
    
        # QUERY = print missions
        elif sec_keyword == "missions":
            output += my_track.print_current_mission_cards()

    # QUERY = city
    elif keyword == "city":
        for city in tokenized:
            if city in database["cities"]:
                visual.mark_city(database["cities"][city]["coords"], color)
                output += print_city(database, city)

    # QUERY = load
    elif keyword == "load":
        for load in tokenized:
            if load in database["loads"]:
                entry = database["loads"][load]
                for city in entry:
                    visual.mark_city(database["cities"][city]["coords"], color)
                    output += print_city(database, city)
    
    else: # all other queries run clear_extra first
        clear_extra(my_track, log, visual)

        # QUERY = multiple cities
        if keyword == "path" and len(tokenized) >= 2:
            cities = []
            for c in tokenized:
                if c in database["cities"]:
                    cities.append([database["cities"][c]["coords"]])
                    visual.mark_city(database["cities"][c]["coords"], color)
                    output += print_city(database, c)
            all_paths, cost = connect_cities(board, None, cities, number_tries=len(cities))
            
            for p in all_paths:
                my_track.append_to_queue(p)
                visual.draw_path(p, color)
            output += "Total cost: " + str(cost) + "\n" + INDENT_1
    
        # QUERY = destination city and load
        elif keyword == "mission" and len(tokenized) >= 2:
            load = tokenized[0]
            end_city = tokenized[1]
            mode = None
            if end_city in database["cities"] and load in database["loads"]:
                start_cities = database["loads"][load][:]
                if len(tokenized) > 2:
                    mode = tokenized[2]
                if mode != "all" and mode != "best":
                    mode = "best" if save else "all"

                end_city_loc = database["cities"][end_city]["coords"]
                visual.mark_city(end_city_loc, color)
                output += print_city(database, end_city)
        
                if mode == "best": # find best path from load to city
                    load_city_locs = [database["cities"][sc]["coords"] for sc in start_cities]
                    
                    path, cost = find_path(load_city_locs, board, my_track, lambda p: p == end_city_loc)
                    my_track.append_to_queue(path)
                    best_load_city = database["points"][path[0]]
        
                    visual.mark_city(database["cities"][best_load_city]["coords"], color)
                    output += print_city(database, best_load_city)
                    
                    output += print_path(path, cost, best_load_city)
                    visual.draw_path(path, color)
                
                elif mode == "all": # default option -> mode == "all"; find all paths from load to city
                    # output all cities first before paths
                    for sc in start_cities:
                        visual.mark_city(database["cities"][sc]["coords"], color)
                        output += print_city(database, sc)
    
                    for sc in start_cities:
                        start_city_loc = database["cities"][sc]["coords"]
                        
                        path, cost = find_path(start_city_loc, board, my_track, lambda p: p == end_city_loc)
                        my_track.append_to_queue(path)
                        output += print_path(path, cost, sc)
                        visual.draw_path(path, color)
        
        elif keyword == "add" and len(tokenized) >= 2:
            sec_keyword = tokenized[0]
            tokenized = tokenized[1:]
        
            # QUERY = connect cities and loads to existing track
            if sec_keyword == "city" or sec_keyword == "load":
                cities = []
                i = 0
                while i < len(tokenized):
                    if tokenized[i] == "city" or tokenized[i] == "load":
                        sec_keyword = tokenized[i]
                    elif tokenized[i] == "one_major":
                        cities.append([database["cities"][c]["coords"] for c in MAJOR_CITIES])
                    elif tokenized[i] == "all_majors":
                        for c in MAJOR_CITIES:
                            cities.append([database["cities"][c]["coords"]])
                    if sec_keyword == "city":
                        c = tokenized[i]
                        if c in database["cities"]:
                            cities.append([database["cities"][c]["coords"]])
                            visual.mark_city(database["cities"][c]["coords"], color)
                            output += print_city(database, c)
                    elif sec_keyword == "load":
                        l = tokenized[i]
                        if l in database["loads"]:
                            cities.append([database["cities"][c]["coords"] for c in database["loads"][l]])
                            for co in cities[-1]:
                                visual.mark_city(co, color)
                                output += print_city(database, database["points"][co])
                    i += 1
                
                all_paths, cost = connect_cities(board, my_track, cities, number_tries=len(cities))

                for p in all_paths:
                    my_track.append_to_queue(p)
                    visual.draw_path(p, color)
                output += "Total cost: " + str(cost) + "\n" + INDENT_1

            # QUERY = connect load and destination city to existing track
            if sec_keyword == "mission":
                cities = []
                
                load = tokenized[0]
                city = tokenized[1]

                if city in database["cities"]:
                    cities.append([database["cities"][city]["coords"]])
                    visual.mark_city(database["cities"][city]["coords"], color)
                    output += print_city(database, city)
                
                if load in database["loads"]:
                    cities.append([database["cities"][c]["coords"] for c in database["loads"][load]])
                    for co in cities[-1]:
                        visual.mark_city(co, color)
                        output += print_city(database, database["points"][co])
                
                all_paths, cost = connect_cities(board, my_track, cities, number_tries=len(cities))

                for p in all_paths:
                    my_track.append_to_queue(p)
                    visual.draw_path(p, color)
                output += "Total cost: " + str(cost) + "\n" + INDENT_1

            # QUERY = add a new mission card
            elif sec_keyword == "card":
                if len(tokenized) < 9:
                    raise SyntaxError("Insufficient number of fields in mission card.")
                my_track.save_mission_card((tokenized[0], tokenized[1], tokenized[2]),
                                           (tokenized[3], tokenized[4], tokenized[5]),
                                           (tokenized[6], tokenized[7], tokenized[8]))

            # QUERY exists but could not be processed
            elif len(query.strip()) > 0:
                raise ValueError("Query could not be processed.")

        # QUERY = compute best track for select missions
        elif keyword == "compute" and len(tokenized) >= 1:
            sec_keyword = tokenized[0]
            if sec_keyword == "all": # compute over all selections of missions
                tokenized = tokenized[1:]
                if len(tokenized) >= 3: # missions were specified
                    choose_mission_1 = tokenized[0] == "y"
                    choose_mission_2 = tokenized[1] == "y"
                    choose_mission_3 = tokenized[2] == "y"
                else: # default: check all cards
                    choose_mission_1 = True
                    choose_mission_2 = True
                    choose_mission_3 = True

                costs, rewards = my_track.compute_all(choose_mission_1, choose_mission_2, choose_mission_3, log,
                                                      visual, color, results_path)
                for i in range(len(costs)):
                    output += "Cost " + str(i + 1) + ":   " + str(costs[i]) + "\n      "
                    output += "Reward " + str(i + 1) + ": " + str(rewards[i]) + "\n    "

            else: # choose specific missions from each card
                select_1 = int(tokenized[0]) if tokenized[0] != '0' else None
                select_2 = int(tokenized[1]) if tokenized[1] != '0' else None
                select_3 = int(tokenized[2]) if tokenized[2] != '0' else None
                if len(tokenized) >= 4:
                    include_majors = tokenized[3] != "n"
                else:
                    include_majors = True

                all_paths, cost, reward = my_track.compute_optimal_track(select_1, select_2, select_3, include_majors)
                for p in all_paths:
                    visual.draw_path(p, color)
                    my_track.append_to_queue(p)
                output += "Total Cost: " + str(cost) + "\n" + INDENT_1
                output += "Reward: " + str(reward) + "\n" + INDENT_1

        # QUERY = draw a custom path
        elif keyword == "draw":
            path = []
            for loc in tokenized:
                if loc in database["cities"]: # city
                    path.append(database["cities"][loc]["coords"])
                elif type(loc) == tuple and len(loc) == 2: # absolute coordinates
                    path.append(loc)
                elif len(path) >= 1: # relative path
                    if loc == "r":
                        path.append((path[-1][0] + 1, path[-1][1]))
                    elif loc == "l":
                        path.append((path[-1][0] - 1, path[-1][1]))
                    elif loc == "ur" or loc == "u":
                        path.append((path[-1][0], path[-1][1] + 1))
                    elif loc == "ul":
                        path.append((path[-1][0] - 1, path[-1][1] + 1))
                    elif loc == "dl" or loc == "d":
                        path.append((path[-1][0], path[-1][1] - 1))
                    elif loc == "dr":
                        path.append((path[-1][0] + 1, path[-1][1] - 1))
                else:
                    raise ValueError("point argument not understood.")
            visual.draw_path(path, color)
            my_track.append_to_queue(path)
        
        # QUERY = remove a mission card
        elif keyword == "remove" and len(tokenized) >= 1:
            sec_keyword = tokenized[0]
            tokenized = tokenized[1:]
            if sec_keyword == "card":
                my_track.remove_mission_card(int(tokenized[0]))
        
        # QUERY = toggle harbor penalty
        elif keyword == "toggle" and len(tokenized) >= 1:
            sec_keyword = tokenized[0]
            if sec_keyword == "harbor":
                board.cycle_harbor_penalty()
                output += "Harbor penalty: " + ("REG" if board.harbor_penalty == REG_HARBOR_PENALTY else "HIGH") + "\n" + INDENT_1

        # QUERY could not be processed
        elif len(query.strip()) > 0:
            raise ValueError("Query could not be processed.")

    if save:
        my_track.save_queued_track(log, True)

    return output
    

if __name__ == '__main__':
    random.seed()
    
    parser = OptionParser()
    parser.add_option("--database", dest="db_path", default=str(DEFAULT_DB_PATH))
    parser.add_option("--board", dest="board_path", default=str(DEFAULT_BOARD_PATH))
    parser.add_option("--image", dest="image_path", default=str(DEFAULT_IMG_PATH))
    parser.add_option("--harbors", dest="harbor_path", default=str(DEFAULT_HARBOR_PATH))
    parser.add_option("--results", dest="results_path", default=str(DEFAULT_RESULTS_PATH))
    opts, args = parser.parse_args()

    database, board = load_files(opts.db_path, opts.board_path, opts.harbor_path)
    log = Log(database)
    visual = Visual(opts.image_path, log)
    my_track = MyTrack(board, database)
    results_path = opts.results_path

    queue = deque()
    i = 1
    while True:
        # update log and visual
        log.step()
        visual.update()

        # Check if actions are queued, or else get new action
        if len(queue) > 0:
            raw_expression = queue.popleft()
            print(str(i) + ": " + raw_expression)
        else:
            raw_expression = input(str(i) + ": ")

        # reload database files
        if raw_expression == "reload":
            database, board = load_files(opts.db_path, opts.board_path, opts.harbor_path)
            log.update_database(database)
            my_track.update_database(database)

        # load queries from specified file
        elif raw_expression[:4] == "file":
            tokenized = raw_expression.split(' ')
            queries = open(tokenized[1]).read().split('\n')
            for q in queries:
                queue.append(q)

        # exit out of program
        elif raw_expression == "e" or raw_expression == "exit":
            visual.quit()
            break
        
        else: # handle query
            try:
                output = handle_query(database, board, my_track, log, visual, results_path, raw_expression)
                if len(output) > 0:
                    print("  >", output)
            except Exception as error:
                import traceback
                traceback.print_exc()
                print("  > ERROR:", str(error))
        i += 1