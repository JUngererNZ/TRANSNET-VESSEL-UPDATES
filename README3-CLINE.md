## File Explanation: Transnet eTender Page Monitor

This README.MD file documents a conversation where a **web page monitoring system** was designed and built. Here's what it contains and what the outcomes will be:

---

### What's in the File

The file is essentially a **chat transcript** between you and Meta AI that resulted in a complete Python application. It includes:

1. **Initial concept** – A simple URL change detection API
2. **Evolution** – Progressive upgrades to add features you requested
3. **Final code** – A complete `main.py` script for a FastAPI server
4. **Setup instructions** – How to install dependencies and run it
5. **Usage examples** – curl commands to interact with the API

---

### What the Application Does

The code creates a **FastAPI web server** that:

| Feature | Description |
|---------|-------------|
| **Page Monitoring** | Fetches a webpage, strips noise (scripts/styles), and creates a SHA-256 hash of the content |
| **Change Detection** | Compares current hash to stored hash to detect changes |
| **Keyword Filtering** | Only alerts when specific words appear (e.g., "Durban", "KZN", "Port Terminals") |
| **Scheduled Checks** | Automatically checks every 8 hours using APScheduler |
| **Email Alerts** | Sends SMTP email notifications when changes match your keywords |
| **Diff Output** | Shows exactly what text was added/removed using Python's `difflib` |
| **REST API** | Endpoints to add URLs, check manually, list watched pages |

---

### Expected Outcomes

Once you run this application, you will have:

1. **A running server** at `http://localhost:8000` that continuously monitors Transnet's eTender page
2. **Automatic notifications** every 8 hours if new Durban/KZN-related tenders appear
3. **Email alerts** showing exactly what changed on the page
4. **Manual control** via API endpoints to check on-demand or add more URLs to monitor
5. **Reduced noise** – only alerts when your specified keywords are found in the changes

---

### Current Status

Based on the file, this is **documentation only** – the actual `main.py` file and `.env` configuration file haven't been created in your project directory yet. Only `README.MD` exists.

Would you like me to create the actual implementation files (`main.py`, `.env`, `requirements.txt`) so you can run this monitoring system?


-----------------

## Transnet eTender Monitor - Successfully Built

I've created a FastAPI web monitoring application with the following files:

### Files Created

**`main.py`** - Complete FastAPI application with:
- Hash-based page change detection (SHA-256)
- 8-hour automatic scheduled checks via APScheduler
- Keyword filtering for "Durban", "KZN", "Port Terminals"
- Diff generation showing exactly what text changed
- Console logging of detected changes

**`requirements.txt`** - Python dependencies:
- fastapi, uvicorn, requests, beautifulsoup4, apscheduler

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/watch` | POST | Add a URL to monitor with optional keywords |
| `/check/{url}` | GET | Manually check a specific URL for changes |
| `/check-all` | GET | Check all watched URLs at once |
| `/watched` | GET | List all currently monitored URLs |

### How to Use

1. **Start the server** (already running):
   ```
   python -m uvicorn main:app --reload
   ```

2. **Add Transnet eTender to watch list**:
   ```
   curl -X POST "http://localhost:8000/watch" -H "Content-Type: application/json" -d "{\"url\": \"https://www.transnet.net/SubsiteRender.aspx?id=8185344\", \"keywords\": [\"Durban\", \"KZN\", \"Port Terminals\"]}"
   ```

3. **Check for changes**:
   ```
   curl "http://localhost:8000/check-all"
   ```

### What Happens Next

- The server automatically checks every 8 hours
- Changes are logged to console when detected
- Only alerts when keywords match (Durban/KZN/Port Terminals)
- Diffs show exactly what text was added or removed
- All data stored in `watched_pages.json` for persistence


------------------

## Transnet eTender Monitor - Complete & Running

### Status: ✅ Active

The application is running at `http://127.0.0.1:8000` and is now monitoring:

| Setting | Value |
|---------|-------|
| **URL** | https://www.transnet.net/SubsiteRender.aspx?id=8185344 |
| **Keywords** | Durban, KZN, Port Terminals |
| **Check Interval** | Every 8 hours (automatic) |

### How It Works

1. **Every 8 hours** - APScheduler automatically checks the Transnet page
2. **Keyword filtering** - Only alerts when "Durban", "KZN", or "Port Portals" appear in changes
3. **Console logging** - Changes are printed to the terminal with diff output
4. **Data persistence** - All data saved in `watched_pages.json`

### Manual Commands

- **Check now**: `python -c "import requests; print(requests.get('http://localhost:8000/check-all').json())"`
- **View watched URLs**: Open `http://localhost:8000/watched` in browser
- **Stop server**: Press `CTRL+C` in the terminal

### Files Created

- `main.py` - FastAPI application
- `requirements.txt` - Python dependencies
- `watched_pages.json` - Auto-created data storage

---------------

for my understanding. walk me through the steps i need to follow

Step-by-Step Walkthrough
Step 1: Start the Server
Every time you want to run the monitor, open a terminal in the project folder and run:

''
python -m uvicorn main:app --host 127.0.0.1 --port 8000
''


