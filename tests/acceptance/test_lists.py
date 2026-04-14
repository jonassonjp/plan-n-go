"""
Testes de aceitação — Listas de Destinos
"""
import re
import pytest
from playwright.sync_api import Page, expect


def test_dashboard_listas_carrega(logged_page: Page, base_url: str):
    logged_page.goto(f"{base_url}/lists/")
    expect(logged_page).to_have_title(re.compile("Listas"))
    expect(logged_page.locator("h1")).to_contain_text("Minhas Listas")


def test_criar_lista_manual(logged_page: Page, base_url: str):
    logged_page.goto(f"{base_url}/lists/")
    logged_page.click("button:has-text('Nova Lista')")
    expect(logged_page.locator("#createModal")).to_be_visible()
    logged_page.fill('input[name="name"]', "Minha Lista E2E")
    logged_page.click('button[type="submit"]:has-text("Criar Lista")')
    expect(logged_page.locator("h1")).to_contain_text("Minha Lista E2E")


def test_criar_lista_inteligente(logged_page: Page, base_url: str):
    logged_page.goto(f"{base_url}/lists/")
    logged_page.click("button:has-text('Nova Lista')")
    logged_page.click("button[data-type='smart']")
    expect(logged_page.locator("#smartCriteria")).to_be_visible()
    logged_page.locator('#smartCriteria label.chip:has-text("Europa")').click()
    logged_page.fill('input[name="name"]', "Europa E2E")
    logged_page.click('button[type="submit"]:has-text("Criar Lista")')
    expect(logged_page.locator("h1")).to_contain_text("Europa E2E")
    expect(logged_page.locator(".list-card__badge--smart, .list-detail-title-row").first).to_be_visible()


def test_editar_lista(logged_page: Page, base_url: str):
    logged_page.goto(f"{base_url}/lists/")
    logged_page.click("button:has-text('Nova Lista')")
    logged_page.fill('input[name="name"]', "Lista Para Editar")
    logged_page.click('button[type="submit"]:has-text("Criar Lista")')
    logged_page.click("button:has-text('Editar')")
    expect(logged_page.locator("#editModal")).to_be_visible()
    name_input = logged_page.locator('#editModal input[name="name"]')
    name_input.fill("Lista Editada E2E")
    logged_page.click('#editModal button[type="submit"]')
    expect(logged_page.locator("h1")).to_contain_text("Lista Editada E2E")


def test_excluir_lista(logged_page: Page, base_url: str):
    logged_page.goto(f"{base_url}/lists/")
    logged_page.click("button:has-text('Nova Lista')")
    logged_page.fill('input[name="name"]', "Lista Para Excluir")
    logged_page.click('button[type="submit"]:has-text("Criar Lista")')
    logged_page.on("dialog", lambda dialog: dialog.accept())
    logged_page.click("button:has-text('Excluir')")
    expect(logged_page).to_have_url(f"{base_url}/lists/")
    expect(logged_page.locator(".list-card__name", has_text="Lista Para Excluir")).to_have_count(0)
