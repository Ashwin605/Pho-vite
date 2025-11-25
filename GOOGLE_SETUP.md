# Google Sign-In Setup Guide

To make Google Sign-In work, you need to get credentials from Google and put them in your `.env` file.

## Step 1: Create Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown at the top and select **"New Project"**.
3. Name it "Phovite" (or anything you like) and click **Create**.

## Step 2: Configure OAuth Consent Screen
1. In the left sidebar, go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** and click **Create**.
3. Fill in the required fields:
   - **App Name**: Phovite
   - **User Support Email**: Select your email.
   - **Developer Contact Information**: Enter your email.
4. Click **Save and Continue** through the other steps (you don't need to add scopes or test users for now).

## Step 3: Create Credentials
1. Go to **APIs & Services** > **Credentials**.
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**.
3. **Application type**: Select **Web application**.
4. **Name**: "Phovite Web Client".
5. **Authorized redirect URIs**:
   - Click **+ ADD URI**.
   - Paste this EXACT URL: `http://127.0.0.1:5000/login/google/callback`
   - (Optional) Add `http://localhost:5000/login/google/callback` as well.
6. Click **Create**.

## Step 4: Update .env File
1. You will see a popup with "Your Client ID" and "Your Client Secret".
2. Copy the **Client ID**.
3. Open the `.env` file in your project folder.
4. Replace `your_google_client_id_here` with the copied ID.
5. Copy the **Client Secret**.
6. Replace `your_google_client_secret_here` with the copied Secret.
7. Save the file.

## Step 5: Restart the App
1. Stop the running server (Ctrl+C).
2. Run `python app.py` again.
3. Go to `http://127.0.0.1:5000/login` and try the button!
