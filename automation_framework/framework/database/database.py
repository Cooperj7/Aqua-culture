"""
Functions to create and manipulate a sqlite database
"""
import time
from enum import Enum
import sqlite3
import logging as log

from datetime import datetime, timedelta


class ResultCount(Enum):

    ONE = "ONE"
    ALL = "ALL"
    NONE = "NONE"


path_to_database = "./framework/database/databases/database.db"
#path_to_database = "../AC_project/db.sqlite3"

def build_db_string(column_names: dict, can_be_null: bool) -> str:
    """
    Create a string to build a sqlite database

    :param column_names:
    :param can_be_null: if the column can be null or not
    :return: a string formatted for sqlite table creation
    """

    formatted_items = ""
    for item in column_names:

        if can_be_null:
            formatted_items += item + " " + column_names[item] + ", "

        else:
            formatted_items += item + " " + column_names[item] + " NOT NULL, "

    return '(' + formatted_items[0:len(formatted_items) - 2] + ')'


def format_list(items: list, has_quotes: bool, has_parenthesis: bool) -> str:
    """
    Converts a list into a formatted string. This is used to insert data into database.

    :param items: items to format
    :param has_quotes: if any of the items contain double quotes
    :param has_parenthesis: if any of the data contains parenthesis
    :return: a formatted string built from the input list
    """
    formatted_items = ""
    for item in items:

        # This means the list being converted is data. If data is a text or string it needs double quotes around it when
        # being entered.
        if isinstance(item, str) and has_quotes:
            formatted_items += f'"{item}", '

        else:
            formatted_items += str(item) + ", "

    # Remove the trailing comma and space
    formatted_items = formatted_items[0:len(formatted_items) - 2]
    if has_parenthesis:
        formatted_items = '(' + formatted_items + ')'

    return formatted_items


def init_database(table_name: str, column_info: dict, can_be_null: bool, path_to_database: str = path_to_database ) -> None:
    """
    Creates the database to store values and other settings

    :param column_info: name and data type for each column
    :param can_be_null: if the column can be null
    :param table_name: name of initial table to create
    :param path_to_database: name of the database to create (if none the default in the .py file will be used)
    """

    log.getLogger().debug("STARTING init_database 'Database'")

    create_database(path_to_database)
    create_table(table_name, column_info, can_be_null, path_to_database)

    log.getLogger().debug("DONE create_table 'Database'")


def create_database(path_to_database: str = path_to_database) -> None:
    """
    Creates the sqlite database file

    :param path_to_database: Name of the database to create
    """

    log.getLogger().debug("STARTING create_database 'Database'")

    connection = sqlite3.connect(path_to_database)

    connection.commit()
    connection.close()

    log.getLogger().debug("DONE create_table 'Database'")


def create_table(table_name: str, column_info: dict, can_be_null: bool, path_to_database: str = path_to_database) -> None:
    """
    Create a table in the given database

    :param table_name: name of the table to create
    :param column_info: dictionary containing the column info key/value = column name/data type (you can also include
        things like primary key)
    :param can_be_null: if the column can contain null values
    :param path_to_database: name of the database to connect to (if none the default in the .py file will be used)
    """

    log.getLogger().debug("STARTING create_table 'Database'")

    formatted_column_names = build_db_string(column_info, can_be_null)
    query = f"CREATE TABLE IF NOT EXISTS {table_name} {formatted_column_names};"

    _execute_query(path_to_database, query, ResultCount.NONE)

    log.getLogger().debug("DONE create_table 'Database'")


def insert_data(table_name: str, data: dict, path_to_database: str = path_to_database) -> None:
    """
    Function to insert data into a table

    :param table_name: table name to insert into
    :param data: data to insert key/value = column name/data value
    :param path_to_database: name of the database to connect to
    """

    log.getLogger().debug("STARTING insert_data 'Database'")

    keys = data.keys()
    values = []
    for key in keys:
        values.append(data[key])

    formatted_keys = format_list(keys, False, True)
    formatted_values = format_list(values, True, True)
    query = f"INSERT INTO {table_name} {formatted_keys} VALUES {formatted_values}"
    _execute_query(path_to_database, query, ResultCount.NONE)

    log.getLogger().debug("DONE insert_data 'Database'")


