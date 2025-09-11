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
ADMIN_SELLER_EMAIL = os.getenv("ADMIN_SELLER_EMAIL")
ADMIN_SELLER_PASSWORD = os.getenv("ADMIN_SELLER_PASSWORD")
PURCHASER_EMAIL = os.getenv("PURCHASER_EMAIL")
PURCHASER_PASSWORD = os.getenv("PURCHASER_PASSWORD")
CONTRACT_MANAGER_EMAIL = os.getenv("CONTRACT_MANAGER_EMAIL")
CONTRACT_MANAGER_PASSWORD = os.getenv("CONTRACT_MANAGER_PASSWORD")
TESTMAIL_JSON_ = os.getenv("TESTMAIL_JSON_")
TESTMAIL_ADRESS_ = os.getenv("TESTMAIL_ADRESS_")
TEST_BUYER_EMAIL = os.getenv("TEST_BUYER_EMAIL")

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


    @allure.step("Авторизуюсь (Покупатель Администратор)")
    def admin_buyer_authorize(self):
        self.page.type(self.EMAIL_INPUT, ADMIN_BUYER_EMAIL)
        self.page.type(self.PASSWORD_INPUT, ADMIN_BUYER_PASSWORD)
        self.page.locator(self.SUBMIT_BUTTON).click()
        return ADMIN_BUYER_EMAIL

    # Не готов Подтя нуть мыло с паролем из .env
    @allure.step("Авторизуюсь (Закупщик)")
    def purchaser_authorize(self):
        self.page.type(self.EMAIL_INPUT, PURCHASER_EMAIL)
        self.page.type(self.PASSWORD_INPUT, PURCHASER_PASSWORD)
        self.page.locator(self.SUBMIT_BUTTON).click()

    # Не готов
    @allure.step("Авторизуюсь (Менеджер контракта")
    def contract_manager_authorize(self):
        self.page.type(self.EMAIL_INPUT, CONTRACT_MANAGER_EMAIL)
        self.page.type(self.PASSWORD_INPUT, CONTRACT_MANAGER_PASSWORD)
        self.page.locator(self.SUBMIT_BUTTON).click()

    @allure.step("Авторизуюсь на vi")
    def vi_test_authorize(self):
        self.page.goto("https://www.vseinstrumenti.ru/")
        pass

    # Не готов
    @allure.step("Авторизуюсь (Продавец администратор")
    def admin_seller_authorize(self):
        self.page.type(self.EMAIL_INPUT, ADMIN_SELLER_EMAIL)
        self.page.type(self.PASSWORD_INPUT, ADMIN_SELLER_PASSWORD)
        self.page.locator(self.SUBMIT_BUTTON).click()

    @allure.step("Авторизуюсь (Тестовый покупатель)")
    def test_buyer_authorize(self):
        self.page.type(self.EMAIL_INPUT, TESTMAIL_ADRESS_)
        self.page.type(self.PASSWORD_INPUT, TEST_BUYER_PASSWORD)
        self.page.locator(self.SUBMIT_BUTTON).click()

    @allure.step("Авторизуюсь (Тестовый покупатель для роли админа)")
    def test_buyer_for_admin_role_authorize(self):
        self.page.type(self.EMAIL_INPUT, TEST_BUYER_EMAIL)
        self.page.type(self.PASSWORD_INPUT, TEST_BUYER_PASSWORD)
        self.page.locator(self.SUBMIT_BUTTON).click()

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
            self.page.locator(self.SUBMIT_BUTTON).click()  # Кнопка "Активировать"
        with allure.step("Кликаю на кнопку Далее"):
            self.page.locator(self.SUBMIT_BUTTON).click()  # Кнопка "Далее"

        with allure.step("Ввожу пароль, подтверждаю его"):
            self.page.type(self.PASSWORD_INPUT, TEST_BUYER_PASSWORD)
            self.page.type(self.CONFIRM_PASSWORD_INPUT, TEST_BUYER_PASSWORD)

        with allure.step("Кликаю на кнопку Войти в систему"):
            self.page.locator(self.SUBMIT_BUTTON).click()

    # Клик для любой подтверждающей кнопки
    def click_submit_button(self):
        self.page.locator(self.SUBMIT_BUTTON).click()

    @allure.step("Получаю текст подсказки в карточке пользователя")
    def get_notification_text(self):
        notification_text = self.page.locator(self.USER_CARD_NOTIFICATION).inner_text()
        return notification_text

