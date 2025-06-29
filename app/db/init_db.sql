-- Tabla de usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    nickname VARCHAR,
    firstname VARCHAR NOT NULL,
    lastname VARCHAR NOT NULL,
    phone VARCHAR,
    is_active BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    user_rol VARCHAR,
    address VARCHAR,
    birthdate VARCHAR,
    gender VARCHAR,
    avatar_url VARCHAR,
    stripe_customer_id VARCHAR,
    google_id VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Tabla de direcciones (relación con usuarios)
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    street VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    state VARCHAR,
    zip_code VARCHAR,
    country VARCHAR,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de tokens de acción (verificación email, etc.)
CREATE TABLE action_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de tokens de restauración de contraseña
CREATE TABLE password_restore_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    old_hashed_password VARCHAR NOT NULL,
    token VARCHAR NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_addresses_user_id ON addresses(user_id);
CREATE INDEX idx_action_tokens_user_id ON action_tokens(user_id);
CREATE INDEX idx_action_tokens_token ON action_tokens(token);
CREATE INDEX idx_password_restore_tokens_user_id ON password_restore_tokens(user_id);
CREATE INDEX idx_password_restore_tokens_token ON password_restore_tokens(token);

-- Comentarios para documentación
COMMENT ON TABLE users IS 'Tabla principal de usuarios del sistema';
COMMENT ON TABLE addresses IS 'Direcciones de los usuarios (máximo 5 por usuario según configuración)';
COMMENT ON TABLE action_tokens IS 'Tokens para acciones como verificación de email';
COMMENT ON TABLE password_restore_tokens IS 'Tokens para restauración de contraseñas';
