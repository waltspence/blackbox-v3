# Deployment Guide

## 1. Firebase Configuration (Backend)

BlackBox v3 requires Google Firestore for state management.

1. **Create Project:** Go to [Firebase Console](https://console.firebase.google.com/) and create a new project.
2. **Enable Firestore:** Navigate to "Firestore Database" and click "Create Database". Start in **Production Mode**.
3. **Generate Credentials:**
   * Go to **Project Settings** > **Service Accounts**.
   * Click **Generate New Private Key**.
   * Save the file as `service-account.json` in the root of the repo.
   * **WARNING:** Add `service-account.json` to `.gitignore`. Never commit this file.

## 2. Discord Bot Configuration (Frontend)

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a **New Application**.
3. Navigate to **Bot** and click **Add Bot**.
4. **Privileged Gateway Intents:** Enable **Message Content Intent**.
5. Copy the **Token**.
6. Invite the bot to your server using OAuth2 URL Generator (Select `bot` scope).

## 3. Environment Variables

Create a `.env` file in production:

```bash
# Core
DISCORD_TOKEN=your_token_here
FIREBASE_CREDENTIALS_JSON=./secrets/service-account.json

# APIs
ODDS_API_KEY=your_key_here

# Config
LOG_LEVEL=INFO
```

## 4. Docker Deployment (Recommended)

This method works for Proxmox, DigitalOcean, or Railway.

### Dockerfile

Ensure the `Dockerfile` in the root is present.

### Build and Run

```bash
# 1. Build the image
docker build -t blackbox-v3 .

# 2. Run the container
# Mount the secrets directory to pass the JSON key securely
docker run -d \
  --name blackbox-bot \
  --restart unless-stopped \
  -v $(pwd)/service-account.json:/app/secrets/service-account.json \
  -e FIREBASE_CREDENTIALS_JSON=/app/secrets/service-account.json \
  --env-file .env \
  blackbox-v3
```

## 5. Cloud Hosting Options

### DigitalOcean (Droplet)

1. Create a Basic Droplet (Ubuntu 22.04, 1GB RAM is sufficient).
2. SSH into Droplet.
3. Install Docker (`apt install docker.io`).
4. Clone repo and transfer `service-account.json` via SCP.
5. Run Docker command above.

### Railway / Render

1. Connect GitHub repo.
2. Add Environment Variables in the UI.
3. Note: For the JSON file, copy the contents of `service-account.json` into a generic Environment Variable (e.g., `FIREBASE_JSON_RAW`) and update `services/db.py` to parse the string instead of reading a file.
