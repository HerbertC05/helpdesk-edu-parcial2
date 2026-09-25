"""Contrato de notificaciones e implementaciones intercambiables."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Notifier(ABC):
    """Contrato polimórfico usado por TicketService (parámetro `notifier`).

    TicketService NUNCA debe preguntar de qué tipo concreto es el notifier
    (nada de `isinstance` ni condicionales por tipo): solo invoca notify().
    """

    @abstractmethod
    def notify(self, *, event: str, ticket_id: int, **payload: Any) -> None: ...


class ConsoleNotifier(Notifier):
    """Implementación "real" que imprime en consola."""

    def notify(self, *, event: str, ticket_id: int, **payload: Any) -> None:
        print(f"[{event}] ticket={ticket_id} {payload}")


class RecordingNotifier(Notifier):
    """Test double: registra las notificaciones en memoria para poder
    verificarlas en las pruebas sin depender de la salida de consola."""

    def __init__(self) -> None:
        self.notifications: list[dict[str, Any]] = []

    def notify(self, *, event: str, ticket_id: int, **payload: Any) -> None:
        self.notifications.append({"event": event, "ticket_id": ticket_id, **payload})


class WebhookNotifier(Notifier):
    """Ejercicio 3: implementación del contrato Notifier que simula el
    envío a un webhook externo. No realiza llamadas HTTP reales ni
    imprime nada: guarda los payloads recibidos en self.sent_payloads
    para que las pruebas puedan inspeccionarlos.
    """

    def __init__(self, url: str = "https://example.com/webhook") -> None:
        self.url = url
        self.sent_payloads: list[dict[str, Any]] = []

    def notify(self, *, event: str, ticket_id: int, **payload: Any) -> None:
        self.sent_payloads.append(
            {"url": self.url, "event": event, "ticket_id": ticket_id, **payload}
        )
