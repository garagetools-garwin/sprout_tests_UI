import os
from multiprocessing.pool import CLOSE

import allure
from playwright.sync_api import Page
from dotenv import load_dotenv

load_dotenv()

TEST_BUYER_EMAIL = os.getenv("TEST_BUYER_EMAIL")
TEST_BUYER_PASSWORD = os.getenv("TEST_BUYER_PASSWORD")
TESTMAIL_ADRESS_ = os.getenv("TESTMAIL_ADRESS_")



class SettingsAccountPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/settings/account/user-list"

    USERS_BUTTON = ".ant-menu-title-content:has-text('Пользователи')"
    # Страница Пользователи
    ADD_USER_BUTTON = ".account-user-list-settings__filters .button-circle.primary"
    EMAIL_INPUT = "#email"
    LASTNAME_INPUT = "#lastName"
    FIRSTNAME_INPUT = "#firstName"
    PATRONYMIC_INPUT = "#patronymic"
    SEND_AN_INVATION_BUTTON = ".ant-drawer-content-wrapper button.ant-btn"
    USER_DELETE_BUTTON = "button.deleting"
    USER_TABLE_ROW = ".ant-table-row.ant-table-row-level-0"
    CONFIRM_DELETION_BUTTON = ".ant-btn.danger"
    SEARCH_INPUT = "input.ant-input.css-amq5gd"
    CLOSE_BUTTON = "button.ant-drawer-close"

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    @allure.step("Кликаю на крестик")
    def click_close_button(self):
        self.page.click(self.CLOSE_BUTTON)

    @allure.step("Закрываю модальное окно")
    def close_modal(self):
        self.page.mouse.click(50, 100)

    @allure.step("Кликаю на иконку Пользователи")
    def click_users_button(self):
        self.page.click(self.USERS_BUTTON)

    @allure.step("Кликаю на иконку Добавить пользователя")
    def click_add_user_button(self):
        self.page.click(self.ADD_USER_BUTTON)

    @allure.step("Добавляю пользователя")
    def add_user(self):
        self.click_add_user_button()
        self.page.type(self.EMAIL_INPUT, TESTMAIL_ADRESS_)
        self.page.type(self.LASTNAME_INPUT, "Тестовый")
        self.page.type(self.FIRSTNAME_INPUT, "Тест")
        self.page.click(self.SEND_AN_INVATION_BUTTON)
        return TEST_BUYER_EMAIL

    @allure.step("Кликаю на первого пользователя в списке")
    def click_first_user_table_row(self):
        self.page.click(self.USER_TABLE_ROW)

    @allure.step("Кликаю кнопку удаления пользователя")
    def click_user_delete_button(self):
        self.page.click(self.USER_DELETE_BUTTON)

    @allure.step("Кликаю кнопку удаления пользователя")
    def confirm_user_deletion(self):
        self.page.click(self.CONFIRM_DELETION_BUTTON)


    @allure.step("Удаляю последнего созданного пользователя")
    def delete_last_created_user(self):
        self.click_first_user_table_row()
        self.click_user_delete_button()
        self.confirm_user_deletion()

    @allure.step("Проверяю, есть ли пользователь по email")
    def is_user_present(self):
        self.page.fill(self.SEARCH_INPUT, TESTMAIL_ADRESS_)
        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(1000)
        return self.page.locator(self.USER_TABLE_ROW).count() > 0

        #TODO удалять по наименованию имейла


#TODO разделять настройки на 3 чтраници или писать все в одной, если в одной, то решить вопрос с PATH и open, возможно стоит сделать из 3 шт. Либо переходим в сетингс и все уже в рамках это страницы юзеры это дркгой класс
#фейковаю почту на один ищ аккаунтов зареганых на sptout