from board import *
from random import sample
from itertools import permutations

NUMBER_TRIES = 7

class Mission: # takes a the attributes of one mission and puts it in an object
    def __init__(self, load, dest_city, reward):
        self.load = load
        self.dest = dest_city
        self.reward = int(reward)
    
    def __str__(self):
        return self.load.ljust(10) + self.dest.ljust(13) + str(self.reward)

class MissionCard: # takes a list of lists describing up to 3 mission cards
    def __init__(self, mission_1, mission_2, mission_3):
        """
        Note: each mission parameter is a tuple (load, destination_city, reward).
        """
        self.missions = []
        self.missions.append(Mission(mission_1[0], mission_1[1], mission_1[2]))
        self.missions.append(Mission(mission_2[0], mission_2[1], mission_2[2]))
        self.missions.append(Mission(mission_3[0], mission_3[1], mission_3[2]))
    
    def get_mission(self, num):
        if 0 <= num - 1 < len(self.missions):
            if self.missions[num - 1] is not None:
                return self.missions[num - 1]
            else:
                return ValueError("No mission loaded in slot " + str(num) + ".")
        else:
            raise ValueError("Index for mission out of bounds.")
    
    def __iter__(self):
        for mission in self.missions:
            yield mission
    
    def __str__(self):
        output = ""
        for mission in self:
            if mission != self.missions[0]:
                output += "                "
            output += str(mission) + "\n    "
        return output

class Track:
    def __init__(self, board):
        self.min_x = board.min_x
        self.max_x = board.max_x
        self.min_y = board.min_y
        self.max_y = board.max_y
        self.orig_board = board
        self.board = [[0 for _ in range(2 * (abs(self.min_x) + abs(self.max_x) + 1))] for _ in
                      range(2 * (abs(self.min_y) + abs(self.max_y) + 1))]
        self.has_track = False
        self.representatives = set()

    def add_representative(self, x, y):
        self.representatives.add((x, y))
        if (x, y) not in self:
            self.add_point(x, y)

    def set_representative(self, x, y):
        if (x, y) not in self:
            self.add_point(x, y)
        self.representatives = {(x, y)}
    
    def add_point(self, x, y):
        x_index = 2 * (x - self.min_x)
        y_index = 2 * (self.max_y - y)
        if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
            self.board[y_index][x_index] = 1

        if not self.has_track and (x,y) not in self.representatives:
            self.set_representative(x, y)
        self.has_track = True

    def remove_point(self, x, y):
        x_index = 2 * (x - self.min_x)
        y_index = 2 * (self.max_y - y)
        if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
            self.board[y_index][x_index] = 0
        if (x, y) in self.representatives:
            self.representatives.remove((x, y))
        # TODO: check if track is now empty

    def add_track(self, sequence):
        def claim_track(self, x, y, dx, dy):
            x_index = 2 * (x - self.min_x) + dx
            y_index = 2 * (self.max_y - y) - dy
            if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
                self.board[y_index][x_index] = 1

        for i in range(len(sequence)):
            x, y = sequence[i]
            self.add_point(x, y)
            if i < len(sequence) - 1:
                dx = sequence[i + 1][0] - x
                dy = sequence[i + 1][1] - y
                if is_one_step(dx, dy):
                    claim_track(self, x, y, dx, dy)

    def __contains__(self, pt):
        if len(pt) == 2:
            x_index = 2 * (pt[0] - self.min_x)
            y_index = 2 * (self.max_y - pt[1])
            if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
                return self.board[y_index][x_index]
        elif len(pt) == 4:
            x_index = 2 * (pt[0] - self.min_x) + pt[2]
            y_index = 2 * (self.max_y - pt[1]) - pt[3]
            if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
                return self.board[y_index][x_index]
        else:
            return False

    def clean(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                self.board[r][c] = 0
        self.has_track = False
        self.representatives = set()

    def remove_unconnected(self, pt):
        self.set_representative(pt[0], pt[1])
        for x in range(self.min_x, self.max_x + 1):
            for y in range(self.min_y, self.max_y + 1):
                if (x != pt[0] or y != pt[1]) and (x, y) in self:
                    connected = False
                    for dx, dy in ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)):
                        if (x, y, dx, dy) in self:
                            connected = True
                    if not connected:
                        self.remove_point(x, y)

    def __iter__(self):
        for x in range(self.min_x, self.max_x + 1):
            for y in range(self.min_y, self.max_y + 1):
                for dx, dy in ((1, 0), (0, -1), (1, -1)):
                    if (x, y, dx, dy) in self:
                        yield [(x, y), (x + dx, y + dy)]

    def __str__(self):
        output = ""
        for x in range(self.min_x, self.max_x + 1):
            for y in range(self.min_y, self.max_y + 1):
                if (x, y) in self:
                    output += "(" + str(x) + ", " + str(y) + ") "
        return output

    def copy(self):
        copy = Track(self.orig_board)
        copy.board = [[self.board[r][c] for c in range(len(self.board[r]))] for r in range(len(self.board))]
        copy.representatives = self.representatives.copy()
        return copy
    
    def union(self, other):
        if len(self.board) != len(other.board) or len(self.board[0]) != len(other.board[0]):
            raise Exception("union called on boards with different dimensions.")
        for r in range(len(other.board)):
            for c in range(len(other.board[r])):
                if other.board[r][c] == 1:
                    self.board[r][c] = 1

