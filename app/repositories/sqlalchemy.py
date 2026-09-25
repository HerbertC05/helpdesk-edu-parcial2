"""Implementación de TicketRepository respaldada por SQLAlchemy.

No se modifica la interfaz abstracta TicketRepository (app/repositories/base.py):
count_by_status() es un método adicional, exclusivo de esta implementación
concreta, tal como pide el Ejercicio 5.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text, func, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
)

from app.models.entities import Ticket, TicketStatus
from app.repositories.base import TicketRepository


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20))


class TicketORM(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=TicketStatus.OPEN.value)

    comments: Mapped[list["CommentORM"]] = relationship(
        cascade="all, delete-orphan", back_populates="ticket"
    )
    history: Mapped[list["HistoryEventORM"]] = relationship(
        cascade="all, delete-orphan", back_populates="ticket"
    )


class CommentORM(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)

    ticket: Mapped["TicketORM"] = relationship(back_populates="comments")


class HistoryEventORM(Base):
    __tablename__ = "ticket_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(Text)

    ticket: Mapped["TicketORM"] = relationship(back_populates="history")


def _ticket_to_domain(row: TicketORM) -> Ticket:
    """Traduce una fila ORM a un Ticket de dominio (dataclass), evitando
    que las capas superiores dependan de detalles de SQLAlchemy."""
    return Ticket(
        id=row.id,
        title=row.title,
        description=row.description,
        requester_id=row.requester_id,
        status=TicketStatus(row.status),
        assignee_id=row.assignee_id,
    )


class SqlAlchemyTicketRepository(TicketRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def next_id(self) -> int:
        # El id real lo asigna la base de datos (autoincremental) en add();
        # este valor solo se usa cuando algún llamador lo requiere antes
        # de persistir el ticket.
        return 0

    def add(self, ticket: Ticket) -> None:
        row = TicketORM(
            title=ticket.title,
            description=ticket.description,
            requester_id=ticket.requester_id,
            assignee_id=ticket.assignee_id,
            status=ticket.status.value,
        )
        self._session.add(row)
        self._session.flush()  # asigna row.id sin cerrar la transacción
        ticket.id = row.id

    def by_id(self, ticket_id: int) -> Ticket | None:
        row = self._session.get(TicketORM, ticket_id)
        return _ticket_to_domain(row) if row is not None else None

    def list(
        self,
        *,
        status: TicketStatus | None = None,
        assignee_id: int | None = None,
        requester_id: int | None = None,
    ) -> list[Ticket]:
        stmt = select(TicketORM)
        if status is not None:
            stmt = stmt.where(TicketORM.status == status.value)
        if assignee_id is not None:
            stmt = stmt.where(TicketORM.assignee_id == assignee_id)
        if requester_id is not None:
            stmt = stmt.where(TicketORM.requester_id == requester_id)
        rows = self._session.scalars(stmt).all()
        return [_ticket_to_domain(row) for row in rows]

    def update(self, ticket: Ticket) -> None:
        row = self._session.get(TicketORM, ticket.id)
        if row is None:
            raise ValueError(f"Ticket {ticket.id} no existe")
        row.title = ticket.title
        row.description = ticket.description
        row.assignee_id = ticket.assignee_id
        row.status = ticket.status.value
        self._session.flush()

    # -- Ejercicio 5: consulta agregada -----------------------------------
    def count_by_status(self) -> dict[str, int]:
        """Conteo de tickets agrupado por status.

        Usa select(TicketORM.status, func.count()).group_by(TicketORM.status);
        devuelve solo los estados realmente presentes en la tabla, y {}
        si no hay tickets.
        """
        stmt = (
            select(TicketORM.status, func.count())
            .select_from(TicketORM)
            .group_by(TicketORM.status)
        )
        rows = self._session.execute(stmt).all()
        return {status: count for status, count in rows}
