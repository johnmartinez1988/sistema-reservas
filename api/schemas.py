from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UsuarioBase(BaseModel):
    email: str

class UsuarioCrear(UsuarioBase):
    password: str

class UsuarioMostrar(UsuarioBase):
    id: int

    class ConfigDict:
        from_attributes = True

class VueloBase(BaseModel):
    origen: str
    destino: str
    fecha: datetime
    precio: int

class VueloCrear(VueloBase):
    pass

class VueloMostrar(VueloBase):
    id: int

    class ConfigDict:
        from_attributes = True

class ReservaBase(BaseModel):
    vuelo_id: int

class ReservaMostrar(ReservaBase):
    id: int
    usuario_id: int
    fecha_reserva: datetime

    class ConfigDict:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str