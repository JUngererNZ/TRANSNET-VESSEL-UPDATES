This was a small project on the side that my daily tasks and linked to.
Öne of my daily tasks is to re/view vessels inbound to port. I am lazy, to "remember" to see if there is an update from the Transnet service provider.
This got me to writing a script/curl/url check on Transnet website. Using tech to my advantage. Granted, could be seen as over engineered, yet if it makes my life a little easier, then why not right?!
The first conversations were with META platform as I was already busy with side conversations. Then took these responses to VSCode Chat, and played off against Cline for better answers......



[12/4, 00:24] Meta AI: Yep, I can code 💻 

I can help you with Python, JavaScript, HTML/CSS, SQL, Java, C++, and more. Whether you need me to:

- *Write code* from scratch
- *Debug* something that's broken  
- *Explain* how a piece of code works
- *Optimize* for speed or readability
- *Build* small scripts, apps, or functions

What did you have in mind? Give me the language + what you want it to do, and we’ll get cracking.
[12/4, 00:24] Meta AI: Yep, can do. Here's a simple but solid API that checks a URL for changes and tells you when content is different.

This uses Python + FastAPI. It saves a hash of the page and compares on each check. Run it and hit `/check` to see if a site changed.

*1. Install dependencies*
pip install fastapi uvicorn requests beautifulsoup4
*2. The API code* `main.py`
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
from datetime import datetime

app = FastAPI()
DB_FILE = "watched_pages.json"

Load existing data
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

Save data
def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_page_hash(url: str, css_selector: str = None) -> str:
    """Fetch page and return hash of content"""
    headers = {'User-Agent': 'Mozilla/5.0 PageChangeBot/1.0'}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')

    # If selector provided, only hash that part of page
    if css_selector:
        target = soup.select_one(css_selector)
        content = str(target) if target else resp.text
    else:
        # Remove script/style tags to avoid false positives from ads/trackers
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        content = soup.get_text()

    return hashlib.sha256(content.encode('utf-8')).hexdigest()

class WatchRequest(BaseModel):
    url: HttpUrl
    css_selector: str | None = None # Optional: watch specific element like "#price" or ".news"

@app.post("/watch")
def watch_url(req: WatchRequest):
    """Add a URL to watch list"""
    db = load_db()
    url = str(req.url)

    try:
        current_hash = get_page_hash(url, req.css_selector)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    db[url] = {
        "last_hash": current_hash,
        "css_selector": req.css_selector,
        "last_checked": datetime.now().isoformat(),
        "last_changed": datetime.now().isoformat()
    }
    save_db(db)
    return {"status": "watching", "url": url, "hash": current_hash}

@app.get("/check/{url:path}")
def check_url(url: HttpUrl, css_selector: str = None):
    """Check if a specific URL has changed since last watch"""
    db = load_db()
    url = str(url)

    if url not in db:
        raise HTTPException(status_code=404, detail="URL not being watched. POST to /watch first")

    old_hash = db[url]["last_hash"]
    selector = css_selector or db[url].get("css_selector")

    try:
        new_hash = get_page_hash(url, selector)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    changed = new_hash!= old_hash
    db[url]["last_checked"] = datetime.now().isoformat()

    if changed:
        db[url]["last_hash"] = new_hash
        db[url]["last_changed"] = datetime.now().isoformat()

    save_db(db)

    return {
        "url": url,
        "changed": changed,
        "last_checked": db[url]["last_checked"],
        "last_changed": db[url]["last_changed"]
    }

@app.get("/check-all")
def check_all():
    """Check all watched URLs for changes"""
    db = load_db()
    results = []

    for url, data in db.items():
        try:
            new_hash = get_page_hash(url, data.get("css_selector"))
            changed = new_hash!= data["last_hash"]

            db[url]["last_checked"] = datetime.now().isoformat()
            if changed:
                db[url]["last_hash"] = new_hash
                db[url]["last_changed"] = datetime.now().isoformat()

            results.append({"url": url, "changed": changed})
        except Exception as e:
            results.append({"url": url, "changed": None, "error": str(e)})

    save_db(db)
    return {"results": results}

@app.get("/watched")
def list_watched():
    """List all URLs currently being watched"""
    return load_db()
*3. Run it*
uvicorn main:app --reload
API will be at `http://localhost:8000`

*4. How to use it*

*Start watching a page:*
curl -X POST "http://localhost:8000/watch" \
-H "Content-Type: application/json" \
-d '{"url": "https://example.com"}'
*Watch just one element* like a price:
curl -X POST "http://localhost:8000/watch" \
-H "Content-Type: application/json" \
-d '{"url": "https://store.com/product", "css_selector": ".price"}'
*Check if it changed:*
curl "http://localhost:8000/check/https://example.com"
Response: `{"url": "...", "changed": true, "last_changed": "2026-04-11T14:23:01"}`

