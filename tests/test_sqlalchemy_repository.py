from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.models.entities import Ticket, TicketStatus
from app.repositories.sqlalchemy import Base, SqlAlchemyTicketRepository


def make_ticket(title: str, status: TicketStatus, requester_id: int = 1) -> Ticket:
    return Ticket(
        id=0,
        title=title,
        description="",
        requester_id=requester_id,
        status=status,
    )


@pytest.fixture
def engine():
    """SQLite en memoria + StaticPool: todas las sesiones comparten la
    misma conexión física, por lo que ven las mismas tablas creadas."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


def test_count_by_status_con_tres_tickets_en_dos_estados(engine):
    # Preparación de datos a través del repositorio (sin transiciones
    # prohibidas ni SQL manual): dos tickets 'open', uno 'assigned'.
    with Session(engine) as session:
        repo = SqlAlchemyTicketRepository(session)
        repo.add(make_ticket("Impresora no enciende", TicketStatus.OPEN))
        repo.add(make_ticket("Sin internet", TicketStatus.OPEN))
        repo.add(make_ticket("Monitor dañado", TicketStatus.ASSIGNED))
        session.commit()  # confirma la transacción
    # La sesión anterior se cierra aquí (fin del bloque `with`).

    # Sesión NUEVA e independiente sobre el mismo engine/conexión.
    with Session(engine) as fresh_session:
        fresh_repo = SqlAlchemyTicketRepository(fresh_session)
        counts = fresh_repo.count_by_status()

    assert counts == {"open": 2, "assigned": 1}
    assert sum(counts.values()) == 3


def test_count_by_status_devuelve_vacio_sin_tickets(engine):
    with Session(engine) as session:
        repo = SqlAlchemyTicketRepository(session)
        counts = repo.count_by_status()

    assert counts == {}


def test_count_by_status_solo_incluye_estados_presentes(engine):
    # Solo se crean tickets 'open': 'assigned' y 'closed' no deben
    # aparecer en el diccionario (no se devuelven estados con conteo cero).
    with Session(engine) as session:
        repo = SqlAlchemyTicketRepository(session)
        repo.add(make_ticket("Teclado dañado", TicketStatus.OPEN))
        session.commit()

    with Session(engine) as fresh_session:
        counts = SqlAlchemyTicketRepository(fresh_session).count_by_status()

    assert counts == {"open": 1}
    assert "assigned" not in counts
    assert "closed" not in counts


def test_count_by_status_usa_una_base_de_prueba_independiente():
    """Un segundo engine, completamente separado del de las otras pruebas,
    para comprobar que el resultado no se contamina entre pruebas."""
    other_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(other_engine)

    with Session(other_engine) as session:
        repo = SqlAlchemyTicketRepository(session)
        repo.add(make_ticket("Ticket aislado", TicketStatus.CLOSED))
        session.commit()

    with Session(other_engine) as fresh_session:
        counts = SqlAlchemyTicketRepository(fresh_session).count_by_status()

    assert counts == {"closed": 1}
