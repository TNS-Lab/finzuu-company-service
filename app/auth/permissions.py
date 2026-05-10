
from fastapi import Request


def require_permissions(*permissions: str):
    async def permission_checker(request: Request):
        # auth_header = request.headers.get("Authorization")

        # if not auth_header or not auth_header.startswith("Bearer "):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Authentication required. Code: 4012"
        #     )

        # payload = {
        #     "route": request.url.path,
        #     "permission": list(permissions)
        # }
        # headers = {
        #     "Content-Type": "application/json",
        #     "Authorization": f"Bearer {auth_header.split(' ')[1]}"
        # }

        # response = http_requests.post(
        #     f"{settings.AUTH_API}/auth/check-permission",
        #     json=payload,
        #     headers=headers
        # )

        # if response.status_code == 200:
        #     return True

        # if response.status_code == 401:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Authentication required. Code: 4013"
        #     )

        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail="You do not have access to this route or insufficient permissions."
        # )

        return True

    return permission_checker
