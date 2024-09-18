import sql_api,csv_api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.sessions import SessionMiddleware
import logging


logging.basicConfig(filename='api.log', filemode='a', level=logging.INFO, \
                    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)d- %(message)s')
app = FastAPI()

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the SessionMiddleware to enable session handling
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

app.include_router(sql_api.router, tags=["NL2SQL on DB"])
app.include_router(csv_api.router, tags=["NL2SQL on CSV"])
# app.include_router(bot_details.router, tags=["Bot Details"])
# app.include_router(response.router, tags=["Get Answer"])
# app.include_router(linkedin_api.router, tags=["Linkedin messages Operations"])

