import psycopg2
from contextlib import contextmanager
from player import Player
# setup

def create_tables(connection):
    with get_cursor(connection) as cursor:
        cursor.execute(CREATE_PLAYERS)
        cursor.execute(CREATE_PROPERTIES)
        cursor.execute(CREATE_NONPROPERTY_SPACES)
        connection.commit()

CREATE_PLAYERS = """
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    money INTEGER NOT NULL,
    position INTEGER NOT NULL,
    turn_order INTEGER NOT NULL
);
"""

CREATE_PROPERTIES = """
CREATE TABLE IF NOT EXISTS properties (
    property_id SERIAL PRIMARY KEY,        -- Unique property ID
    name TEXT NOT NULL,                    -- Property name
    cost INTEGER NOT NULL,                 -- Cost to buy
    base_rent INTEGER NOT NULL,            -- Rent cost without improvements
    owner_id INTEGER REFERENCES players(player_id),  -- Player ID who owns the property
    improvements INTEGER NOT NULL DEFAULT 0 -- Number of improvements (e.g., houses or hotels)
);"""

CREATE_NONPROPERTY_SPACES = """
CREATE TABLE IF NOT EXISTS nonpropertyspaces (
space_id SERIAL PRIMARY KEY,
name TEXT NOT NULL,
description TEXT NOT NULL,
action TEXT NOT NULL
)"""
# Queries for ya
# Insert QS
INSERT_PLAYER = '''INSERT INTO players (name, money, position, turn_order) VALUES (%s, %s, %s, %s) RETURNING player_id;'''
INSERT_PROPERTY = """INSERT INTO properties (name, cost, base_rent, owner_id, improvements) VALUES (%s, %s, %s, NULL, %s) RETURNING property_id;"""
INSERT_NONPROPERTY_SPACE = """INSERT INTO nonpropertyspaces (name, description, action) VALUES (%s, %s, %s) RETURNING space_id;"""
# SELECT QS
SELECT_ALL_PLAYERS = '''SELECT * FROM players;'''
SELECT_ALL_PROPERTIES =  """SELECT property_id, name, cost, base_rent, owner_id, improvements FROM properties;"""
# UPDATE QS
UPDATE_PLAYER = '''UPDATE players SET name=%s, money=%s, position =%s, turn_order=%s WHERE player_id=%s;'''
UPDATE_PROPERTY = """UPDATE properties SET owner_id=%s, improvements=%s WHERE property_id=%s;"""
# DELETE QS
DELETE_PLAYER = '''DELETE FROM players WHERE player_id=%s;'''
# CHECK
CHECK_NONPROPERTY_SPACE = """SELECT space_id FROM nonpropertyspaces WHERE name = %s;"""
CHECK_PROPERTY = """SELECT property_id FROM properties WHERE name = %s;"""
CHECK_PLAYER = """SELECT player_id FROM players WHERE name = %s;"""
# Functions insert
def insert_player(connection, name, money, position, turn_order):
    with get_cursor(connection) as cursor:
        cursor.execute(CHECK_PLAYER, (name, ))
        existing = cursor.fetchone()
        if existing:
            print(f' Player {name} already exists')
            return existing[0]
        cursor.execute(INSERT_PLAYER, (name, money, position,turn_order))
        connection.commit()
        return cursor.fetchone()[0]
def insert_property(connection, name, cost, base_rent, owner_id=None, improvements=0):
    with get_cursor(connection) as cursor:
        cursor.execute(CHECK_PROPERTY, (name, ))
        existing = cursor.fetchone()
        if existing:
            print(f'Property {name} already exists')
            return existing[0]

        cursor.execute(INSERT_PROPERTY, (name, cost, base_rent, improvements))
        connection.commit()
        return cursor.fetchone()[0]
def insert_nonproperty(connection, name, description, action):
    with get_cursor(connection) as cursor:
        cursor.execute(CHECK_NONPROPERTY_SPACE, (name,))
        existing = cursor.fetchone()
        if existing:
            print(f"Non-property space '{name}' already exists in the database. Skipping insertion.")
            return existing[0]  # Return the existing space_id

        # Insert the non-property space if it doesn't exist
        cursor.execute(INSERT_NONPROPERTY_SPACE, (name, description, action))
        connection.commit()
        return cursor.fetchone()[0]  # Return the new space_id
# Collect all
def get_all_players(connection):
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_ALL_PLAYERS)
        rows = cursor.fetchall()
        return [
            {
                "player_id": row[0],
                "name": row[1],
                "money": row[2],
                "turn_order": row[3]

            }
            for row in rows
        ]
def get_all_properties(connection):
    with connection.cursor() as cursor:
        cursor.execute(SELECT_ALL_PROPERTIES)
        rows = cursor.fetchall()
        return [
            {
                "property_id": row[0],
                "name": row[1],
                "cost": row[2],
                "base_rent": row[3],
                "owner_id": row[4],
                "improvements": row[5],
            }
            for row in rows
        ]
# Update
def update_player(connection, player_id, name, money, position, turn_order):
    with get_cursor(connection) as cursor:
        cursor.execute(UPDATE_PLAYER, (name, money, position, turn_order, player_id))
    connection.commit()
def update_property(connection, property_id, owner_id=None, improvements=0):
    with get_cursor(connection) as cursor:
        cursor.execute(UPDATE_PROPERTY, (owner_id, improvements, property_id))
        connection.commit()

# Delete if necessary
def delete_player(connection, id):
    with get_cursor(connection) as cursor:
        cursor.execute(DELETE_PLAYER, id)
        return cursor.lastrowid
def save_player_to_DB(connection, players):
    for turn_order, player in enumerate(players):
        insert_player(connection, player.name, player.money, turn_order)
def load_player_from_DB(connection):
    player_data = get_all_players(connection)
    player = [
        Player(
            name=data["name"],
            money=data["money"],
        )
        for data in player_data
    ]
    return player

def save_player_state_to_DB(connection, player):
    update_player(connection, player.name, player.money, player.turn_order)
@contextmanager
def get_cursor(connection):
    with connection:
        with connection.cursor() as cursor:
            yield cursor