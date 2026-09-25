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
Installed 5 packages in 5ms
...............                                                          [100%]
15 passed in 0.03s
```

No se registraron fallos. Las 15 pruebas (6 del ejercicio 1, 4 del
ejercicio 2 y 5 del ejercicio 3) pasan correctamente.

## Notas

- Los repositorios en memoria (`app/repositories/memory.py`) se usan para
  las pruebas de los tres ejercicios de la Serie II, ya que ninguno de
  ellos requiere persistencia SQL (las etiquetas se mantienen en memoria
  y no se migran al esquema, tal como indica el enunciado del ejercicio 1).
- `TicketService` no contiene ningún condicional por tipo de `notifier`:
  tanto `RecordingNotifier` como `WebhookNotifier` cumplen el mismo
  contrato `Notifier.notify(...)`, demostrando la inyección polimórfica
  pedida en el ejercicio 3.
