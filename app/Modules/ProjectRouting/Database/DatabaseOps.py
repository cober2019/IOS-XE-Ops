import sqlite3


def delete_table_ios_xe(mydb, cursor) -> None:
    """Deletes existing database table Routing_IOS_XE"""

    try:
        cursor.execute('''DROP TABLE Routing_IOS_XE''')
        mydb.commit()
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        pass


def db_table_cleanup(f):
    """Decorator for database table cleanup"""

    def db_check(self, mydb, cursor):

        funtion = None

        if f.__name__ == "create_database_table_ios_xe":
            delete_table_ios_xe(mydb, cursor)
            funtion = f(self, mydb, cursor)

        return funtion

    return db_check


def db_update_ios_xe(mydb, cursor, vrf=None, prefix=None, protocol=None, admin_distance=None, nexthops=None,
                     interfaces=None, metric=None, age=None, tag=None) -> None:

    cursor.execute("INSERT INTO Routing_IOS_XE VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %
                   (vrf, prefix, protocol, admin_distance, metric, nexthops, interfaces, tag, age))
    mydb.commit()


class RoutingDatabase:
    """Class of methods performs database funtions:
                                Creates tables in database
                                Inserts rows into database tables"""

    def __init__(self, mydb, conn):
        self.create_database_table_ios_xe(mydb, conn)

    @db_table_cleanup
    def create_database_table_ios_xe(self, mydb, cursor) -> None:
        """Create routing TABLE in routing database"""

        cursor.execute('''CREATE TABLE Routing_IOS_XE (vrf, prefix, protocol, admin_distance, metric, nexthops, 
        interfaces, tag, age)''')
        mydb.commit()



