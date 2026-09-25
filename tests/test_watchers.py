from __future__ import annotations

import pytest

from app.domain.errors import TicketNotFoundError


def test_watchers_sin_tecnico_devuelve_solo_al_solicitante(ticket_service):
    ticket = ticket_service.create(
        title="No hay internet", description="Sala de juntas", requester_id=1
    )

    watchers = ticket_service.watchers(ticket.id)

    assert [w.id for w in watchers] == [1]


def test_watchers_con_tecnico_devuelve_ambos_sin_duplicar(ticket_service):
    ticket = ticket_service.create(
        title="Monitor dañado", description="Piso 3", requester_id=1
    )
    ticket_service.assign(ticket.id, technician_id=2)

    watchers = ticket_service.watchers(ticket.id)

    assert [w.id for w in watchers] == [1, 2]


def test_watchers_deduplica_cuando_solicitante_y_tecnico_coinciden(
    ticket_service, user_repo
):
    # Escenario controlado: el mismo usuario funge como solicitante y,
    # tras la asignación, como técnico de su propio ticket.
    ticket = ticket_service.create(
        title="Actualizar mi propio equipo", description="", requester_id=2
    )
    ticket_service.assign(ticket.id, technician_id=2)

    watchers = ticket_service.watchers(ticket.id)

    assert [w.id for w in watchers] == [2]
    assert len(watchers) == 1


def test_watchers_propaga_error_si_el_ticket_no_existe(ticket_service):
    with pytest.raises(TicketNotFoundError):
        ticket_service.watchers(999)
