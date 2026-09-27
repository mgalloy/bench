# encoding: utf-8

"""Library routines to handle querying a database..
"""

import configparser
from contextlib import closing
import datetime
import os

import mysql
import mysql.connector


class DatabaseError(Exception):
    """Exception to indicate a problem connecting to the database."""


def get_db_info(config_filename: str, config_section: str, default_section: str) -> tuple:
    """Read a configuration file with the login information for the database.
    The config file should have sections like::

        [mysql]
        host     : server.hao.ucar.edu
        user     : mgalloy
        password : MYPASSWORD
        database : MLSO

    This routine needs the file path for the config file and the section to use.
    """
    cp = configparser.ConfigParser(default_section=default_section)
    cp.read(config_filename)

    host = cp.get(config_section, "host")
    user = cp.get(config_section, "user")
    password = cp.get(config_section, "password")
    database = cp.get(config_section, "database")

    return host, user, password, database


def get_connection(config_filename: str, config_section: str, default_section: str):
    """Make connection to database given the configuration filename and section
    within it with login details for the database. Returns connection.
    """
    if config_filename is None:
        raise DatabaseError("database.config_filename is not defined")

    if not os.path.exists(config_filename):
        raise DatabaseError("database.config_filename not found")

    if config_section is None:
        raise DatabaseError("database.config_section is not defined")

    host, user, password, database = get_db_info(config_filename, config_section, default_section)

    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
    )

    return connection


def query(
    connection: mysql.connector.connection.MySQLConnection,
    sql_cmd: str,
):
    with closing(connection.cursor()) as cursor:
        cursor.execute(sql_cmd)
        results = cursor.fetchall()
        column_names = cursor.column_names
    return results, column_names


def type2str(v):
    if isinstance(v, datetime.datetime):
        return v.strftime("%Y-%m-%dT%H:%M:%S")
    return str(v)


def database_handler(args):
    """Handle join sub-command actions."""
    q = args.query
    db_filename = os.path.expanduser("~/.my.cnf")
    db_sectionname = "bench"
    db_default_sectionname = "client"
    with closing(get_connection(db_filename, db_sectionname, db_default_sectionname)) as connection:
        try:
            results, column_names = query(connection, q)
        except mysql.connector.errors.ProgrammingError as e:
            args.parser.error(e)
        except mysql.connector.errors.IntegrityError as e:
            args.parser.error(e)
        except mysql.connector.errors.DatabaseError as e:
            args.parser.error(e)
    # print("  ".join(column_names))
    for r in results:
        print("  ".join([type2str(i) for i in r]))


def add_arguments(subparsers):
    """Add join sub-command arguments."""
    database_parser = subparsers.add_parser(
        "database",
        aliases=["db"],
        help="query a database",
    )
    database_parser.add_argument(
        "query",
        help="SQL query",
    )
    database_parser.set_defaults(func=database_handler, parser=database_parser)
