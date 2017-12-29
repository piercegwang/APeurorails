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
            for action, location in query[1]:
                output += action + " "
                for l in location:
                    if l in self.database["points"]:
                        output += self.database["points"][l]
                    else:
                        output += str(l)
                    output += " "
                output += "\n        "
        return output
    
    
    def pop(self, only_last_query=False):
        if len(self.query_log) > 0:
            if only_last_query:
                if self.query_log[-1][0] == self.current_query - 1:
                    self.query_log.pop()
            else:
                self.query_log.pop()
    
    def update_database(self, database):
        self.database = database
    
    def clean(self):
        self.query_log = []
    
    def __iter__(self):
        for query in self.query_log:
            yield query