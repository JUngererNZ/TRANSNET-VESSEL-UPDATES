Reviewing the file content to explain its purpose and expected outcome.

Read [](file:///c%3A/Users/Jason/Projects/TRANSNET-VESSEL-UPDATES/README.MD#1-1), lines 1 to 200

## What this file is

README.MD is not a real Python program by itself. It is a text document showing:

- a chat-style intro from “Meta AI”
- a sample Python + FastAPI app
- instructions for running and using that app
- a specific monitoring use case for a Transnet eTender page

## What the code in the file does

If you take the sample code and save it as `main.py`, it would create a small web API that:

- fetches a web page
- computes a SHA-256 hash of the page content
- optionally watches only a specific CSS selector on the page
- stores watched URLs and their last hash in `watched_pages.json`
- exposes endpoints:
  - `POST /watch` to start watching a URL
  - `GET /check/{url}` to see whether that URL changed since last watch
  - `GET /check-all` to check every watched URL
  - `GET /watched` to list current watched URLs

## Expected outcome

If you run it with:

`uvicorn main:app --reload`

you get an API at `http://localhost:8000` that can:

- register a page to watch
- detect when page content changes
- update stored state when a change happens
- optionally monitor only part of a page via `css_selector`

## Specific use case included

The file also includes a suggested target:

- `https://www.transnet.net/SubsiteRender.aspx?id=8185344`

It says this is Transnet’s eTender page and suggests watching the whole page or a narrower selector like `main` to avoid false alerts from unrelated page changes.

## Bottom line

The README is describing a simple website-change-watcher API. The outcome is a service that can monitor a page and tell you if it changed, and it recommends using it to monitor the Transnet eTender page.

-----------------------

Read [](file:///c%3A/Users/Jason/Projects/TRANSNET-VESSEL-UPDATES/README3-CLINE.md#1-1), lines 1 to 200

## Step-by-Step Guide to Using the Transnet eTender Monitor

Based on the content in README3-CLINE.md, here's a clear walkthrough of what you need to do to set up and use the web page monitoring system for Transnet's eTender page. The file indicates this is a FastAPI application that monitors for changes and alerts only when specific keywords (like "Durban", "KZN", "Port Terminals") appear.

### Prerequisites
- Python installed on your system
- The files main.py and requirements.txt need to exist in your project folder (if not, you'll need to create them from the code in the README)

### Step 1: Install Dependencies
Open a PowerShell terminal in your project folder (TRANSNET-VESSEL-UPDATES) and run:

```powershell
pip install -r requirements.txt
```

This installs FastAPI, uvicorn, requests, beautifulsoup4, and apscheduler.

### Step 2: Start the Server
In the same terminal, run:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

- You'll see output like: `INFO: Uvicorn running on http://127.0.0.1:8000`
- **Important**: Keep this terminal open - the server must stay running for monitoring to work
- The server will automatically check the monitored URLs every 8 hours

### Step 3: Add the Transnet eTender Page to Monitor
Open a **second PowerShell terminal** (keep the first one running) and run this command to add the URL:

```powershell
python -c "import requests; r = requests.post('http://localhost:8000/watch', json={'url': 'https://www.transnet.net/SubsiteRender.aspx?id=8185344', 'keywords': ['Durban', 'KZN', 'Port Terminals']}); print(r.json())"
```

- This tells the server to watch Transnet's eTender page
- It will only alert when changes contain "Durban", "KZN", or "Port Terminals"
- Expected response: `{'status': 'watching', 'url': 'https://...', 'keywords': ['Durban', 'KZN', 'Port Terminals']}`

### Step 4: Let It Monitor Automatically
- The server now runs scheduled checks every 8 hours automatically
- When changes are detected that match your keywords, you'll see output in the first terminal like:

```
[2026-04-13T18:00:00] Running scheduled check...
[CHANGE DETECTED] 2026-04-13T18:00:05
URL: https://www.transnet.net/SubsiteRender.aspx?id=8185344
Keyword match: ['Durban', 'KZN', 'Port Terminals']
--- DIFF ---
+ New tender: Supply and delivery of equipment - Durban Port
- Old tender: Closed tender #12345
```

### Step 5: Manual Check (Optional)
If you want to check immediately without waiting for the 8-hour schedule:

```powershell
python -c "import requests; print(requests.get('http://localhost:8000/check-all').json())"
```

- This forces an immediate check of all watched URLs
- Response shows if any changes were detected

### Step 6: View Currently Watched URLs
Open your browser and go to: `http://localhost:8000/watched`

This shows all URLs being monitored with their settings.

### Step 7: Stop the Server
When you want to stop monitoring:
- Go back to the first terminal
- Press `Ctrl+C` to stop the server

### What Happens During Monitoring
- The app fetches the Transnet page every 8 hours
- It strips out scripts, styles, and other noise
- Creates a SHA-256 hash of the remaining content
- Compares to the previously stored hash
- If different AND keywords match → logs the change with a diff showing exactly what text was added/removed
- Updates the stored hash for the next check

### Data Storage
- All monitoring data is saved in watched_pages.json in your project folder
- This persists between server restarts

### Troubleshooting
- If the server doesn't start: Make sure all dependencies are installed and no other process is using port 8000
- If no changes detected: The page might not have changed, or changes don't contain your keywords
- For manual testing: You can use curl commands instead of the Python one-liners if preferred

This setup gives you automated monitoring of Transnet's eTender page with targeted alerts for Durban/KZN-related tenders. The system runs continuously in the background once started.


--------------

Read [](file:///c%3A/Users/Jason/Projects/TRANSNET-VESSEL-UPDATES)

Read [](file:///c%3A/Users/Jason/Projects/TRANSNET-VESSEL-UPDATES/main.py)

Replacing 15 lines with 34 lines in [](file:///c%3A/Users/Jason/Projects/TRANSNET-VESSEL-UPDATES/main.py)


```

```


Replacing 7 lines with 7 lines in [](file:///c%3A/Users/Jason/Projects/TRANSNET-VESSEL-UPDATES/main.py)

Replacing 7 lines with 7 lines in [](file:///c%3A/Users/Jason/Projects/TRANSNET-VESSEL-UPDATES/main.py)


```

```


Replacing 12 lines with 12 lines in [](file:///c%3A/Users/Jason/Projects/TRANSNET-VESSEL-UPDATES/main.py)


```

```


Replacing 8 lines with 37 lines in [](file:///c%3A/Users/Jason/Projects/TRANSNET-VESSEL-UPDATES/main.py)


```

```


Ran terminal command: import main; print('Script imports successfully')

Ran terminal command: import main; print('Script imports successfully')

## Updated Script with Logging

I've updated main.py to add file logging for the monitoring outputs. Here's what changed:

### New Features Added

1. **File Logging**: All change detection outputs are now written to monitor.log in your project folder, in addition to console output.

2. **New Endpoint `/logs`**: 
   - Access via `http://localhost:8000/logs`
   - Returns the last 50 lines from the log file (configurable with `?lines=100`)
   - Similar to `/watched` but for logs

3. **New Endpoint `/export-watched-to-log`**:
   - Access via `http://localhost:8000/export-watched-to-log`
   - Copies all current watched URLs and their details into the log file
   - Useful for easy reading of watched data in the log

### How It Works Now

- **Automatic Logging**: Every 8 hours, when the scheduled check runs, it logs to both console and monitor.log
- **Change Detections**: When changes are found, the diff and details are logged to the file
- **Export Function**: You can manually trigger an export of watched URLs to the log anytime

### Usage

1. **Start the server** (same as before):
   ```powershell
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

2. **View logs in browser**:
   - Go to `http://localhost:8000/logs` to see recent log entries

3. **Export watched URLs to log**:
   - Visit `http://localhost:8000/export-watched-to-log` to append current watched data to the log file

4. **Read the log file directly**:
   - Open monitor.log in your project folder for a complete history

### Log File Format

The monitor.log file will contain entries like:
```
2026-04-13 12:00:00,000 - INFO - Running scheduled check...
2026-04-13 12:00:05,000 - INFO - [CHANGE DETECTED] 2026-04-13T12:00:05
2026-04-13 12:00:05,001 - INFO - URL: https://www.transnet.net/SubsiteRender.aspx?id=8185344
2026-04-13 12:00:05,002 - INFO - Keyword match: ['Durban', 'KZN', 'Port Terminals']
2026-04-13 12:00:05,003 - INFO - --- DIFF ---
+ New tender added...
```

This gives you persistent logging of all monitoring activity, easily readable in the log file or via the `/logs` endpoint. The watched data can be exported to the log for combined viewing.

--------------

No, you don't need to restart if it's already running—just start the server if it's not running yet.

The logging setup happens when the main.py module is imported (which occurs when you start the FastAPI server with `uvicorn`). Once the server is running:

- The monitor.log file will be created immediately
- Logs will be written as checks occur (every 8 hours automatically, or when you manually trigger `/check-all` or `/export-watched-to-log`)

If you want to see logs right away without waiting:
1. Start the server: `python -m uvicorn main:app --host 127.0.0.1 --port 8000`
2. Visit `http://localhost:8000/export-watched-to-log` to add the current watched URLs to the log
3. Or trigger a manual check: `http://localhost:8000/check-all`

The log file will then contain entries like the watched export and any change detections. You can view it at `http://localhost:8000/logs` or open monitor.log directly.

--------------

No, you don't need to restart if it's already running—just start the server if it's not running yet.

The logging setup happens when the main.py module is imported (which occurs when you start the FastAPI server with `uvicorn`). Once the server is running:

- The monitor.log file will be created immediately
- Logs will be written as checks occur (every 8 hours automatically, or when you manually trigger `/check-all` or `/export-watched-to-log`)

If you want to see logs right away without waiting:
1. Start the server: `python -m uvicorn main:app --host 127.0.0.1 --port 8000`
2. Visit `http://localhost:8000/export-watched-to-log` to add the current watched URLs to the log
3. Or trigger a manual check: `http://localhost:8000/check-all`

The log file will then contain entries like the watched export and any change detections. You can view it at `http://localhost:8000/logs` or open monitor.log directly.

