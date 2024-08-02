from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '("Enter sql password here")'
app.config['MYSQL_DB'] = 'flight_booking'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

# Create the database if it doesn't exist
def create_database():
    db_connection = MySQLdb.connect(
        host='localhost',
        user='root',
        passwd='("Enter sql password here")'
    )
    cursor = db_connection.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS flight_booking')
    db_connection.commit()
    cursor.close()
    db_connection.close()

# Create tables
def create_tables():
    db_connection = MySQLdb.connect(
        host='localhost',
        user='root',
        passwd='("Enter sql password here")',
        db='flight_booking'
    )
    cursor = db_connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            flight_id INT AUTO_INCREMENT PRIMARY KEY,
            source VARCHAR(100),
            destination VARCHAR(100),
            price DECIMAL(10, 2),
            available_from DATE,
            available_to DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            flight_id INT,
            name VARCHAR(100),
            phone VARCHAR(20),
            email VARCHAR(100),
            card_details VARCHAR(100),
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
        )
    ''')
    db_connection.commit()
    cursor.close()
    db_connection.close()

# Insert flight data into the flights table
def insert_flight_data():
    db_connection = MySQLdb.connect(
        host='localhost',
        user='root',
        passwd='("Enter sql password here")',
        db='flight_booking'
    )
    cursor = db_connection.cursor()

    flights_data = [
        ("BLR", "New York", 90000.00),
        ("BLR", "London", 67500.00),
        ("BLR", "Tokyo", 82500.00),
        ("BLR", "Sydney", 82500.00),
        ("BLR", "Paris", 71250.00),
        ("BLR", "Dubai", 52500.00),
        ("BLR", "Singapore", 48750.00),
        ("BLR", "Hong Kong", 56250.00),
        ("BLR", "Rome", 73500.00),
        ("BLR", "Berlin", 63750.00)
    ]

    for source, destination, price in flights_data:
        try:
            cursor.execute('''
                INSERT INTO flights (source, destination, price, available_from, available_to)
                VALUES (%s, %s, %s, NOW(), NOW() + INTERVAL 30 DAY)
            ''', (source, destination, price))
            db_connection.commit()
        except Exception as e:
            print(f"Error inserting flight: {e}")
            db_connection.rollback()

    cursor.close()
    db_connection.close()







# Existing routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flights', methods=['GET'])
def get_flights():
    db_connection = MySQLdb.connect(
        host='localhost',
        user='root',
        passwd='("Enter sql password here")',
        db='flight_booking'
    )
    cursor = db_connection.cursor()
    try:
        cursor.execute('SELECT * FROM flights')
        flights = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"Error fetching flights: {e}")
        return jsonify(message='Error fetching flights'), 500
    finally:
        db_connection.close()

    return jsonify(flights), 200

@app.route('/book_now')
def book_now_page():
    db_connection = MySQLdb.connect(
        host='localhost',
        user='root',
        passwd='("Enter sql password here")',
        db='flight_booking'
    )
    cursor = db_connection.cursor()
    try:
        cursor.execute('SELECT * FROM flights')
        flights = cursor.fetchall()

        # Convert tuples to dictionaries
        flight_list = []
        for flight in flights:
            flight_dict = {
                'flight_id': flight[0],
                'source': flight[1],
                'destination': flight[2],
                'price': flight[3]
            }
            flight_list.append(flight_dict)
    except Exception as e:
        print(f"Error fetching flights: {e}")
        flight_list = []
    finally:
        cursor.close()
        db_connection.close()

    return render_template('book_now.html', flights=flight_list)

@app.route('/book_flight', methods=['POST'])
def book_flight():
    flight_id = request.form.get('flight_id')
    print(f"Received flight_id: {flight_id}")  # Debug print

    if not flight_id:
        print("No flight ID provided in the form data")
        return redirect(url_for('book_now_page'))

    return redirect(url_for('enter_details', flight_id=flight_id))

@app.route('/enter_details', methods=['GET', 'POST'])
def enter_details():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        card_details = request.form.get('card_details')
        flight_id = request.form.get('flight_id')

        if not flight_id:
            print("Flight ID not provided")
            return redirect(url_for('book_now_page'))

        db_connection = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='("Enter sql password here")',
            db='flight_booking'
        )
        cursor = db_connection.cursor()

        try:
            cursor.execute('INSERT INTO bookings (flight_id, name, phone, email, card_details) VALUES (%s, %s, %s, %s, %s)', 
                           (flight_id, name, phone, email, card_details))
            db_connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Error booking flight: {e}")
            return jsonify(message='Error booking flight'), 500
        finally:
            db_connection.close()

        return redirect(url_for('booking_confirmation', flight_id=flight_id))

    flight_id = request.args.get('flight_id')
    source = request.args.get('source')
    destination = request.args.get('destination')
    price = request.args.get('price')

    if not flight_id:
        print("Flight ID not provided")
        return redirect(url_for('book_now_page'))

    return render_template('enter_details.html', source=source, destination=destination, price=price, flight_id=flight_id)

@app.route('/booking_confirmation')
def booking_confirmation():
    flight_id = request.args.get('flight_id')
    print(f"Received flight_id in booking_confirmation: {flight_id}")  # Debug print

    if flight_id:
        db_connection = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd='("Enter sql password here")',
            db='flight_booking'
        )
        cursor = db_connection.cursor()

        try:
            cursor.execute('SELECT source, destination, price FROM flights WHERE flight_id = %s', (flight_id,))
            flight = cursor.fetchone()
        except Exception as e:
            print(f"Error fetching flight details: {e}")
            flight = None
        finally:
            cursor.close()
            db_connection.close()

        if flight:
            source, destination, price = flight
            return render_template('booking_confirmation.html', source=source, destination=destination, price=price)
        else:
            return "Flight not found", 404
    else:
        return "Flight ID not provided", 400

if __name__ == '__main__':
    create_database()
    create_tables()
    insert_flight_data()  # Add this line to insert flight data
    app.run(debug=True)
