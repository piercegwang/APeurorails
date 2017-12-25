import json

def load_database(filename):
    """
    Loads JSON database of Eurorails.

    :param filename: path to database
    :return: database as a dictionary
    """
    with open(filename, 'r') as f:
        database = json.load(f)
    return database

