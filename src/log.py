class Log:
    def __init__(self, database):
        self.query_log = []
        self.current_query = 0
        self.database = database

    def record(self, action, location):
        if len(self.query_log) > 0 and self.query_log[-1][0] == self.current_query:
            self.query_log[-1][1].append([action, location])
        else:
            self.query_log.append([self.current_query, [[action, location]]])    
    
    def step(self):
        self.current_query += 1
    
    def print(self):
        output = ""
        for query in self.query_log:
            output += str(query[0]) + ": "
            for i in range(len(query[1])):
                action, location = query[1][i]
                output += action + " "
                if len(location) >= 1:
                    if location[0] in self.database["points"]:
                        output += self.database["points"][location[0]]
                    else:
                        output += str(location[0])
                if len(location) >= 2:
                    output += " ... "
                    if location[-1] in self.database["points"]:
                        output += self.database["points"][location[-1]]
                    else:
                        output += str(location[-1])
                output += "\n    "
                if i < len(query[1]) - 1:
                    output += "   "
        return output
    
    
    def pop(self, only_last_query=False):
        if len(self.query_log) > 0:
            if only_last_query:
                if self.query_log[-1][0] == self.current_query - 1:
                    self.query_log.pop()
            else:
                self.query_log.pop()
        else:
            raise IndexError("pop from empty log.")
    
    def update_database(self, database):
        self.database = database
    
    def clean(self):
        self.query_log = []
    
    def __iter__(self):
        for query in self.query_log:
            yield query