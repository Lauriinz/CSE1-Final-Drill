from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_httpauth import HTTPBasicAuth
import datetime

app = Flask(__name__)

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Update with your MySQL username
app.config['MYSQL_PASSWORD'] = 'root'  # Update with your MySQL password
app.config['MYSQL_DB'] = 'clubmembers'

# Initialize MySQL and Bcrypt
mysql = MySQL(app)
auth = HTTPBasicAuth()

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Club Management API"})

# Person Endpoints
@app.route('/persons', methods=['GET'])
def get_persons():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Person")
    persons = cursor.fetchall()
    cursor.close()
    return jsonify(persons)

@app.route('/persons', methods=['POST'])
def create_person():
    data = request.get_json()
    try:
        # Ensure the required fields are present
        person_name = data['person_name']
        person_address = data.get('person_address', '')
        phone_number = data.get('phone_number', '')
        email_address = data['email_address']

        # Insert into the database
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Person (person_name, person_address, phone_number, email_address) VALUES (%s, %s, %s, %s)",
            (person_name, person_address, phone_number, email_address)
        )
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Person created successfully"}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/persons/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    data = request.get_json()
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Person WHERE person_id = %s", (person_id,))
    person = cursor.fetchone()
    if not person:
        cursor.close()
        return jsonify({"error": "Person not found"}), 404

    try:
        cursor.execute(
            "UPDATE Person SET person_name = %s, person_address = %s, phone_number = %s, email_address = %s WHERE person_id = %s",
            (
                data.get('person_name', person[1]),
                data.get('person_address', person[2]),
                data.get('phone_number', person[3]),
                data.get('email_address', person[4]),
                person_id
            )
        )
        conn.commit()
        cursor.close()
        return jsonify({"message": "Person updated successfully"})
    except Exception as e:
        cursor.close()
        return jsonify({"error": str(e)}), 400

