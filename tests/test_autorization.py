import time

import allure
from playwright.sync_api import expect

from page_opjects.autorization_page import AutorizationPage

def test_autorization(page_fixture, base_url):
    autorization_page = AutorizationPage(page_fixture)
    response = autorization_page.open(base_url)
    with allure.step("Проверяю статус код страницы"):
        assert response.ok, f"Страница не ok, статус: {response.status}"
    autorization_page.authorize()
    with allure.step("Проверяю, что пользователь перешел на страницу настроек профиля"):
        expect(page_fixture).to_have_url(f"{base_url}/profile")
    with allure.step("Проверяю, что профиль пользователь имеет корректный email"):
        expect(page_fixture).to_have_url(f"{base_url}/profile")
    #email to have value=USER_EMAIL

    # здесь будет проверка на то, что авторизация прошла успешно
    # Проверить "с возвращением"
    # проверить, что страница сменилась на настройки, проверить что введенная почта соответствует той, что была введена

def test_type_check(page_fixture):
    from playwright.sync_api import Page
    assert isinstance(page_fixture, Page)