# Sistema de Gestión de Reservas de Aerolínea

## Descripción del Proyecto

Este es un sistema de gestión de reservas para una aerolínea que permite a los usuarios:

1.  **Buscar Vuelos:** Buscar vuelos por fecha, origen y destino.
2.  **Reservar un Vuelo:** Reservar un vuelo seleccionado.
3.  **Consultar Reservas:** Ver sus reservas actuales.
4.  **Cancelar Reservas:** Cancelar una reserva.

Este backend está implementado utilizando FastAPI, una base de datos SQLite, y gestiona la autenticación básica de usuarios con JWT.

## Requisitos Técnicos Cumplidos

* **API RESTful:** Implementada con FastAPI.
* **AutoDocumentación:** Disponible a través de Swagger UI en `/docs` y ReDoc en `/redoc`.
* **Base de Datos:** Se utiliza SQLite para almacenar la información.
* **Pruebas:** Se incluyen pruebas unitarias.
* **Gestión de Usuarios:** Implementación básica de creación de usuario, inicio de sesión (con JWT).
* **Docker:** El proyecto se puede ejecutar utilizando Docker.

## Instrucciones para la Instalación y Ejecución del Proyecto

### Requisitos Previos

* [Docker](https://www.docker.com/get-started) instalado en el sistema.

### Ejecución con Docker Compose

1.  Clonar este repositorio.
2.  Navegar al directorio raíz del proyecto (`sistema_reservas`).
3.  Ejecuta el siguiente comando para construir y levantar el contenedor:
    ```
    docker-compose up --build
    ```
### Si tiene problemas al ejecutar este comando, intenta con el siguiente:

    ```
    docker compose up --build
    ```

4.  La API estará disponible en `http://localhost:8000`.

### Acceder a la AutoDocumentación

* **Swagger UI:** Abrir navegador y ve a `http://localhost:8000/docs`.
* **ReDoc:** Abrir navegador y ve a `http://localhost:8000/redoc`.

### Ejecutar las Pruebas Unitarias (Dentro del Contenedor)

1.  Asegúrate de que el contenedor esté en ejecución (ver instrucciones arriba).
2.  Ejecuta el siguiente comando para acceder al shell del contenedor:
    ```
    docker-compose exec app bash
    ```
3.  Dentro del contenedor, navega al directorio `app`:
    ```
    cd app
    ```
4.  Ejecuta las pruebas utilizando `pytest`:
    ```
    python -m pytest ./tests
    ```

## Ejemplos de Uso de la API

Aquí algunos ejemplos de cómo interactuar con la API utilizando `curl` (se puede usar otras herramientas como Postman):

NOTA: Se debe reemplazar los campos que estén dentro de `<>` sin incluir dichos marcadores de posición. El `ACCESS_TOKEN` debe ser reemplazado por el token que se obtuvo al iniciar sesión, y el `ID_DEL_VUELO` y `ID_DE_LA_RESERVA` deben ser los IDs correspondientes en la base de datos. El token se incluye en la cabecera `Authorization`.

### Crear un Usuario

```
curl -X POST -H "Content-Type: application/json" -d '{"email": "nuevo_usuario@example.com", "password": "contraseña123"}' http://localhost:8000/usuarios/
```

### Iniciar sesion y obtener token de acceso

```
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "username=nuevo_usuario@example.com&password=contraseña123" http://localhost:8000/token
```
# Guardar el token de acceso que se devuelve en el json, se necesitara para autorizar las solicitudes. 

### Crear vuelos

```
curl -X POST -H "Content-Type: application/json" -d '{"origen": "Bogotá", "destino": "Medellín", "fecha": "2025-04-15T10:00:00", "precio": 100}' http://localhost:8000/vuelos/
```

### Reservar un vuelo (Se necesita un token de acceso)

```
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <ACCESS_TOKEN>" -d '{"vuelo_id": <ID_DEL_VUELO>}' http://localhost:8000/reservas/
```

### Consultar reservas (Se necesita un token de acceso)

```
curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://localhost:8000/reservas/
```

### Cancelar una reserva (Se necesita un token de acceso)

```
curl -X DELETE -H "Authorization: Bearer <ACCESS_TOKEN>" http://localhost:8000/reservas/<ID_DE_LA_RESERVA>
```