You'll see:


INFO: Uvicorn running on http://127.0.0.1:8000
Leave this terminal open - the server must stay running to work.


Step 2: Add a URL to Monitor
Open a second terminal (keep the server running in the first one) and run:

''
python -c "import requests; r = requests.post('http://localhost:8000/watch', json={'url': 'https://www.transnet.net/SubsiteRender.aspx?id=8185344', 'keywords': ['Durban', 'KZN', 'Port Terminals']}); print(r.json())"
''

What this does:

Sends the Transnet URL to your server
Tells it to only alert when "Durban", "KZN", or "Port Terminals" appear
Server fetches the page, creates a hash, and saves it
Response:


{'status': 'watching', 'url': 'https://...', 'keywords': ['Durban', 'KZN', 'Port Terminals']}
Step 3: Automatic Monitoring (Every 8 Hours)
You don't need to do anything. The server automatically:

Checks the Transnet page every 8 hours
Compares current content to saved content
If changed AND keywords match → prints alert to terminal
Saves new content hash for next comparison
Example terminal output when change detected:


[2026-04-13T18:00:00] Running scheduled check...
[CHANGE DETECTED] 2026-04-13T18:00:05
URL: https://www.transnet.net/SubsiteRender.aspx?id=8185344
Keyword match: ['Durban', 'KZN', 'Port Terminals']
--- DIFF ---
+ New tender: Supply and delivery of equipment - Durban Port
- Old tender: Closed tender #12345
Step 4: Manual Check (Anytime)
If you want to check immediately without waiting 8 hours:


python -c "import requests; print(requests.get('http://localhost:8000/check-all').json())"
Response:


{
  "results": [
    {
      "url": "https://www.transnet.net/...",
      "changed": true,
      "diff": "+ New line of text..."
    }
  ]
}
Step 5: View What You're Monitoring
Open your browser to:


http://localhost:8000/watched
Shows all URLs being watched, their keywords, and last check time.

Summary: Daily Routine
When	What to Do
Once	Start the server (python -m uvicorn main:app --host 127.0.0.1 --port 8000)
Once	Add URLs to monitor
Every 8 hours	Server checks automatically (watch terminal for alerts)
Anytime	Manually check with /check-all
When done	Press CTRL+C to stop server
What Files Do What
File	Purpose
main.py	The application code
requirements.txt	Python packages needed
watched_pages.json	Stores your watched URLs and their content hashes
Would you like me to clarify any specific step?



Task Completed

Step-by-Step Walkthrough
Step 1: Start the Server
Every time you want to run the monitor, open a terminal in the project folder and run:


python -m uvicorn main:app --host 127.0.0.1 --port 8000
You'll see:


INFO: Uvicorn running on http://127.0.0.1:8000
Leave this terminal open - the server must stay running to work.

Step 2: Add a URL to Monitor
Open a second terminal (keep the server running in the first one) and run:


python -c "import requests; r = requests.post('http://localhost:8000/watch', json={'url': 'https://www.transnet.net/SubsiteRender.aspx?id=8185344', 'keywords': ['Durban', 'KZN', 'Port Terminals']}); print(r.json())"
What this does:

Sends the Transnet URL to your server
Tells it to only alert when "Durban", "KZN", or "Port Terminals" appear
Server fetches the page, creates a hash, and saves it
Response:


{'status': 'watching', 'url': 'https://...', 'keywords': ['Durban', 'KZN', 'Port Terminals']}
Step 3: Automatic Monitoring (Every 8 Hours)
You don't need to do anything. The server automatically:

Checks the Transnet page every 8 hours
Compares current content to saved content
If changed AND keywords match → prints alert to terminal
Saves new content hash for next comparison
Example terminal output when change detected:


[2026-04-13T18:00:00] Running scheduled check...
[CHANGE DETECTED] 2026-04-13T18:00:05
URL: https://www.transnet.net/SubsiteRender.aspx?id=8185344
Keyword match: ['Durban', 'KZN', 'Port Terminals']
--- DIFF ---
+ New tender: Supply and delivery of equipment - Durban Port
- Old tender: Closed tender #12345
Step 4: Manual Check (Anytime)
If you want to check immediately without waiting 8 hours:


python -c "import requests; print(requests.get('http://localhost:8000/check-all').json())"
Response:


{
  "results": [
    {
      "url": "https://www.transnet.net/...",
      "changed": true,
      "diff": "+ New line of text..."
    }
  ]
}
Step 5: View What You're Monitoring
Open your browser to:


http://localhost:8000/watched
Shows all URLs being watched, their keywords, and last check time.

Summary: Daily Routine
When	What to Do
Once	Start the server (python -m uvicorn main:app --host 127.0.0.1 --port 8000)
Once	Add URLs to monitor
Every 8 hours	Server checks automatically (watch terminal for alerts)
Anytime	Manually check with /check-all
When done	Press CTRL+C to stop server
What Files Do What
File	Purpose
main.py	The application code
requirements.txt	Python packages needed
watched_pages.json	Stores your watched URLs and their content hashes
Let me know if you'd like clarification on any specific step!