from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from pydantic import ValidationError

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="UniShort QR API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/shorten")
def shorten_url(request: Request, url_data: schemas.URLBase, db: Session = Depends(get_db)):
    try:
        original_url = str(url_data.url)
    except Exception:
        raise HTTPException(status_code=400, detail="URL invalida")

    existing = db.query(models.ShortURL).filter(models.ShortURL.original_url == original_url).first()
    if existing:
        short_url = f"http://{request.headers.get('host') or 'localhost:8000'}/s/{existing.short_code}"
        return {"short_code": existing.short_code, "short_url": short_url, "original_url": original_url}

    for _ in range(10):
        short_code = utils.generate_short_code(6)
        if not db.query(models.ShortURL).filter(models.ShortURL.short_code == short_code).first():
            break
    else:
        raise HTTPException(status_code=500, detail="No se pudo generar un codigo unico")

    db_url = models.ShortURL(short_code=short_code, original_url=original_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    host = request.headers.get('host') or 'localhost:8000'
    short_url = f"http://{host}/s/{short_code}"
    return {"short_code": short_code, "short_url": short_url, "original_url": original_url}


@app.get("/s/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    db_url = db.query(models.ShortURL).filter(models.ShortURL.short_code == short_code).first()
    if db_url is None:
        raise HTTPException(status_code=404, detail="Enlace corto no encontrado")
    return RedirectResponse(url=db_url.original_url)


@app.get("/")
def root():
    return {"message": "UniShort QR API", "docs": "/docs"}
