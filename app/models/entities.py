"""Entidades del dominio HelpDesk EDU."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.domain.errors import ValidationError


class Role(StrEnum):
    REQUESTER = "requester"
    TECHNICIAN = "technician"
    ADMIN = "admin"


class TicketStatus(StrEnum):
    OPEN = "open"
    ASSIGNED = "assigned"
    CLOSED = "closed"


@dataclass
class User:
    id: int
    name: str
    email: str
    role: Role


@dataclass
class Comment:
    id: int
    ticket_id: int
    author_id: int
    body: str
    created_at: datetime = field(default_factory=lambda: datetime.now().astimezone())


@dataclass
class HistoryEvent:
    id: int
    ticket_id: int
    description: str
    created_at: datetime = field(default_factory=lambda: datetime.now().astimezone())


@dataclass
class Ticket:
    id: int
    title: str
    description: str
    requester_id: int
    status: TicketStatus = TicketStatus.OPEN
    assignee_id: int | None = None
    comments: list[Comment] = field(default_factory=list)
    history: list[HistoryEvent] = field(default_factory=list)

    # --- Ejercicio 1: Etiquetas y encapsulamiento -----------------------
    # Colección interna, no forma parte del constructor (init=False) y no
    # se muestra en repr(). Cada instancia obtiene su propia lista gracias
    # a default_factory=list.
    _tags: list[str] = field(default_factory=list, init=False, repr=False)

    @property
    def tags(self) -> tuple[str, ...]:
        """Vista de solo lectura de las etiquetas del ticket.

        Se expone como tupla (inmutable) y sin `@tags.setter`, por lo que
        `ticket.tags = [...]` lanza AttributeError: no hay forma de
        reasignar la colección desde fuera de la clase.
        """
        return tuple(self._tags)

    def add_tag(self, tag: str) -> None:
        """Agrega una etiqueta normalizada, validada y sin duplicados.

        - Normaliza con strip().lower().
        - Rechaza valores vacíos (o solo espacios) con ValidationError.
        - Ignora silenciosamente los duplicados (idempotente).
        """
        normalized = tag.strip().lower()
        if not normalized:
            raise ValidationError("La etiqueta no puede estar vacía")
        if normalized in self._tags:
            return
        self._tags.append(normalized)
