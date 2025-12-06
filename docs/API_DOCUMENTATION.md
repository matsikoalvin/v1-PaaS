# Bukoto GuestHouse - REST API Documentation

## Overview
The REST API provides authentication and user management endpoints for the Bukoto GuestHouse property management system. All data is stored in Firebase Realtime Database.

## Base URL
```
http://localhost:5000
```

## Authentication
User tokens are stored in localStorage after successful login:
```javascript
localStorage.getItem('userToken')
```

## Endpoints

### 1. Sign Up
**Endpoint:** `POST /signup`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "username": "john_doe"
}
```

**Request Headers:**
```
Content-Type: application/json
```

**Response (201 Created):**
```json
{
  "message": "Sign up successful",
  "uid": "user_id_123",
  "email": "user@example.com",
  "username": "john_doe"
}
```

**Response (409 Conflict):**
```json
{
  "error": "Email already registered"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Password must be at least 6 characters"
}
```

**Validation Rules:**
- Email: Must be valid email format
- Password: Minimum 6 characters
- Username: Minimum 3 characters
- Email must be unique
- Username must be unique

**Error Responses:**
- `400`: Missing required fields or validation failed
- `409`: Email or username already exists
- `500`: Server error

---

### 2. Login
**Endpoint:** `POST /login`

Authenticate user with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Request Headers:**
```
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "uid": "user_id_123",
  "email": "user@example.com",
  "username": "john_doe",
  "role": "user",
  "token": "firebase_custom_token"
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Invalid email or password"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Email and password are required"
}
```

**Error Responses:**
- `400`: Missing email or password
- `401`: Invalid credentials
- `500`: Server error

---

### 3. Get User Info
**Endpoint:** `GET /user/<uid>`

Retrieve user information by user ID.

**URL Parameters:**
- `uid` (string, required): User ID

**Response (200 OK):**
```json
{
  "uid": "user_id_123",
  "email": "user@example.com",
  "username": "john_doe",
  "role": "user",
  "created_at": 1702000000000
}
```

**Response (404 Not Found):**
```json
{
  "error": "User not found"
}
```

**Note:** Password is never returned in responses for security.

---

### 4. Update User Info
**Endpoint:** `PUT /user/<uid>`

Update user information.

**URL Parameters:**
- `uid` (string, required): User ID

**Request Body:**
```json
{
  "username": "new_username",
  "email": "newemail@example.com",
  "role": "admin"
}
```

**Request Headers:**
```
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "message": "User updated successfully",
  "uid": "user_id_123",
  "username": "new_username",
  "email": "newemail@example.com",
  "role": "admin"
}
```

**Response (404 Not Found):**
```json
{
  "error": "User not found"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "No valid fields to update"
}
```

**Updatable Fields:**
- `username` (string)
- `email` (string)
- `role` (string)

**Note:** Password cannot be updated via this endpoint for security.

---

### 5. Logout
**Endpoint:** `POST /logout`

Log out a user (client-side session termination).

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

---

## Database Structure

### Firebase Realtime Database

```
users/
├── user_id_123/
│   ├── uid: "user_id_123"
│   ├── email: "user@example.com"
│   ├── username: "john_doe"
│   ├── password: "salt$hash"  (hashed with PBKDF2)
│   ├── role: "user"
│   └── created_at: 1702000000000
├── user_id_456/
│   └── ...
```

---

## Security Features

### Password Security
- Passwords are hashed using PBKDF2 with SHA-256
- Each password has a unique salt
- Passwords are never returned in API responses
- Stored as: `salt$hash`

### Error Handling
- Generic "Invalid email or password" message for login failures (prevents email enumeration)
- Sensitive data (passwords) are never exposed in responses
- CORS enabled for frontend integration
- Input validation on all endpoints

### Rate Limiting (Recommended)
- Implement Flask-Limiter for production
- Suggested: 5 login attempts per minute per IP
- Suggested: 3 signup attempts per minute per IP

---

## Usage Examples

### JavaScript (Fetch API)

#### Sign Up
```javascript
const response = await fetch('http://localhost:5000/signup', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123',
    username: 'john_doe'
  })
});

const data = await response.json();
if (response.ok) {
  console.log('User created:', data);
  // Redirect to login
  window.location.href = 'sign-in.html';
} else {
  console.error('Error:', data.error);
}
```

#### Login
```javascript
const response = await fetch('http://localhost:5000/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();
if (response.ok) {
  // Store token
  localStorage.setItem('userToken', data.token);
  localStorage.setItem('userId', data.uid);
  // Redirect to dashboard
  window.location.href = 'dashboard.html';
} else {
  console.error('Login failed:', data.error);
}
```

#### Get User Info
```javascript
const userId = localStorage.getItem('userId');
const response = await fetch(`http://localhost:5000/user/${userId}`);
const userData = await response.json();

if (response.ok) {
  console.log('User info:', userData);
} else {
  console.error('Error:', userData.error);
}
```

#### Update User
```javascript
const userId = localStorage.getItem('userId');
const response = await fetch(`http://localhost:5000/user/${userId}`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'new_username'
  })
});

const data = await response.json();
if (response.ok) {
  console.log('User updated:', data);
} else {
  console.error('Update failed:', data.error);
}
```

---

## Setup Instructions

### Prerequisites
- Python 3.8+
- Flask
- Flask-CORS
- Firebase Admin SDK

### Installation

1. Install dependencies:
```bash
pip install flask flask-cors firebase-admin
```

2. Set up Firebase:
   - Create Firebase project
   - Download service account key as `firebase-key.json`
   - Place in project root

3. Configure database URL:
```bash
# Set environment variable
$env:FIREBASE_DATABASE_URL = "https://your-project.firebaseio.com"

# Or place firebase-key.json in project root
```

4. Run the server:
```bash
python app.py
```

Server will start on `http://localhost:5000`

---

## Testing Endpoints

### Using cURL

#### Sign Up
```bash
curl -X POST http://localhost:5000/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","username":"testuser"}'
```

#### Login
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

#### Get User
```bash
curl -X GET http://localhost:5000/user/user_id_123
```

#### Update User
```bash
curl -X PUT http://localhost:5000/user/user_id_123 \
  -H "Content-Type: application/json" \
  -d '{"username":"newusername"}'
```

---

## Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Login successful |
| 201 | Created | User registered successfully |
| 400 | Bad Request | Missing required fields |
| 401 | Unauthorized | Invalid credentials |
| 404 | Not Found | User not found |
| 409 | Conflict | Email already exists |
| 500 | Server Error | Internal error |

---

## Future Enhancements

- [ ] Email verification flow
- [ ] Password reset functionality
- [ ] Token refresh mechanism
- [ ] Rate limiting implementation
- [ ] Admin user management endpoints
- [ ] User role-based access control
- [ ] Two-factor authentication (2FA)
- [ ] OAuth integration (Google, Facebook)
- [ ] Session management
- [ ] Audit logging

---

## Support

For issues or questions, refer to:
- Firebase Documentation: https://firebase.google.com/docs
- Flask Documentation: https://flask.palletsprojects.com
- CORS Documentation: https://flask-cors.readthedocs.io