def select_data(table_name: str, result_count: ResultCount,
                columns: list = None, order_by: str = None, path_to_database: str = path_to_database):
    """
    Basic select query

    :param table_name: table to get data from
    :param result_count: how many results to show from the query
    :param columns: columns to retrieve data from (Leave as None to select all columns)
    :param order_by: how to order the rows format is "ORDER BY column_name [ASC|DESC]"
    :param path_to_database: name of database to connect to
    :return: all the rows in the given columns
    """

    log.getLogger().debug("STARTING select_data 'Database'")

    if columns is None:
        columns = "*"

    else:
        columns = format_list(columns, False, False)

    query = f"SELECT {columns} FROM {table_name}"
    if order_by is not None:
        query += " " + order_by

    log.getLogger().debug("DONE select_data 'Database'")

    return _execute_query(path_to_database, query, result_count)


def update_output_state(output_name:str, output_state: bool, path_to_database: str = path_to_database):
    """
    Update the sate of the output in the database

    :param path_to_database: name of the database to connect to
    :param output_name: name of the output to update (based on the name in the object settings)
    :param output_state: the current state of the output object
    :return: Updates the status of the output object in the database
    """

    update = f"UPDATE output_states " \
             f"SET date_time = '{datetime.now().strftime('%m/%d/%Y %H:%M:%S')}', output_state = '{str(output_state)}'" \
             f"WHERE output_name = '{output_name}'"
    return _execute_query(path_to_database, update, ResultCount.NONE)


def _execute_query(path_to_database: str, query: str, result_count: ResultCount) -> list:
    """
    Used to execute sqlite queries

    :param path_to_database: name of the database to connect to
    :param query: sqlite query to execute
    :param result_count: the number of results that should be returned by the method
    :return: list of results from a query
    """

    log.getLogger().debug(f"STARTING _execute_query 'Database'")

    result = None
    try:

        # Connect to database
        connection = sqlite3.connect(path_to_database)
        cursor = connection.cursor()

        for try_count in range(0, 2):
            try:

                # Execute the query
                cursor.execute(query)
                break

            except sqlite3.OperationalError as ex:
                log.getLogger().critical("FAILED to _execute_query()")
                print(ex)
                time.sleep(.001)

        if result_count == ResultCount.ALL:
            result = cursor.fetchall()

        elif result_count == ResultCount.ONE:
            result = cursor.fetchone()

        elif result_count is ResultCount.NONE or result_count is None:

            # User does not care about return value so return None
            result = None

        else:
            raise ValueError("Result count for queries must be 'ALL', 'ONE' or None")

        # Save the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()

    except Exception as ex:

        print(ex)
        log.getLogger().critical(f"CRITICAL: Could not execute the query '{query}' on the '{path_to_database}' database.")

    log.getLogger().debug(f"DONE get_sensor_reading 'Database'")

    return result


def get_sensor_reading(table_name: str, columns: list, path_to_database: str = path_to_database) -> list:
    """
    Retrieves the most recent value in the database for the target sensor

    :param path_to_database: name of database to connect to
    :param table_name: name of table to get sensor value from
    :param columns: the name of sensor to get the value of
    :return: a list with the date and time then the retrieved sensor value
    """

    log.getLogger().debug(f"STARTING get_sensor_reading 'Database'")

    query_result = select_data(table_name, ResultCount.ONE, columns, "ORDER BY date_time DESC LIMIT 1",
                               path_to_database=path_to_database)

    log.getLogger().debug(f"DONE get_sensor_reading 'Database'")

    return query_result


def purge_old_data(table_name: str, max_age: int, path_to_database: str = path_to_database) -> None:
    """
    Delete rows that are older than the given number of days

    :param path_to_database: name of the database to connect to
    :param table_name: name of table to check for old rows
    :param max_age: max number of days since inserting a row before purging
    :return: None
    """

    log.getLogger().debug(f"STARTING purge_old_data 'Database'")

    oldest_date = datetime.now()
    oldest_date = oldest_date - timedelta(days=max_age)
    oldest_date = oldest_date.strftime("%m/%d/%Y %H:%M:%S")

    update = f"DELETE FROM {table_name} WHERE date_time < '{oldest_date}'"
    _execute_query(path_to_database, update, ResultCount.NONE)

    log.getLogger().debug(f"DONE purge_old_data 'Database'")


def clear_data_in_table(table_name: str, path_to_database: str = path_to_database):

    log.getLogger().debug(f"STARTING clear_data_in_table 'Database'")

    update = f"DELETE FROM {table_name}"
    _execute_query(path_to_database, update, ResultCount.NONE)

    log.getLogger().debug(f"DONE clear_data_in_table 'Database'")