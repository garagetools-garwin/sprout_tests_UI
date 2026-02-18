import time
import allure
from playwright.sync_api import Page, expect


class PersonalLimitsSettingsPage:
    """Page Object для страницы Персональные лимиты (/settings/account/personal-limits)"""

    def __init__(self, page: Page):
        self.page = page

    PATH = "/settings/account/personal-limits"

    # Кнопка «+ Установить новый»
    ADD_NEW_BUTTON = "button:has-text('Установить новый')"

    # Поиск по пользователям на странице
    SEARCH_INPUT = "input[placeholder*='Введите имя, фамилию или e-mail']"

    # Строки пользователей с лимитами
    USER_ROW = ".ant-list-item, tr.ant-table-row.ant-table-row-level-0"
    USER_NAME_IN_ROW = ".ant-list-item-meta-title, .text-controls-accent"
    USER_EMAIL_IN_ROW = ".ant-list-item-meta-description, .text-body"
    USER_LIMIT_VALUE = ".ff-medium, .text-body:has-text('остаток за период')"

    # Кнопки действий в строке пользователя
    EDIT_BUTTON = "button[aria-label='edit'], .ant-btn-icon-only:has(svg), button:has(.anticon-edit)"
    DELETE_BUTTON = "button[aria-label='delete'], .ant-btn-icon-only:has(.anticon-delete)"

    # Пустой список
    EMPTY_LIST_TEXT = "text=Список пользователей пуст"

    # Toast-уведомления
    LIMIT_SET_TOAST = "text=/Персональный лимит сотрудника.*установлен/"
    LIMIT_CHANGED_TOAST = "text=/Персональный лимит сотрудника.*изменен/"
    LIMIT_DELETED_TOAST = "text=/Персональный лимит сотрудника.*удален/"

    @allure.step("Открываю страницу персональных лимитов")
    def open(self, base_url: str):
        return self.page.goto(base_url + self.PATH)

    @allure.step("Нажимаю '+ Установить новый'")
    def click_add_new(self):
        self.page.locator(self.ADD_NEW_BUTTON).click()
        self.page.wait_for_timeout(500)

    @allure.step("Ввожу поисковый запрос на странице: {query}")
    def search_user(self, query: str):
        self.page.locator(self.SEARCH_INPUT).fill(query)
        self.page.wait_for_timeout(1000)

    @allure.step("Очищаю поиск")
    def clear_search(self):
        self.page.locator(self.SEARCH_INPUT).fill("")
        self.page.wait_for_timeout(500)

    @allure.step("Получаю строки пользователей с лимитами")
    def get_user_rows(self):
        return self.page.locator(self.USER_ROW)

    @allure.step("Получаю количество пользователей с лимитами")
    def get_users_count(self) -> int:
        self.page.wait_for_load_state('networkidle')
        # Проверяем, не пуст ли список
        if self.page.locator(self.EMPTY_LIST_TEXT).is_visible():
            return 0
        return self.get_user_rows().count()

    @allure.step("Проверяю, что список пользователей пуст")
    def is_list_empty(self) -> bool:
        return self.page.locator(self.EMPTY_LIST_TEXT).is_visible()

    @allure.step("Нахожу строку пользователя по email: {email}")
    def find_user_row_by_email(self, email: str):
        """Возвращает локатор строки пользователя по email"""
        return self.page.locator(f"{self.USER_ROW}:has-text('{email}')")

    @allure.step("Проверяю наличие пользователя с email: {email}")
    def is_user_present(self, email: str) -> bool:
        return self.find_user_row_by_email(email).count() > 0

    @allure.step("Получаю отображаемый лимит пользователя с email: {email}")
    def get_user_limit_text(self, email: str) -> str:
        row = self.find_user_row_by_email(email)
        # Берём текст с суммой (правая часть строки)
        return row.inner_text()

    @allure.step("Нажимаю кнопку редактирования лимита у пользователя с email: {email}")
    def click_edit_user_limit(self, email: str):
        row = self.find_user_row_by_email(email)
        row.locator(self.EDIT_BUTTON).click()
        self.page.wait_for_timeout(500)

    @allure.step("Нажимаю кнопку удаления лимита у пользователя с email: {email}")
    def click_delete_user_limit(self, email: str):
        row = self.find_user_row_by_email(email)
        row.locator(self.DELETE_BUTTON).click()
        self.page.wait_for_timeout(500)

    @allure.step("Нажимаю кнопку редактирования лимита по индексу: {index}")
    def click_edit_by_index(self, index: int = 0):
        self.get_user_rows().nth(index).locator(self.EDIT_BUTTON).click()
        self.page.wait_for_timeout(500)

    @allure.step("Нажимаю кнопку удаления лимита по индексу: {index}")
    def click_delete_by_index(self, index: int = 0):
        self.get_user_rows().nth(index).locator(self.DELETE_BUTTON).click()
        self.page.wait_for_timeout(500)

    # === Проверки toast-уведомлений === #

    @allure.step("Проверяю toast об установке лимита")
    def is_limit_set_toast_visible(self) -> bool:
        try:
            self.page.wait_for_selector(
                self.LIMIT_SET_TOAST, state="visible", timeout=5000
            )
            return True
        except Exception:
            return False

    @allure.step("Проверяю toast об изменении лимита")
    def is_limit_changed_toast_visible(self) -> bool:
        try:
            self.page.wait_for_selector(
                self.LIMIT_CHANGED_TOAST, state="visible", timeout=5000
            )
            return True
        except Exception:
            return False

    @allure.step("Проверяю toast об удалении лимита")
    def is_limit_deleted_toast_visible(self) -> bool:
        try:
            self.page.wait_for_selector(
                self.LIMIT_DELETED_TOAST, state="visible", timeout=5000
            )
            return True
        except Exception:
            return False


