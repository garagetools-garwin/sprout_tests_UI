import os
import time
from multiprocessing.pool import CLOSE
import random
from faker import Faker
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

fake = Faker('ru_RU')
load_dotenv()

TEST_BUYER_EMAIL = os.getenv("TEST_BUYER_EMAIL")
TEST_BUYER_PASSWORD = os.getenv("TEST_BUYER_PASSWORD")
TESTMAIL_ADRESS_ = os.getenv("TESTMAIL_ADRESS_")

class UsersSettingsPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/settings/account/user-list"

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
    SEARCH_INPUT = "input.ant-input.css-2nkxv5"
    CLOSE_BUTTON = "button.ant-drawer-close"
    USER_CARD = ".ant-table-row.ant-table-row-level-0"
    MODAL = 'div.ant-drawer-content-wrapper'
    ADMIN_BADGE = ".user-role-chip__name:has-text('Администратор аккаунта')"

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    @allure.step("Кликаю на крестик")
    def click_close_button(self):
        self.page.locator(self.CLOSE_BUTTON).click()
    @allure.step("Закрываю модальное окно")
    def close_modal(self):
        self.page.mouse.click(50, 100)

    @allure.step("Кликаю на иконку Добавить пользователя")
    def click_add_user_button(self):
        self.page.locator(self.ADD_USER_BUTTON).click()

    @allure.step("Добавляю пользователя")
    def add_user(self):
        self.click_add_user_button()
        self.page.type(self.EMAIL_INPUT, TESTMAIL_ADRESS_)
        self.page.type(self.LASTNAME_INPUT, "Тестовый")
        self.page.type(self.FIRSTNAME_INPUT, "Тест")
        self.page.locator(self.SEND_AN_INVATION_BUTTON).click()
        return TEST_BUYER_EMAIL

    @allure.step("Кликаю на первого пользователя в списке")
    def click_first_user_table_row(self):
        self.page.locator(self.USER_TABLE_ROW).nth(0).click()

    @allure.step("Кликаю кнопку удаления пользователя")
    def click_user_delete_button(self):
        self.page.locator(self.USER_DELETE_BUTTON).click()

    @allure.step("Кликаю кнопку удаления пользователя")
    def confirm_user_deletion(self):
        self.page.locator(self.CONFIRM_DELETION_BUTTON).click()


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

    def get_users_cards(self):
        return self.page.locator(self.USER_CARD)

    @allure.step("Открываю карточку пользователя по email {email}")
    def open_user_card_by_email(self, email):
        row = self.page.locator(f"{self.USER_CARD}:has-text('{email}')")
        row.click()

    @allure.step("Проверяю наличие плашки 'Администратор аккаунта' у пользователя в списке")
    def is_admin_badge_present(self, email):
        row = self.page.locator(f"{self.USER_CARD}:has-text('{email}')")
        return row.locator(self.ADMIN_BADGE).is_visible()


