
# Club Management API

This is a RESTful API built with Flask for managing club members, clubs, and users. It includes features for user authentication, managing clubs and people, and handling club memberships.

## Features
- User registration and login
- CRUD operations for persons and clubs
- Membership management for clubs
- Token-based authentication using JWT

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/club-management-api.git
    ```

2. Navigate to the project folder:

    ```bash
    cd club-management-api
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up MySQL and create a database named `clubmembers`.

5. Update the MySQL credentials and secret key in the code.

## API Endpoints

### Authentication
- **POST** `/login` - Login and get a JWT token.
- **POST** `/register` - Register a new user.

### Persons
- **GET** `/persons` - Get a list of all persons.
- **POST** `/persons` - Create a new person.
- **PUT** `/persons/<person_id>` - Update a person's info.
- **DELETE** `/persons/<person_id>` - Delete a person.

### Clubs
- **GET** `/clubs` - Get a list of all clubs.
- **POST** `/clubs` - Create a new club.
- **PUT** `/clubs/<club_id>` - Update a club's info.
- **DELETE** `/clubs/<club_id>` - Delete a club.

### Club Members
- **POST** `/clubmembers` - Add a person to a club.
- **GET** `/clubmembers` - List all club members.

## Running the Application

Run the application with:

```bash
python app.py
```

By default, the app will be available at `http://127.0.0.1:5000`.
