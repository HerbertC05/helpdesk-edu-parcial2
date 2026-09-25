"""Implementaciones en memoria de los repositorios (útiles para pruebas)."""

from __future__ import annotations

from app.models.entities import Ticket, TicketStatus, User
from app.repositories.base import TicketRepository, UserRepository


class InMemoryTicketRepository(TicketRepository):
    def __init__(self) -> None:
        self._tickets: dict[int, Ticket] = {}
        self._counter = 0

    def next_id(self) -> int:
        self._counter += 1
        return self._counter

    def add(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket

    def by_id(self, ticket_id: int) -> Ticket | None:
        return self._tickets.get(ticket_id)

    def list(
        self,
        *,
        status: TicketStatus | None = None,
        assignee_id: int | None = None,
        requester_id: int | None = None,
    ) -> list[Ticket]:
        values = list(self._tickets.values())
        if status is not None:
            values = [t for t in values if t.status == status]
        if assignee_id is not None:
            values = [t for t in values if t.assignee_id == assignee_id]
        if requester_id is not None:
            values = [t for t in values if t.requester_id == requester_id]
        return values

    def update(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket


class InMemoryUserRepository(UserRepository):
    def __init__(self, users: list[User] | None = None) -> None:
        self._users: dict[int, User] = {u.id: u for u in (users or [])}
        self._counter = len(self._users)

    def next_id(self) -> int:
        self._counter += 1
        return self._counter

    def add(self, user: User) -> None:
        self._users[user.id] = user

    def by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)
