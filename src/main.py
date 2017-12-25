import utils
import sys

DEFAULT_DB_PATH = "../database/eurorails_cities.json"

def handle_query(database, query):
    # QUERY = city
    if query in database["cities"]:
        return database[query]

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        db_path = sys.argv[1]
    else:
        db_path = DEFAULT_DB_PATH

    database = utils.load_database(db_path)

    i = 1
    while True:
        raw_expression = input(str(i) + ": ")
        if raw_expression == "exit":
            break
        else:
            try:
                output = handle_query(database, raw_expression)
                if output is not None:
                    print("  > ", output)
            except Exception as error:
                print("  > ERROR: " + repr(error))
        i += 1