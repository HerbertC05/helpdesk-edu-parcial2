-- Datos de ejemplo para docs/database/queries_parcial2.sql

INSERT INTO users (name, email, role) VALUES
    ('Ana Solicitante',   'ana@example.com',   'requester'),
    ('Beto Técnico',      'beto@example.com',  'technician'),
    ('Carla Técnica',     'carla@example.com', 'technician'),
    ('Dani Solicitante',  'dani@example.com',  'requester');
-- ids: 1 Ana, 2 Beto, 3 Carla, 4 Dani

INSERT INTO tickets (title, description, requester_id, assignee_id, status) VALUES
    ('Impresora no enciende',   'Piso 2',        1, 2, 'assigned'),  -- id 1
    ('Sin internet en sala',    'Sala de juntas', 1, 2, 'assigned'), -- id 2
    ('Monitor dañado',          'Piso 3',        4, 3, 'assigned'),  -- id 3
    ('Actualizar antivirus',    'Equipo de Dani', 4, NULL, 'open'),  -- id 4 (abierto, sin técnico)
    ('Proyector no enciende',   'Sala 4',        1, NULL, 'open');   -- id 5 (abierto, sin técnico)

INSERT INTO comments (ticket_id, author_id, body) VALUES
    (1, 2, 'Reviso hoy en la tarde'),
    (1, 1, 'Gracias, quedo pendiente'),
    (3, 3, 'Se solicitó repuesto');
-- Los tickets 2, 4 y 5 quedan intencionalmente SIN comentarios (para la consulta c).

INSERT INTO ticket_history (ticket_id, description) VALUES
    (1, 'Ticket creado'),
    (1, 'Asignado a Beto Técnico'),
    (2, 'Ticket creado'),
    (2, 'Asignado a Beto Técnico'),
    (3, 'Ticket creado'),
    (3, 'Asignado a Carla Técnica');
-- El ticket 1 tiene 2 filas de historial: se usa en la demostración de la parte (d).
