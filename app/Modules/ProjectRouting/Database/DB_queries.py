"""Helper funtions for routing table databse lookups/queries"""

import sqlite3

mydb = sqlite3.connect("Routing")
cursor = mydb.cursor()
cursor_2 = mydb.cursor()
route_tables = []


# Begin DB Table information-----------------------------------------------


def get_tables_names() -> None:
    """Get database table names"""

    try:
        for row in cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\''):
            route_tables.append(row[0])
    except sqlite3.OperationalError:
        pass


def get_db_tables_with_data() -> list:
    """Gets database tables. If table is empty pass"""

    full_dbs = []
    get_tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table in get_tables:
        check_table_rows = cursor_2.execute(F'SELECT count(*) FROM {table[0]}')
        for row in check_table_rows:
            if row[0] == 0:
                pass
            else:
                full_dbs.append(table[0])

    return full_dbs


# End DB Table information-----------------------------------------------

# Begin DB Quiries-------------------------------------------------------


def query_db_ios(vrf, query, index) -> None:
    """Find databse entries with arbitrary routing attributes"""

    vrf_query = cursor.execute('SELECT * FROM Routing_IOS_XE WHERE vrf=?', (vrf,))
    matched_query = 0
    for row in vrf_query:
        if query in row[index] and "," in row[index]:
            print(f"\nVRF: {row[0]}\nPrefix: {row[1]}\nProtocol: {row[2]}\nAdmin-Distance: {row[3]}\n"
                  f"Hop(s): {row[5]}\nOut-Interface(s): {row[6]}\nMetric(s): {row[4]}\nTag: {row[7]}\nAge: {row[8]}")

            matched_query += 1

        elif query == row[index]:
            print(f"\nVRF: {row[0]}\nPrefix: {row[1]}\nProtocol: {row[2]}\nAdmin-Distance: {row[3]}\n"
                  f"Hop(s): {row[5]}\nOut-Interface(s): {row[6]}\nMetric(s): {row[4]}\nTag: {row[7]}\nAge: {row[8]}")

            matched_query += 1

    print(f"\nTotal Routes: {matched_query}")


def query_db_ios_routes(vrf, query, index) -> None:
    """Find routes based off query, can be full route with prefix, no mask, or just octets (192.168.)"""

    vrf_query = cursor.execute('SELECT * FROM Routing_IOS_XE WHERE vrf=?', (vrf,))
    matched_query = 0
    for row in vrf_query:
        if query in row[index]:
            print(f"\nVRF: {row[0]}\nPrefix: {row[1]}\nProtocol: {row[2]}\nAdmin-Distance: {row[3]}\n"
                  f"Hop(s): {row[5]}\nOut-Interface(s): {row[6]}\nMetric(s): {row[4]}\nTag: {row[7]}\nAge: {row[8]}\n")

            matched_query += 1

    print(f"\nTotal Routes: {matched_query}")


def view_routes_ios(cursor) -> None:
    """View all database entries, no filters"""

    query = cursor.execute('SELECT * FROM Routing_IOS_XE')

    return query

# End DB Quiries-------------------------------------------------------

# Begin query Helpers. Prequery attributes----------------------------


def get_routing_interfaces(table) -> dict:
    """Gets routing interfaces from table"""

    interfaces = {}
    get_interfaces = cursor.execute(f'SELECT interfaces FROM {table}')
    for row in get_interfaces:
        if row[0].rfind(", ") != -1:
            split_interfaces = row[0].split(", ")
            for i in split_interfaces:
                interfaces[i[0]] = None
        else:
            interfaces[row] = None

    return interfaces


def get_protocols(table) -> dict:
    """Gets route protocol with types from the the routing table"""

    protocol = {}
    get_protocol = cursor.execute(f'SELECT interfaces FROM {table}')
    for i in get_protocol:
        protocol[i[0][0]] = "None"

    return protocol

# End query Helpers. Prequery attributes----------------------------

# Begin query builders----------------------------------------------


def search_db_ios(vrf=None, prefix=None, protocol=None, metric=None, ad=None, tag=None, interface=None) -> None:
    """Find databse entries by artbitrary attribute using **attributes (kwargs)
                            vrf, admin-distance, metric, prefix, next-hop, tag"""

    if vrf is None or vrf == "":
        vrf = "global"
    else:
        pass

    if protocol is not None:
        query_db_ios(vrf=vrf, query=protocol, index=2)
    if prefix is not None:
        query_db_ios_routes(vrf=vrf, query=prefix, index=1)
    if metric is not None:
        query_db_ios(vrf=vrf, query=metric, index=4)
    if ad is not None:
        query_db_ios(vrf=vrf, query=ad, index=3)
    if tag is not None:
        query_db_ios(vrf=vrf, query=tag, index=7)
    if interface is not None:
        query_db_ios(vrf=vrf, query=interface, index=6)


# End query builders----------------------------------------------
