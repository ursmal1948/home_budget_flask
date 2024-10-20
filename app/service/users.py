from dataclasses import dataclass
from typing import Any
import datetime
from app.persistent.repository import UserRepository, ActivationTokenRepository
from app.persistent.entity import ActivationTokenEntity
from app.service.dto import RegisterUserDto, UserDto, CreateUserDto
from app.persistent.entity import UserEntity
import random
import string
from app.mail.configuration import MailSender
from app.config import (
    ACTIVATION_TOKEN_LENGTH,
    ACTIVATION_TOKEN_EXPIRATION_TIME_IN_SECONDS
)
from werkzeug.exceptions import NotFound
from app.security.configuration import guard
import logging

logging.basicConfig(level=logging.INFO)


@dataclass
class UserService:
    user_repository: UserRepository

    def add_user(self, user_dto: CreateUserDto) -> dict[str, Any]:
        username = user_dto.name
        if self.user_repository.find_by_name(username):
            raise ValueError('Username already exists')

        email = user_dto.email
        if self.user_repository.find_by_email(email):
            raise ValueError('Email already exists')

        hashed_password = guard.hash_password(user_dto.password)

        user_entity = UserEntity(
            name=user_dto.name,
            hashed_password=hashed_password,
            email=user_dto.email,
            roles=user_dto.roles
        )

        self.user_repository.save_or_update(user_entity)
        return UserDto.from_user_entity(user_entity).to_dict()

    def get_by_name(self, name: str) -> dict[str, Any]:
        user = self.user_repository.find_by_name(name)
        if not user:
            raise NotFound('User not found')
        return UserDto.from_user_entity(user).to_dict()

    def get_by_email(self, email: str) -> dict[str, Any]:
        user = self.user_repository.find_by_email(email)
        if not user:
            raise NotFound('User not found')

        return UserDto.from_user_entity(user).to_dict()

    def get_by_id(self, user_id: int) -> dict[str, Any]:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFound('User not found')

        return UserDto.from_user_entity(user).to_dict()

    def get_total_income(self, user_id: int) -> int:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFound('User not found')

        return self.user_repository.calculate_total_income(user_id)


@dataclass
class UserSecurityService:
    user_repository: UserRepository
    activation_token_repository: ActivationTokenRepository

    def register_user(self, register_user_dto: RegisterUserDto) -> dict[str, Any]:

        if not register_user_dto.check_passwords():
            raise ValueError('Passwords do not match')

        if self.user_repository.find_by_email(register_user_dto.name):
            raise ValueError('Name already exists')

        if self.user_repository.find_by_email(register_user_dto.email):
            raise ValueError('Email already exists')

        user_entity = register_user_dto.with_password(
            guard.hash_password(register_user_dto.password)).to_user_entity()
        self.user_repository.save_or_update(user_entity)

        timestamp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            seconds=ACTIVATION_TOKEN_EXPIRATION_TIME_IN_SECONDS)
        token = UserSecurityService._generate_token(ACTIVATION_TOKEN_LENGTH)
        user_id = user_entity.id
        self.activation_token_repository.save_or_update(
            ActivationTokenEntity(
                timestamp=timestamp.timestamp(),
                token=token,
                user_id=user_id
            )
        )
        MailSender.send(register_user_dto.email, 'Activate Your Account', f'<h1>Activation Token: {token}</h1>')

        return UserDto.from_user_entity(user_entity).to_dict()

    def activate_user(self, token: str) -> dict[str, Any]:
        activation_token_with_user = self.activation_token_repository.find_by_token(token)

        if activation_token_with_user is None:
            raise NotFound('User not found')

        self.activation_token_repository.delete_by_id(activation_token_with_user.id)

        if not activation_token_with_user.is_active():
            raise ValueError('Token has been expired')

        user_to_activate = activation_token_with_user.user
        user_to_activate.is_active = True
        self.user_repository.save_or_update(user_to_activate)
        return UserDto.from_user_entity(user_to_activate).to_dict()

    @staticmethod
    def _generate_token(size: int) -> str:
        characters = string.ascii_letters + string.digits
        return ''.join([random.choice(characters) for _ in range(size)])
