from fastapi import FastAPI, Depends, status
import secrets
import string
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Link
from sqlalchemy.exc import IntegrityError

app = FastAPI()

@app.get('/')
def home():
    return "Welcome to URL Shortner"

BASE_62 = string.ascii_letters + string.digits
BASE_LENGTH = 6

def generate_slug(db: Session):
    while True:
        slug = ''.join(secrets.choice(BASE_62) for _ in range(BASE_LENGTH))
        if db.query(Link).filter(Link.slug == slug).first() is None:
            return slug

class ShortenURLRequest(BaseModel):
    url : str

class ShortenURLResponse(BaseModel):
    slug : str
    short_url : str

@app.post('/shorten', response_model=ShortenURLResponse)
def create_short_url(request: ShortenURLRequest, db: Session = Depends(get_db)):
    MAX_RETRIES = 3

    for attempt in range(MAX_RETRIES):
        slug = generate_slug(db)

        new_link = Link(
            slug=slug,
            original_url=request.url
        )
        db.add(new_link)

        try:
            db.commit()
            db.refresh(new_link)
            break
        except IntegrityError:
            db.rollback()
    else:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Failed to generate unique slug, Try again"
        )

    return ShortenURLResponse(
        slug = slug,
        short_url = f"http://127.0.0.1:8000/{slug}"
    )

@app.get('/{slug}')
def redirect_url(slug: str, db:Session = Depends(get_db)):
    link = db.query(Link).filter(Link.slug == slug).first()
    if link is None:
        raise HTTPException(status_code=404, detail="URL Not Found")
    
    return RedirectResponse(
        url = link.original_url,
        status_code = status.HTTP_302_FOUND
    )