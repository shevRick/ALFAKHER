import sqlite3

# List of car models
car_models = [
    ('Toyota', 'Corolla'),
    ('Toyota', 'Camry'),
    ('Toyota', 'RAV4'),
    ('Toyota', 'Highlander'),
    ('Toyota', 'Tacoma'),
    ('Toyota', 'Tundra'),
    ('Toyota', 'Prius'),
    ('Toyota', 'Sienna'),
    ('Honda', 'Civic'),
    ('Honda', 'Accord'),
    ('Honda', 'CR-V'),
    ('Honda', 'Pilot'),
    ('Honda', 'Fit'),
    ('Honda', 'HR-V'),
    ('Honda', 'Odyssey'),
    ('Honda', 'Ridgeline'),
    ('Ford', 'Focus'),
    ('Ford', 'Fusion'),
    ('Ford', 'Mustang'),
    ('Ford', 'Escape'),
    ('Ford', 'Explorer'),
    ('Ford', 'F-150'),
    ('Ford', 'Edge'),
    ('Ford', 'Expedition'),
    ('Chevrolet', 'Malibu'),
    ('Chevrolet', 'Cruze'),
    ('Chevrolet', 'Equinox'),
    ('Chevrolet', 'Tahoe'),
    ('Chevrolet', 'Suburban'),
    ('Chevrolet', 'Silverado'),
    ('Chevrolet', 'Traverse'),
    ('Chevrolet', 'Blazer'),
    ('Nissan', 'Altima'),
    ('Nissan', 'Sentra'),
    ('Nissan', 'Maxima'),
    ('Nissan', 'Rogue'),
    ('Nissan', 'Murano'),
    ('Nissan', 'Pathfinder'),
    ('Nissan', 'Frontier'),
    ('Nissan', 'Titan'),
    ('BMW', '3 Series'),
    ('BMW', '5 Series'),
    ('BMW', '7 Series'),
    ('BMW', 'X3'),
    ('BMW', 'X5'),
    ('BMW', 'X7'),
    ('BMW', 'Z4'),
    ('BMW', 'i3'),
    ('Mercedes-Benz', 'C-Class'),
    ('Mercedes-Benz', 'E-Class'),
    ('Mercedes-Benz', 'S-Class'),
    ('Mercedes-Benz', 'GLA'),
    ('Mercedes-Benz', 'GLC'),
    ('Mercedes-Benz', 'GLE'),
    ('Mercedes-Benz', 'GLS'),
    ('Mercedes-Benz', 'AMG GT'),
    ('Audi', 'A3'),
    ('Audi', 'A4'),
    ('Audi', 'A6'),
    ('Audi', 'Q3'),
    ('Audi', 'Q5'),
    ('Audi', 'Q7'),
    ('Audi', 'Q8'),
    ('Audi', 'R8'),
    ('Volkswagen', 'Golf'),
    ('Volkswagen', 'Passat'),
    ('Volkswagen', 'Jetta'),
    ('Volkswagen', 'Tiguan'),
    ('Volkswagen', 'Atlas'),
    ('Volkswagen', 'Touareg'),
    ('Volkswagen', 'Beetle'),
    ('Volkswagen', 'Arteon'),
    ('Hyundai', 'Elantra'),
    ('Hyundai', 'Sonata'),
    ('Hyundai', 'Tucson'),
    ('Hyundai', 'Santa Fe'),
    ('Hyundai', 'Palisade'),
    ('Hyundai', 'Kona'),
    ('Hyundai', 'Venue'),
    ('Hyundai', 'Ioniq'),
    ('Kia', 'Optima'),
    ('Kia', 'Forte'),
    ('Kia', 'Sportage'),
    ('Kia', 'Sorento'),
    ('Kia', 'Telluride'),
    ('Kia', 'Soul'),
    ('Kia', 'Stinger'),
    ('Kia', 'Seltos'),
    ('Subaru', 'Impreza'),
    ('Subaru', 'Legacy'),
    ('Subaru', 'Outback'),
    ('Subaru', 'Forester'),
    ('Subaru', 'Crosstrek'),
    ('Subaru', 'Ascent'),
    ('Subaru', 'WRX'),
    ('Subaru', 'BRZ'),
    ('Tesla', 'Model S'),
    ('Tesla', 'Model 3'),
    ('Tesla', 'Model X'),
    ('Tesla', 'Model Y'),
    ('Tesla', 'Roadster'),
    ('Tesla', 'Cybertruck')
]

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('car_park_management.db')
c = conn.cursor()

# Create table
c.execute('''
CREATE TABLE IF NOT EXISTS car_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    model TEXT NOT NULL
)
''')

# Insert car models into the table
c.executemany('INSERT INTO car_models (brand, model) VALUES (?, ?)', car_models)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Car models table created and populated successfully.")
