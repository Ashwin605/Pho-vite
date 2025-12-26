# Firebase Setup Guide

## 1. Frontend Configuration

The frontend configuration is located in `static/js/firebase-config.js`. You have already set this up with:

- Project ID: phovite-7ae18
- Auth Domain: phovite-7ae18.firebaseapp.com

### IMPORTANT: Authorize Localhost

If you see an error saying "This domain is not authorized for OAuth operations", you must fix this in the Firebase Console:

1. Go to **Authentication** > **Settings** > **Authorized Domains**.
2. Click **Add Domain**.
3. Add `localhost`.
4. Add `127.0.0.1`.
5. **For Render Deployment:** Add `pho-vite.onrender.com` to the list.
6. (Optional) If you use a custom domain, add that too.

## 2. Backend Configuration (Critical)

For the Python backend (`app.py`) to verify user logins, it needs **Admin Privileges**. This is securely handled using a Service Account Key.

### How to get the key:

1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Open your project (**phovite-7ae18**).
3. Click the **Gear Icon** > **Project Settings**.
4. Go to the **Service accounts** tab.
5. Click **Generate new private key**.
6. A JSON file will download.

### Where to put it:

1. Rename the downloaded file to `firebase_credentials.json`.
2. Move it to the root of this project: `c:\Users\ASHWIN\Downloads\Pho-vite-main\Pho-vite-main\firebase_credentials.json`.

**Note:** Do NOT commit this file to GitHub or share it publicly. It gives full administrative access to your Firebase project.

## 3. Python Dependencies

We have already installed the required `firebase-admin` package.

## 4. Verification

Once the file is in place, restart the Flask server:

```bash
python app.py
```

Login and Signup should now work seamlessly with Firebase!
