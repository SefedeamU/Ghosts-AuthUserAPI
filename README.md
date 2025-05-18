# Guía de despliegue y pruebas para Auth Microservice

## 📖 ¿Qué es este proyecto?

**Auth Microservice** es un microservicio de autenticación y gestión de usuarios desarrollado en Python con FastAPI. Forma parte de una arquitectura de microservicios y se encarga de todas las operaciones relacionadas con la autenticación y la seguridad de los usuarios.

### Funcionalidades principales

- **Registro de usuarios:** Permite crear nuevas cuentas de usuario con validación de datos.
- **Inicio de sesión:** Autenticación mediante email y contraseña, con generación de tokens JWT.
- **Verificación de email:** Envío de correos de verificación y endpoints para confirmar la cuenta.
- **Recuperación y cambio de contraseña:** Solicitud y confirmación de restablecimiento de contraseña mediante tokens seguros.
- **Gestión de sesiones:** Validación y verificación de tokens JWT para proteger rutas privadas.
- **Deshacer cambio de contraseña:** Permite revertir un cambio de contraseña reciente si fue realizado por error o sin autorización.
- **Endpoints seguros y documentación automática:** Todos los endpoints están documentados y protegidos según las mejores prácticas de seguridad.

---

## 🐍 Entorno virtual Python (opcional)

Si deseas trabajar o probar el microservicio localmente (sin Docker), puedes crear y activar un entorno virtual de Python:

### 1. Crear el entorno virtual

Desde la raíz del proyecto, ejecuta:

```sh
python -m venv .venv
```

### 2. Activar el entorno virtual

- **En Windows:**
  ```sh
  .venv\Scripts\activate
  ```
- **En Linux/Mac:**
  ```sh
  source .venv/bin/activate
  ```

### 3. Instalar dependencias

```sh
pip install -r requirements.txt
```

### 4. Salir del entorno virtual

```sh
deactivate
```

---

## 🚀 Despliegue de la API con Docker Compose

### 1. Requisitos previos

- Tener Docker y Docker Compose.
- Tener el archivo `.env` configurado correctamente en la raíz del microservicio (Estas serán las credenciales con las que los contenedores de bases de datos de prueba se configuren).

### 2. Levantar la API y la base de datos

Desde la raíz del proyecto, ejecuta:
```sh
docker network create ghosts-network
```

```sh
docker compose up --build -d
```

Esto hará lo siguiente:
- Creará la red de docker por la cual se comunicarán los contenedores.
- Construirá la imagen de la API y levantará el contenedor `ghosts-auth-api`.
- Levantará el contenedor de base de datos `ghosts-auth-db`.
- Expondrá la API en el puerto `8000` de tu máquina local.

### 3. Acceder a la documentación automática (Swagger UI)

Una vez que los contenedores estén corriendo, abre tu navegador y visita:

```
http://localhost:8000/docs
```

Aquí podrás consultar y probar todos los endpoints de la API de forma interactiva gracias a Swagger UI.

---

## 🧪 Ejecución de pruebas automáticas

### 1. Levantar el entorno de pruebas

El entorno de pruebas utiliza un archivo de configuración especial: `docker-compose.test.yml`, asegúrate de configurar las variables del entorno de pruebas dentro de este archivo.

Para ejecutar los tests, corre:

```sh
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

Esto hará lo siguiente:
- Levantará una base de datos de pruebas (`ghosts-auth-db-test`).
- Construirá y ejecutará el contenedor de pruebas (`ghosts-auth-api-test`), que correrá automáticamente todos los tests con `pytest`.
- Al finalizar los tests, los contenedores se detendrán automáticamente.

### 2. Limpiar los contenedores y volúmenes de pruebas

Después de ejecutar los tests, puedes limpiar los recursos con:

```sh
docker compose -f docker-compose.test.yml down -v
```

---

## 📚 Resumen rápido

- **Levantar API y DB:**  
  `docker compose up --build`
- **Swagger UI:**  
  [http://localhost:8000/docs](http://localhost:8000/docs)
- **Ejecutar tests:**  
  `docker compose -f docker-compose.test.yml up --build --abort-on-container-exit`
- **Limpiar entorno de pruebas:**  
  `docker compose -f docker-compose.test.yml down -v`

---

¿Dudas o problemas? Consulta los logs de los contenedores con:

```sh
docker compose logs
```

---