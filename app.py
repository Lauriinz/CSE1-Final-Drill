from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///club_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Club(db.Model):
    __tablename__ = 'club'
    club_id = db.Column(db.Integer, primary_key=True)
    club_short_name = db.Column(db.String(50), nullable=False)
    club_long_name = db.Column(db.String(100), nullable=False)
    club_fees = db.Column(db.Float, nullable=False)
    club_description = db.Column(db.Text, nullable=False)

class Member(db.Model):
    __tablename__ = 'member'
    person_id = db.Column(db.Integer, primary_key=True)
    person_name = db.Column(db.String(100), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'), nullable=False)
    date_joined = db.Column(db.Date, default=datetime.utcnow)
    date_left = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=False)

    club = db.relationship('Club', backref=db.backref('members', lazy=True))

# Create the database tables
with app.app_context():
    db.create_all()

# Error Handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request'}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

# CRUD Operations

# Create Club
@app.route('/clubs', methods=['POST'])
def create_club():
    data = request.get_json()

    # Input validation
    if not data.get('club_short_name') or not data.get('club_long_name'):
        abort(400, 'Missing required fields: club_short_name or club_long_name')
    
    new_club = Club(
        club_short_name=data['club_short_name'],
        club_long_name=data['club_long_name'],
        club_fees=data['club_fees'],
        club_description=data['club_description']
    )

    db.session.add(new_club)
    db.session.commit()

    return jsonify({'message': 'Club created successfully', 'club_id': new_club.club_id}), 201

# Get all Clubs
@app.route('/clubs', methods=['GET'])
def get_clubs():
    clubs = Club.query.all()
    result = [{"club_id": club.club_id, "club_short_name": club.club_short_name, "club_long_name": club.club_long_name} for club in clubs]
    return jsonify(result)

# Get a specific Club by ID
@app.route('/clubs/<int:club_id>', methods=['GET'])
def get_club(club_id):
    club = Club.query.get_or_404(club_id)
    return jsonify({
        'club_id': club.club_id,
        'club_short_name': club.club_short_name,
        'club_long_name': club.club_long_name,
        'club_fees': club.club_fees,
        'club_description': club.club_description
    })

# Update Club
@app.route('/clubs/<int:club_id>', methods=['PUT'])
def update_club(club_id):
    club = Club.query.get_or_404(club_id)
    data = request.get_json()

    club.club_short_name = data.get('club_short_name', club.club_short_name)
    club.club_long_name = data.get('club_long_name', club.club_long_name)
    club.club_fees = data.get('club_fees', club.club_fees)
    club.club_description = data.get('club_description', club.club_description)

    db.session.commit()
    return jsonify({'message': 'Club updated successfully'}), 200

# Delete Club
@app.route('/clubs/<int:club_id>', methods=['DELETE'])
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    db.session.delete(club)
    db.session.commit()
    return jsonify({'message': 'Club deleted successfully'}), 200

# Create Member
@app.route('/members', methods=['POST'])
def create_member():
    data = request.get_json()

    if not data.get('person_name') or not data.get('club_id') or not data.get('status'):
        abort(400, 'Missing required fields: person_name, club_id, or status')

    new_member = Member(
        person_name=data['person_name'],
        club_id=data['club_id'],
        status=data['status']
    )

    db.session.add(new_member)
    db.session.commit()

    return jsonify({'message': 'Member created successfully', 'person_id': new_member.person_id}), 201

# Get all Members
@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    result = [{"person_id": member.person_id, "person_name": member.person_name, "status": member.status} for member in members]
    return jsonify(result)

# Get a specific Member by ID
@app.route('/members/<int:person_id>', methods=['GET'])
def get_member(person_id):
    member = Member.query.get_or_404(person_id)
    return jsonify({
        'person_id': member.person_id,
        'person_name': member.person_name,
        'status': member.status,
        'date_joined': member.date_joined,
        'date_left': member.date_left
    })

# Update Member
@app.route('/members/<int:person_id>', methods=['PUT'])
def update_member(person_id):
    member = Member.query.get_or_404(person_id)
    data = request.get_json()

    member.person_name = data.get('person_name', member.person_name)
    member.status = data.get('status', member.status)

    db.session.commit()
    return jsonify({'message': 'Member updated successfully'}), 200

# Delete Member
@app.route('/members/<int:person_id>', methods=['DELETE'])
def delete_member(person_id):
    member = Member.query.get_or_404(person_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
