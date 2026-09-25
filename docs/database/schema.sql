-- Esquema HelpDesk EDU para PostgreSQL
-- Corresponde a las entidades de app/models/entities.py

DROP TABLE IF EXISTS ticket_history CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(120) NOT NULL,
    email   VARCHAR(120) NOT NULL UNIQUE,
    role    VARCHAR(20)  NOT NULL CHECK (role IN ('requester', 'technician', 'admin'))
);

CREATE TABLE tickets (
    id            SERIAL PRIMARY KEY,
    title         VARCHAR(200) NOT NULL,
    description   TEXT NOT NULL DEFAULT '',
    requester_id  INTEGER NOT NULL REFERENCES users(id),
    assignee_id   INTEGER REFERENCES users(id),
    status        VARCHAR(20) NOT NULL DEFAULT 'open'
                  CHECK (status IN ('open', 'assigned', 'closed')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE comments (
    id          SERIAL PRIMARY KEY,
    ticket_id   INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    author_id   INTEGER NOT NULL REFERENCES users(id),
    body        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabla de historial real del esquema (equivalente a HistoryEvent)
CREATE TABLE ticket_history (
    id          SERIAL PRIMARY KEY,
    ticket_id   INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_comments_ticket_id ON comments(ticket_id);
CREATE INDEX idx_history_ticket_id ON ticket_history(ticket_id);
