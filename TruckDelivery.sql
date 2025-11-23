PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS odometer_logs;
DROP TABLE IF EXISTS maintenance_logs;
DROP TABLE IF EXISTS deliveries;
DROP TABLE IF EXISTS drivers;
DROP TABLE IF EXISTS trucks;

CREATE TABLE trucks (
    truck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    license_plate TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE drivers (
    driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone_number TEXT NOT NULL UNIQUE,
    truck_id INTEGER NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (truck_id) REFERENCES trucks(truck_id) 
);

CREATE TABLE deliveries (
    delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id INTEGER NOT NULL,
    pickup_address TEXT NOT NULL,
    dropoff_address TEXT NOT NULL,
    scheduled_pickup DATETIME NOT NULL,
    scheduled_dropoff DATETIME NOT NULL,
    actual_pickup DATETIME,
    actual_dropoff DATETIME,
    status TEXT NOT NULL CHECK(status IN ('Pending', 'In Transit', 'Delivered', 'Cancelled'))
                DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (truck_id) REFERENCES trucks(truck_id) 
);

CREATE TABLE maintenance_logs (
    maintenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id INTEGER NOT NULL,
    service_date DATETIME NOT NULL,
    service_type TEXT NOT NULL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (truck_id) REFERENCES trucks(truck_id) 
);

CREATE TABLE odometer_logs (
    odometer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id INTEGER NOT NULL,
    odometer_reading INTEGER NOT NULL CHECK (odometer_reading >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (truck_id) REFERENCES trucks(truck_id) 
);

INSERT INTO trucks (code, license_plate) VALUES
('Truck-06', 'CZ37FYGP'),
('Truck-12', 'XW42TYGP'),
('Truck-15', 'DJ68LKGP'),
('Truck-09', 'DN42FJGP');

INSERT INTO drivers (first_name, last_name, phone_number, truck_id) VALUES
('Alexander', 'Michael', '079 427 5345', (SELECT truck_id FROM trucks WHERE code = 'Truck-06')),
('Dimitri', 'Ladas', '081 077 3537', (SELECT truck_id FROM trucks WHERE code = 'Truck-12')),
('Leandro', 'Pimentel', '060 526 2335', (SELECT truck_id FROM trucks WHERE code = 'Truck-15')),
('Jarod', 'Labuschagne', '076 333 3914', (SELECT truck_id FROM trucks WHERE code = 'Truck-09'));

INSERT INTO deliveries (truck_id, pickup_address, dropoff_address, scheduled_pickup, scheduled_dropoff, actual_pickup, actual_dropoff, status) VALUES
((SELECT truck_id FROM trucks WHERE code = 'Truck-06'), 'Depot A, Johannesburg', 'Client X, Pretoria', '2025-10-20 08:00:00', '2025-10-20 12:00:00', '2025-10-20 08:15:00', '2025-10-20 11:45:00', 'Delivered'),
((SELECT truck_id FROM trucks WHERE code = 'Truck-12'), 'Depot B, Johannesburg', 'Client Y, Sandton', '2025-10-21 09:00:00', '2025-10-21 13:00:00', NULL, NULL, 'Pending');

INSERT INTO maintenance_logs (truck_id, service_date, service_type, notes) VALUES
((SELECT truck_id FROM trucks WHERE code = 'Truck-06'), '2025-09-15', 'Oil Change', 'Changed oil and filter.'),
((SELECT truck_id FROM trucks WHERE code = 'Truck-12'), '2025-09-20', 'Tire Rotation', 'Rotated all tires.'),
((SELECT truck_id FROM trucks WHERE code = 'Truck-15'), '2025-09-25', 'Brake Inspection', 'Inspected brakes; no issues found.');

INSERT INTO odometer_logs (truck_id, odometer_reading) VALUES
((SELECT truck_id FROM trucks WHERE code = 'Truck-06'), 15000),
((SELECT truck_id FROM trucks WHERE code = 'Truck-12'), 12050),
((SELECT truck_id FROM trucks WHERE code = 'Truck-15'), 9800),
((SELECT truck_id FROM trucks WHERE code = 'Truck-09'), 11025);

