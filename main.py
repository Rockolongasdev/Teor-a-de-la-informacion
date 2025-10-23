from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Sherlock Web API")

# CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LookupRequest(BaseModel):
    usernames: list[str]
    timeout: int = 10

class SiteResult(BaseModel):
    site: str
    url: str
    found: bool
    timestamp: str

@app.get("/")
def root():
    return {
        "service": "Sherlock Web API",
        "version": "1.0",
        "endpoints": ["/api/lookup", "/api/demo"]
    }

@app.post("/api/lookup")
async def lookup_usernames(request: LookupRequest):
    """
    Ejecuta Sherlock para buscar usernames en redes sociales.
    Uso educativo únicamente - respetar ToS de cada plataforma.
    """
    if not request.usernames or len(request.usernames) > 3:
        raise HTTPException(400, "Proporciona 1-3 usernames")
    
    results = []
    
    for username in request.usernames:
        # Validar username
        if not username or len(username) > 50:
            continue
            
        try:
            # Crear directorio temporal
            output_dir = Path("/tmp/sherlock")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"{username}.json"
            
            # Ejecutar Sherlock
            cmd = [
                "sherlock",
                username,
                "--json",
                str(output_file),
                "--timeout", str(request.timeout),
                "--print-found"
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Leer resultados
            if output_file.exists():
                with open(output_file, 'r') as f:
                    sherlock_data = json.load(f)
                
                # Normalizar formato
                timestamp = datetime.now().isoformat()
                
                for site, info in sherlock_data.items():
                    if isinstance(info, dict):
                        results.append({
                            "username": username,
                            "site": site,
                            "url": info.get("url_user", ""),
                            "found": info.get("status", {}).get("status") == "Claimed",
                            "timestamp": timestamp
                        })
                
                # Limpiar archivo temporal
                output_file.unlink()
            else:
                # Si no hay archivo, usar datos de muestra
                raise FileNotFoundError("No se generó output")
                
        except subprocess.TimeoutExpired:
            raise HTTPException(408, f"Timeout buscando {username}")
        except Exception as e:
            # En caso de error, devolver datos de demo
            return {"results": get_demo_data(username), "demo": True}
    
    return {"results": results, "demo": False}

@app.get("/api/demo")
def demo_data():
    """Devuelve datos de demostración para testing sin Sherlock"""
    return {"results": get_demo_data("johndoe"), "demo": True}

def get_demo_data(username: str):
    """Datos de muestra para cuando Sherlock no está disponible"""
    timestamp = datetime.now().isoformat()
    
    sites = [
        ("GitHub", f"https://github.com/{username}", True),
        ("Twitter", f"https://twitter.com/{username}", True),
        ("Instagram", f"https://instagram.com/{username}", False),
        ("Reddit", f"https://reddit.com/user/{username}", True),
        ("LinkedIn", f"https://linkedin.com/in/{username}", False),
        ("YouTube", f"https://youtube.com/@{username}", True),
        ("TikTok", f"https://tiktok.com/@{username}", False),
        ("Facebook", f"https://facebook.com/{username}", True),
    ]
    
    return [
        {
            "username": username,
            "site": site,
            "url": url,
            "found": found,
            "timestamp": timestamp
        }
        for site, url, found in sites
    ]

@app.get("/health")
def health():
    return {"status": "ok"}