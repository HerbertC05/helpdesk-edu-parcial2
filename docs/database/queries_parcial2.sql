-- Ejercicio 4 — SQL e integridad referencial
-- Ejecutar después de schema.sql y seed_data.sql sobre la base helpdesk_edu.

-- =====================================================================
-- (a) Tickets abiertos con el nombre del solicitante, mediante JOIN
-- =====================================================================
SELECT
    t.id,
    t.title,
    t.status,
    u.name AS requester_name
FROM tickets t
JOIN users u ON u.id = t.requester_id
WHERE t.status = 'open'
ORDER BY t.id;


-- =====================================================================
-- (b) Conteo de tickets por técnico asignado, agrupado por id y nombre,
--     con HAVING para excluir conteos cero y orden descendente
-- =====================================================================
SELECT
    u.id AS technician_id,
    u.name AS technician_name,
    COUNT(t.id) AS ticket_count
FROM users u
JOIN tickets t ON t.assignee_id = u.id
GROUP BY u.id, u.name
HAVING COUNT(t.id) > 0
ORDER BY ticket_count DESC;


-- =====================================================================
-- (c) Tickets sin comentarios, mediante NOT EXISTS
-- =====================================================================
SELECT
    t.id,
    t.title,
    t.status
FROM tickets t
WHERE NOT EXISTS (
    SELECT 1 FROM comments c WHERE c.ticket_id = t.id
)
ORDER BY t.id;

-- Equivalente con LEFT JOIN (misma salida, forma alternativa):
-- SELECT t.id, t.title, t.status
-- FROM tickets t
-- LEFT JOIN comments c ON c.ticket_id = t.id
-- WHERE c.id IS NULL
-- ORDER BY t.id;


-- =====================================================================
-- (d) Demostración de ON DELETE CASCADE sobre ticket_history,
--     dentro de BEGIN y ROLLBACK (los datos NO deben quedar afectados)
-- =====================================================================
BEGIN;

-- Conteo inicial: debe ser mayor que cero (el ticket 1 tiene 2 eventos).
SELECT COUNT(*) AS history_count_before FROM ticket_history WHERE ticket_id = 1;

-- Borrar el ticket 1 dispara ON DELETE CASCADE sobre ticket_history
-- (y también sobre comments, que referencia tickets con la misma cláusula).
DELETE FROM tickets WHERE id = 1;

-- Conteo tras el DELETE: debe ser cero, la cascada eliminó el historial.
SELECT COUNT(*) AS history_count_after_delete FROM ticket_history WHERE ticket_id = 1;

-- Se revierte la transacción: NINGÚN cambio debe persistir.
ROLLBACK;

-- Conteo tras el ROLLBACK: debe volver a ser igual al conteo inicial.
SELECT COUNT(*) AS history_count_after_rollback FROM ticket_history WHERE ticket_id = 1;
