from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('TruckDelivery.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """
    Main dashboard page.
    Similar to lecturer's index(): shows high-level KPIs.
    """
    conn = get_db_connection()

    truck_count = conn.execute("SELECT COUNT(*) FROM trucks").fetchone()[0]
    driver_count = conn.execute("SELECT COUNT(*) FROM drivers").fetchone()[0]
    delivery_count = conn.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0]
    maintenance_count = conn.execute("SELECT COUNT(*) FROM maintenance_logs").fetchone()[0]

    avg_odometer = conn.execute("""
        SELECT AVG(odometer_reading) FROM odometer_logs
    """).fetchone()[0] or 0
    conn.close()

    return render_template(
        'index.html',
        truck_count=truck_count,
        driver_count=driver_count,
        delivery_count=delivery_count,
        maintenance_count=maintenance_count,
        avg_odometer=avg_odometer
    )

@app.route('/drivers')
def view_drivers():
    """
    Drivers page: later we'll show drivers from DB in the table.
    """
    conn = get_db_connection()
    drivers = conn.execute("""
        SELECT d.driver_id,
               d.first_name,
               d.last_name,
               d.phone_number,
               t.code AS truck_code,
               t.license_plate
        FROM drivers d
        JOIN trucks t ON d.truck_id = t.truck_id
        ORDER BY d.first_name
    """).fetchall()
    conn.close()
    return render_template('drivers.html', drivers=drivers)

@app.route('/history')
def view_history():
    return render_template('history.html')

@app.route('/vehicle')
def view_vehicle():
    return render_template('vehicle.html')

@app.route('/trucks', methods=['GET'])
def get_trucks():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM trucks ORDER BY code").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

@app.route('/trucks/<int:truck_id>', methods=['GET'])
def get_truck(truck_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM trucks WHERE truck_id = ?", (truck_id,)).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Truck not found"}), 404

    return jsonify(dict(row)), 200

@app.route('/trucks/add', methods=['POST'])
def add_truck():
    data = request.json
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO trucks (code, license_plate) VALUES (?, ?)",
        (data['code'], data['license_plate'])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Truck added"}), 201

@app.route('/trucks/<int:truck_id>/update', methods=['POST'])
def update_truck(truck_id):
    data = request.json
    conn = get_db_connection()
    conn.execute(
        "UPDATE trucks SET code = ?, license_plate = ? WHERE truck_id = ?",
        (data['code'], data['license_plate'], truck_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Truck updated"}), 200

@app.route('/drivers/add', methods=['POST'])
def add_driver():
    data = request.json
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO drivers (first_name, last_name, phone_number, truck_id)
        VALUES (?, ?, ?, ?)
    """, (data['first_name'], data['last_name'], data['phone_number'], data['truck_id']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Driver added"}), 201

@app.route('/drivers/<int:driver_id>/update', methods=['POST'])
def update_driver(driver_id):
    data = request.json
    conn = get_db_connection()
    conn.execute("""
        UPDATE drivers
        SET first_name = ?, last_name = ?, phone_number = ?, truck_id = ?
        WHERE driver_id = ?
    """, (data['first_name'], data['last_name'], data['phone_number'],
          data['truck_id'], driver_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Driver updated"}), 200

@app.route('/deliveries', methods=['GET'])
def get_deliveries():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT d.delivery_id,
               t.code AS truck_code,
               d.pickup_address,
               d.dropoff_address,
               d.scheduled_pickup,
               d.scheduled_dropoff,
               d.actual_pickup,
               d.actual_dropoff,
               d.status
        FROM deliveries d
        JOIN trucks t ON d.truck_id = t.truck_id
        ORDER BY d.scheduled_pickup DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

@app.route('/deliveries/add', methods=['POST'])
def add_delivery():
    data = request.json
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO deliveries (
            truck_id, pickup_address, dropoff_address,
            scheduled_pickup, scheduled_dropoff, status
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data['truck_id'],
        data['pickup_address'],
        data['dropoff_address'],
        data['scheduled_pickup'],
        data['scheduled_dropoff'],
        data.get('status', 'Pending')
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Delivery added"}), 201

@app.route('/deliveries/<int:delivery_id>/update', methods=['POST'])
def update_delivery(delivery_id):
    data = request.json
    conn = get_db_connection()
    conn.execute("""
        UPDATE deliveries
        SET status = ?
        WHERE delivery_id = ?
    """, (data['status'], delivery_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Delivery updated"}), 200

@app.route('/maintenance/<int:truck_id>', methods=['GET'])
def get_maintenance(truck_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT maintenance_id, truck_id, service_date, service_type, notes
        FROM maintenance_logs
        WHERE truck_id = ?
        ORDER BY service_date DESC
    """, (truck_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

@app.route('/maintenance/add', methods=['POST'])
def add_maintenance():
    data = request.json
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO maintenance_logs (truck_id, service_date, service_type, notes)
        VALUES (?, ?, ?, ?)
    """, (data['truck_id'], data['service_date'], data['service_type'], data.get('notes')))
    conn.commit()
    conn.close()
    return jsonify({"message": "Maintenance record added"}), 201

@app.route('/odometer/<int:truck_id>', methods=['GET'])
def get_odometer(truck_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT odometer_id, truck_id, odometer_reading, created_at
        FROM odometer_logs
        WHERE truck_id = ?
        ORDER BY created_at DESC
    """, (truck_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

@app.route('/odometer/add', methods=['POST'])
def add_odometer():
    data = request.json
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO odometer_logs (truck_id, odometer_reading)
        VALUES (?, ?)
    """, (data['truck_id'], data['odometer_reading']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Odometer reading added"}), 201

if __name__ == '__main__':
    app.run(debug=True)
