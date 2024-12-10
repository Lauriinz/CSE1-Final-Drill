# Club Management Database API

## Description
A Flask-based REST API for managing clubs, members, events, and payments in a club management database.

## Installation
```bash
pip install -r requirements.txt
```

## Configuration
To configure the database:
1. Use the SQLite database provided or update the app to connect to your preferred database (e.g., MySQL, PostgreSQL).
2. Update the SQLALCHEMY_DATABASE_URI in the Flask app to match your database configuration.

Environment variables needed:
- ```DB_HOST```: The host for the database (e.g., localhost or IP address of the database server)
- ```DB_USER```: Database username (e.g., root)
- ```DB_PASSWORDRD```: Database password
- ```DB_NAME```: Name of the database (e.g., club_management)

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /	| GET	| Welcome message |
| /clubs	| GET	| List all clubs |
| /clubs	| POST	| Add a new club |
| /clubs/<club_id>	| GET	| Get details of a specific club |
| /clubs/<club_id>	| PUT	| Update a club's details |
| /clubs/<club_id>	| DELETE	| Delete a club |
| /members	| GET	| List all members |
| /members	| POST	| Add a new member |
| /members/<person_id>	| GET	| Get details of a specific member |
| /members/<person_id>	| PUT	| Update a member's details |
| /members/<person_id>	| DELETE	| Delete a member |
| /events	| GET	| List all events |
| /events	| POST	| Add a new event |
| /events/<event_id>	| GET	| Get details of a specific event |
| /events/<event_id>	| PUT	| Update an event's details |
| /events/<event_id>	| DELETE	| Delete an event |
| /payments	| GET	| List all payments |
| /payments	| POST	| Add a new payment |
| /payments/<payment_id>	| GET	| Get details of a specific payment |
| /payments/<payment_id>	| PUT	| Update a payment's details |
| /payments/<payment_id>	| DELETE	| Delete a payment |

## Testing
To test the API:
1. Ensure you have ```pytest``` and ```pytest-mock``` installed. You can install them with:
```bash
pip install pytest pytest-mock
```
2. Run the tests by executing the following command:
```bash
pytest api_test.py
```

## Git Commit Guidelines
Use conventional commits:
```bash
feat: add CRUD endpoints for events
fix: resolve member deletion issue
docs: update database configuration details
test: add tests for club creation and retrieval
```
