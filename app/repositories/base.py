"""Contrato abstracto para los repositorios de tickets."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.entities import Ticket, TicketStatus


class TicketRepository(ABC):
    @abstractmethod
    def add(self, ticket: Ticket) -> None: ...

    @abstractmethod
    def by_id(self, ticket_id: int) -> Ticket | None: ...

    @abstractmethod
    def list(
        self,
        *,
        status: TicketStatus | None = None,
        assignee_id: int | None = None,
        requester_id: int | None = None,
    ) -> list[Ticket]: ...

    @abstractmethod
    def next_id(self) -> int: ...

    @abstractmethod
    def update(self, ticket: Ticket) -> None: ...


class UserRepository(ABC):
    @abstractmethod
    def add(self, user) -> None: ...

    @abstractmethod
    def by_id(self, user_id: int): ...

    @abstractmethod
    def next_id(self) -> int: ...
