"""."""
from .database import Database
from sqlite3 import IntegrityError
from .app import app
import json

database = Database("main.db")

database_models = {
    "Client": {
        "Data": ["TEXT", "NULL", "UNIQUE"],
        "Value": ["TEXT", "NULL"],
    },
    "ServerPrefixes": {
        "ServerId": ["TEXT", "NOT NULL", "UNIQUE"],
        "Prefix": ["TEXT"],
        "InTextWraps": ["TEXT"]
    },
    "BotAdmins": {
        "Id": ["TEXT", "NOT NULL"]
    },
    "Searches": {
        "Card": ["TEXT", "UNIQUE"],
        "Count": ["INTEGER"],
        "Last_used": ["DATETIME"]
    }
}


for table in database_models:
    try:
        x = database.add_table(table, database_models[table])
    except IntegrityError:
        pass
    if x is True:
        print("\tAdding table: {} to db: ".format(table))
database.insert_row(
    "Client", {"data": "Secret", "value": ""}, raise_integ="hide")
database.insert_row(
    "Client", {"data": "Token", "value": ""}, raise_integ="hide")
database.insert_row(
    "Client", {"data": "Client_Id", "value": ""}, raise_integ="hide")
database.insert_row(
    "Client", {"data": "Hs_json_last", "value": "0"}, raise_integ="hide")
database.change_data(
    "Client", {"Value": "0"}, {"Data": "Hs_json_last"})
print("\nDatabase loaded!\n")