class SelectEmployeeModal:
    """Модальное окно '1. Выберите сотрудника'"""

    def __init__(self, page: Page):
        self.page = page

    MODAL = ".ant-modal-content"
    TITLE = "text=Выберите сотрудника"
    SEARCH_INPUT = "input[placeholder*='Поиск по сотрудникам']"
    USER_ITEM = ".ant-modal-content .ant-list-item, .ant-modal-content .user-add-modal__list-item"
    USER_NAME = ".ant-list-item-meta-title"
    USER_EMAIL = ".ant-list-item-meta-description"
    SELECT_BUTTON = "button:has-text('Выбрать')"
    CANCEL_BUTTON = "button:has-text('Отмена')"

    @allure.step("Проверяю, что модалка выбора сотрудника открыта")
    def is_visible(self) -> bool:
        return self.page.locator(self.TITLE).is_visible()

    @allure.step("Ищу сотрудника: {query}")
    def search_employee(self, query: str):
        self.page.locator(self.SEARCH_INPUT).fill(query)
        self.page.wait_for_timeout(1000)

    @allure.step("Получаю элементы списка сотрудников")
    def get_employee_items(self):
        return self.page.locator(self.USER_ITEM)

    @allure.step("Получаю количество сотрудников в списке")
    def get_employees_count(self) -> int:
        return self.get_employee_items().count()

    @allure.step("Выбираю сотрудника по индексу: {index}")
    def select_employee_by_index(self, index: int = 0):
        self.get_employee_items().nth(index).click()
        self.page.wait_for_timeout(300)

    @allure.step("Выбираю сотрудника по email: {email}")
    def select_employee_by_email(self, email: str):
        self.page.locator(f"{self.USER_ITEM}:has-text('{email}')").click()
        self.page.wait_for_timeout(300)

    @allure.step("Нажимаю 'Выбрать'")
    def click_select(self):
        self.page.locator(self.SELECT_BUTTON).click()
        self.page.wait_for_timeout(500)

    @allure.step("Нажимаю 'Отмена'")
    def click_cancel(self):
        self.page.locator(self.CANCEL_BUTTON).click()
        self.page.wait_for_timeout(300)

    @allure.step("Выбираю сотрудника по email и подтверждаю")
    def select_and_confirm_by_email(self, email: str):
        self.select_employee_by_email(email)
        self.click_select()

    @allure.step("Выбираю сотрудника по индексу и подтверждаю")
    def select_and_confirm_by_index(self, index: int = 0):
        self.select_employee_by_index(index)
        self.click_select()


class SetLimitModal:
    """Модальное окно '2. Изменение персонального лимита'"""

    def __init__(self, page: Page):
        self.page = page

    MODAL = ".ant-modal-content"
    TITLE = "text=Изменение персонального лимита"
    LIMIT_INPUT = ".ant-modal-content input[type='text'], .ant-modal-content input.ant-input-number-input"
    SAVE_BUTTON = ".ant-modal-content button:has-text('Сохранить')"
    CANCEL_BUTTON = ".ant-modal-content button:has-text('Отмена')"
    CLOSE_BUTTON = ".ant-modal-content .ant-modal-close"
    REMAINING_LABEL = "text=Остаток за период"

    @allure.step("Проверяю, что модалка изменения лимита открыта")
    def is_visible(self) -> bool:
        return self.page.locator(self.TITLE).is_visible()

    @allure.step("Получаю текущее значение лимита из поля")
    def get_limit_value(self) -> str:
        return self.page.locator(self.LIMIT_INPUT).input_value()

    @allure.step("Устанавливаю значение лимита: {value}")
    def set_limit(self, value: str):
        limit_input = self.page.locator(self.LIMIT_INPUT)
        limit_input.click()
        limit_input.fill("")
        limit_input.fill(value)

    @allure.step("Нажимаю 'Сохранить'")
    def click_save(self):
        self.page.locator(self.SAVE_BUTTON).click()
        self.page.wait_for_timeout(1000)

    @allure.step("Нажимаю 'Отмена'")
    def click_cancel(self):
        self.page.locator(self.CANCEL_BUTTON).click()
        self.page.wait_for_timeout(300)

    @allure.step("Закрываю модалку крестиком")
    def click_close(self):
        self.page.locator(self.CLOSE_BUTTON).click()
        self.page.wait_for_timeout(300)

    @allure.step("Устанавливаю лимит и сохраняю: {value}")
    def set_and_save(self, value: str):
        self.set_limit(value)
        self.click_save()


class DeleteLimitModal:
    """Модальное окно подтверждения удаления лимита"""

    def __init__(self, page: Page):
        self.page = page

    CONFIRM_TEXT = "text=Вы уверены"
    CONFIRM_DELETE_BUTTON = ".button-lg.danger"
    CANCEL_BUTTON = "button:has-text('Отмена')"

    @allure.step("Проверяю, что окно подтверждения удаления открыто")
    def is_visible(self) -> bool:
        return self.page.locator(self.CONFIRM_TEXT).is_visible()

    @allure.step("Подтверждаю удаление")
    def confirm_delete(self):
        self.page.locator(self.CONFIRM_DELETE_BUTTON).click()
        self.page.wait_for_timeout(1000)

    @allure.step("Отменяю удаление")
    def cancel_delete(self):
        self.page.locator(self.CANCEL_BUTTON).click()
        self.page.wait_for_timeout(300)
