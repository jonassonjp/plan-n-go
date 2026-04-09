"""
Configuração dos testes de aceitação (Playwright).
"""
import os
import pytest
from playwright.sync_api import Page


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
TEST_EMAIL = "teste@plango.app"
TEST_PASSWORD = "senha@1234"


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def logged_page(page: Page, base_url: str) -> Page:
    """Fixture que retorna uma página já autenticada."""
    page.goto(f"{base_url}/accounts/login/")
    page.fill('input[name="email"]', TEST_EMAIL)
    page.fill('input[name="password"]', TEST_PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{base_url}/destinations/")
    return page
