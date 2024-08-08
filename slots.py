

import sqlite3

# Connect to your database
conn = sqlite3.connect('car_park_management.db')

# Create a cursor object
cur = conn.cursor()

# Create table
cur.execute('''
CREATE TABLE IF NOT EXISTS ParkingSlots (
    slot_number INTEGER PRIMARY KEY,
    status TEXT DEFAULT 'available' -- 'available' or 'occupied'
)
''')

# Insert statements
insert_statements = [
    "INSERT INTO ParkingSlots (slot_number, status) VALUES (1, 'available')",
    "INSERT INTO ParkingSlots (slot_number, status) VALUES (2, 'available')",
    "INSERT INTO ParkingSlots (slot_number, status) VALUES (3, 'occupied')",
    "INSERT INTO ParkingSlots (slot_number, status) VALUES (4, 'available')",
    "INSERT INTO ParkingSlots (slot_number, status) VALUES (5, 'occupied')",
    "INSERT INTO ParkingSlots (slot_number, status) VALUES (6, 'available')",
    "INSERT INTO ParkingSlots (slot_number, status) VALUES (7, 'available')",
    "INSERT INTO ParkingSlots (slot_number, status) VALUES (8, 'occupied')",
    "INSERT INTO ParkingSlots (slot_number, status) VALUES (9, 'available')",
    "INSERT INTO ParkingSlots (slot_number, status) VALUES (10, 'available')"
]

# Execute each insert statement
for statement in insert_statements:
    cur.execute(statement)

# Commit the changes
conn.commit()

# Close the connection
conn.close()
