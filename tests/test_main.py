from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api import database, models
from api.config import SECRET_KEY, ALGORITHM
from jose import jwt
from datetime import datetime, timedelta

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

def override_obtener_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[database.obtener_db] = override_obtener_db

client = TestClient(app)

def crear_token_prueba(email: str):
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def test_crear_usuario():
    response = client.post(
        "/usuarios/", json={"email": "test@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_iniciar_sesion():
    client.post(
        "/usuarios/", json={"email": "test_login@example.com", "password": "password"}
    )
    response = client.post(
        "/token", data={"username": "test_login@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_buscar_vuelos():
    fecha = datetime.now().isoformat()
    client.post("/vuelos/", json={"origen": "Bogotá", "destino": "Medellín", "fecha": fecha, "precio": 100})
    response = client.get(f"/vuelos/?origen=Bogotá&destino=Medellín")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_reservar_vuelo():
    client.post(
        "/usuarios/", json={"email": "test_reserva@example.com", "password": "password"}
    )
    token = client.post(
        "/token", data={"username": "test_reserva@example.com", "password": "password"}
    ).json()["access_token"]
    fecha = datetime.now().isoformat()
    vuelo_response = client.post("/vuelos/", json={"origen": "Cali", "destino": "Pereira", "fecha": fecha, "precio": 80})
    vuelo_id = vuelo_response.json()["id"]
    response = client.post(
        "/reservas/", json={"vuelo_id": vuelo_id}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["vuelo_id"] == vuelo_id

def test_consultar_reservas():
    client.post(
        "/usuarios/", json={"email": "test_consultar@example.com", "password": "password"}
    )
    token = client.post(
        "/token", data={"username": "test_consultar@example.com", "password": "password"}
    ).json()["access_token"]
    fecha = datetime.now().isoformat()
    vuelo1 = client.post("/vuelos/", json={"origen": "Barranquilla", "destino": "Cartagena", "fecha": fecha, "precio": 120}).json()["id"]
    client.post("/reservas/", json={"vuelo_id": vuelo1}, headers={"Authorization": f"Bearer {token}"})
    response = client.get("/reservas/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_cancelar_reserva():
    client.post(
        "/usuarios/", json={"email": "test_cancelar@example.com", "password": "password"}
    )
    token = client.post(
        "/token", data={"username": "test_cancelar@example.com", "password": "password"}
    ).json()["access_token"]
    fecha = datetime.now().isoformat()
    vuelo = client.post("/vuelos/", json={"origen": "Medellín", "destino": "Santa Marta", "fecha": fecha, "precio": 150}).json()["id"]
    reserva = client.post("/reservas/", json={"vuelo_id": vuelo}, headers={"Authorization": f"Bearer {token}"}).json()
    response = client.delete(f"/reservas/{reserva['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204