@app.route('/persons/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Person WHERE person_id = %s", (person_id,))
    person = cursor.fetchone()
    if not person:
        cursor.close()
        return jsonify({"error": "Person not found"}), 404

    cursor.execute("DELETE FROM Person WHERE person_id = %s", (person_id,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Person deleted successfully"})

# Club Endpoints (similar to previous implementation)
@app.route('/clubs', methods=['GET'])
def get_clubs():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Club")
    clubs = cursor.fetchall()
    cursor.close()
    return jsonify(clubs)

@app.route('/clubs', methods=['POST'])
def create_club():
    data = request.get_json()
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Club (club_short_name, club_long_name, club_fees, club_description) VALUES (%s, %s, %s, %s)",
            (data['club_short_name'], data.get('club_long_name'), data['club_fees'], data.get('club_description'))
        )
        conn.commit()
        cursor.close()
        return jsonify({"message": "Club created successfully"}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400

@app.route('/clubs/<int:club_id>', methods=['PUT'])
def update_club(club_id):
    data = request.get_json()
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Club WHERE club_id = %s", (club_id,))
    club = cursor.fetchone()
    if not club:
        cursor.close()
        return jsonify({"error": "Club not found"}), 404

    try:
        cursor.execute(
            "UPDATE Club SET club_short_name = %s, club_long_name = %s, club_fees = %s, club_description = %s WHERE club_id = %s",
            (
                data.get('club_short_name', club[1]),
                data.get('club_long_name', club[2]),
                data.get('club_fees', club[3]),
                data.get('club_description', club[4]),
                club_id
            )
        )
        conn.commit()
        cursor.close()
        return jsonify({"message": "Club updated successfully"})
    except Exception as e:
        cursor.close()
        return jsonify({"error": str(e)}), 400

@app.route('/clubs/<int:club_id>', methods=['DELETE'])
def delete_club(club_id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Club WHERE club_id = %s", (club_id,))
    club = cursor.fetchone()
    if not club:
        cursor.close()
        return jsonify({"error": "Club not found"}), 404

    cursor.execute("DELETE FROM Club WHERE club_id = %s", (club_id,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Club deleted successfully"})

#CLUB MEMBER ENDPOINTS
@app.route('/clubmembers', methods=['GET'])
def get_clubmembers():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ClubMember")
    clubmembers = cursor.fetchall()
    cursor.close()
    return jsonify(clubmembers)

@app.route('/clubmembers', methods=['POST'])
def create_clubmember():
    data = request.get_json()
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ClubMember (person_id, club_id, date_joined, date_left, membership_status) VALUES (%s, %s, %s, %s, %s)",
            (data['person_id'], data['club_id'], data['date_joined'], data.get('date_left'), data['membership_status'])
        )
        conn.commit()
        cursor.close()
        return jsonify({"message": "Club member created successfully"}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400

@app.route('/clubmembers/<int:member_id>', methods=['PUT'])
def update_clubmember(member_id):
    data = request.get_json()
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ClubMember WHERE member_id = %s", (member_id,))
    clubmember = cursor.fetchone()
    if not clubmember:
        cursor.close()
        return jsonify({"error": "Club member not found"}), 404

    try:
        cursor.execute(
            "UPDATE ClubMember SET person_id = %s, club_id = %s, date_joined = %s, date_left = %s, membership_status = %s WHERE member_id = %s",
            (
                data.get('person_id', clubmember[1]),
                data.get('club_id', clubmember[2]),
                data.get('date_joined', clubmember[3]),
                data.get('date_left', clubmember[4]),
                data.get('membership_status', clubmember[5]),
                member_id
            )
        )
        conn.commit()
        cursor.close()
        return jsonify({"message": "Club member updated successfully"})
    except Exception as e:
        cursor.close()
        return jsonify({"error": str(e)}), 400

@app.route('/clubmembers/<int:member_id>', methods=['DELETE'])
def delete_clubmember(member_id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ClubMember WHERE member_id = %s", (member_id,))
    clubmember = cursor.fetchone()
    if not clubmember:
        cursor.close()
        return jsonify({"error": "Club member not found"}), 404

    cursor.execute("DELETE FROM ClubMember WHERE member_id = %s", (member_id,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Club member deleted successfully"})

# Facility Endpoints
@app.route('/facilities', methods=['GET'])
def get_facilities():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Facility")
    facilities = cursor.fetchall()
    cursor.close()
    return jsonify(facilities)

@app.route('/facilities', methods=['POST'])
def create_facility():
    data = request.get_json()
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Facility (club_id, facility_name, date_available, date_not_available, facility_cost) VALUES (%s, %s, %s, %s, %s)",
            (data['club_id'], data['facility_name'], data.get('date_available'), data.get('date_not_available'), data['facility_cost'])
        )
        conn.commit()
        cursor.close()
        return jsonify({"message": "Facility created successfully"}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400

@app.route('/facilities/<int:facility_id>', methods=['PUT'])
def update_facility(facility_id):
    data = request.get_json()
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Facility WHERE facility_id = %s", (facility_id,))
    facility = cursor.fetchone()
    if not facility:
        cursor.close()
        return jsonify({"error": "Facility not found"}), 404

    try:
        cursor.execute(
            "UPDATE Facility SET club_id = %s, facility_name = %s, date_available = %s, date_not_available = %s, facility_cost = %s WHERE facility_id = %s",
            (
                data.get('club_id', facility[1]),
                data.get('facility_name', facility[2]),
                data.get('date_available', facility[3]),
                data.get('date_not_available', facility[4]),
                data.get('facility_cost', facility[5]),
                facility_id
            )
        )
        conn.commit()
        cursor.close()
        return jsonify({"message": "Facility updated successfully"})
    except Exception as e:
        cursor.close()
        return jsonify({"error": str(e)}), 400

@app.route('/facilities/<int:facility_id>', methods=['DELETE'])
def delete_facility(facility_id):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Facility WHERE facility_id = %s", (facility_id,))
    facility = cursor.fetchone()
    if not facility:
        cursor.close()
        return jsonify({"error": "Facility not found"}), 404

    cursor.execute("DELETE FROM Facility WHERE facility_id = %s", (facility_id,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Facility deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)
