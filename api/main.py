from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, database, auth
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import datetime

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- Gestión de Usuarios ---
@app.post("/usuarios/", response_model=schemas.UsuarioMostrar, tags=["usuarios"])
def crear_nuevo_usuario(usuario: schemas.UsuarioCrear, db: Session = Depends(database.obtener_db)):
    db_usuario = auth.obtener_usuario(db, email=usuario.email)
    if db_usuario:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return auth.crear_usuario(db=db, usuario=usuario)

@app.get("/usuarios/me/", response_model=schemas.UsuarioMostrar, tags=["usuarios"])
async def obtener_usuario_actual(usuario: models.Usuario = Depends(auth.obtener_usuario_actual)):
    return usuario

@app.post("/token", response_model=schemas.Token, tags=["usuarios"])
async def iniciar_sesion(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.obtener_db)):
    usuario = auth.obtener_usuario(db, email=form_data.username)
    if not usuario or not auth.verificar_clave(form_data.password, usuario.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    access_token = auth.crear_token_acceso(data={"sub": usuario.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Búsqueda de Vuelos ---
@app.get("/vuelos/", response_model=List[schemas.VueloMostrar], tags=["vuelos"])
def buscar_vuelos(fecha: datetime = None, origen: str = None, destino: str = None, db: Session = Depends(database.obtener_db)):
    query = db.query(models.Vuelo)
    if fecha:
        query = query.filter(models.Vuelo.fecha == fecha)
    if origen:
        query = query.filter(models.Vuelo.origen == origen)
    if destino:
        query = query.filter(models.Vuelo.destino == destino)
    return query.all()

@app.post("/vuelos/", response_model=schemas.VueloMostrar, tags=["vuelos"])
def crear_vuelo(vuelo: schemas.VueloCrear, db: Session = Depends(database.obtener_db)):
    db_vuelo = models.Vuelo(**vuelo.model_dump())
    db.add(db_vuelo)
    db.commit()
    db.refresh(db_vuelo)
    return db_vuelo

@app.get("/vuelos/{vuelo_id}", response_model=schemas.VueloMostrar, tags=["vuelos"])
def obtener_vuelo(vuelo_id: int, db: Session = Depends(database.obtener_db)):
    db_vuelo = db.query(models.Vuelo).filter(models.Vuelo.id == vuelo_id).first()
    if db_vuelo is None:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return db_vuelo

# --- Gestión de Reservas ---
@app.post("/reservas/", response_model=schemas.ReservaMostrar, tags=["reservas"])
def reservar_vuelo(reserva: schemas.ReservaBase, usuario: models.Usuario = Depends(auth.obtener_usuario_actual), db: Session = Depends(database.obtener_db)):
    db_vuelo = db.query(models.Vuelo).filter(models.Vuelo.id == reserva.vuelo_id).first()
    if not db_vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    db_reserva = models.Reserva(usuario_id=usuario.id, vuelo_id=reserva.vuelo_id)
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@app.get("/reservas/", response_model=List[schemas.ReservaMostrar], tags=["reservas"])
def consultar_reservas(usuario: models.Usuario = Depends(auth.obtener_usuario_actual), db: Session = Depends(database.obtener_db)):
    return db.query(models.Reserva).filter(models.Reserva.usuario_id == usuario.id).all()

@app.delete("/reservas/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["reservas"])
def cancelar_reserva(reserva_id: int, usuario: models.Usuario = Depends(auth.obtener_usuario_actual), db: Session = Depends(database.obtener_db)):
    db_reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id, models.Reserva.usuario_id == usuario.id).first()
    if not db_reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada o no pertenece al usuario")
    db.delete(db_reserva)
    db.commit()
    return {"mensaje": "Reserva cancelada"}