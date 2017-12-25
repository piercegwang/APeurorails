import json

def load_database(filename):
    """
    Loads JSON database of Eurorails.

    :param filename:
    :return:
    """
    database = json.loads(filename)
    return database

