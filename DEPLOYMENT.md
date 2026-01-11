# 🚀 Deploy IRC Chat App to Railway

This guide will help you deploy your IRC Chat application to Railway.

## Prerequisites

- A GitHub account
- A Railway account (sign up at https://railway.app)
- Git installed on your computer

## Step 1: Push to GitHub

### 1.1 Create a new GitHub repository

1. Go to https://github.com/new
2. Repository name: `irc-chat-app` (or your preferred name)
3. Description: "Terminal-based IRC chat application"
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

### 1.2 Push your code

After creating the repository, GitHub will show you commands. Use these:

```bash
cd "d:\Vedhas Shinde\IRC chat app"
git init
git add .
git commit -m "Initial commit: IRC Chat Application"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/irc-chat-app.git
git push -u origin main
```

**Note:** Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 2: Deploy to Railway

### 2.1 Create Railway Project

1. Go to https://railway.app
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub account
5. Select your `irc-chat-app` repository
6. Railway will automatically detect it's a Python app

### 2.2 Configure Deployment

Railway will automatically:
- Detect `requirements.txt` and install dependencies
- Use the `Procfile` to start the server
- Assign a public URL

### 2.3 Get Your Deployment URL

1. Once deployed, click on your project
2. Go to "Settings" → "Networking"
3. Click "Generate Domain"
4. You'll get a URL like: `https://your-app.up.railway.app`

## Step 3: Connect Clients to Deployed Server

### Update Client Connection

To connect the terminal client to your Railway server, update the client code:

1. Open `client/client.py`
2. Find the line: `sio = socketio.Client()`
3. When connecting, use your Railway URL instead of localhost

For example:
```python
# Instead of: sio.connect('http://localhost:5000')
# Use: sio.connect('https://your-app.up.railway.app')
```

## Important Notes

### Server vs Client

- **Server**: Runs on Railway (cloud) - always accessible
- **Client**: Runs on your local terminal - connects to Railway server

### WebSocket Support

Railway supports WebSocket connections by default, so Socket.IO will work perfectly!

### Logs & Monitoring

View your application logs in Railway:
1. Click on your deployment
2. Go to "Deployments" tab
3. Click on the active deployment
4. View real-time logs

### Environment Variables (Optional)

If you need to add environment variables:
1. Go to your project in Railway
2. Click "Variables"
3. Add your variables (e.g., `SECRET_KEY`)

## Troubleshooting

### Deployment Failed

- Check the build logs in Railway
- Ensure `requirements.txt` has all dependencies
- Verify `Procfile` is correct

### Can't Connect from Client

- Make sure you're using the Railway URL (not localhost)
- Ensure the Railway deployment is running (green status)
- Check that the domain is generated and accessible

### Port Issues

- Don't worry about ports! Railway automatically assigns and manages ports
- The server code now reads from `PORT` environment variable

## Testing Your Deployment

1. Open your Railway URL in a browser: `https://your-app.up.railway.app`
2. You should see a Flask message (not a full page, that's normal)
3. This confirms the server is running!

## Next Steps

After successful deployment:

1. ✅ Server is live 24/7 on Railway
2. ✅ Update client code to connect to Railway URL
3. ✅ Share the URL with friends to connect their clients
4. ✅ Monitor logs and usage in Railway dashboard

---

## Quick Reference

### Railway Commands

- **Redeploy**: Push changes to GitHub, Railway auto-deploys
- **View Logs**: Dashboard → Your Project → Deployments → Logs
- **Rollback**: Dashboard → Deployments → Select previous version

### Local Development

For local testing, keep using:
```bash
start_chat.bat
```

This uses `localhost:5000` - perfect for testing before pushing changes!

---

**Need Help?** 
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
