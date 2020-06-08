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

path_to_databases = "./framework/database/databases/"


def format_dict(items: dict, can_be_null: bool) -> str:

    formatted_items = ""
    for item in items:

        if can_be_null:
            formatted_items += item + " " + items[item] + ", "

        else:
            formatted_items += item + " " + items[item] + " NOT NULL, "

    return '(' + formatted_items[0:len(formatted_items) - 2] + ')'


def format_list(items: list, has_quotes: bool, has_parenthesis: bool):

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


def init_database(database_name: str, table_name: str, column_info: dict, can_be_null: bool):

    log.getLogger().debug("STARTING init_database 'Database'")

    create_database(database_name)
    create_table(database_name, table_name, column_info, can_be_null)

    log.getLogger().debug("DONE create_table 'Database'")


def create_database(database_name: str) -> None:
    """
    Creates the sqlite database file

    :param database_name: None
    """

    log.getLogger().debug("STARTING create_database 'Database'")

    connection = sqlite3.connect(database_name)

    connection.commit()
    connection.close()

    log.getLogger().debug("DONE create_table 'Database'")


def create_table(database_name: str, table_name: str, column_info: dict, can_be_null: bool) -> None:
    """
    Create a table in the given database

    :param database_name: name of the database to connect to
    :param table_name: name of the table to create
    :param column_info: dictionary containing the column info key/value = column name/data type (you can also include
        things like primary key)
    :param can_be_null: if the column can contain null values
    """

    log.getLogger().debug("STARTING create_table 'Database'")

    formatted_column_names = format_dict(column_info, can_be_null)
    query = f"CREATE TABLE IF NOT EXISTS {table_name} {formatted_column_names};"

    _execute_query(database_name, query, ResultCount.NONE)

    log.getLogger().debug("DONE create_table 'Database'")


def insert_data(database_name: str, table_name: str, data: dict) -> None:
    """
    Function to insert data into a table.

    :param database_name: name of database to connect to
    :param table_name: table name to insert into
    :param data: data to insert key/value = column name/data value
    """

    log.getLogger().debug("STARTING insert_data 'Database'")

    keys = data.keys()
    values = []
    for key in keys:
        values.append(data[key])

    formatted_keys = format_list(keys, False, True)
    formatted_values = format_list(values, True, True)
    query = f"INSERT INTO {table_name} {formatted_keys} VALUES {formatted_values}"
    _execute_query(database_name, query, ResultCount.NONE)

    log.getLogger().debug("DONE insert_data 'Database'")


def select_data(database_name: str, table_name: str, result_count: ResultCount,
                columns: list = None, order_by: str = None):
    """
    Basic select query.

    :param database_name: name of database to connect to
    :param table_name: table to get data from
    :param columns: columns to retrieve data from (Leave as None to select all columns)
    :param order_by: how to order the rows format is "ORDER BY column_name [ASC|DESC]"
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

    return _execute_query(database_name, query, result_count)


def update_output_state(database_name: str, output_name:str, output_state: bool):

    update = f"UPDATE output_states " \
             f"SET date_time = '{datetime.now().strftime('%m/%d/%Y %H:%M:%S')}', output_state = '{str(output_state)}'" \
             f"WHERE output_name = '{output_name}'"
    return _execute_query(path_to_databases + database_name, update, ResultCount.NONE)


def _execute_query(database_name: str, query: str, result_count: ResultCount) -> list:
    """
    Used to execute sqlite queries.

    :param database_name: name of the database to connect to
    :param query: sqlite query to execute
    :param result_count: the number of results that should be returned by the method
    :return:
    """

    log.getLogger().debug(f"STARTING _execute_query 'Database'")

    result = None
    try:

        # Connect to database
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()

        for try_count in range(0, 2):
            try:

                # Execute the query
                cursor.execute(query)
                break

            except sqlite3.OperationalError:
                log.getLogger().critical("FAILED to _execute_query()")
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

        print(print(ex))
        log.getLogger().critical(f"CRITICAL: Could not execute the query '{query}' on the '{database_name}' database.")

    log.getLogger().debug(f"DONE get_sensor_reading 'Database'")

    return result


def get_sensor_reading(database_name: str, table_name: str, columns: list) -> list:
    """
    Retrieves the most recent value in the database for the target sensor.

    :param database_name: name of database to connect to
    :param table_name: name of table to get sensor value from
    :param columns: the name of sensor to get the value of
    :return: a list with the date and time then the retrieved sensor value
    """

    log.getLogger().debug(f"STARTING get_sensor_reading 'Database'")

    query_result = select_data(database_name, table_name, ResultCount.ONE, columns, "ORDER BY date_time DESC LIMIT 1")

    log.getLogger().debug(f"DONE get_sensor_reading 'Database'")

    return query_result


def purge_old_data(database_name: str, table_name: str, max_age: int) -> None:
    """
    Delete rows that are older than the given number of days.

    :param database_name: name of the database to connect to
    :param table_name: name of table to check for old rows
    :param max_age: max number of days since inserting a row before purging
    :return: None
    """

    log.getLogger().debug(f"STARTING purge_old_data 'Database'")

    oldest_date = datetime.now()
    oldest_date = oldest_date - timedelta(days=max_age)
    oldest_date = oldest_date.strftime("%m/%d/%Y %H:%M:%S")

    update = f"DELETE FROM {table_name} WHERE date_time < '{oldest_date}'"
    _execute_query(path_to_databases + database_name, update, ResultCount.NONE)

    log.getLogger().debug(f"DONE purge_old_data 'Database'")