class UserModal:
    def __init__(self, page: Page):
        self.page = page

    EMAIL_INPUT = 'input#email'
    LASTNAME_INPUT = 'input#lastName'
    FIRSTNAME_INPUT = 'input#firstName'
    PATRONYMIC_INPUT = 'input#patronymic'
    POSITION_INPUT = "input#position"
    PHONE_INPUT = "input#phone"
    EMAIL_TIP = "#email_help"
    LASTNAME_TIP = '#lastName_help'
    FIRSTNAME_TIP = '#firstName_help'
    PATRONYMIC_TIP = 'input#patronymic'
    SEND_INVITE_BUTTON = "button:has-text('Отправить приглашение')"
    SAVE_BUTTON = "button:has-text('Сохранить')"
    MAIN_ROLE_BUTTON = ".user-card-role-selector"
    USER_CARD_ROLES_BLOCK = ".mb-11.d-flex.align-center.flex-wrap"

    ALL_CHECKBOX = "input[type='checkbox']"
    MANAGER_LINK = "a[href='/request-list/manager']"
    WORKSPACE_LIST_LINK = "a[href='/workspace-list']"
    HEAD_ROLE_LABEL = "label:has-text('Руководитель подразделения')"
    HEAD_ROLE_INPUT = ".ant-select-selection-search-input"
    DELETE_BUTTON = "button.deleting"


    @allure.step("Удаляю последнего созданного пользователя")
    def delete_last_created_user(self):
        self.click_first_user_table_row()
        self.click_user_delete_button()
        self.confirm_user_deletion()

    @allure.step("Заполняю обязательные поля заданными значениями")
    def fill_main_fields(self, email, last_name, first_name):
        self.page.locator(self.EMAIL_INPUT).fill(email)
        self.page.locator(self.LASTNAME_INPUT).fill(last_name)
        self.page.locator(self.FIRSTNAME_INPUT).fill(first_name)

    @allure.step("Заполняю все поля случайными значениями")
    def fill_in_data_randomize(self):
        # Генерируем данные
        last_name = fake.last_name()
        first_name = fake.first_name()
        patronymic = fake.middle_name()
        position = fake.job()
        phone = f"+7 ({random.randint(900, 999)}) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"

        self.page.locator(self.LASTNAME_INPUT).fill(last_name)
        self.page.locator(self.FIRSTNAME_INPUT).fill(first_name)
        self.page.locator(self.PATRONYMIC_INPUT).fill(patronymic)
        self.page.locator(self.POSITION_INPUT).fill(position)
        self.page.locator(self.PHONE_INPUT).fill(phone)

        return last_name, first_name, patronymic, position, phone

    @allure.step("Нажимаю Отправить приглашение")
    def click_send_invite(self):
        self.page.locator(self.SEND_INVITE_BUTTON).click()

    @allure.step("Нажимаю Сохранить")
    def click_save_button(self):
        self.page.locator(self.SAVE_BUTTON).click()

    @allure.step("Нажимаю Назначить роль")
    def click_main_role_button(self):
        self.page.locator(self.MAIN_ROLE_BUTTON).click()

    @allure.step("Дважды кликаю по чекбоксу Все, чтобы сбросить роли")
    def deselect_all_roles(self):
        all_checkbox = self.page.locator(self.ALL_CHECKBOX).first
        if not all_checkbox.is_checked():
            all_checkbox.click()
            all_checkbox.click()
        else:
            all_checkbox.click()

    @allure.step("Выбираю все роли (клик по чекбоксу Все)")
    def select_all_roles(self):
        all_checkbox = self.page.locator(self.ALL_CHECKBOX).first
        all_checkbox.click()

    @allure.step("Перехожу в подразделение и раскрываю поиск по 'Руководитель подразделения'")
    def open_head_role_selector(self):
        # Если есть кнопка очистки (ant-select-clear), кликаем по ней
        inp = self.page.locator(self.HEAD_ROLE_LABEL)
        inp.hover()
        clear_btn = self.page.locator('span.ant-select-clear')
        if clear_btn.count() > 0 and clear_btn.is_visible():
            clear_btn.hover()
            clear_btn.click()
        inp = inp.locator("xpath=../../..").locator(self.HEAD_ROLE_INPUT)
        inp.click()

    @allure.step("Перехожу по ссылке {url}")
    def go_to_url(self, url):
        self.page.goto(url)

    @allure.step("Открываю последнюю карточку пользователя")
    def open_last_user_card(self, cards):
        cards.last.click()

    @allure.step("Получаю блок ролей")
    def get_roles_block(self):
        return self.page.locator(self.USER_CARD_ROLES_BLOCK)

    @allure.step("Проверяю наличие ссылки на менеджера")
    def is_manager_link_visible(self):
        return self.page.locator(self.MANAGER_LINK).is_visible()

    @allure.step("Проверяю наличие ссылки карты оснащения")
    def is_workspace_list_link_visible(self):
        return self.page.locator(self.WORKSPACE_LIST_LINK).is_visible()

    @allure.step("Проверяю наличие админских прав путем перехода в настройки аккаунта")
    def transition_to_contracts_page_assertion(self, base_url):
        # Переход на нужную страницу
        self.page.goto(base_url + "/settings/account/contracts")

        # Явное ожидание, что URL изменился на нужный
        expect(self.page).to_have_url(base_url + "/settings/account/contracts", timeout=7000)

        # Проверка по заголовку страницы (если есть)
        expect(self.page.locator("span.ant-menu-title-content").first).to_contain_text(
            "Контракты")  # если заголовок "Контракты"

    @allure.step("Проверяю отсутствие админских прав путем перехода в настройки аккаунта")
    def transition_to_contracts_page_assertion_not(self, base_url):
        # Переход на нужную страницу
        self.page.goto(base_url + "/settings/account/contracts")

        time.sleep(2)
        # Явное ожидание, что URL изменился на нужный
        expect(self.page).not_to_have_url(base_url + "/settings/account/contracts", timeout=7000)




    @allure.step("Открываю страницу списка пользователей")
    def open(self, base_url):
        self.page.goto(f"{base_url}/settings/account/user-list")





    ROLES_BTN = "div:has-text('Назначить роль')"
    ADMIN_ROLE_CHECKBOX = "label:has-text('Администратор аккаунта') input[type='checkbox']"
    CLOSE_BTN = "button[aria-label='close'], .ant-modal-close"

    @allure.step("Открываю окно ролей")
    def open_roles(self):
        self.page.locator(self.ROLES_BTN).click()

    @allure.step("Включаю роль администратора")
    def set_admin_role(self):
        cb = self.page.locator(self.ADMIN_ROLE_CHECKBOX)
        if not cb.is_checked():
            cb.click()

    @allure.step("Отключаю роль администратора")
    def unset_admin_role(self):
        cb = self.page.locator(self.ADMIN_ROLE_CHECKBOX)
        if cb.is_checked():
            cb.click()

    @allure.step("Закрываю карточку пользователя")
    def close(self):
        self.page.locator(self.CLOSE_BTN).click()

    @allure.step("Проверяю, что роль администратора установлена внутри карточки")
    def is_admin_role_displayed_in_card(self):
        return self.page.locator("text=Администратор аккаунта").is_visible()

    @allure.step("Проверяю, что у root нельзя отключить роль администратора")
    def admin_role_is_not_toggleable(self):
        cb = self.page.locator(self.ADMIN_ROLE_CHECKBOX)
        # Проверяем, что чекбокс disabled
        assert cb.is_disabled(), "Чекбокс роли администратора должен быть неактивен для root"

    @allure.step("Проверяю, что root-пользователя нельзя удалить")
    def root_delete_button_is_disabled(self):
        delete_btn = self.page.locator(self.DELETE_BUTTON)
        assert delete_btn.is_disabled(), "Кнопка удаления должна быть неактивна для root"


        #TODO удалять по наименованию имейла


#TODO разделять настройки на 3 чтраници или писать все в одной, если в одной, то решить вопрос с PATH и open, возможно стоит сделать из 3 шт. Либо переходим в сетингс и все уже в рамках это страницы юзеры это дркгой класс
#фейковаю почту на один ищ аккаунтов зареганых на sptout