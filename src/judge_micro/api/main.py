import os
from fastapi import FastAPI
from fastapi.routing import APIRouter
from judge_micro.config.settings import setting
from judge_micro.api.routes import heartbeat, judge

api_router = APIRouter()
api_router.include_router(heartbeat.router)
api_router.include_router(judge.router)

def get_app(debug: bool = None) -> FastAPI:
    # If debug is not explicitly set, use environment variable or setting
    if debug is None:
        debug = os.getenv('JUDGE_IS_DEBUG', 'false').lower() in ('true', '1', 'yes') or setting.JUDGE_IS_DEBUG
    
    if debug:
        app = FastAPI(
            title="Judge Micro API",
            service_name="judge_micro_api",
            description="API for Judge Micro service",
            version="0.0.3",
            license_info={
                "name": "Apache License 2.0",
            },
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
            debug=True,
        )
    else:
        app = FastAPI(
            title="Judge Micro API",
            service_name="judge_micro_api",
            description="API for Judge Micro service",
            version="0.0.3",
            license_info={
                "name": "Apache License 2.0",
            },
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
            debug=False,
        )
    app.include_router(router=api_router, prefix="")
    return app