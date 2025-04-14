from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import database, models, schemas
from sqlalchemy.orm import Session
from .config import SECRET_KEY, ALGORITHM
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verificar_clave(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def obtener_clave_hash(password):
    return pwd_context.hash(password)

def crear_token_acceso(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def obtener_usuario(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def obtener_usuario_por_id(db: Session, usuario_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    hashed_password = obtener_clave_hash(usuario.password)
    db_usuario = models.Usuario(email=usuario.email, hashed_password=hashed_password)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

async def obtener_usuario_activo(db: Session = Depends(database.obtener_db), token: str = Depends(oauth2_scheme)):
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credenciales_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credenciales_exception
    usuario = obtener_usuario(db, email=token_data.email)
    if usuario is None:
        raise credenciales_exception
    return usuario

async def obtener_usuario_actual(usuario: models.Usuario = Depends(obtener_usuario_activo)):
    return usuario