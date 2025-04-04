# Study Group Management API
A Django-based API for managing study groups, user authentication, and personal flashcards.

## API Documentation
After starting the server, visit `http://localhost:8000/swagger/` to view the interactive API documentation, which includes all endpoints, request/response schemas, and the ability to test the API directly.

## Endpoints
Below is a list of available endpoints with example requests and responses.

- **POST /api/users/register/** - Register a new user
  - **Request**: `{"username": "testuser", "email": "test@example.com", "password": "test123"}`
  - **Response (201)**: `{"user": {"id": 1, "username": "testuser", "email": "test@example.com"}, "token": "your-token"}`
  - **Response (400)**: `{"email": ["This field is required."]}`

- **POST /api/users/login/** - Login and get token
  - **Request**: `{"username": "testuser", "password": "test123"}`
  - **Response (200)**: `{"token": "your-token"}`
  - **Response (401)**: `{"error": "Invalid credentials"}`

- **GET /api/users/{id}/** - Get user details
  - **Headers**: `Authorization: Token your-token`
  - **Response (200)**: `{"id": 1, "username": "testuser", "email": "test@example.com"}`
  - **Response (404)**: `{"error": "User not found"}`

- **POST /api/groups/** - Create a study group
  - **Headers**: `Authorization: Token your-token`
  - **Request**: `{"name": "Python Study Group", "description": "Learn Python together"}`
  - **Response (201)**: `{"id": 1, "name": "Python Study Group", "description": "Learn Python together", "creator": {"id": 1, "username": "testuser", "email": "test@example.com"}, "members": [{"id": 1, "username": "testuser", "email": "test@example.com"}]}`
  - **Response (400)**: `{"name": ["This field is required."]}`

- **GET /api/groups/** - List all groups (paginated, 10 per page)
  - **Response (200)**: `{"count": 15, "next": "http://localhost:8000/api/groups/?page=2", "previous": null, "results": [/* list of groups */]}`

- **GET /api/groups/{id}/** - View group details
  - **Response (200)**: `{"id": 1, "name": "Python Study Group", "description": "Learn Python together", "creator": {"id": 1, "username": "testuser", "email": "test@example.com"}, "members": [/* list of members */]}`
  - **Response (404)**: `{"error": "Group not found"}`

- **PUT /api/groups/{id}/** - Update group (creator only)
  - **Headers**: `Authorization: Token your-token`
  - **Request**: `{"name": "Advanced Python Study Group", "description": "For advanced learners"}`
  - **Response (200)**: `{"id": 1, "name": "Advanced Python Study Group", "description": "For advanced learners", "creator": {"id": 1, "username": "testuser", "email": "test@example.com"}, "members": [/* list of members */]}`
  - **Response (403)**: `{"error": "Only the creator can update this group"}`

- **DELETE /api/groups/{id}/** - Delete group (creator only)
  - **Headers**: `Authorization: Token your-token`
  - **Response (204)**: No content
  - **Response (403)**: `{"error": "Only the creator can delete this group"}`

- **POST /api/groups/{id}/join/** - Join a group
  - **Headers**: `Authorization: Token your-token`
  - **Response (200)**: `{"message": "Joined group successfully"}`
  - **Response (404)**: `{"error": "Group not found"}`

- **POST /api/flashcards/** - Create a flashcard
  - **Headers**: `Authorization: Token your-token`
  - **Request**: `{"front": "What is Python?", "back": "A programming language", "category": "Programming"}`
  - **Response (201)**: `{"id": 1, "front": "What is Python?", "back": "A programming language", "category": "Programming", "created_at": "2025-04-04T12:00:00Z"}`
  - **Response (400)**: `{"front": ["This field is required."]}`

- **GET /api/flashcards/** - List user's flashcards (paginated, 10 per page)
  - **Headers**: `Authorization: Token your-token`
  - **Response (200)**: `{"count": 15, "next": "http://localhost:8000/api/flashcards/?page=2", "previous": null, "results": [/* list of flashcards */]}`

- **PUT /api/flashcards/{id}/** - Update a flashcard
  - **Headers**: `Authorization: Token your-token`
  - **Request**: `{"front": "What is Django?", "back": "A Python web framework", "category": "Web Development"}`
  - **Response (200)**: `{"id": 1, "front": "What is Django?", "back": "A Python web framework", "category": "Web Development", "created_at": "2025-04-04T12:00:00Z"}`
  - **Response (404)**: `{"error": "Flashcard not found or not authorized"}`

- **DELETE /api/flashcards/{id}/** - Delete a flashcard
  - **Headers**: `Authorization: Token your-token`
  - **Response (204)**: No content
  - **Response (404)**: `{"error": "Flashcard not found or not authorized"}`

## Setup Locally
1. Clone the repo: `git clone https://github.com/Natcod/study-group-api.git`
2. Activate virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start the server: `python manage.py runserver`