"""
Testes de aceitação — Autenticação
"""
import re
import pytest
from playwright.sync_api import Page, expect


def test_pagina_login_carrega(page: Page, base_url: str):
    page.goto(f"{base_url}/accounts/login/")
    expect(page).to_have_title(re.compile("Plan N'Go"))
    expect(page.locator('input[name="email"]')).to_be_visible()
    expect(page.locator('input[name="password"]')).to_be_visible()


def test_login_com_credenciais_validas(page: Page, base_url: str):
    page.goto(f"{base_url}/accounts/login/")
    page.fill('input[name="email"]', "teste@plango.app")
    page.fill('input[name="password"]', "senha@1234")
    page.click('button[type="submit"]')
    expect(page).to_have_url(f"{base_url}/destinations/")


def test_login_com_senha_errada_exibe_erro(page: Page, base_url: str):
    page.goto(f"{base_url}/accounts/login/")
    page.fill('input[name="email"]', "teste@plango.app")
    page.fill('input[name="password"]', "senhaerrada")
    page.click('button[type="submit"]')
    expect(page.locator(".alert--error")).to_be_visible()


def test_logout(logged_page: Page, base_url: str):
    logged_page.goto(f"{base_url}/destinations/")
    logged_page.click("button.app-navbar__logout")
    expect(logged_page).to_have_url(f"{base_url}/")
