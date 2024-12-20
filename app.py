from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_httpauth import HTTPBasicAuth
import jwt
import datetime
import json
from flask_bcrypt import Bcrypt 
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Update with your MySQL username
app.config['MYSQL_PASSWORD'] = 'root'  # Update with your MySQL password
app.config['MYSQL_DB'] = 'clubmembers'
app.config["SECRET_KEY"] = "beerus12"

# Initialize MySQL and Bcrypt
mysql = MySQL(app)
auth = HTTPBasicAuth()
bcrypt = Bcrypt(app) 

USER_DATA_FILE = "users.json"

def load_users():
    try:
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file)

users = load_users()

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users[username]['password'], password):
        return username

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username not in users or not check_password_hash(users[username]['password'], password):
        return jsonify({"error": "Invalid credentials"}), 401

    if 'token' not in users[username]:
        token = jwt.encode({
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config["SECRET_KEY"], algorithm="HS256")
        users[username]['token'] = token
        save_users(users)
    else:
        token = users[username]['token']

    return jsonify({"token": token})

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user") 

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if username in users:
        return jsonify({"error": "Account already exists"}), 400

    users[username] = {
        "password": generate_password_hash(password),
        "role": role
    }
    save_users(users)

    return jsonify({"message": "Registered successfully"}), 201

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Missing token"}), 401

        try:
            decoded_token = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            request.username = decoded_token["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Expired Token"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return wrapper

def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            username = getattr(request, "username", None)
            user_role = users.get(username, {}).get("role")
            if not user_role or user_role not in required_roles:
                return jsonify({"error": "Access forbidden: insufficient permissions"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Club Management API"})

# Person Endpoints
@app.route('/persons', methods=['GET'])
@token_required
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
@role_required(["admin"])
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
@role_required(["admin"])
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
@role_required(["admin"])
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
@role_required(["admin"])
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
@role_required(["admin"])
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
