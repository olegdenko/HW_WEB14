import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import pytest
import unittest
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient
from fastapi import FastAPI
from main import app

templates = Jinja2Templates(directory="templates")

@pytest.fixture
def test_app():
    return app

@pytest.mark.asyncio
async def test_home_route(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.get("/", headers={"X-Forwarded-For": "127.0.0.1"})
    assert response.status_code == 200
    assert "My App" in response.text

@pytest.mark.asyncio
async def test_login_route(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.get("/login", headers={"X-Forwarded-For": "127.0.0.1"})
    assert response.status_code == 200
    assert "My App" in response.text

if __name__ == '__main__':
    unittest.main()