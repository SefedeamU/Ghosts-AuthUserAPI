# Ghosts Auth Microservice - Guía de despliegue y mantenimiento

Esta guía te permitirá levantar y mantener este microservicio de autenticación y usuarios, incluso si nunca has usado FastAPI, Docker o Alembic.

---

## 1. Configuración del archivo `.env`

Crea un archivo llamado `.env` en la raíz del proyecto (junto a `docker-compose.yml`) con el siguiente contenido:

```
DATABASE_USER=usuario
DATABASE_PASSWORD=contraseña
DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_NAME=nombre_basedatos
SECRET_KEY=12345
ALLOWED_COUNTRIES=USA,Mexico,Canada,Spain,France
MAX_ADDRESSES_PER_USER=5
```

- **Nota:** No dejes espacios antes o después del `=`.
- **DATABASE_HOST** debe ser `db` (el nombre del servicio de base de datos en Docker Compose).

---

## 2. Levantar los servicios con Docker Compose

Desde la raíz del proyecto, ejecuta:

```
docker-compose up -d
```

Esto descargará las imágenes necesarias y levantará tanto la API como la base de datos PostgreSQL.

---

## 3. Preparar la base de datos con Alembic (solo la primera vez)

### a) Entra al contenedor de la API

```
docker-compose exec auth-api bash
```
(o usa `sh` si bash no está disponible)

```
docker-compose exec auth-api sh
```

### b) Genera la migración inicial

```
alembic revision --autogenerate -m "create initial tables"
```

### c) Aplica la migración

```
alembic upgrade head
```

Esto creará todas las tablas necesarias en la base de datos según los modelos definidos en el código.

---

## 4. Mantener la base de datos actualizada (cada vez que cambies los modelos)

Cada vez que modifiques los modelos SQLAlchemy (por ejemplo, agregues o elimines campos/tablas):

### a) Genera una nueva migración

```
docker-compose exec auth-api alembic revision --autogenerate -m "describe your change"
```

### b) Aplica la migración

```
docker-compose exec auth-api alembic upgrade head
```

---

## 5. Acceder a la documentación interactiva de la API

Una vez que el servicio esté corriendo, abre tu navegador y visita:

- [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)

Aquí podrás probar todos los endpoints y ver la documentación generada automáticamente.

---

## 6. Comandos útiles

- **Ver logs de los servicios:**
  ```
  docker-compose logs -f
  ```
- **Reiniciar los servicios:**
  ```
  docker-compose restart
  ```
- **Detener los servicios:**
  ```
  docker-compose down
  ```

---

## 7. Notas adicionales

- **No uses `localhost` como host de la base de datos en el `.env`, usa siempre `db` para que los contenedores se comuniquen correctamente.**
- **No es necesario crear tablas manualmente en la base de datos, Alembic se encarga de esto.**
- **Para producción, asegúrate de proteger tu archivo `.env` y cambiar las contraseñas por valores seguros.**

---

¿Dudas o problemas?  
Consulta la documentación oficial de [FastAPI](https://fastapi.tiangolo.com/), [Docker Compose](https://docs.docker.com/compose/), [Alembic](https://alembic.sqlalchemy.org/) o contacta al responsable del proyecto.