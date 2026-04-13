from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import difflib
import logging

app = FastAPI()
DB_FILE = "watched_pages.json"
LOG_FILE = "monitor.log"
scheduler = BackgroundScheduler()
scheduler.start()

# Set up logging to file
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Also log to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)


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
    resp = requests.get(url, headers=headers, timeout=15, verify=False)
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

    changed = new_hash != old_hash
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

        # Generate diff
        diff_text = get_diff(old_content, new_content)
        db[url]["last_hash"] = new_hash
        db[url]["last_content"] = new_content
        db[url]["last_changed"] = datetime.now().isoformat()
        db[url]["last_diff"] = diff_text

        logger.info(f"[CHANGE DETECTED] {datetime.now().isoformat()}")
        logger.info(f"URL: {url}")
        if keywords:
            logger.info(f"Keyword match: {keywords}")
        logger.info(f"--- DIFF ---\n{diff_text[:3000]}")

        result["diff"] = diff_text

    save_db(db)
    return result


def check_all_watched():
    """Job that runs every 8 hours"""
    logger.info(f"Running scheduled check...")
    db = load_db()
    for url in db.keys():
        result = check_single_url(url)
        if result.get("changed"):
            logger.info(f"  -> Changes detected for {url}")
        elif result.get("error"):
            logger.warning(f"  -> Error checking {url}: {result['error']}")
        else:
            logger.info(f"  -> No changes for {url}")


# Schedule it: every 8 hours
scheduler.add_job(check_all_watched, 'interval', hours=1)


class WatchRequest(BaseModel):
    url: HttpUrl
    css_selector: str | None = None
    keywords: list[str] = []


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


@app.get("/logs")
def get_logs(lines: int = 50):
    """Get the last N lines from the log file"""
    if not os.path.exists(LOG_FILE):
        return {"logs": []}
    
    with open(LOG_FILE, 'r') as f:
        all_lines = f.readlines()
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
    
    return {"logs": [line.strip() for line in recent_lines]}


@app.get("/export-watched-to-log")
def export_watched_to_log():
    """Export current watched URLs to the log file"""
    db = load_db()
    logger.info("=== EXPORTED WATCHED URLS ===")
    for url, data in db.items():
        logger.info(f"Watched URL: {url}")
        logger.info(f"  Keywords: {data.get('keywords', [])}")
        logger.info(f"  Last checked: {data.get('last_checked', 'Never')}")
        logger.info(f"  Last changed: {data.get('last_changed', 'Never')}")
        if data.get('last_diff'):
            logger.info(f"  Last diff: {data['last_diff'][:500]}...")
        logger.info("---")
    return {"status": "exported", "urls": list(db.keys())}


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()