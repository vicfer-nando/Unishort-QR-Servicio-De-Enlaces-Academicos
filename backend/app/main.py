import os
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app import models, utils

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Unishort QR API",
    version="1.0.0",
    docs_url="/docs"
)

API_KEY_SECRET = os.getenv("API_KEY_SECRET", "unishort-secret-key-2026")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticacion requerida. Cabecera X-API-Key ausente."
        )
    if api_key != API_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. API Key invalida o sin permisos."
        )
    return api_key

class URLCreateRequest(BaseModel):
    url: HttpUrl

def get_url_model_info():
    """Detecta la clase del modelo y sus atributos de URL y short_code de forma dinámica"""
    model_cls = getattr(models, "ShortURL", getattr(models, "URLItem", getattr(models, "URL", None)))
    if not model_cls:
        for attr_name in dir(models):
            attr = getattr(models, attr_name)
            if isinstance(attr, type) and hasattr(attr, "__tablename__"):
                model_cls = attr
                break
    
    # Detectar el campo de la URL destino (target_url, original_url, o url)
    url_attr = "target_url"
    if not hasattr(model_cls, "target_url"):
        for candidate in ["original_url", "url", "full_url", "long_url"]:
            if hasattr(model_cls, candidate):
                url_attr = candidate
                break
                
    return model_cls, url_attr

@app.post("/shorten", status_code=status.HTTP_201_CREATED)
def create_short_url(
    payload: URLCreateRequest, 
    db: Session = Depends(get_db),
    auth: str = Depends(verify_api_key)
):
    target_url = str(payload.url)
    model_cls, url_attr = get_url_model_info()
    
    # Filtrar dinámicamente según la columna existente
    filter_kwargs = {url_attr: target_url}
    existing = db.query(model_cls).filter_by(**filter_kwargs).first()
    if existing:
        return {"short_code": existing.short_code, "short_url": f"/s/{existing.short_code}"}

    short_code = utils.generate_short_code()
    create_kwargs = {url_attr: target_url, "short_code": short_code}
    db_item = model_cls(**create_kwargs)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"short_code": db_item.short_code, "short_url": f"/s/{db_item.short_code}"}

@app.get("/s/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    model_cls, url_attr = get_url_model_info()
    item = db.query(model_cls).filter(model_cls.short_code == short_code).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Enlace corto no encontrado"
        )
    dest_url = getattr(item, url_attr)
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=dest_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)