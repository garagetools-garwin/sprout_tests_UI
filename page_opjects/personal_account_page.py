import os
from multiprocessing.pool import CLOSE
import random
from faker import Faker
import allure
from playwright.sync_api import Page
from dotenv import load_dotenv

fake = Faker('ru_RU')
load_dotenv()

TEST_BUYER_EMAIL = os.getenv("TEST_BUYER_EMAIL")
TEST_BUYER_PASSWORD = os.getenv("TEST_BUYER_PASSWORD")
TESTMAIL_ADRESS_ = os.getenv("TESTMAIL_ADRESS_")

class PersonalAccountPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/settings/profile"

    # ADD_USER_BUTTON = ".account-user-list-settings__filters .button-circle.primary"

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    # @allure.step("Кликаю на крестик")
    # def click_close_button(self):
    #     self.page.locator(self.CLOSE_BUTTON).click()
    # @allure.step("Закрываю модальное окно")
    # def close_modal(self):
    #     self.page.mouse.click(50, 100)