*Key features:*
- *Hash-based*: Fast, doesn’t store whole page
- *CSS selectors*: Watch only part of a page to avoid false alerts from ads/footers
- *Strips scripts*: Ignores trackers that change every load
- *`/check-all`*: Check everything you’re watching in one call

*Want me to add:*
1. *Email/Discord alerts* when it changes?
2. *Scheduling* so it auto-checks every hour?
3. *Diff output* showing what text actually changed?

What kind of site are you trying to monitor?


https://www.transnet.net/SubsiteRender.aspx?id=8185344


Got it — you want to monitor *Transnet's eTender page* for changes 7333

That specific URL `https://www.transnet.net/SubsiteRender.aspx?id=8185344` is Transnet's Current eTender System page. It lists tenders across all operating divisions and will progressively be replaced by their new eSupplier Portal. 7333

*Here's how to use the API I gave you to watch it:*

*1. Start watching the whole page*
curl -X POST "http://localhost:8000/watch" \
-H "Content-Type: application/json" \
-d '{"url": "https://www.transnet.net/SubsiteRender.aspx?id=8185344"}'
*2. Watch only the tender listings*
The page has lots of boilerplate text. To avoid false alerts when footers/copyright changes, target just the tender section. Inspecting the page, you'd likely use something like:
curl -X POST "http://localhost:8000/watch" \
-H "Content-Type: application/json" \
-d '{
  "url": "https://www.transnet.net/SubsiteRender.aspx?id=8185344",
  "css_selector": "main"
}'
_Note: You'd need to inspect the actual HTML to get the exact selector. `main` is a guess. Use browser DevTools → right click tender list → Copy selector._

*3. Check if it changed*
curl "http://localhost:8000/check/https://www.transnet.net/SubsiteRender.aspx?id=8185344"
*Important quirks with Transnet's site:*
1. *They're migrating*: Transnet says to check both the old E-tender system AND the new eSupplier Portal for opportunities. You might want to watch both URLs.
2. *Dynamic content*: Tender pages often have dates/timestamps that change daily. The code I gave you strips `<script>` and `<style>` tags to reduce noise, but you may still get false positives.
3. *Fraud warnings*: Transnet warns about fake RFPs/RFQs. If you're building this for business use, add manual verification before acting on a "change". 334c

*Want me to upgrade the code for you?* I can add:
1. *Email alerts* when new tenders appear
2. *Cron scheduling* to auto-check every 30 min
3. *Diff output* so you see exactly what text was added/removed
4. *Multiple URLs* so you watch the old eTender + new eSupplier Portal together

Since you're in Cape Town, also worth noting Transnet lists opportunities for Cape Town port. Want me to add a filter so it only alerts you for tenders mentioning "Cape Town", "Western Cape", or "TPT"? bf19

Which upgrades do you want?


[12/4, 02:42] Meta AI: The API I gave you is written in *Python* 🐍 

Specifically:
- *Language*: Python 3.8+
- *Framework*: FastAPI – for the API endpoints
- *Key libraries*: 
    - `requests` – fetches the webpage
    - `beautifulsoup4` – parses HTML so we can target specific parts
    - `uvicorn` – runs the server

Why Python? It's the fastest way to get this running and easy to extend with email alerts, scheduling, etc.

Want me to rewrite it in another language like http://Node.js/JavaScript, Go, or PHP?
[12/4, 02:43] Meta AI: Perfect — Python it is then ✅ 

That's the best choice for this anyway. FastAPI is lightweight, fast, and the `requests` + `BeautifulSoup` combo handles web scraping really well.

*To get you running in 60 seconds:*
1. Save the code I sent as `main.py`
2. `pip install fastapi uvicorn requests beautifulsoup4`
3. `uvicorn main:app --reload`
4. Then POST your Transnet URL to start watching it

*Next steps for your Transnet monitor?*  
Pick what you need and I’ll add it to the code:
1. *Auto-check every X minutes* with APScheduler so you don’t have to hit `/check-all` manually
2. *Email/WhatsApp alerts* when a new tender appears 
3. *Keyword filter* so it only alerts for “Cape Town”, “Port Terminals”, etc
4. *Show the diff* – tell you exactly what text was added/removed

Which one should we build in first?
[12/4, 02:43] Jason: Python is preferred


Gotcha — we’ll make it check every 8 hours, email you on changes, only alert for “Durban” tenders, and show you exactly what text changed 🔍

Here’s the upgraded Python code:

*1. Install new dependencies*
pip install fastapi uvicorn requests beautifulsoup4 apscheduler python-dotenv difflib
*2. Create `.env` file* for email settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
EMAIL_TO=your_email@gmail.com
_For Gmail, use an App Password, not your normal password. Settings → Security → 2-Step Verification → App passwords_

*3. Updated `main.py`*
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import difflib

