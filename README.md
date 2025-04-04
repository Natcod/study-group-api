# Study Group Management API
A Django-based API for managing study groups, user authentication, and personal flashcards.

## Endpoints
- POST /api/users/register/ - Register a new user
- POST /api/users/login/ - Login and get token
- GET /api/users/{id}/ - Get user details
- POST /api/groups/ - Create a study group
- GET /api/groups/ - List all groups
- GET /api/groups/{id}/ - View group details
- PUT /api/groups/{id}/ - Update group (creator only)
- DELETE /api/groups/{id}/ - Delete group (creator only)
- POST /api/groups/{id}/join/ - Join a group
- POST /api/flashcards/ - Create a flashcard
- GET /api/flashcards/ - List user's flashcards
- PUT /api/flashcards/{id}/ - Update a flashcard
- DELETE /api/flashcards/{id}/ - Delete a flashcard

## Setup Locally
1. Clone the repo: `git clone https://github.com/Natcod/study-group-api.git`
2. Activate virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start the server: `python manage.py runserver`