from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Sherlock Web API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LookupRequest(BaseModel):
    usernames: list[str]

@app.get("/")
def root():
    return {"service": "Sherlock Web API", "version": "1.0"}

@app.post("/api/lookup")
async def lookup_usernames(request: LookupRequest):
    if not request.usernames or len(request.usernames) > 3:
        raise HTTPException(400, "Proporciona 1-3 usernames")
    
    results = []
    
    for username in request.usernames:
        timestamp = datetime.now().isoformat()
        
        # Datos de demostración realistas
        sites = [
            ("GitHub", f"https://github.com/{username}", True),
            ("Twitter/X", f"https://twitter.com/{username}", True),
            ("Instagram", f"https://instagram.com/{username}", True),
            ("Reddit", f"https://reddit.com/user/{username}", True),
            ("LinkedIn", f"https://linkedin.com/in/{username}", False),
            ("YouTube", f"https://youtube.com/@{username}", True),
            ("TikTok", f"https://tiktok.com/@{username}", False),
            ("Facebook", f"https://facebook.com/{username}", True),
            ("Telegram", f"https://t.me/{username}", True),
            ("Medium", f"https://medium.com/@{username}", False),
            ("Twitch", f"https://twitch.tv/{username}", True),
            ("Pinterest", f"https://pinterest.com/{username}", False),
            ("Tumblr", f"https://{username}.tumblr.com", True),
            ("Flickr", f"https://flickr.com/photos/{username}", False),
            ("SoundCloud", f"https://soundcloud.com/{username}", True),
            ("Spotify", f"https://open.spotify.com/user/{username}", False),
            ("DeviantArt", f"https://deviantart.com/{username}", True),
            ("Behance", f"https://behance.net/{username}", False),
            ("Dribbble", f"https://dribbble.com/{username}", False),
            ("Stack Overflow", f"https://stackoverflow.com/users/{username}", True),
        ]
        
        for site, url, found in sites:
            results.append({
                "username": username,
                "site": site,
                "url": url,
                "found": found,
                "timestamp": timestamp
            })
    
    return {"results": results, "demo": True}

@app.get("/api/demo")
def demo_data():
    return {"results": [], "demo": True}

@app.get("/health")
def health():
    return {"status": "ok"}