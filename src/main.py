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
DEFAULT_MISSIONS_PATH = "../results/"

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

def clear_extra(my_track, log, visual):
    my_track.clean()
    my_track.queue_from_log(log)
    my_track.save_queued_track(log, False)
    visual.redraw()

def undo(my_track, log, visual):
    my_track.clean()
    log.pop()
    my_track.queue_from_log(log)
    my_track.save_queued_track(log, False)
    visual.redraw()

def handle_query(database, board, my_track, log, visual, query):
    tokenized = query.split(' ')
    keyword = tokenized[0]
    tokenized = tokenized[1:]
    output = ""
    color = (random.randrange(0, 150), random.randrange(0, 150), random.randrange(0, 150))
    save = len(keyword) > 0 and keyword[-1] == "*"
    if save:
        keyword = keyword[:-1]
    
    # QUERY = clear board
    if keyword == "clean":
        if len(tokenized) >= 2 and tokenized[1] == "all":
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
        tokenized = tokenized[1:]
        
        # QUERY = print log
        if sec_keyword == "log":
            return log.print()
    
        # QUERY = print missions
        elif sec_keyword == "missions":
            return my_track.print_current_mission_cards()

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
                entry = database["loads"][tokenized[0]]
                for city in entry:
                    visual.mark_city(database["cities"][city]["coords"], color)
                    output += print_city(database, city)
    
    else:
        clear_extra(my_track, log, visual)

        # QUERY = two cities
        if keyword == "path" and len(tokenized) >= 2:
            start_city = tokenized[0]
            end_city = tokenized[1]
            additional_cities = tokenized[2:]
            
            if start_city in database["cities"] and end_city in database["cities"]:
                start_city_loc = database["cities"][start_city]["coords"]
                end_city_loc = database["cities"][end_city]["coords"]
        
                visual.mark_city(start_city_loc, color)
                visual.mark_city(end_city_loc, color)
                output += print_city(database, start_city)
                output += print_city(database, end_city)
                
                path, cost = find_path(end_city_loc, board, my_track, lambda p: p == start_city_loc)
                my_track.append_to_queue(path)
                output += print_path(path, cost)
                visual.draw_path(path, color)
            
            if len(additional_cities) > 0:
                for city in additional_cities:
                    my_track.save_queued_track(log, save)
                    city_loc = database["cities"][city]["coords"]
    
                    visual.mark_city(city_loc, color)
                    output += print_city(database, city)
    
                    path, cost = find_path(city_loc, board, my_track, lambda p: p in my_track)
                    my_track.append_to_queue(path)
                    output += print_path(path, cost)
                    visual.draw_path(path, color)
            
                my_track.save_queued_track(log, save)
    
        # QUERY = destination city and load
        elif keyword == "mission" and (len(tokenized) >= 3):
            if tokenized[0] in ('1', '2', '3') and tokenized[1] in ('1', '2', '3'):
                mission = my_track.get_mission_card(int(tokenized[0])).get_mission(int(tokenized[1]))
                load = mission.load
                end_city = mission.dest
                reward = mission.reward
                tokenized = tokenized[2:]
            else:
                load = tokenized[0]
                end_city = tokenized[1]
                reward = tokenized[2]
                tokenized = tokenized[3:]
            mode = None
            if end_city in database["cities"] and load in database["loads"]:
                start_cities = database["loads"][load][:]
                if len(tokenized) > 0:
                    mode = tokenized[0]
                if mode != "all" and mode != "best":
                    mode = "default"
        
                if mode == "best" or (mode == "default" and save): # find best path from load to city
                    load_city_locs = [database["cities"][sc]["coords"] for sc in start_cities]
                    end_city_loc = database["cities"][end_city]["coords"]
                    path, cost = find_path(end_city_loc, board, my_track, lambda p: p in load_city_locs)
                    my_track.append_to_queue(path)
                    best_load_city = database["points"][path[0]]
        
                    visual.mark_city(database["cities"][best_load_city]["coords"], color)
                    output += print_city(database, best_load_city)
                    visual.mark_city(database["cities"][end_city]["coords"], color)
                    output += print_city(database, end_city)
                    
                    output += print_path(path, cost, best_load_city)
                    visual.draw_path(path, color)
                    output += "Cost:   " + str(cost) + "\n    "
                
                elif mode == "all" or (mode == "default" and not save): # default option -> mode == "all"; find all paths from load to city
                    for sc in start_cities:
                        visual.mark_city(database["cities"][sc]["coords"], color)
                        output += print_city(database, sc)
                    visual.mark_city(database["cities"][end_city]["coords"], color)
                    output += print_city(database, end_city)
    
                    for sc in start_cities:
                        start_city_loc = database["cities"][sc]["coords"]
                        end_city_loc = database["cities"][end_city]["coords"]
                        
                        path, cost = find_path(start_city_loc, board, my_track, lambda p: p == end_city_loc)
                        my_track.append_to_queue(path)
                        output += print_path(path, cost, sc)
                        visual.draw_path(path, color)

                output += "Reward: " + str(reward) + "\n    "
            
            elif end_city not in database["cities"]:
                raise ValueError(end_city + " is not a city in the database.")
            elif load not in database["loads"]:
                raise ValueError(load + " is not a valid load in the database.")
        
        elif keyword == "add":
            sec_keyword = tokenized[0]
            tokenized = tokenized[1:]
        
            # QUERY = connect cities to existing track
            if sec_keyword == "city":
                
                if not my_track.has_track:
                    raise Exception("No track currently owned.")
        
                for q in tokenized:
                    if q in database["cities"]:
                        city = q
                        city_loc = database["cities"][city]["coords"]
                        visual.mark_city(city_loc, color)
                        output += print_city(database, city)
                        path, cost = find_path(city_loc, board, my_track, lambda p: p == p in my_track)
                        my_track.append_to_queue(path)
                        
                        visual.draw_path(path, color)
                        output += print_path(path, cost)
    
            # QUERY = connect loads to existing track
            elif sec_keyword == "load":
            
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
            
                            path, cost = find_path(load_city_loc, board, my_track, lambda p: p in my_track)
            
                            if opt_cost is None or cost < opt_cost or (
                                    cost == opt_cost and len(path) < len(opt_path)):
                                opt_path = path
                                opt_cost = cost
                                opt_city = sc
            
                            output += print_path(path, cost, sc)
            
                        output += "Best: " + opt_city + "\n    "
                        my_track.append_to_queue(opt_path)
                        visual.draw_path(opt_path, color)
    
            # QUERY = destination city and load
            elif sec_keyword == "mission" and (len(tokenized) == 2 or len(tokenized) == 3):
                
                if tokenized[0] in ('1', '2', '3') and tokenized[1] in ('1', '2', '3'):
                    mission = my_track.get_mission_card(int(tokenized[0])).get_mission(int(tokenized[1]))
                    load = mission.load
                    end_city = mission.dest
                    reward = mission.reward
                else:
                    load = tokenized[0]
                    end_city = tokenized[1]
                    reward = tokenized[2]
                end_city_loc = database["cities"][end_city]["coords"]
                
                if end_city in database["cities"] and load in database["loads"]:
                    start_cities = database["loads"][load][:]
    
                    for sc in start_cities:
                        visual.mark_city(database["cities"][sc]["coords"], color)
                        output += print_city(database, sc)
                    visual.mark_city(database["cities"][end_city]["coords"], color)
                    output += print_city(database, end_city)
    
                    path, cost = find_path(end_city_loc, board, my_track, lambda p: p in my_track)
                    my_track.append_to_queue(path)
                    output += print_path(path, cost, end_city)
                    visual.draw_path(path, color)
                    my_track.save_queued_track(log, save)
    
                    opt_load_city = None
                    opt_path = None
                    opt_cost = None
                    for sc in start_cities:
                        start_city_loc = database["cities"][sc]["coords"]
                        end_city_loc = database["cities"][end_city]["coords"]
    
                        path, cost = find_path(start_city_loc, board, my_track, lambda p: p in my_track)
                        
                        if opt_cost is None or cost < opt_cost:
                            opt_load_city = sc
                            opt_path = path
                            opt_cost = cost
                            
                    my_track.append_to_queue(opt_path)
                    output += print_path(opt_path, opt_cost, opt_load_city)
                    visual.draw_path(opt_path, color)
                    output += "Cost:   " + str(opt_cost) + "\n    "
                    output += "Reward: " + str(reward) + "\n    "

            # QUERY = add a new mission card
            elif sec_keyword == "card":
                if len(tokenized) < 9:
                    raise ValueError("Missing fields in mission card.")
                my_track.save_mission_card((tokenized[0], tokenized[1], tokenized[2]), (tokenized[3], tokenized[4],
                                           tokenized[5]), (tokenized[6], tokenized[7], tokenized[8]))

            # QUERY exists but could not be processed
            elif len(query.strip()) > 0:
                raise ValueError("Query could not be processed.")

        # QUERY = compute best track for select missions
        elif keyword == "compute":
            select_1 = int(tokenized[0])
            select_2 = None
            select_3 = None
            if len(tokenized) >= 2:
                select_2 = int(tokenized[1])
                if len(tokenized) >= 3:
                    select_3 = int(tokenized[2])
            all_paths, cost, reward = my_track.compute_optimal_track(select_1, select_2, select_3, True)
            for p in all_paths:
                visual.draw_path(p, color)
                my_track.append_to_queue(p)
            output += "Total Cost: " + str(cost) + "\n    "
            output += "Reward: " + str(reward) + "\n    "

        # QUERY = compute all missions
        elif keyword == "all" and len(tokenized) >= 3:
            choose_mission_1 = tokenized[0] == "y"
            choose_mission_2 = tokenized[1] == "y"
            choose_mission_3 = tokenized[2] == "y"
            costs, rewards = my_track.compute_all(choose_mission_1, choose_mission_2, choose_mission_3, log, visual, color, DEFAULT_MISSIONS_PATH)
            for i in range(len(costs)):
                output += "Cost " + str(i+1) + ":   " + str(costs[i]) + "\n      "
                output += "Reward " + str(i+1) + ": " + str(rewards[i]) + "\n    "

        # QUERY = draw a custom path
        elif keyword == "draw":
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
            my_track.append_to_queue(path)
        
        # QUERY = remove a mission card
        elif keyword == "remove":
            sec_keyword = tokenized[0]
            tokenized = tokenized[1:]
            if sec_keyword == "card":
                my_track.remove_mission_card(int(tokenized[0]))
        
        # QUERY exists but could not be processed
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
    parser.add_option("--harbors", dest="harbor_path", default=str(DEFAULT_HARBOR_PATH))
    opts, args = parser.parse_args()

    database, board = load_files(opts.db_path, opts.board_path, opts.harbor_path)
    log = Log(database)
    visual = Visual(DEFAULT_IMG_PATH, log)
    my_track = MyTrack(board, database)

    queue = deque()
    i = 1
    while True:
        log.step()
        visual.update()

        if len(queue) > 0:
            raw_expression = queue.popleft()
            print(str(i) + ": " + raw_expression)
        else:
            raw_expression = input(str(i) + ": ")

        if raw_expression == "reload":
            database, board = load_files(opts.db_path, opts.board_path, opts.harbor_path)
            log.update_database(database)
            my_track.update_database(database)

        # QUERY = file
        elif raw_expression[:4] == "file":
            tokenized = raw_expression.split(' ')
            queries = open(tokenized[1]).read().split('\n')
            for q in queries:
                queue.append(q)


        elif raw_expression == "e" or raw_expression == "exit":
            visual.quit()
            break
        
        else:
            try:
                output = handle_query(database, board, my_track, log, visual, raw_expression)
                if len(output) > 0:
                    print("  >", output)
            except Exception as error:
                import traceback
                traceback.print_exc()
                print("  > ERROR:", str(error))
        i += 1