class MyTrack(Track):
    def __init__(self, board, database):
        Track.__init__(self, board)
        self.database = database
        self.queued_track = []
        self.mission_cards = [None, None, None]

    def clean(self):
        Track.clean(self)
        self.empty_queued_track()
    
    def count_major_cities(self):
        major_cities = ["madrid", "london", "paris", "berlin", "ruhr", "wien", "holland", "milano"]
        count = 0
        for mc in major_cities:
            if self.database["cities"][mc]["coords"] in self:
                count += 1
        return count
    
    def update_database(self, database):
        self.database = database
    
    def copy(self):
        copy = MyTrack(self.orig_board, self.database)
        copy.board = [[self.board[r][c] for c in range(len(self.board[r]))] for r in range(len(self.board))]
        copy.representatives = self.representatives.copy()
        copy.database = self.database
        copy.queued_track = []
        copy.mission_cards = [None, None, None]
        return copy

    ###############
    # QUEUE LOGIC #
    ###############
    def append_to_queue(self, path):
        self.queued_track.append(path)

    def save_queued_track(self, log=None, add_to_log=True):
        for path in self.queued_track:
            self.add_track(path)
            if add_to_log and log is not None:
                log.record("path", path)
        self.empty_queued_track()

    def empty_queued_track(self):
        self.queued_track = []

    def queue_from_log(self, log):
        for query in log:
            for action, location in query[1]:
                if action == "path":
                    self.append_to_queue(location)
    
    #################
    # MISSION LOGIC #
    #################
    def save_mission_card(self, mission_1, mission_2, mission_3):
        i = 0
        while i < len(self.mission_cards) and self.mission_cards[i] is not None:
            i += 1
        if i < len(self.mission_cards):
            self.mission_cards[i] = MissionCard(mission_1, mission_2, mission_3)
        else:
            raise Exception("All mission card slots filled.")
    
    def remove_mission_card(self, num):
        if 1 <= num <= 3:
            self.mission_cards[num - 1] = None
            return True
        else:
            return False

    def print_current_mission_cards(self):
        output = ""
        for i in range(len(self.mission_cards)):
            mission_card = self.mission_cards[i]
            if mission_card is not None:
                output += "Mission Card " + str(i + 1) + ": "
                output += str(mission_card)
        return output

    def get_mission_card(self, num):
        if 1 <= num <= 3:
            return self.mission_cards[num - 1]
        else:
            raise ValueError("Index for mission cards out of bounds.")
    
    def has_mission_card(self, num):
        if 1 <= num <= 3:
            return self.mission_cards[num - 1] is not None
        else:
            raise ValueError("Index for mission cards out of bounds.")

    def compute_optimal_track(self, mission_select_1=None, mission_select_2=None, mission_select_3=None, require_major_city=False):
        cities = []
        loads = []
        reward = 0
        if mission_select_1 is not None and self.has_mission_card(1):
            mission_1 = self.get_mission_card(1).get_mission(mission_select_1)
            cities.append(self.database["cities"][mission_1.dest]["coords"])
            loads.append(mission_1.load)
            reward += mission_1.reward
        if mission_select_2 is not None and self.has_mission_card(2):
            mission_2 = self.get_mission_card(2).get_mission(mission_select_2)
            cities.append(self.database["cities"][mission_2.dest]["coords"])
            loads.append(mission_2.load)
            reward += mission_2.reward
        if mission_select_3 is not None and self.has_mission_card(3):
            mission_3 = self.get_mission_card(3).get_mission(mission_select_3)
            cities.append(self.database["cities"][mission_3.dest]["coords"])
            loads.append(mission_3.load)
            reward += mission_3.reward

        all_cities = [[c] for c in cities]
        for l in loads:
            all_cities.append([self.database["cities"][city]["coords"] for city in self.database["loads"][l]])
        if require_major_city:
            if self.count_major_cities() == 0:
                major_cities = [self.database["cities"][mc]["coords"] for mc in MAJOR_CITIES]
                all_cities.append(major_cities)

        all_paths, cost = connect_cities(self.orig_board, self, all_cities, NUMBER_TRIES)
        return all_paths, cost, reward

    def compute_all(self, mission_1, mission_2, mission_3, visual, color, filepath):
        mission_cards = []
        if mission_1:
            if self.has_mission_card(1):
                mission_cards.append(self.get_mission_card(1))
                mission_1_options = [1, 2, 3]
            else:
                raise Exception("Missing mission card 1.")
        else:
            mission_1_options = [0]
        if mission_2:
            if self.has_mission_card(2):
                mission_cards.append(self.get_mission_card(2))
                mission_2_options = [1, 2, 3]
            else:
                raise Exception("Missing mission card 2.")
        else:
            mission_2_options = [0]
        if mission_3:
            if self.has_mission_card(3):
                mission_cards.append(self.get_mission_card(3))
                mission_3_options = [1, 2, 3]
            else:
                raise Exception("Missing mission card 3.")
        else:
            mission_3_options = [0]

        costs = []
        rewards = []

        for choice_1 in mission_1_options:
            for choice_2 in mission_2_options:
                for choice_3 in mission_3_options:
                    name_append = str(choice_1) + str(choice_2) + str(choice_3)
                    p, c, r = self.compute_optimal_track(choice_1, choice_2, choice_3, True) # polymerase chain reaction
                    visual.save(filepath + "missions_" + name_append + ".png", p, color)
                    costs.append(c)
                    rewards.append(r)

        return costs, rewards


