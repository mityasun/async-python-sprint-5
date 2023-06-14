import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api.v1.files import files_router
from src.api.v1.ping import ping_router
from src.core.config import app_settings
from src.schemas.users import UserCreate, UserRead, UserUpdate
from src.services.users import auth_backend, fastapi_users

app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.get("/")
def read_root():
    """Main page with welcome."""

    return (f'Welcome to {app_settings.app_title}! API docs: '
            f'http://{app_settings.project_host}:{app_settings.project_port}'
            f'/redoc'
            )


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/api/v1/auth/jwt', tags=[app_settings.tag_auth]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/api/v1/auth', tags=[app_settings.tag_auth]
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix='/api/v1/auth', tags=[app_settings.tag_auth]
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/v1/users", tags=['Users'],
)
app.include_router(ping_router, prefix='/api/v1')
app.include_router(files_router, prefix='/api/v1')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port
    )
