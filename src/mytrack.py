from board import *

class Mission: # takes a the attributes of one mission and puts it in an object
    def __init__(self, load, dest_city, reward):
        self.load = load
        self.dest = dest_city
        self.reward = reward

class MissionCard: # takes a list of lists describing up to 3 mission cards
    def __init__(self, mission_1, mission_2=None, mission_3=None):
        self.missions = []
        self.missions.append(Mission(mission_1[0], mission_1[1], mission_1[2]))
        if mission_2 is not None:
            self.missions.append(Mission(mission_2[0], mission_2[1], mission_2[2]))
        if mission_3 is not None:
            self.missions.append(Mission(mission_3[0], mission_3[1], mission_3[2]))

class MyTrack:
    def __init__(self, board, database):
        self.min_x = board.min_x
        self.max_x = board.max_x
        self.min_y = board.min_y
        self.max_y = board.max_y
        self.board = [[0 for _ in range(2 * (abs(self.min_x) + abs(self.max_x) + 1))] for _ in
                      range(2 * (abs(self.min_y) + abs(self.max_y) + 1))]
        self.databse = database
        self.queued_track = []
        self.has_track = False
        self.mission_cards = [None, None, None]

    def add_track(self, sequence):
        def claim_point(self, x, y):
            x_index = 2 * (x - self.min_x)
            y_index = 2 * (self.max_y - y)
            if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
                self.board[y_index][x_index] = 1
            self.has_track = True

        def claim_track(self, x, y, dx, dy):
            x_index = 2 * (x - self.min_x) + dx
            y_index = 2 * (self.max_y - y) - dy
            if 0 <= x_index < len(self.board[0]) and 0 <= y_index < len(self.board):
                self.board[y_index][x_index] = 1
                
        for i in range(len(sequence)):
            x, y = sequence[i]
            claim_point(self, x, y)
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
        self.empty_queued_track()
        self.has_track = False
    
    def __iter__(self):
        for x in range(self.min_x, self.max_x + 1):
            for y in range(self.min_y, self.max_y + 1):
                for dx, dy in ((1, 0), (0, -1), (1, -1)):
                    if (x, y, dx, dy) in self:
                        yield [(x, y), (x + dx, y + dy)]

    def update_database(self, database):
        self.database = database

    ###############
    # QUEUE LOGIC #
    ###############
    def append_to_queue(self, path):
        self.queued_track.append(path)

    def save_queued_track(self, log, relog=True):
        for path in self.queued_track:
            self.add_track(path)
            if relog:
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
    def add_mission_card(self, mission_1, mission_2, mission_3):
        i = 0
        while self.mission_cards[i] is None and i < len(self.mission_cards):
            i += 1
        if i < len(self.mission_cards):
            self.mission_cards[i] = MissionCard(mission_1, mission_2, mission_3)
        else:
            raise Exception("All mission card slots filled.")
    
    def remove_mission_card(self, num):
        if 1 <= num <= 3:
            self.mission_cards[num - 1] = None

    def mission_costs(self):
        raise NotImplementedError("mission_costs not implemented yet.")
        # m1Possible = []
        # m2Possible = []
        # m3Possible = []
        # for i in range(0,3)
        #     load = database["loads"][self.mission_cards[i].load]
        #     entry = database["loads"][tokenized[0]]
        #     for city in entry:
        #         visual.mark_city(database["cities"][city]["coords"], color)
        #         output += print_city(database, city)
        # i=0
        # while self.mission_cards[i] is not None and i < len(self.mission_cards):
        #     
        #     path, cost = find_path(self.mission_cards[i], self.board, lambda p: p == end_city_loc)
        #     i += 1