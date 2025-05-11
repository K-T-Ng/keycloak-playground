from typing import Set
from fastapi import Request
from fastapi.responses import RedirectResponse, Response
from jwcrypto.jwt import JWException

from src.model import Role, UserToken, AccessToken
from src.exception import LoginException, PermissionException
from src.dependencies import KeycloakOpenIDClient, CryptoClient


class AuthService:
    @staticmethod
    async def redirect_to_keycloak(
        request: Request, keycloak_client: KeycloakOpenIDClient
    ) -> RedirectResponse:
        """Redirect user to keycloak login page for authentication

        Args:
            request (Request): fastAPI request object
            keycloak_client (KeycloakOpenIDClient): inject keycloak client

        Returns:
            RedirectResponse: redirect response for redirect user to keycloak login page
        """
        redirect_uri: str = str(request.url_for("callback"))
        redirect_url = await keycloak_client.a_auth_url(
            redirect_uri=redirect_uri, scope="openid"
        )
        return RedirectResponse(redirect_url)

    @staticmethod
    async def logout_from_keycloak(
        request: Request, keycloak_client: KeycloakOpenIDClient
    ) -> RedirectResponse:
        """Revoke access token from keycloak

        Args:
            request (Request): fastAPI request object
            keycloak_client (KeycloakOpenIDClient): inject keycloak client

        Returns:
            RedirectResponse: redirect response for redirect user to home page
        """
        response = RedirectResponse(url="/")

        access_token = AuthService.read_token_from_cookie(request, "access_token")
        if access_token:
            response.delete_cookie("access_token", httponly=True, samesite="lax")

        refresh_token = AuthService.read_token_from_cookie(request, "refresh_token")
        if refresh_token:
            try:
                await keycloak_client.a_logout(refresh_token)
            except Exception as exc:
                print(exc)

            response.delete_cookie("refresh_token", httponly=True, samesite="lax")

        return response

    @staticmethod
    async def exchange_access_token(
        request: Request, keycloak_client: KeycloakOpenIDClient, code: str
    ) -> RedirectResponse:
        """Exchange access token via OpenID Connection Authorization Code flow

        Args:
            request (Request): fastAPI request object
            response (Response): fastAPI response object
            keycloak_client (KeycloakOpenIDClient): inject keycloak client
            code (str): authorization code nonce, used in token request

        Returns:
            RedirectResponse: redirect to homepage
        """
        redirect_uri: str = str(request.url_for("callback"))
        token_json = await keycloak_client.a_token(
            grant_type="authorization_code",
            code=code,
            redirect_uri=redirect_uri,
            scope="openid",
        )
        user_token = UserToken.model_validate(token_json)

        response = RedirectResponse(url="/")
        AuthService.write_token_to_cookie(response, "access_token", user_token.access_token)
        AuthService.write_token_to_cookie(response, "refresh_token", user_token.refresh_token)
        return response

    @staticmethod
    async def check_user_permission(
        request: Request, keycloak_client: KeycloakOpenIDClient, allow_roles: Set[Role]
    ):
        """Determine whether user has enough permission to get the resource
        Raise LoginException / PermissionException if needed

        Args:
            request (Request): fastAPI request object
            keycloak_client (KeycloakOpenIDClient): inject keycloak client
            allow_roles (List[Role]): whitelist roles
        """
        cookie_access_token: str | None = AuthService.read_token_from_cookie(request, "access_token")
        if not cookie_access_token:
            raise LoginException("User has not login yet")

        try:
            access_token_json = await keycloak_client.a_decode_token(
                cookie_access_token
            )
        except JWException:
            raise LoginException("Access token expired or invalid")

        access_token = AccessToken.model_validate(access_token_json)
        if all(role not in allow_roles for role in access_token.realm_access.roles):
            raise PermissionException("Permission denied")


    @staticmethod
    def write_token_to_cookie(response: Response, key: str, value: str):
        crypto_client = CryptoClient()
        response.set_cookie(
            key=key,
            value=crypto_client.encrypt(value),
            httponly=True,
            samesite="lax"
        )

    @staticmethod
    def read_token_from_cookie(request: Request, key: str) -> str:
        crypto_client = CryptoClient()
        cookie = request.cookies.get(key)
        return crypto_client.decrypt(cookie)
