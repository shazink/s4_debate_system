# 🚀 Deploying S4 to Render

This project includes a `render.yaml` Blueprint for easy deployment.

## 1. Push to GitHub
Make sure your latest code is on GitHub (we just committed it!).

## 2. Deploy on Render
1. Create a free account at [render.com](https://render.com).
2. Go to **Dashboard** → **New +** → **Blueprint**.
3. Connect your GitHub repository (`s4_debate_system`).
4. Give it a name (e.g., `s4-debate-demo`).
5. Click **Apply**.

## 3. Configure Environment Variables
Render will ask for Environment Variables defined in `render.yaml`.
- **GROQ_API_KEY**: Paste your key starting with `gsk_...`

## 4. Verify & Launch
- Render will auto-deploy.
- Wait for the build to finish (installing dependencies).
- When it says "Live", click the URL (e.g., `https://s4-debate-demo.onrender.com`).

## 5. Troubleshooting
- **Logs**: Click the "Logs" tab in Render to see if the server started.
- **Port**: Render automatically detects port 5000 (default for Flask). If it fails, add environment variable `PORT=10000` and update `api.py` to use `os.environ.get('PORT', 5000)` (though gunicorn usually handles binding).
    - *Note: Our `render.yaml` runs `gunicorn api:app` which binds to the port Render provides automatically.*

---
**That's it! Your multi-agent debate system is now live on the web! 🌍**
