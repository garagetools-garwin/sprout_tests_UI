import os
import time

import allure
import requests
from playwright.sync_api import Page
from dotenv import load_dotenv

load_dotenv()

ADMIN_BUYER_EMAIL = os.getenv("ADMIN_BUYER_EMAIL")
ADMIN_BUYER_PASSWORD = os.getenv("ADMIN_BUYER_PASSWORD")
TEST_BUYER_PASSWORD = os.getenv("TEST_BUYER_PASSWORD")
TESTMAIL_JSON_ = os.getenv("TESTMAIL_JSON_")
TESTMAIL_ADRESS_ = os.getenv("TESTMAIL_ADRESS_")

class AutorizationPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/login"

    EMAIL_INPUT = "#email"
    PASSWORD_INPUT = "#password"
    CONFIRM_PASSWORD_INPUT = "#passwordConfirm"
    SUBMIT_BUTTON = "div button[type='submit']"
    USER_CARD_NOTIFICATION = ".notification__container .text-tag"


    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)


    @allure.step("Авторизуюсь")
    def admin_buyer_authorize(self):
        self.page.type(self.EMAIL_INPUT, ADMIN_BUYER_EMAIL)
        self.page.type(self.PASSWORD_INPUT, ADMIN_BUYER_PASSWORD)
        self.page.click(self.SUBMIT_BUTTON)
        return ADMIN_BUYER_EMAIL

    @allure.step("Авторизуюсь")
    def test_buyer_authorize(self):
        self.page.type(self.EMAIL_INPUT, TESTMAIL_ADRESS_)
        self.page.type(self.PASSWORD_INPUT, TEST_BUYER_PASSWORD)
        self.page.click(self.SUBMIT_BUTTON)
        return

    @allure.step("Получаю ссылку для активации аккаунта")
    def get_activation_link_testmail_app(self):
        time.sleep(15)
        response = requests.get(url=f"{TESTMAIL_JSON_}")
        response_json = response.json()
        email_text = response_json["emails"][0]["text"]
        pre_activation_url = email_text.split("]]\n[")[1]
        activation_url = pre_activation_url.split("]")[0]
        return activation_url

    @allure.step("Активирую аккаунт")
    def activate_account(self, browser):
        context = browser.new_context()
        page = context.new_page()
        activation_url = self.get_activation_link_testmail_app()
        page.goto(activation_url)
        with allure.step("Кликаю на кнопку Активировать"):
            self.click_submit_button()
        with allure.step("Кликаю на кнопку Далее"):
            self.click_submit_button()
        with allure.step("Ввожу пароль, подтверждаю его"):
            self.page.type(self.PASSWORD_INPUT, TEST_BUYER_PASSWORD)
            self.page.type(self.CONFIRM_PASSWORD_INPUT, TEST_BUYER_PASSWORD)
        with allure.step("Кликаю на кнопку Войти в систему"):
            self.click_submit_button()

    @allure.step("Активирую аккаунт вручную через письмо")
    def activate_account_directly(self):
        activation_url = self.get_activation_link_testmail_app()
        self.page.goto(activation_url)

        with allure.step("Кликаю на кнопку Активировать"):
            self.page.click(self.SUBMIT_BUTTON)  # Кнопка "Активировать"
        with allure.step("Кликаю на кнопку Далее"):
            self.page.click(self.SUBMIT_BUTTON)  # Кнопка "Далее"

        with allure.step("Ввожу пароль, подтверждаю его"):
            self.page.type(self.PASSWORD_INPUT, TEST_BUYER_PASSWORD)
            self.page.type(self.CONFIRM_PASSWORD_INPUT, TEST_BUYER_PASSWORD)

        with allure.step("Кликаю на кнопку Войти в систему"):
            self.page.click(self.SUBMIT_BUTTON)

    # Клик для любой подтверждающей кнопки
    def click_submit_button(self):
        self.page.click(self.SUBMIT_BUTTON)

    @allure.step("Получаю текст подсказки в карточке пользователя")
    def get_notification_text(self):
        notification_text = self.page.locator(self.USER_CARD_NOTIFICATION).inner_text()
        return notification_text

