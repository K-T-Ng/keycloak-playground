from enum import Enum
from typing import List, Set

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Setting(BaseSettings):
    """Application configuration"""

    keycloak_url: str = Field(alias="KEYCLOAK_URL")
    keycloak_realm_name: str = Field(alias="KEYCLOAK_REALM_NAME")
    keycloak_client_id: str = Field(alias="KEYCLOAK_CLIENT_ID")
    keycloak_client_secret: str = Field(alias="KEYCLOAK_CLIENT_SECRET")

    fernet_encrypt_key: str = Field(alias="FERNET_ENCRYPT_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class UserToken(BaseModel):
    """Response model from keycloak token exchange"""

    token_type: str = Field(
        description="Describes how the token can be used. Most commonly Bearer token usage."
    )
    access_token: str = Field(description="The resulting access token")
    expires_in: int = Field(description="TTL for the access token in seconds")
    refresh_token: str = Field(description="The resulting refresh token")
    refresh_expires_in: int = Field(description="TTL for the refresh token in seconds")
    id_token: str = Field(description="The resulting ID token")


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class RealmAccess(BaseModel):
    roles: Set[Role]


class AccessToken(BaseModel):
    realm_access: RealmAccess
    name: str
    preferred_username: str
