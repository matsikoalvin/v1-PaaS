# Login Setup Guide for Bukoto GuestHouse

## Prerequisites
- Firebase project created and configured
- Flask backend running on `http://localhost:5000`
- Firebase credentials JSON file (`firebase-key.json`) in project root

## Step 1: Set Up Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing one
3. Enable Authentication:
   - Go to Authentication → Sign-in method
   - Enable "Email/Password" provider
4. Create test user or use existing account

## Step 2: Get Firebase Configuration

1. In Firebase Console, go to Project Settings → Your apps
2. Select Web app or create new one
3. Copy the Firebase config object
4. Update the config in `sign-in.html`:

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```

## Step 3: Backend Configuration

1. Ensure your Firebase service account key is saved as `firebase-key.json` in project root
2. Or set environment variable:
   ```powershell
   $env:FIREBASE_CONFIG_PATH = "C:\path\to\firebase-key.json"
   ```

3. Install required Python package:
   ```bash
   pip install flask-cors
   ```

4. Start Flask backend:
   ```bash
   python app.py
   ```

## Step 4: Test Login

### Option A: Create Firebase User First
1. Go to Firebase Console → Authentication → Users
2. Click "Add user" or let users sign up via sign-up page
3. Use those credentials to log in

### Option B: Use Existing Firebase User
1. If you already have Firebase users, log in with their credentials

## Login Flow

The login process works like this:

1. **User enters email & password** → sign-in.html form
2. **Firebase authenticates** → validates with Firebase
3. **Get ID token** → Firebase provides secure token
4. **Send to backend** → POST to `/login` endpoint on Flask
5. **Backend verifies token** → uses Firebase Admin SDK
6. **Store session** → saves token and user info to localStorage
7. **Redirect to dashboard** → user logged in and accessing the app

## Features Implemented

✅ Firebase email/password authentication
✅ Error handling with user-friendly messages
✅ Loading state during authentication
✅ Auto-redirect if already logged in
✅ Backend token verification
✅ Secure session storage (localStorage)
✅ Automatic redirect to dashboard on success

## Error Messages

- "Email address not found" → User not registered, prompt to sign up
- "Incorrect password" → Wrong credentials
- "Invalid email address" → Malformed email
- "Your account has been disabled" → Admin disabled account

## Frontend to Backend Communication

### Login Endpoint
- **URL**: `http://localhost:5000/login`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "idToken": "firebase_token_here"
  }
  ```
- **Response** (Success - 200):
  ```json
  {
    "message": "Login successful",
    "uid": "user_id",
    "email": "user@example.com"
  }
  ```
- **Response** (Error - 401/500):
  ```json
  {
    "error": "Invalid token"
  }
  ```

## Next Steps

1. Add sign-up page functionality (similar to sign-in)
2. Implement logout functionality
3. Add authentication guards to protected pages
4. Store user session with backend database
5. Add password reset functionality
6. Implement refresh token mechanism

## Troubleshooting

### Firebase not initializing
- Check Firebase config values are correct
- Ensure Firebase project has Authentication enabled
- Check browser console for errors

### CORS errors
- Ensure `Flask-CORS` is installed
- Verify backend is running on `http://localhost:5000`
- Check that Firebase config authDomain matches your domain

### Backend not responding
- Ensure Flask app is running: `python app.py`
- Check that port 5000 is not in use
- Verify `firebase-key.json` is accessible

### Can't find user
- Create test user in Firebase Console
- Or use sign-up page to register first
- Email must match exactly (case-sensitive in some cases)

## Security Notes

⚠️ **Important**: 
- Never commit Firebase config or private keys to public repos
- Store sensitive data in environment variables
- Use HTTPS in production
- Implement rate limiting for login attempts
- Add 2FA for enhanced security
