"""Servicio de aplicación para tickets."""

from __future__ import annotations

from app.domain.errors import DuplicateAssignmentError, TicketNotFoundError, ValidationError
from app.models.entities import HistoryEvent, Ticket, TicketStatus, User
from app.repositories.base import TicketRepository
from app.services.notifications import Notifier
from app.services.users import UserService


class TicketService:
    def __init__(
        self,
        repository: TicketRepository,
        users: UserService,
        notifier: Notifier | None = None,
    ) -> None:
        self._repository = repository
        self._users = users
        self._notifier = notifier

    # -- Consultas básicas -------------------------------------------------
    def require(self, ticket_id: int) -> Ticket:
        ticket = self._repository.by_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(ticket_id)
        return ticket

    def list(self, **filters) -> list[Ticket]:
        return self._repository.list(**filters)

    # -- Creación ------------------------------------------------------------
    def create(self, *, title: str, description: str, requester_id: int) -> Ticket:
        self._users.require(requester_id)
        if not title.strip():
            raise ValidationError("El título no puede estar vacío")

        ticket = Ticket(
            id=self._repository.next_id(),
            title=title.strip(),
            description=description.strip(),
            requester_id=requester_id,
        )
        self._repository.add(ticket)
        return ticket

    # -- Ejercicio 3: asignación con protección contra duplicados -----------
    def assign(self, ticket_id: int, technician_id: int) -> Ticket:
        ticket = self.require(ticket_id)
        technician = self._users.require(technician_id)

        # La validación ocurre ANTES de tocar historial o notificar.
        if ticket.assignee_id == technician_id:
            raise DuplicateAssignmentError(ticket_id, technician_id)

        ticket.assignee_id = technician_id
        ticket.status = TicketStatus.ASSIGNED
        ticket.history.append(
            HistoryEvent(
                id=len(ticket.history) + 1,
                ticket_id=ticket_id,
                description=f"Asignado a {technician.name}",
            )
        )
        self._repository.update(ticket)

        if self._notifier is not None:
            self._notifier.notify(
                event="ticket_assigned",
                ticket_id=ticket_id,
                technician_id=technician_id,
            )

        return ticket

    # -- Ejercicio 2: observadores -------------------------------------------
    def watchers(self, ticket_id: int) -> list[User]:
        """Devuelve el solicitante y, si existe, el técnico asignado.

        No repite usuarios con el mismo id (por ejemplo, si un técnico se
        asigna a sí mismo un ticket que él mismo solicitó). Se apoya
        únicamente en self.require() y self._users.require(): no accede
        directamente a repositorios de otros servicios.
        """
        ticket = self.require(ticket_id)

        watchers: list[User] = []
        seen_ids: set[int] = set()

        requester = self._users.require(ticket.requester_id)
        watchers.append(requester)
        seen_ids.add(requester.id)

        if ticket.assignee_id is not None:
            technician = self._users.require(ticket.assignee_id)
            if technician.id not in seen_ids:
                watchers.append(technician)
                seen_ids.add(technician.id)

        return watchers

    # -- Ejercicio 1: etiquetas -----------------------------------------------
    def add_tag(self, ticket_id: int, tag: str) -> Ticket:
        ticket = self.require(ticket_id)
        ticket.add_tag(tag)  # normalización/validación vive en la entidad
        self._repository.update(ticket)
        return ticket
