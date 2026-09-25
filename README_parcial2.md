# Parcial 2 — HelpDesk EDU

Este repositorio contiene la Serie II (práctica) resuelta sobre una copia
propia del proyecto HelpDesk EDU trabajado en clase, conservando su
estructura por capas (dominio, modelos, repositorios, servicios).

## Estructura del repositorio

```
app/
  domain/
    errors.py          # Jerarquía de excepciones de dominio
  models/
    entities.py         # Role, TicketStatus, User, Comment, HistoryEvent, Ticket
  repositories/
    base.py              # TicketRepository / UserRepository (ABC)
    memory.py             # Implementaciones en memoria (usadas en pruebas)
  services/
    users.py              # UserService.require()
    notifications.py       # Notifier, ConsoleNotifier, RecordingNotifier, WebhookNotifier
    tickets.py              # TicketService: create, assign, watchers, add_tag
tests/
  conftest.py
  test_tags.py                        # Ejercicio 1
  test_watchers.py                     # Ejercicio 2
  test_assignment_and_notifiers.py      # Ejercicio 3
pyproject.toml
README_parcial2.md
```

## Flujo de ramas usado

```
main
 └── merge ← Feacture_etiquetasEcapsuladas
       └── commits: entidades + errores + tags
 └── merge ← Feacture_observadoresWatchers
       └── commits: TicketService.watchers()
 └── merge ← Feacture_excepcionesNotificador
       └── commits: DuplicateAssignmentError + WebhookNotifier
```

(Cada feature se desarrolló en su propia rama, con commits incrementales,
y se integró a `main` mediante *merge*, según lo solicitado en el
enunciado.)

## Archivos modificados/creados por ejercicio

### Ejercicio 1 — Etiquetas y encapsulamiento
- `app/models/entities.py`: se agregó `_tags` (`field(default_factory=list, init=False, repr=False)`),
  la propiedad de solo lectura `tags` (devuelve tupla, sin setter) y el
  método `add_tag(tag)` con normalización (`strip().lower()`), rechazo de
  valores vacíos (`ValidationError`) y deduplicación.
- `app/domain/errors.py`: uso de `ValidationError` ya existente.
- `tests/test_tags.py`: normalización, duplicados, rechazo de espacios en
  blanco, independencia entre dos tickets y rechazo de reasignación
  pública (`ticket.tags = [...]` → `AttributeError`).

### Ejercicio 2 — Observadores y relaciones entre objetos
- `app/services/tickets.py`: método `watchers(ticket_id) -> list[User]`,
  implementado únicamente con `self.require(ticket_id)` y
  `self._users.require(id)` (sin acceder a repositorios ajenos).
- `tests/test_watchers.py`: un observador sin técnico, dos observadores
  con técnico distinto, deduplicación cuando solicitante y técnico
  coinciden, y propagación de `TicketNotFoundError`.

### Ejercicio 3 — Excepciones y polimorfismo
- `app/domain/errors.py`: `DuplicateAssignmentError(DomainError)`.
- `app/services/tickets.py`: `assign()` valida y lanza
  `DuplicateAssignmentError` **antes** de tocar `history` o notificar.
- `app/services/notifications.py`: `WebhookNotifier` (implementa
  `Notifier`, guarda payloads en `self.sent_payloads`, sin HTTP ni
  impresión), inyectado por el parámetro `notifier` ya existente en
  `TicketService`.
- `tests/test_assignment_and_notifiers.py`: excepción al reasignar,
  ausencia de cambios en historial/notificaciones tras el error,
  asignación válida que notifica y verificación del payload registrado
  por `WebhookNotifier`.

### Ejercicio 4 — SQL e integridad referencial
- `docs/database/schema.sql`: esquema PostgreSQL (`users`, `tickets`,
  `comments`, `ticket_history`), con `ON DELETE CASCADE` en `comments.ticket_id`
  y `ticket_history.ticket_id` hacia `tickets(id)`.
- `docs/database/seed_data.sql`: datos de ejemplo (4 usuarios, 5 tickets,
  3 comentarios, 6 eventos de historial).
- `docs/database/queries_parcial2.sql`: las cuatro consultas pedidas
  (a) tickets abiertos + JOIN con el solicitante, (b) conteo por técnico
  con `HAVING`/`ORDER BY ... DESC`, (c) tickets sin comentarios con
  `NOT EXISTS` (se incluye también la variante `LEFT JOIN` comentada),
  (d) demostración de `ON DELETE CASCADE` sobre `ticket_history` dentro
  de `BEGIN`/`ROLLBACK`.
- `docs/database/queries_output.txt`: salida real capturada al ejecutar
  el archivo anterior contra una instancia de PostgreSQL 16.

