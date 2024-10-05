import json

with open("config/config.json") as fh:
    config = json.load(fh)

DBNAME = config["dbName"]
DBURL = config["dbURL"]
DBPASS = config["dbPass"]
DBUSER = config["dbUser"]
