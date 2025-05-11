from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

from src.dependencies import KeycloakOpenIDClient
from src.model import Role
from src.security import AuthService
from src.exception import LoginException, PermissionException

app = FastAPI()


@app.get("/")
async def home(
    request: Request,
    keycloak_client: Annotated[KeycloakOpenIDClient, Depends(KeycloakOpenIDClient)],
):
    """Home page

    Returns:
        Dict: list of endpoints and usage
    """
    try:
        await AuthService.check_user_permission(
            request=request,
            keycloak_client=keycloak_client,
            allow_roles={Role.USER, Role.ADMIN},
        )
    except LoginException:
        return RedirectResponse(url="/login")
    except PermissionException:
        return HTTPException(
            status_code=403, detail="You don't have enough permission to view this page"
        )

    return {
        "/": "homepage, allow all user to access after login",
        "/login": "redirect user to keycloak, for login",
        "/logout": "revoke auth token from keycloak, redirect user to /",
        "/admin": "admin page, only allow user with admin role to access",
    }


@app.get("/login", response_class=RedirectResponse)
async def login(
    request: Request,
    keycloak_client: Annotated[KeycloakOpenIDClient, Depends(KeycloakOpenIDClient)],
):
    """
    Login endpoint, redirect user to keycloak

    Returns:
        RedirectResponse: The redirect URL to keycloak login page
    """
    return await AuthService.redirect_to_keycloak(request, keycloak_client)


@app.get("/logout", response_class=RedirectResponse)
async def logout(
    request: Request,
    keycloak_client: Annotated[KeycloakOpenIDClient, Depends(KeycloakOpenIDClient)],
):
    """
    Logout endpoint, revoke access token from keycloak

    Returns:
        RedirectResponse: The redirect URL to home page
    """
    return await AuthService.logout_from_keycloak(request, keycloak_client)


@app.get("/callback", response_class=RedirectResponse)
async def callback(
    request: Request,
    keycloak_client: Annotated[KeycloakOpenIDClient, Depends(KeycloakOpenIDClient)],
    code: str,
):
    """Retrieve user token for authorization code flow, and store encrypted access token to cookie.

    Args:
        code (str): code for retrieving access token
    """
    return await AuthService.exchange_access_token(request, keycloak_client, code)


@app.get("/admin")
async def admin(
    request: Request,
    keycloak_client: Annotated[KeycloakOpenIDClient, Depends(KeycloakOpenIDClient)],
):
    try:
        await AuthService.check_user_permission(
            request=request, keycloak_client=keycloak_client, allow_roles={Role.ADMIN}
        )
    except LoginException:
        return RedirectResponse(url="/login")
    except PermissionException:
        return HTTPException(
            status_code=403, detail="You don't have enough permission to view this page"
        )
    return "admin page, only allow user with admin role to access"


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
