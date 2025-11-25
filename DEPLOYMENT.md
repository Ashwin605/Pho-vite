# 🚀 Deploying PhoVite to Render

Follow these simple steps to get your app live on the internet!

## Prerequisites

1.  **GitHub Account**: You need to push your code to a GitHub repository.
2.  **Render Account**: Sign up at [render.com](https://render.com).

## Step 1: Push Code to GitHub

1.  Create a new repository on GitHub.
2.  Run these commands in your project folder:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

*(Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual details)*

## Step 2: Create Web Service on Render

1.  Go to your [Render Dashboard](https://dashboard.render.com/).
2.  Click **"New +"** and select **"Web Service"**.
3.  Connect your GitHub account and select your **PhoVite** repository.
4.  **Configuration**:
    *   **Name**: `phovite` (or whatever you like)
    *   **Region**: Choose the one closest to you.
    *   **Branch**: `main`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `./build.sh`
    *   **Start Command**: `gunicorn app:app`
5.  **Environment Variables** (Scroll down to "Advanced"):
    *   Click "Add Environment Variable"
    *   Key: `GEMINI_API_KEY`
    *   Value: `Your_Gemini_API_Key_Here` (Copy from your .env file)
    *   Key: `PYTHON_VERSION`
    *   Value: `3.10.0`

## Step 3: Database (Important!)

**Option A: Simple (Data deleted on restart)**
*   If you just click "Create Web Service" now, it will use SQLite.
*   ⚠️ **Warning**: All user accounts and invitations will be **deleted** every time you redeploy or the server restarts.

**Option B: Persistent (Recommended)**
1.  Go to Render Dashboard > **"New +"** > **"PostgreSQL"**.
2.  Name: `phovite-db`.
3.  Plan: **Free** (good for testing) or Starter.
4.  Click **Create Database**.
5.  Copy the **"Internal Database URL"**.
6.  Go back to your Web Service > **Environment**.
7.  Add a new variable:
    *   Key: `DATABASE_URL`
    *   Value: Paste the Internal Database URL.

## Step 4: Deploy

1.  Click **"Create Web Service"**.
2.  Render will start building your app. You can watch the logs.
3.  Once it says "Live", click the URL at the top (e.g., `https://phovite.onrender.com`).

## Troubleshooting

*   **Build Failed?** Check the logs. Make sure `requirements.txt` is in the root folder.
*   **App Error?** Check the "Logs" tab.
*   **Database Error?** Ensure `DATABASE_URL` is correct.

## 🎉 You're Live!
Share your URL with friends!
