from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    reservas = relationship("Reserva", back_populates="usuario")

class Vuelo(Base):
    __tablename__ = "vuelos"

    id = Column(Integer, primary_key=True, index=True)
    origen = Column(String)
    destino = Column(String)
    fecha = Column(DateTime)
    precio = Column(Integer)
    reservas = relationship("Reserva", back_populates="vuelo")

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    vuelo_id = Column(Integer, ForeignKey("vuelos.id"))
    fecha_reserva = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="reservas")
    vuelo = relationship("Vuelo", back_populates="reservas")