### Ejercicio 5 — Consulta agregada y persistencia con SQLAlchemy
- `app/repositories/sqlalchemy.py`: modelos ORM (`UserORM`, `TicketORM`,
  `CommentORM`, `HistoryEventORM`) y `SqlAlchemyTicketRepository`, que
  implementa la interfaz abstracta `TicketRepository` sin modificarla, y
  agrega `count_by_status() -> dict[str, int]` mediante
  `select(TicketORM.status, func.count()).group_by(TicketORM.status)`.
- `tests/test_sqlalchemy_repository.py`: crea tres tickets (dos `open`,
  uno `assigned`) usando el repositorio, confirma la transacción
  (`session.commit()`), cierra esa sesión y vuelve a consultar
  `count_by_status()` desde una **sesión nueva** sobre el mismo engine
  SQLite en memoria con `StaticPool`. También cubre el caso de una base
  vacía (`{}`) y un caso con una base de prueba independiente.

## Cómo ejecutar las pruebas

```bash
uv run pytest -q
```

## Resultado de la ejecución (`uv run pytest -q`)

**Antes de implementar los ejercicios:** no aplica — los módulos
`app/domain/errors.py`, `app/models/entities.py`,
`app/services/tickets.py` y `app/services/notifications.py` se crearon
directamente con las tres funcionalidades ya incorporadas en este
repositorio nuevo; no hubo una versión previa sin ellas que ejecutar.

**Después de implementar los ejercicios:**

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: .venv
Downloading sqlalchemy (4.5MiB)
Installed 2 packages in 2ms
...................                                                      [100%]
19 passed in 0.87s
```

No se registraron fallos. Las 19 pruebas (6 del ejercicio 1, 4 del
ejercicio 2, 5 del ejercicio 3 y 4 del ejercicio 5) pasan correctamente.

## Ejercicio 4 — Ejecución y evidencia en PostgreSQL

Instrucciones reproducibles (usando psql; equivalente vía Docker con el
mapeo de puertos `5433:5432` visto en clase — ajustar host/puerto según
corresponda):

```bash
createdb -U <usuario> helpdesk_edu
psql -U <usuario> -d helpdesk_edu -f docs/database/schema.sql
psql -U <usuario> -d helpdesk_edu -f docs/database/seed_data.sql
psql -U <usuario> -d helpdesk_edu -f docs/database/queries_parcial2.sql
```

Salida real obtenida (PostgreSQL 16):

```
 id |         title         | status |  requester_name
----+-----------------------+--------+------------------
  4 | Actualizar antivirus  | open   | Dani Solicitante
  5 | Proyector no enciende | open   | Ana Solicitante
(2 rows)

 technician_id | technician_name | ticket_count
---------------+------------------+--------------
             2 | Beto Técnico     |            2
             3 | Carla Técnica    |            1
(2 rows)

 id |         title         |  status
----+-----------------------+----------
  2 | Sin internet en sala  | assigned
  4 | Actualizar antivirus  | open
  5 | Proyector no enciende | open
(3 rows)

BEGIN
 history_count_before
----------------------
                    2
(1 row)

DELETE 1
 history_count_after_delete
----------------------------
                          0
(1 row)

ROLLBACK
 history_count_after_rollback
------------------------------
                            2
(1 row)
```

**Verificación de integridad tras el ROLLBACK** (los datos permanecen
intactos: siguen los 5 tickets, 3 comentarios y 6 filas de historial
originales):

```
 tickets | comments | history
---------+----------+---------
       5 |        3 |       6
(1 row)
```

## Limitaciones

- El esquema de `docs/database/*.sql` y los modelos ORM de
  `app/repositories/sqlalchemy.py` se definieron desde cero para este
  parcial, replicando fielmente las entidades de dominio
  (`app/models/entities.py`) y las reglas de cascada vistas en clase;
  no se contó con el `database.sql` original del proyecto de clase para
  reutilizarlo literalmente.
- `SqlAlchemyTicketRepository.next_id()` devuelve un valor no
  significativo (0): en esta implementación el id real lo asigna la
  base de datos (columna autoincremental) dentro de `add()`, por lo que
  ningún llamador debe depender de `next_id()` para repositorios SQL.
- No se ejecutaron pruebas de integración de `SqlAlchemyTicketRepository`
  contra PostgreSQL real (solo SQLite en memoria, como permite el
  enunciado); el ejercicio 4 sí se validó contra PostgreSQL real.

## Notas

- Los repositorios en memoria (`app/repositories/memory.py`) se usan para
  las pruebas de los tres ejercicios de la Serie II, ya que ninguno de
  ellos requiere persistencia SQL (las etiquetas se mantienen en memoria
  y no se migran al esquema, tal como indica el enunciado del ejercicio 1).
- `TicketService` no contiene ningún condicional por tipo de `notifier`:
  tanto `RecordingNotifier` como `WebhookNotifier` cumplen el mismo
  contrato `Notifier.notify(...)`, demostrando la inyección polimórfica
  pedida en el ejercicio 3.
