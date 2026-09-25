from __future__ import annotations

import pytest

from app.domain.errors import ValidationError
from app.models.entities import Ticket


def make_ticket(ticket_id: int = 1) -> Ticket:
    return Ticket(
        id=ticket_id,
        title="Impresora no enciende",
        description="La impresora del piso 2 no responde",
        requester_id=1,
    )


def test_add_tag_normaliza_strip_y_lower():
    ticket = make_ticket()

    ticket.add_tag("  Urgente  ")
    ticket.add_tag("HARDWARE")

    assert ticket.tags == ("urgente", "hardware")


def test_add_tag_evita_duplicados_tras_normalizar():
    ticket = make_ticket()

    ticket.add_tag("Urgente")
    ticket.add_tag("urgente")
    ticket.add_tag("  URGENTE ")

    assert ticket.tags == ("urgente",)


def test_add_tag_rechaza_valores_vacios_o_solo_espacios():
    ticket = make_ticket()

    with pytest.raises(ValidationError):
        ticket.add_tag("")

    with pytest.raises(ValidationError):
        ticket.add_tag("    ")

    # El rechazo no debe dejar residuos en la colección interna.
    assert ticket.tags == ()


def test_tags_son_independientes_entre_dos_tickets():
    ticket_a = make_ticket(ticket_id=1)
    ticket_b = make_ticket(ticket_id=2)

    ticket_a.add_tag("red")
    ticket_a.add_tag("urgente")
    ticket_b.add_tag("hardware")

    assert ticket_a.tags == ("red", "urgente")
    assert ticket_b.tags == ("hardware",)


def test_tags_devuelve_tupla_inmutable():
    ticket = make_ticket()
    ticket.add_tag("red")

    assert isinstance(ticket.tags, tuple)


def test_reasignar_tags_publicamente_falla():
    ticket = make_ticket()

    with pytest.raises(AttributeError):
        ticket.tags = ["hack"]  # type: ignore[misc]
