import os

import allure
from playwright.sync_api import Page


class HomePage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/"

    SETTINGS_BUTTON = ".sidebar-item.sidebar-item__active"

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)


    @allure.step("Кликаю на иконку настроек")
    def click_settings_button(self):
        self.page.click(self.SETTINGS_BUTTON)



#фейковаю почту на один ищ аккаунтов зареганых на sptout