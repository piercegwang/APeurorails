import src.utils as utils

db_path = ""

def handle_query(database, query):
    # QUERY = city
    if query in database:
        return database[query]

if __name__ == '__main__':
    database = utils.load_database(db_path)

    i = 1
    while True:
        raw_expression = input(str(i) + ": ")
        if raw_expression == "QUIT":
            break
        else:
            try:
                output = handle_query(database, raw_expression)
                if answer is not None:
                    print("  >", answer)
            except Exception as error:
                print("  err> " + repr(error))