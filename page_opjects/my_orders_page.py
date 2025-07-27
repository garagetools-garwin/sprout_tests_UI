import os

import allure
from playwright.sync_api import Page

class MyOrdersPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/request-list/user"

    # NEW_ORDER_IDENTIFICATOR = ".new-indicator"
    NEW_ORDER_IDENTIFICATOR = ".new-indicator + .text-controls-accent.ellipsis"
    ORDER_NUMBER = ".text-controls-accent.ellipsis"

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    @allure.step("Получаю номер нового заказа")
    def get_order_number(self):
        with allure.step("Нахожу блок с меткой нового заказа"):
            text = self.page.locator(self.NEW_ORDER_IDENTIFICATOR).nth(0).inner_text()
            print(text)
            return text


