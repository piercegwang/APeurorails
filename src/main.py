import utils
import sys

DEFAULT_DB_PATH = "../database/eurorails_cities.json"

def handle_query(database, query):
    # QUERY = city
    if query in database["cities"]:
        entry = database["cities"][query]
        output = query + ":\n"
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
        return output

    # QUERY = load
    elif query in database["loads"]:
        entry = database["loads"][query]
        output = ""
        for city in entry:
            output += handle_query(database, city) + "\n    "
        return output
    else:
        raise ValueError("Query could not be processed.")

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
                    print("  >", output)
            except Exception as error:
                print("  > ERROR:", str(error))
        i += 1