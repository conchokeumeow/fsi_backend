import sentry_sdk
import traceback
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
print("=== ENV CHECK ===")
print("POSTGRES_SERVER:", settings.POSTGRES_SERVER)
print("POSTGRES_DB:", settings.POSTGRES_DB)
print("POSTGRES_USER:", settings.POSTGRES_USER)
print("POSTGRES_PASSWORD:", settings.POSTGRES_PASSWORD)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=True,  
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

@app.middleware("http")
async def log_exceptions(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print("\n====== EXCEPTION CAUGHT ======")
        print(e)
        traceback.print_exc()
        raise e

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

print("OPENAPI URL:", app.openapi_url)
