# Message Service RESTful API


FastAPI, PostgreSQL (Supabase), SQL Alchemy ORM, Uvicorn ASGI

Service for sending and managing plain-text messages between users.

---

## Setup

- Create a .env file with supplied database URL (This is a connection string to a hosted supabase PostgreSQL server, this can be changed to a local one given you have the connection string for it.)
- Create a python virtual environment with "python -m venv env"
- Activate python virtual environment 
- Run  "pip install -r requirements.txt" ./MessageService_Assignment folder
- (In case of a local server, run "python init_db.py" to intialize the local database)
- Run "uvicorn main:app --reload" in the ./MessageService_Assignment/app folder
- Go to specified URL (probably http://127.0.0.1:8000) and then add /docs to the end to see Swagger API documentation, here you can also find specific curl commands 

## Tasks

1. **Submit a message to a defined recipient, identified with some identifier, e.g. email address, phone number, user name or similar.**  
   - Endpoint: `POST /users/{username}/messages`  
   - Submit a message from a sender to a recipient by their usernames.

2. **Fetch unread messages**  
   - Endpoint: `GET /users/{username}/messages?filterUnread=true&start=0&stop=10`  
   - Returns unread messages for a user, pagination via `start` and `stop` query params, ordered by time. (Here filterUnread query is true)

3. **Delete a single message**  
   - Endpoint: `DELETE /users/{username}/messages/{message_id}`  
   - Deletes a specific message by ID for the given user (recipient).

4. **Delete multiple messages**  
   - Endpoint: `DELETE /users/{username}/messages`  
   - Accepts JSON body with a list of message IDs to delete.

5. **Fetch messages (including read and unread)**  
   - Endpoint: `GET /users/{username}/messages?filterUnread=false&start=0&stop=10`  
   - Returns all messages for a user, pagination via `start` and `stop` query params, ordered by time. (Here filterUnread query is false)

---

## Other Endpoints

5. **Get all users**  
   - `GET /users`  
   - Retrieves a list of all users with their usernames and IDs.

6. **Get all messages**  
   - `GET /messages`  
   - Retrieves all messages across all users with message details.

7. **Delete a user**  
   - `DELETE /users/{username}`  
   - Deletes a user by username (and typically their associated messages).

8. **Mark all messages as read**  
   - `PATCH /users/{username}/messages`  
   - Marks all unread messages for the specified user as read.

9. **Add a new user**  
   - `POST /users`  
   - Creates a new user with provided details (username, email, phone number, address).

---

## Example curl command

**Get a user's unread messages:**
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/users/user2/messages?filterUnread=true&start=0&stop=10' \
  -H 'accept: application/json'