import sqlite3
import json


def add_ship(ship_data):
    with sqlite3.connect("./shipping.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            INSERT INTO Ship VALUES (null, ?, ?)
            """,
            (ship_data["name"], ship_data["hauler_id"]),
        )

    return True if db_cursor.rowcount > 0 else False


def update_ship(id, ship_data):
    with sqlite3.connect("./shipping.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            UPDATE Ship
                SET
                    name = ?,
                    hauler_id = ?
            WHERE id = ?
            """,
            (ship_data["name"], ship_data["hauler_id"], id),
        )

        rows_affected = db_cursor.rowcount

    return True if rows_affected > 0 else False


def delete_ship(pk):
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute(
            """
        DELETE FROM Ship WHERE id = ?
        """,
            (pk,),
        )
        number_of_rows_deleted = db_cursor.rowcount

    return True if number_of_rows_deleted > 0 else False


def list_ships(url):
    # Initialize query
    select_string = """
        SELECT
            s.id,
            s.name,
            s.hauler_id"""
    from_string = """
        FROM Ship s
        """
    # Check if "_expand" is used
    if "_expand" in url["query_params"]:
        for value in url["query_params"]["_expand"]:
            if value == "hauler":
                select_string += """,
                    h.id haulerId,
                    h.name haulerName,
                    h.dock_id"""
                from_string += """
                    JOIN Hauler h
                        ON h.id = s.hauler_id
                        """

    query_string = select_string + from_string

    # Open a connection to the database
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute(query_string)
        query_results = db_cursor.fetchall()

        # Initialize an empty list and then add each dictionary to it
        ships = []
        if "_expand" in url["query_params"]:
            for value in url["query_params"]["_expand"]:
                if value == "hauler":
                    for row in query_results:
                        hauler = {
                            "id": row["haulerId"],
                            "name": row["haulerName"],
                            "dock_id": row["dock_id"],
                        }
                        ship = {
                            "id": row["id"],
                            "name": row["name"],
                            "hauler_id": row["hauler_id"],
                            "hauler": hauler,
                        }
                        ships.append(ship)
        else:
            for row in query_results:
                ships.append(dict(row))

        # Serialize Python list to JSON encoded string
        serialized_ships = json.dumps(ships)

    return serialized_ships


def retrieve_ship(pk):
    # Open a connection to the database
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute(
            """
        SELECT
            s.id,
            s.name,
            s.hauler_id
        FROM Ship s
        WHERE s.id = ?
        """,
            (pk,),
        )
        query_results = db_cursor.fetchone()

        # Serialize Python list to JSON encoded string
        dictionary_version_of_object = dict(query_results)
        serialized_ship = json.dumps(dictionary_version_of_object)

    return serialized_ship
