# NGROK SETUP FOR ELEVENLABS WEBHOOK

## Step 1: Install ngrok
```bash
# If you don't have ngrok installed:
brew install ngrok

# Or download from https://ngrok.com/download
```

## Step 2: Run Your Flask App Locally
```bash
cd "/Users/melville/Documents/11 labs webhook"
python app.py
```
*Your app will start on http://localhost:5000*

## Step 3: Start ngrok (in a NEW terminal)
```bash
# Open a new terminal and run:
ngrok http 5000
```

## Step 4: Copy Your Webhook URL
ngrok will show output like:
```
Session Status    online
Session Expires   7 hours, 59 minutes
Version           3.x.x
Region            United States (us)
Latency           24ms
Web Interface     http://127.0.0.1:4040
Forwarding        https://abc123-def456.ngrok-free.app -> http://localhost:5000
```

**Copy the HTTPS URL**: `https://abc123-def456.ngrok-free.app`

## Step 5: Update ElevenLabs Webhook
1. Go to ElevenLabs Dashboard
2. Go to your agent settings
3. In Webhook URL field, enter: `https://YOUR_NGROK_URL.ngrok-free.app/webhook/elevenlabs`
4. Save the settings

## Step 6: Test Your Setup
1. Test endpoint: `https://YOUR_NGROK_URL.ngrok-free.app/test`
2. Start a conversation with your agent
3. Watch the terminal for webhook calls

## Important Notes:
- Each time you restart ngrok, the URL changes
- Free ngrok URLs expire after ~8 hours
- Keep both terminals running (Flask app + ngrok)
- Use the HTTPS URL, not HTTP
