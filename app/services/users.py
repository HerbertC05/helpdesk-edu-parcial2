"""Servicio de usuarios."""

from __future__ import annotations

from app.domain.errors import UserNotFoundError
from app.models.entities import User
from app.repositories.base import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def by_id(self, user_id: int) -> User | None:
        return self._repository.by_id(user_id)

    def require(self, user_id: int) -> User:
        user = self._repository.by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    def create(self, *, name: str, email: str, role) -> User:
        user = User(id=self._repository.next_id(), name=name, email=email, role=role)
        self._repository.add(user)
        return user
