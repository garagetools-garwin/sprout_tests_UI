import os

import allure
from playwright.sync_api import Page
from dotenv import load_dotenv

load_dotenv()

ADMIN_BUYER_EMAIL = os.getenv("ADMIN_BUYER_EMAIL")
ADMIN_BUYER_PASSWORD = os.getenv("ADMIN_BUYER_PASSWORD")

class AutorizationPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/login"

    EMAIL_INPUT = "#email"
    PASSWORD_INPUT = "#password"
    SUBMIT_BUTTON = "div button[type='submit']"


    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)


    @allure.step("Авторизуюсь")
    def authorize(self):
        self.page.type(self.EMAIL_INPUT, ADMIN_BUYER_EMAIL)
        self.page.type(self.PASSWORD_INPUT, ADMIN_BUYER_PASSWORD)
        self.page.click(self.SUBMIT_BUTTON)
        return ADMIN_BUYER_EMAIL
