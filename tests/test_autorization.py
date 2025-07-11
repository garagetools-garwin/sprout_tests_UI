import allure
from playwright.sync_api import expect

from page_opjects.autorization_page import AutorizationPage

@allure.title("Авторизация")
def test_autorization(page_fixture, base_url):
    autorization_page = AutorizationPage(page_fixture)
    response = autorization_page.open(base_url)
    with allure.step("Проверяю статус код страницы"):
        assert response.ok, f"Страница не ok, статус: {response.status}"
    autorization_page.admin_buyer_authorize()
    with allure.step("Проверяю, что пользователь перешел на страницу настроек профиля"):
        expect(page_fixture).to_have_url(f"{base_url}/profile")








    # Проверить "с возвращением"
    # проверить что введенная почта соответствует той, что была введена #email to have value=USER_EMAIL