import re
import logging
import redis.asyncio as redis
import asyncio
import uvicorn
from ipaddress import ip_address
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from typing import Callable
import pathlib

from sqlalchemy.orm import Session

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware

from src.database.db import get_db
from src.routes import auth, notes, tags, contacts, users
from src.conf.config import settings

logging.basicConfig(level=logging.DEBUG)


app = FastAPI()
origins = ["*"]
user_agent_ban_list = []  # [r"Gecko"]
banned_ips = [
    ip_address("192.168.1.1"),
    ip_address("192.168.1.2"),
    ip_address("127.0.0.12"),
]

ALLOWED_IPS = [
    ip_address("192.168.1.0"),
    ip_address("172.16.0.0"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router, prefix="/api")
# app.include_router(tags.router, prefix="/api")
# app.include_router(notes.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix='/api')

templates = Jinja2Templates(directory="templates")


favicon_path = pathlib.Path("src/favicon/favicon.ico")

@app.middleware("http")
async def ban_ips(request: Request, call_next: Callable):
    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    ip = ip_address(client_ip)

    if ip in banned_ips:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned (IP)"}
        )
    
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned (Words)"})
    
    response = await call_next(request)
    return response

# @app.middleware("http")
# async def ban_ips(request: Request, call_next: Callable):
#     ip = ip_address(request.client.host)
#     if ip in banned_ips:
#         return JSONResponse(
#             status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned (IP)"}
#         )
#     user_agent = request.headers.get("user-agent")
#     for ban_pattern in user_agent_ban_list:
#         if re.search(ban_pattern, user_agent):
#             return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned (Words)"})
#     response = await call_next(request)
#     return response


@app.on_event("startup")
async def startup():
    await asyncio.sleep(1)
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


@app.get("/favicon.ico", response_class=FileResponse)
def get_favicon():
    """
    The get_favicon function returns the path to the favicon.ico file.
    
    :return: The favicon_path variable
    :doc-author: Trelent
    """
    return favicon_path


@app.get(
    "/",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
    response_class=HTMLResponse,
    description="Main Page",
)
async def home(request: Request):
    """
    The home function is the default route for our application.
    It returns a TemplateResponse object, which renders the home.html template
    and passes it a context containing the title of our app and request object.
    
    :param request: Request: Pass the request object to the template
    :return: A templateresponse object
    :doc-author: Trelent
    """
    return templates.TemplateResponse(
        "home.html", {"request": request, "title": "My App"}
    )


@app.get("/login", response_class=HTMLResponse, description="Login")
async def login(request: Request):
    """
    The login function handles the login page.
        It returns a TemplateResponse object with the template name and context.
    
    
    :param request: Request: Get the request object
    :return: A templateresponse object
    :doc-author: Trelent
    """
    return templates.TemplateResponse(
        "login.html", {"request": request, "title": "My App"}
    )


@app.get(
    "/register",
    response_class=HTMLResponse,
    description="Sign Up",
    dependencies=[Depends(RateLimiter(times=1, seconds=300))],
)
async def register(request: Request):
    """
    The register function is responsible for handling the registration of new users.
    It will render a template with a form that allows the user to enter their email address,
    password, and password confirmation. The function will then validate these inputs and create 
    a new user in our database if everything checks out.
    
    :param request: Request: Pass the request object to the template
    :return: A templateresponse object
    :doc-author: Trelent
    """
    return templates.TemplateResponse(
        "register.html", {"request": request, "title": "My App"}
    )


@app.get("/api/healthchaker")
def healthchaker(db: Session = Depends(get_db)):
    """
    The healthchaker function is a simple function that returns a JSON object with the message &quot;Hello World&quot;.
    This function is used to test if the API server is running.
    
    
    :param db: Session: Access the database
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
