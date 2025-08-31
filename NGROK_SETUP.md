# NGROK SETUP FOR LOCAL TESTING

## 1. Install ngrok
```bash
# On macOS with Homebrew:
brew install ngrok

# Or download from: https://ngrok.com/download
```

## 2. Start Your Flask Backend
```bash
cd "/Users/melville/Documents/11 labs webhook"
python app.py
```
Your app will run on http://localhost:5001

## 3. Start ngrok (in a NEW terminal)
```bash
ngrok http 5001
```

## 4. Get Your Webhook URL
ngrok will show:
```
Forwarding  https://abc123-xyz.ngrok-free.app -> http://localhost:5001
```

Your webhook URL is: `https://abc123-xyz.ngrok-free.app/webhook/elevenlabs`

## 5. Update 11 Labs Configuration

### In 11 Labs Dashboard:
1. Go to your agent settings
2. Update the webhook URL to your ngrok URL
3. Make sure HMAC secret matches your .env file

### In Your .env File:
```
HMAC_SECRET=your-hmac-secret-from-11labs
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-key
```

## 6. Test the Flow

### Direct Agent Test (bypasses frontend):
1. Go to 11 Labs dashboard
2. Test your agent directly
3. Check your terminal for webhook logs
4. Check Supabase for saved data

### Frontend Test:
1. Run frontend: `cd /Users/melville/Documents/elevenlabs-chat-app && npm run dev`
2. Go to http://localhost:3000
3. Enter name and user ID
4. Start conversation
5. Check webhook logs

## Debugging Tips

- Watch ngrok logs at http://127.0.0.1:4040
- Check Flask terminal for webhook receipts
- Verify HMAC secret matches exactly
- Ensure database tables exist with correct schema
