import os

import allure
from playwright.sync_api import Page


class HomePage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/"

    SETTINGS_ICON = ".sidebar-item.sidebar-item__active"
    SETTINGS_BUTTON = ".sidebar-item__label.sidebar__header-label"

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)


    @allure.step("Кликаю на иконку настроек")
    def click_settings_button(self):
        self.page.hover(self.SETTINGS_ICON)
        self.page.locator(self.SETTINGS_BUTTON).click()



#фейковаю почту на один ищ аккаунтов зареганых на sptout