load_dotenv()
app = FastAPI()
DB_FILE = "watched_pages.json"
scheduler = BackgroundScheduler()
scheduler.start()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_page_content(url: str, css_selector: str = None) -> tuple[str, str]:
    """Fetch page and return both text content and hash"""
    headers = {'User-Agent': 'Mozilla/5.0 PageChangeBot/1.0'}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')

    if css_selector:
        target = soup.select_one(css_selector)
        content = str(target) if target else resp.text
    else:
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        content = soup.get_text()

    # Normalize whitespace to reduce false positives
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    clean_content = '\n'.join(lines)

    content_hash = hashlib.sha256(clean_content.encode('utf-8')).hexdigest()
    return clean_content, content_hash

def send_email(subject: str, body: str):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS, EMAIL_TO]):
        print("Email not configured, skipping send")
        return
    msg = MIMEText(body, 'plain')
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = EMAIL_TO
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Email failed: {e}")

def get_diff(old_text: str, new_text: str) -> str:
    """Return a readable diff between two text versions"""
    diff = difflib.unified_diff(
        old_text.splitlines(),
        new_text.splitlines(),
        fromfile='old',
        tofile='new',
        lineterm=''
    )
    return '\n'.join(diff)

def check_single_url(url: str) -> dict:
    db = load_db()
    if url not in db:
        return {"error": "URL not watched"}

    data = db[url]
    old_hash = data["last_hash"]
    old_content = data.get("last_content", "")
    selector = data.get("css_selector")
    keywords = data.get("keywords", [])

    try:
        new_content, new_hash = get_page_content(url, selector)
    except Exception as e:
        return {"url": url, "error": str(e)}

    changed = new_hash!= old_hash
    db[url]["last_checked"] = datetime.now().isoformat()
    result = {"url": url, "changed": changed}

    if changed:
        # Check keyword filter
        if keywords:
            keyword_found = any(kw.lower() in new_content.lower() for kw in keywords)
            if not keyword_found:
                db[url]["last_hash"] = new_hash
                db[url]["last_content"] = new_content
                save_db(db)
                result["changed"] = False
                result["note"] = f"Content changed but no keywords {keywords} found"
                return result

        # Generate diff and send email
        diff_text = get_diff(old_content, new_content)
        db[url]["last_hash"] = new_hash
        db[url]["last_content"] = new_content
        db[url]["last_changed"] = datetime.now().isoformat()
        db[url]["last_diff"] = diff_text

        subject = f"Transnet tender update detected: {url}"
        body = f"Change detected at {datetime.now().isoformat()}\nURL: {url}\n"
        if keywords:
            body += f"Keyword match: {keywords}\n"
        body += f"\n--- DIFF ---\n{diff_text[:3000]}" # Trim for email
        send_email(subject, body)

        result["diff"] = diff_text

    save_db(db)
    return result

def check_all_watched():
    """Job that runs every 8 hours"""
    print(f"[{datetime.now().isoformat()}] Running scheduled check...")
    db = load_db()
    for url in db.keys():
        check_single_url(url)

Schedule it: every 8 hours
scheduler.add_job(check_all_watched, 'interval', hours=8)

class WatchRequest(BaseModel):
    url: HttpUrl
    css_selector: str | None = None
    keywords: list[str] = [] # Only alert if these words appear

@app.post("/watch")
def watch_url(req: WatchRequest):
    db = load_db()
    url = str(req.url)
    try:
        content, current_hash = get_page_content(url, req.css_selector)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    db[url] = {
        "last_hash": current_hash,
        "last_content": content,
        "css_selector": req.css_selector,
        "keywords": req.keywords,
        "last_checked": datetime.now().isoformat(),
        "last_changed": datetime.now().isoformat(),
        "last_diff": ""
    }
    save_db(db)
    return {"status": "watching", "url": url, "keywords": req.keywords}

@app.get("/check/{url:path}")
def check_url(url: HttpUrl):
    return check_single_url(str(url))

@app.get("/check-all")
def check_all():
    db = load_db()
    results = [check_single_url(url) for url in db.keys()]
    return {"results": results}

@app.get("/watched")
def list_watched():
    return load_db()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
*4. Run it*
uvicorn main:app --reload
*5. Start watching Transnet for Durban tenders*
curl -X POST "http://localhost:8000/watch" \
-H "Content-Type: application/json" \
-d '{
  "url": "https://www.transnet.net/SubsiteRender.aspx?id=8185344",
  "keywords": ["Durban", "KZN", "Port Terminals"]
}'
*How it works now:*
1. *Every 8 hours*: APScheduler auto-runs `check_all_watched` in background
2. *Email*: If page changes AND contains "Durban", "KZN", or "Port Terminals", you get an email
3. *Durban filter*: Ignores changes unless your keywords are in the new content
4. *Diff*: Email body + `/check` response includes a unified diff showing +/- lines

*Test it immediately*: `curl http://localhost:8000/check-all`

Transnet’s site is heavy and that URL covers all divisions. If you want less noise, we should find the exact CSS selector for just the tender table. Want me to help you grab that?

Also — Transnet is moving to a new eSupplier Portal. Want me to add that URL to the watch list too?
