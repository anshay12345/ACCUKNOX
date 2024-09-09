# Django Social Network API

This project is a social network API built with Django and Django Rest Framework. It includes features such as user authentication, friend requests, and user search functionality. The project uses SQLite as the database.

## Features

- User authentication (signup, login)
- Send, accept, and reject friend requests
- List friends
- List pending friend requests
- Search users by email and name

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```
### 2. Create a Virtual Environment
Create a virtual environment to isolate the project dependencies.
```bash
python -m venv venv
```
Activate the virtual environment:
- On Windows:
  
```bash
  venv\Scripts\activate
  ```
- On macOS and Linux:
  
```bash
  source venv/bin/activate
  ```
### 3. Install Dependencies
Install the project dependencies from the requirements.txt file.
```bash
pip install -r requirements.txt
```
### 4. Apply Migrations
Run the database migrations to set up the SQLite database.
```bash
python manage.py migrate
```
### 5. Start the Development Server
Start the Django development server.
```bash
python manage.py runserver
```
## API Endpoints
### User Authentication
- **Signup**: POST /api/users/signup/
  - Request Body: {"email": "user@example.com", "name": "Anshay Rastogi", "password": "password123"}
- **Login**: POST /api/login/
  - Request Body: {"email": "user@example.com", "password": "password123"}
### Friend Requests
- **Send Friend Request**: POST /api/users/friend-request/send/
  - Request Body: {"to_user_id": 2}
- **Accept Friend Request**: POST /api/users/friend-request/accept/
  - Request Body: {"from_user_email": "user2@example.com"}
- **Reject Friend Request**: POST /api/users/friend-request/reject/
  - Request Body: {"from_user_email": "user2@example.com"}
### User Management
- **List Friends**: GET /api/users/friends/
- **List Pending Friend Requests**: GET /api/users/friend-requests/pending/
- **Search Users**: GET /api/users/search/?q=Ansh
## Postman Collection file
### Read the collection file for details
