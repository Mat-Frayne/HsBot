"""."""
from threading import Thread
from database import Database
from sqlite3 import (IntegrityError, OperationalError)
from random import (choice)
import string
d = Database("test.db")
database_models = {
    "test": {
        "Index": ["TEXT", "NULL", "UNIQUE"],
        "Value": ["TEXT", "NULL"],
    }
}
for table in database_models:
    try:
        x = d.add_table(table, database_models[table])
    except IntegrityError:
        pass
d.close()
threads = []

global x
x = 0

print(d.table_data("test", "Value", "QZZQWWO6EF"))
# 9342
# def add(x, y):
#     """."""
#     f = None
#     while not f:
#         try:
#             d = Database("test.db")
#             d.insert_row(
#                 "test", {"Index": x, "Value": y}, raise_integ="hide")
#             d.close()
#             print("{} {:>10} : {:<10}".format(
#                   str(len(threads)), str(x), str(80000)))
#             f = 1
#         except OperationalError:
#             pass

# while x < 80000:
#     if len(threads) >= 250:
#         for c in threads:
#             if not c.isAlive():
#                 # print("Killed Thread #" + str(threads.index(c)))
#                 threads.pop(threads.index(c))
#     else:
#         y = ''.join(
#             choice(
#                 string.ascii_uppercase + string.digits) for _ in range(10))
#         th = Thread(target=add, args=(x, y))
#         threads.append(th)
#         th.start()
#         x = x + 1

# print("Done")
