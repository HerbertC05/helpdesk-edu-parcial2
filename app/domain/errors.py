"""Jerarquía de excepciones del dominio HelpDesk EDU."""

from __future__ import annotations


class DomainError(Exception):
    """Excepción base de la que heredan todos los errores de dominio."""


class NotFoundError(DomainError):
    """Se lanza cuando una entidad requerida no existe."""


class TicketNotFoundError(NotFoundError):
    def __init__(self, ticket_id: int) -> None:
        super().__init__(f"Ticket {ticket_id} no existe")
        self.ticket_id = ticket_id


class UserNotFoundError(NotFoundError):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"Usuario {user_id} no existe")
        self.user_id = user_id


class ValidationError(DomainError):
    """Se lanza cuando un dato de entrada viola una regla del dominio."""


class DuplicateAssignmentError(DomainError):
    """Se lanza al intentar asignar un ticket al técnico que ya lo tiene.

    Ejercicio 3 (Serie II): debe lanzarse ANTES de modificar el historial
    o de emitir notificaciones, dejando el ticket sin cambios.
    """

    def __init__(self, ticket_id: int, technician_id: int) -> None:
        super().__init__(
            f"El ticket {ticket_id} ya está asignado al técnico {technician_id}"
        )
        self.ticket_id = ticket_id
        self.technician_id = technician_id
