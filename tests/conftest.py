from __future__ import annotations

import pytest

from app.models.entities import Role, User
from app.repositories.memory import InMemoryTicketRepository, InMemoryUserRepository
from app.services.notifications import RecordingNotifier, WebhookNotifier
from app.services.tickets import TicketService
from app.services.users import UserService


@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository(
        [
            User(id=1, name="Ana Solicitante", email="ana@example.com", role=Role.REQUESTER),
            User(id=2, name="Beto Técnico", email="beto@example.com", role=Role.TECHNICIAN),
            User(id=3, name="Carla Técnica", email="carla@example.com", role=Role.TECHNICIAN),
        ]
    )


@pytest.fixture
def ticket_repo() -> InMemoryTicketRepository:
    return InMemoryTicketRepository()


@pytest.fixture
def users_service(user_repo) -> UserService:
    return UserService(user_repo)


@pytest.fixture
def recording_notifier() -> RecordingNotifier:
    return RecordingNotifier()


@pytest.fixture
def webhook_notifier() -> WebhookNotifier:
    return WebhookNotifier()


@pytest.fixture
def ticket_service(ticket_repo, users_service, recording_notifier) -> TicketService:
    return TicketService(ticket_repo, users_service, notifier=recording_notifier)
