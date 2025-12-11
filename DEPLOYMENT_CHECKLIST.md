# Deployment Checklist for Render

If Google Login is not working on Render, please check the following:

## 1. Configure Environment Variables on Render
Your local `.env` file is **NOT** uploaded to Render for security. You must manually add these variables in the Render Dashboard.

1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Select your web service (PhoVite).
3. Click on **Environment**.
4. Add the following keys and values (copy them from your local `.env` file):
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GEMINI_API_KEY`
   - `ADMIN_EMAIL`
   - `ADMIN_PASSWORD`
   - `JAMENDO_CLIENT_ID`

## 2. Update Google Cloud Console
Google needs to know your Render URL to allow redirects.

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
2. Edit your **OAuth 2.0 Client ID**.
3. Under **Authorized JavaScript origins**, add:
   - `https://your-app-name.onrender.com` (Replace `your-app-name` with your actual Render app name)
4. Under **Authorized redirect URIs**, add:
   - `https://your-app-name.onrender.com/login/google/callback`
5. Click **Save**.

## 3. Verify HTTPS
Render uses HTTPS. Your app is already configured with `ProxyFix` to handle this, so it should work automatically once the above steps are done.

## 4. Redeploy
After adding Environment Variables, Render usually restarts your app. If not, click **Manual Deploy** > **Deploy latest commit** to ensure everything is picked up.
