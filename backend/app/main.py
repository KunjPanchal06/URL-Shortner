from fastapi import FastAPI
import secrets
import string
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from fastapi import HTTPException

app = FastAPI()

@app.get('/')
def home():
    return "Welcome to URL Shortner"

link_store = {}
BASE_62 = string.ascii_letters + string.digits
BASE_LENGTH = 6

def generate_slug():
    while True:
        slug = ''.join(secrets.choice(BASE_62) for _ in range(BASE_LENGTH))
        if slug not in link_store:
            return slug

class ShortenURLRequest(BaseModel):
    url : str

class ShortenURLResponse(BaseModel):
    slug : str
    short_url : str

@app.post('/shorten', response_model=ShortenURLResponse)
def create_short_url(request: ShortenURLRequest):
    slug = generate_slug()
    link_store[slug] = request.url
    return ShortenURLResponse(
        slug = slug,
        short_url = f"http://127.0.0.1:8000/{slug}"
    )

@app.get('/{slug}')
def redirect_url(slug: str):
    url = link_store.get(slug)
    if url is None:
        raise HTTPException(status_code=404, detail="URL Not Found")
    
    return RedirectResponse(
        url = url,
        status_code = 302
    )