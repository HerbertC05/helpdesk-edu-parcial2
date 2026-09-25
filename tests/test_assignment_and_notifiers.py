from __future__ import annotations

import pytest

from app.domain.errors import DuplicateAssignmentError
from app.services.notifications import WebhookNotifier
from app.services.tickets import TicketService


def test_reasignar_al_mismo_tecnico_lanza_duplicate_assignment_error(ticket_service):
    ticket = ticket_service.create(
        title="Teclado no funciona", description="", requester_id=1
    )
    ticket_service.assign(ticket.id, technician_id=2)

    with pytest.raises(DuplicateAssignmentError):
        ticket_service.assign(ticket.id, technician_id=2)


def test_reasignacion_duplicada_no_modifica_historial_ni_notifica(
    ticket_service, recording_notifier
):
    ticket = ticket_service.create(
        title="Mouse no funciona", description="", requester_id=1
    )
    ticket_service.assign(ticket.id, technician_id=2)

    historial_previo = list(ticket.history)
    notificaciones_previas = list(recording_notifier.notifications)

    with pytest.raises(DuplicateAssignmentError):
        ticket_service.assign(ticket.id, technician_id=2)

    assert ticket.history == historial_previo
    assert recording_notifier.notifications == notificaciones_previas


def test_webhook_notifier_inyectado_registra_payload_en_asignacion_valida(
    ticket_repo, users_service
):
    webhook = WebhookNotifier(url="https://hooks.example.com/tickets")
    service = TicketService(ticket_repo, users_service, notifier=webhook)

    ticket = service.create(
        title="Proyector no enciende", description="Sala 4", requester_id=1
    )
    service.assign(ticket.id, technician_id=3)

    assert len(webhook.sent_payloads) == 1
    payload = webhook.sent_payloads[0]
    assert payload["event"] == "ticket_assigned"
    assert payload["ticket_id"] == ticket.id
    assert payload["technician_id"] == 3
    assert payload["url"] == "https://hooks.example.com/tickets"


def test_webhook_notifier_no_usa_http_ni_impresion(capsys):
    webhook = WebhookNotifier()

    webhook.notify(event="ticket_assigned", ticket_id=1, technician_id=2)

    captured = capsys.readouterr()
    assert captured.out == ""  # no imprime nada en consola
    assert webhook.sent_payloads == [
        {
            "url": "https://example.com/webhook",
            "event": "ticket_assigned",
            "ticket_id": 1,
            "technician_id": 2,
        }
    ]


def test_ticket_service_no_conoce_el_tipo_concreto_del_notifier(
    ticket_repo, users_service
):
    """TicketService debe funcionar igual sin importar la implementación
    concreta de Notifier que se inyecte (inyección polimórfica, sin
    condicionales por tipo dentro de TicketService)."""
    webhook = WebhookNotifier()
    service = TicketService(ticket_repo, users_service, notifier=webhook)

    ticket = service.create(title="Sin audio", description="", requester_id=1)
    service.assign(ticket.id, technician_id=2)

    assert webhook.sent_payloads  # se notificó a través del contrato genérico
