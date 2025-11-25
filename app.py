from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your-secret-key-here'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('TruckDelivery.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    conn = get_db_connection()

    truck_count = conn.execute("SELECT COUNT(*) FROM trucks").fetchone()[0]

    driver_count = conn.execute("SELECT COUNT(*) FROM drivers").fetchone()[0]

    delivery_count = conn.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0]

    delivered = conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='Delivered'").fetchone()[0]

    pending = conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='Pending'").fetchone()[0]

    in_transit = conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='In Transit'").fetchone()[0]

    on_time = conn.execute("""
        SELECT COUNT(*) FROM deliveries 
        WHERE status='Delivered' AND actual_dropoff <= scheduled_dropoff
    """).fetchone()[0]
    on_time_percent = round((on_time / delivered * 100), 1) if delivered > 0 else 0

    avg_odometer = conn.execute("SELECT AVG(odometer_reading) FROM odometer_logs").fetchone()[0] or 0
    avg_odometer = round(avg_odometer, 0)
    
    maintenance_count = conn.execute("SELECT COUNT(*) FROM maintenance_logs").fetchone()[0]

    utilization = round((delivery_count / truck_count), 1) if truck_count > 0 else 0

    delay_result = conn.execute("""
        SELECT AVG((julianday(actual_dropoff) - julianday(scheduled_dropoff)) * 24) 
        FROM deliveries 
        WHERE status='Delivered' AND actual_dropoff > scheduled_dropoff
    """).fetchone()[0]
    avg_delay = round(delay_result, 1) if delay_result else 0

    conn.close()

    return render_template('home.html',
                         truck_count=truck_count,
                         driver_count=driver_count,
                         delivery_count=delivery_count,
                         delivered=delivered,
                         pending=pending,
                         in_transit=in_transit,
                         on_time_percent=on_time_percent,
                         avg_odometer=avg_odometer,
                         maintenance_count=maintenance_count,
                         utilization=utilization,
                         avg_delay=avg_delay,
                         avg_idle='0',
                         customer_queries='Customer feedback pending review.',
                         satisfaction_score='4.2/5.0')

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
    conn = get_db_connection()
    
    total_deliveries = conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='Delivered'").fetchone()[0]
    
    total_maintenance = conn.execute("SELECT COUNT(*) FROM maintenance_logs").fetchone()[0]
    
    truck_count = conn.execute("SELECT COUNT(*) FROM trucks").fetchone()[0]
    
    utilization = round((total_deliveries / truck_count * 100), 0) if truck_count > 0 else 0
    
    on_time = conn.execute("""
        SELECT COUNT(*) FROM deliveries 
        WHERE status='Delivered' AND actual_dropoff <= scheduled_dropoff
    """).fetchone()[0]
    on_time_percent = round((on_time / total_deliveries * 100), 1) if total_deliveries > 0 else 0

    rejected_orders = conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='Cancelled'").fetchone()[0]

    conn.close()

    return render_template('history.html',
                         total_deliveries=total_deliveries,
                         total_maintenance=total_maintenance,
                         utilization=utilization,
                         on_time_percent=on_time_percent,
                         rejected_orders=rejected_orders,
                         avg_delay=0.5,
                         avg_idle=1.5,
                         order_accuracy=98.5,
                         avg_returns=0.2,
                         customer_queries='Package delivery times, route optimization requests, vehicle condition inquiries',
                         satisfaction_score='4.7/5.0')

@app.route('/vehicle')
def view_vehicle():
    conn = get_db_connection()
    trucks = conn.execute("SELECT * FROM trucks ORDER BY code").fetchall()

    if trucks:
        first_truck_id = trucks[0]['truck_id']
        
        odometer = conn.execute("""
            SELECT odometer_reading FROM odometer_logs 
            WHERE truck_id = ? 
            ORDER BY created_at DESC LIMIT 1
        """, (first_truck_id,)).fetchone()

        mileage = odometer[0] if odometer else 0

        maintenance = conn.execute("""
            SELECT COUNT(*) FROM maintenance_logs WHERE truck_id = ?
        """, (first_truck_id,)).fetchone()[0]

        deliveries = conn.execute("""
            SELECT COUNT(*) FROM deliveries WHERE truck_id = ? AND status='Delivered'
        """, (first_truck_id,)).fetchone()[0]

        utilization = 95
        
        last_service = conn.execute("""
            SELECT service_date FROM maintenance_logs 
            WHERE truck_id = ? 
            ORDER BY service_date DESC LIMIT 1
        """, (first_truck_id,)).fetchone()
        
        next_service_date = 'N/A'
        if last_service:
            from datetime import datetime, timedelta
            last_date = datetime.fromisoformat(last_service[0])
            next_date = last_date + timedelta(days=90)
            next_service_date = next_date.strftime('%Y-%m-%d')

        pending_delivery = conn.execute("""
            SELECT scheduled_dropoff FROM deliveries 
            WHERE truck_id = ? AND status='Pending' 
            ORDER BY scheduled_dropoff LIMIT 1
        """, (first_truck_id,)).fetchone()
        expected_delivery_time = '1'

        if pending_delivery:
            from datetime import datetime
            dropoff_time = datetime.fromisoformat(pending_delivery[0])
            hours_until = (dropoff_time - datetime.now()).total_seconds() / 3600
            if hours_until > 0:
                expected_delivery_time = f"{hours_until:.1f} hours"
    else:
        mileage = 0
        maintenance = 0
        deliveries = 0
        utilization = 0
        next_service_date = 'N/A'
        expected_delivery_time = '1 hour'

    conn.close()

    return render_template('vehicle.html',
                         trucks=trucks,
                         mileage=mileage,
                         maintenance_count=maintenance,
                         delivery_count=deliveries,
                         utilization=utilization,
                         next_service_date=next_service_date,
                         expected_delivery_time=expected_delivery_time)

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
