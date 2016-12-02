#!/usr/bin/env python

"""Database handler for sqlite3."""

import sqlite3
import json
from prettytable import PrettyTable


class Database():
    """Database Management class for sqlite3."""

    def __init__(self, file="database.db", debug=False):
        """."""
        self.file = file
        self.conn = None
        self.connect()
        self.close()
        self.debug = debug

    def all(self):
        """."""
        data = ""
        tables = self.tables()
        for x in tables:
            tb = PrettyTable([x[1] for x in self.table_schema(x)])
            tb.border = False
            tdata = self.table_data(x, raw=True)
            for xi in tdata:
                tb.add_row(xi)
            data = "{}\n{}:\n{}\n\n".format(data, x, tb)
        return data

    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.file)
        c = self.conn.cursor()
        return c

    def close(self, conn=None):
        """
        Close a connection.

        Paramaters:
            conn (<class 'sqlite3.Cursor'>:optional:default=self.conn)
                                            - the connection to close
        """
        if conn is None:
            conn = self.conn
        try:
            conn.close()
        except Exception as e:
            print(e)

    def commit(self, conn=None):
        """
        Commit a excecution.

        Paramaters:
            conn (<class 'sqlite3.Cursor'>:optional:default=self.conn)
                                            - the connection to commit on
        """
        if conn is None:
            conn = self.conn
        try:
            conn.commit()
        except Exception as e:
            print(e)

    def tables(self):
        """
        Return all database tables.

        returns list.
        """
        c = self.connect()
        c.execute('''SELECT name FROM sqlite_master WHERE type='table';''')
        self.commit()
        tables = c.fetchall()
        self.close()
        try:
            for index, table in enumerate(tables):
                tables[index] = table[0]
        except Exception as e:
            print(e)
        return tables

    def table_exists(self, table):
        """Check if table exsists within the database.

        paramiters:
            table (str:required) - table name to check

        returns bool.
        """
        if table in self.tables():
            return True
        else:
            return False

    def add_table(self, table, table_schema={"": ""}, o=""):
        """
        Add a table to the database.

        Paramaters:
            table (str:required) - table name
            table_schema (json/dict:optional:default={"": ""})
                *must be in the format of {"Col1_name": "Col1_Data_type",
                                           "Col2_name": "Col2_Data_type" ..}
                    for example: {"person_id": "int(3)", "Name": "str(50)"}
                *to add NOT NULL put data_type in an array
                    for example {"person_id": ["int(2)", "NOT NULL"],
                                 "Name": "str(50)"}
                        *NOT NULL must be uppercase
        """
        if self.table_exists(table):
            print("The table \"{}\" already exists."
                  .format(table))
            return False
        try:
            try:
                js = json.loads(str(table_schema))
            except ValueError:
                table_schema = json.dumps(table_schema)
                js = json.loads(str(table_schema))
        except Exception as e:
            print("Error in adding table", e)  # sys.exc_info()[0]
            raise
            return False
        if len(js) is 0:
            print("Error in adding table, Bad Json")  # sys.exc_info()[0]
            raise
            return False
        c = self.connect()
        cols = ""
        for x in js:
            if type(js[x]) is str:
                cols = cols + '{} {},'.format(x, js[x])
            elif type(js[x]) is list:
                coli = ''
                for xi in js[x]:
                    # if xi == "NOT NULL" or xi == "UNIQUE":
                    coli = coli + ' {}'.format(xi)
                    # else:
                    #     coli = coli + ' {}'.format(xi)
                cols = cols + '{} {},'.format(x, coli)
        i = 'CREATE TABLE "{}" ({}) {};'.format(str(table), cols[:-1], o)
        try:
            c.execute(i)
        except Exception as e:
            print(i)
            raise e
        self.commit()
        self.close()
        return True

    def remove_table(self, table):
        """
        Drop a table from the database.

        Paramaters:
            table (str:required) - the table name to drop
        """
        if not self.table_exists(table):
            print("cannot delete table as theres no table named \"{}\"."
                  .format(table))
            return False
        c = self.connect()
        c.execute('DROP TABLE {}'.format(table))
        self.commit()
        self.close()
        return True

    def table_data(self, table, column=None, query=None, selector="=",
                   raw=False, nocase=False):
        """."""
        if not self.table_exists(table):
            print("cannot find table named \"{}\"."
                  .format(table))
            return False
        c = self.connect()
        if column is not None:
            i = 'SELECT * FROM [{}] WHERE {} {} "{}"{};'\
                .format(table, column, selector, query.replace("'", "''"),
                        " COLLATE NOCASE" if nocase else "")
        else:
            i = 'SELECT * FROM [{}];'\
                .format(table)

        try:
            c.execute(i)
        except Exception as e:
            print(i)
            raise e
        self.commit()
        all_rows = c.fetchall()
        self.close()
        data = []
        # print(all_rows)
        if self.debug:
            print(i)
        if raw:
            return all_rows
        for xi in range(len(all_rows)):
            data.append([])
            data[xi] = {}
            for x, y in enumerate(self.table_schema(table)):
                data[xi][y[1]] = all_rows[xi][x]
        return data

    def table_schema(self, table):
        """
        Return a tables schema.

        Paramaters:
            table (str:required) - the table to query.
        """
        c = self.connect()
        c.execute("PRAGMA table_info([{}])".format(table))
        result = c.fetchall()
        self.commit()
        self.close()
        return result

    def add_column(
        self, table, column,
        default=None, default_type="TEXT",
            raise_integ=False):
        """."""
        c = self.connect()
        try:
            i = 'ALTER TABLE {} ADD COLUMN {} {} DEFAULT {};'\
                .format(table, column, default_type, "NULL" if not default else "'{}'".format(default))
            c.execute(i)
            self.commit()
        except sqlite3.IntegrityError as e:
            if raise_integ is True:
                raise e
            elif raise_integ in ["hide", "Hide", "HIDE"]:
                pass
            else:
                print(e)
            return False
        except Exception as e:
            print(i)
            raise e
        if self.debug:
            print(i)
        self.close()
        return True

    def remove_column(self, table, column):
        """."""
        pass

    def insert_row(self, table, data, o="", raise_integ=False):
        """."""
        if not self.table_exists(table):
            print("The table \"{}\" doesn't exists."
                  .format(table))
            return False
        try:
            try:
                js = json.loads(str(data))
            except ValueError:
                data = json.dumps(data)
                js = json.loads(str(data))
        except Exception as e:
            print("Error in adding table", e)  # sys.exc_info()[0]
            raise
            return False
        if len(js) is 0:
            print("Error in adding table, Bad Json")  # sys.exc_info()[0]
            raise
            return False
        cols = ""
        vals = ""
        for x in js:
            cols = cols + '"{}",'.format(x).replace("'", "''")
            vals = vals + '"{}",'.format(js[x]).replace("'", "''")
        c = self.connect()
        try:
            i = 'INSERT INTO \"{}\" ({}) VALUES ({})'\
                .format(table, cols[:-1], vals[:-1])
            c.execute(i)
            self.commit()
        except sqlite3.IntegrityError as e:
            if raise_integ is True:
                raise e
            elif raise_integ in ["hide", "Hide", "HIDE"]:
                pass
            else:
                print(e)
            return False
        except Exception as e:
            print(i)
            raise e
        if self.debug:
            print(i)
        self.close()
        return True

    def delete_row(self, table, selectors={}, selector_type="OR"):
        """."""
        if not self.table_exists(table):
            print("The table \"{}\" doesn't exists."
                  .format(table))
            return False
        try:
            try:
                selec = json.loads(str(selectors))
            except ValueError:
                datas = json.dumps(selectors)
                selec = json.loads(str(datas))
        except Exception as e:
            print("Error in removing row", e)  # sys.exc_info()[0]
            raise
            return False
        selectors = ""
        for x, y in enumerate(selec):
            if x == 0:
                selectors = "WHERE"
            if x > 0:
                selectors = "{} {}".format(selectors, selector_type)
            if type(selec[y]) is not int:
                if selec[y] is None:
                    selec[y] = "Null"
                    selectors = "{} {} is {}".format(selectors, y, selec[y])
                else:
                    selec[y] = "'{}'".format(selec[y])
            if selec[y] is not "Null":
                selectors = "{} {} = {}".format(selectors, y, selec[y])
        c = self.connect()
        try:
            i = 'DELETE FROM {} {};'\
                .format(table, selectors).replace("'", "''")
            c.execute(i)
            self.commit()
        except sqlite3.IntegrityError as e:
            print(e)
            return False
        except Exception as e:
            print(i)
            raise e

        self.close()
        return True

    def change_data(self, table, data, selectors={}, selector_type="OR"):
        """Change data in a table.

        Equivilent to:
            sql:
                UPDATE {TABLE} SET {data:column_name} = {data:value}
                WHERE {selectors:column_name} = {selectors:value};

        Paramatars:
            table (str:required) the table to change
            data (dict:required) the data to change in the format of
                                            {"column_name":"value"}
            selectors (dict:optional:default={} the row selectors in the
                                        format of {"column_name": "value"}
            selector_type (str:optional:default="OR") the selector type when
                                                        chaining selectors.
                    - can be either "OR" or "AND"
        """
        if not self.table_exists(table):
            print("The table \"{}\" doesn't exists."
                  .format(table))
            return False

        try:
            try:
                js = json.loads(str(data))
            except ValueError:
                data = json.dumps(data)
                js = json.loads(str(data))
        except Exception as e:
            print("Error in changing data", e)  # sys.exc_info()[0]
            raise
            return False

        try:
            try:
                selec = json.loads(str(selectors))
            except ValueError:
                datas = json.dumps(selectors)
                selec = json.loads(str(datas))
        except Exception as e:
            print("Error in adding table", e)  # sys.exc_info()[0]
            raise
            return False
        if len(js) is 0:
            print("Error in adding row, Bad Json")  # sys.exc_info()[0]
            raise
            return False
        cols = ""
        for x, y in enumerate(js):
            if x > 0:
                cols = cols + ", "
            if type(js[y]) is not int:
                js[y] = "'{}'".format(js[y].replace("'", "''"))
            cols = "{}{} = {}".format(cols, y.replace("'", "''"), js[y])

        selectors = ""
        for x, y in enumerate(selec):
            if x == 0:
                selectors = "WHERE"
            if x > 0:
                selectors = "{} {}".format(selectors, selector_type)
            if type(selec[y]) is not int:
                if selec[y] is None:
                    selec[y] = "Null"
                    selectors = "{} {} is {}".format(selectors, y, selec[y])
                else:
                    selec[y] = "'{}'".format(selec[y])
            if selec[y] is not "Null":
                selectors = "{} {} = {}".format(selectors, y, selec[y])
        c = self.connect()
        try:
            i = 'UPDATE {} SET {} {};'\
                .format(table, cols, selectors)
            c.execute(i)
            self.commit()
        except sqlite3.IntegrityError as e:
            print(e)
            return False
        except Exception as e:
            print(i)
            raise e
        if self.debug is True:
            print(i)
        self.close()
        return True

    def execute(self, string, *args):
        """
        .

        table = mytable
        Database.ececute("insert into {}", table)
        =insert into mytable
        """
        try:
            c = self.connect()
            i = string.format(arg for arg in args)
            i = c.execute(i)
            i = i.fetchall()
            self.commit()
            self.close()
        except sqlite3.IntegrityError as e:
            print(i)
            print(e)
            return False
        self.close()
        return i