def connect_cities(board, my_track, cities, number_tries=1):
    def contained(tracks):
        def __contained(point):
            for t in tracks:
                if point in t:
                    return True
            return False
        return __contained

    tracks = []
    if my_track is not None and my_track.has_track:
        tracks.append(my_track)
    for group in cities:
        t = Track(board)
        for c in group:
            t.add_representative(c[0], c[1])
        tracks.append(t)
    
    opt_paths = None
    opt_cost = None
    actual_number_tries = number_tries if number_tries <= len(tracks) else len(tracks)
    order = sample(range(len(tracks)), actual_number_tries)
    for i in range(actual_number_tries):
        tracks_cp = [t.copy() for t in tracks]
        home = tracks_cp.pop(order[i])
        all_paths = []
        total_cost = 0
        
        while len(tracks_cp) > 0:
            p, c = find_path(home.representatives, board, home, reached_goal=contained(tracks_cp), reverse=True)
            home.add_track(p)
            i = 0
            while i < len(tracks_cp):
                t = tracks_cp[i]
                if p[-1] in t:
                    home.union(t)
                    tracks_cp.pop(i)
                else:
                    i += 1
            home.remove_unconnected(p[0])
            all_paths.append(p)
            total_cost += c
        
        if opt_cost is None or opt_cost > total_cost:
            opt_paths = all_paths
            opt_cost = total_cost

    return opt_paths, opt_cost
            
            
            