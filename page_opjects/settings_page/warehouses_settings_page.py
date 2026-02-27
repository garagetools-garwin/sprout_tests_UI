import time
import allure
from playwright.sync_api import Page
from faker import Faker

fake = Faker('ru_RU')


class WarehousesSettingsPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/settings/account/stock-list"

    # Страница Склады
    ADD_WAREHOUSE_BUTTON = "button:has-text('Добавить склад'), .button-circle.primary"
    WAREHOUSE_TABLE_ROW = ".ant-table-row.ant-table-row-level-0"
    SEARCH_INPUT = "input.ant-input"
    MODAL = "div.ant-drawer-content-wrapper"
    CLOSE_BUTTON = "button.ant-drawer-close"

    # Экшн-меню (как в SubdivisionAddressesPage)
    ACTION_MENU = ".ant-table-content button.ant-btn-icon-only.ant-dropdown-trigger"
    EDIT_OPTION = "text=Редактировать"
    DELETE_OPTION = "text=Удалить"

    # Фильтры
    FILTER_BUTTON = "button:has-text('Фильтр'), .filter-button"
    FILTER_INACTIVE = "text=Неактивны"
    FILTER_NOT_LINKED = "text=Не привязаны к подразделению"
    FILTER_CLEAR_ALL = "text=Очистить все"
    FILTER_TAG = ".ant-tag, .filter-tag"

    # Оповещения
    SUCCESS_TOAST = "text=/Новый склад.*добавлен/"
    EDIT_SUCCESS_TOAST = "text=/Склад.*изменен/"
    DELETE_SUCCESS_TOAST = "text=/Склад.*удален/"

    # Подтверждение удаления (как в SubdivisionAddressesPage)
    DELETE_CONFIRM_BUTTON = ".button-lg.danger"

    @allure.step("Открываю страницу складов")
    def open(self, base_url: str):
        return self.page.goto(base_url + self.PATH)

    @allure.step("Кликаю на кнопку 'Добавить склад'")
    def click_add_warehouse(self):
        self.page.locator(self.ADD_WAREHOUSE_BUTTON).click()
        self.page.wait_for_timeout(500)

    @allure.step("Получаю строки таблицы складов")
    def get_warehouse_rows(self):
        return self.page.locator(self.WAREHOUSE_TABLE_ROW)

    @allure.step("Получаю количество складов в списке")
    def get_warehouses_count(self) -> int:
        self.page.wait_for_load_state('networkidle')
        return self.page.locator(self.WAREHOUSE_TABLE_ROW).count()

    @allure.step("Проверяю, что модальное окно (drawer) открыто")
    def is_modal_visible(self) -> bool:
        return self.page.locator(self.MODAL).is_visible()

    @allure.step("Закрываю модальное окно кнопкой крестик")
    def close_modal(self):
        self.page.locator(self.CLOSE_BUTTON).click()
        self.page.wait_for_timeout(300)

    @allure.step("Закрываю модальное окно кликом вне окна")
    def close_modal_by_click_outside(self):
        self.page.locator(".ant-drawer-mask").click(position={"x": 10, "y": 10})
        self.page.wait_for_timeout(300)

    @allure.step("Ищу склад по названию: {query}")
    def search_warehouse(self, query: str):
        self.page.locator(self.SEARCH_INPUT).fill(query)
        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(1000)

    @allure.step("Проверяю наличие склада в списке: {name}")
    def is_warehouse_present(self, name: str) -> bool:
        return self.page.locator(f"{self.WAREHOUSE_TABLE_ROW}:has-text('{name}')").count() > 0

    # === Экшн-меню (по аналогии с SubdivisionAddressesPage) === #

    @allure.step("Навожу на экшн-меню склада с индексом {index}")
    def hover_action_menu(self, index=0):
        self.page.locator(self.WAREHOUSE_TABLE_ROW).nth(index).hover()
        self.page.locator(self.ACTION_MENU).nth(index).click()

    @allure.step("Кликаю 'Редактировать' в экшн-меню")
    def click_edit_option(self):
        self.page.locator(self.EDIT_OPTION).click()
        self.page.wait_for_timeout(500)

    @allure.step("Кликаю 'Удалить' в экшн-меню")
    def click_delete_option(self):
        self.page.locator(self.DELETE_OPTION).click()

    @allure.step("Подтверждаю удаление склада")
    def confirm_delete(self):
        self.page.locator(self.DELETE_CONFIRM_BUTTON).click()
        self.page.wait_for_timeout(1000)

    # === Оповещения === #

    @allure.step("Проверяю отображение оповещения об успешном добавлении")
    def is_success_toast_visible(self) -> bool:
        try:
            self.page.wait_for_selector(self.SUCCESS_TOAST, state="visible", timeout=5000)
            return True
        except Exception:
            return False

    @allure.step("Проверяю отображение оповещения об успешном редактировании")
    def is_edit_success_toast_visible(self) -> bool:
        try:
            self.page.wait_for_selector(self.EDIT_SUCCESS_TOAST, state="visible", timeout=5000)
            return True
        except Exception:
            return False

    @allure.step("Проверяю отображение оповещения об удалении")
    def is_delete_success_toast_visible(self) -> bool:
        try:
            self.page.wait_for_selector(self.DELETE_SUCCESS_TOAST, state="visible", timeout=5000)
            return True
        except Exception:
            return False

    # === Поиск индекса склада по имени === #

    @allure.step("Ищу индекс склада по названию: {name}")
    def find_warehouse_index_by_name(self, name: str) -> int:
        """Возвращает индекс строки склада по названию, или -1 если не найден"""
        rows = self.get_warehouse_rows()
        for i in range(rows.count()):
            if name in rows.nth(i).inner_text():
                return i
        return -1

    # === Открытие карточки через экшн-меню === #

    @allure.step("Открываю карточку склада через экшн-меню (Редактировать) по индексу {index}")
    def open_warehouse_card(self, index=0):
        """Hover → экшн-меню → Редактировать"""
        self.hover_action_menu(index)
        self.click_edit_option()

    @allure.step("Открываю карточку склада по названию: {name}")
    def open_warehouse_card_by_name(self, name: str):
        """Ищет склад по имени, открывает через экшн-меню → Редактировать"""
        index = self.find_warehouse_index_by_name(name)
        assert index >= 0, f"Склад '{name}' не найден в списке"
        self.open_warehouse_card(index)

    # === Удаление через экшн-меню === #

    @allure.step("Удаляю склад через экшн-меню по индексу {index}")
    def delete_warehouse_by_index(self, index=0):
        """Hover → экшн-меню → Удалить → подтверждение"""
        self.hover_action_menu(index)
        self.click_delete_option()

    @allure.step("Удаляю склад по названию: {name}")
    def delete_warehouse_by_name(self, name: str):
        """Ищет склад по имени, удаляет через экшн-меню"""
        index = self.find_warehouse_index_by_name(name)
        assert index >= 0, f"Склад '{name}' не найден в списке"
        self.delete_warehouse_by_index(index)

    # === Методы для фильтров === #

    @allure.step("Открываю фильтры")
    def open_filters(self):
        self.page.locator(self.FILTER_BUTTON).click()
        self.page.wait_for_timeout(300)

    @allure.step("Выбираю фильтр 'Неактивны'")
    def select_filter_inactive(self):
        self.page.locator(self.FILTER_INACTIVE).click()
        self.page.wait_for_timeout(500)

    @allure.step("Выбираю фильтр 'Не привязаны к подразделению'")
    def select_filter_not_linked(self):
        self.page.locator(self.FILTER_NOT_LINKED).click()
        self.page.wait_for_timeout(500)

    @allure.step("Очищаю все фильтры")
    def clear_all_filters(self):
        self.page.locator(self.FILTER_CLEAR_ALL).click()
        self.page.wait_for_timeout(500)

    @allure.step("Проверяю наличие плашки фильтра")
    def is_filter_tag_visible(self) -> bool:
        return self.page.locator(self.FILTER_TAG).is_visible()

    @allure.step("Получаю количество плашек фильтров")
    def get_filter_tags_count(self) -> int:
        return self.page.locator(self.FILTER_TAG).count()


class WarehouseModal:
    def __init__(self, page: Page):
        self.page = page

    MODAL = "div.ant-drawer-content-wrapper"

    # Поля формы
    NAME_INPUT = "input#name"
    CITY_INPUT = "input#city"
    POSTAL_CODE_INPUT = "input#postalCode"
    ADDRESS_INPUT = "textarea#address"

    # Автозаполнение адреса (как в AddressModal из subdivisions)
    ADDRESS_SEARCH_INPUT = ".ant-input.css-2nkxv5.ant-select-selection-search-input"
    SUGGESTION_ITEM = ".ant-select-item.ant-select-item-option"

    # Подсказки валидации
    NAME_HELP = "#name_help"
    ADDRESS_HELP = "#address_help"
    CITY_HELP = "#city_help"
    REQUIRED_FIELD_TEXT = "Обязательное поле при сохранении"

    # Кнопки
    ADD_BUTTON = "button:has-text('Добавить склад')"
    SAVE_BUTTON = "button:has-text('Сохранить изменения')"
    DELETE_BUTTON = "button:has-text('Удалить склад')"
    CLOSE_BUTTON = "button.ant-drawer-close"

    # Подтверждение удаления (как в SubdivisionAddressesPage)
    DELETE_CONFIRM_TEXT = "text=Вы уверены"
    DELETE_CONFIRM_BUTTON = ".button-lg.danger"
    CANCEL_DELETE_BUTTON = "button:has-text('Отмена')"
    # CANCEL_DELETE_BUTTON = ".ant-modal-content button:has-text('Отмена')"

    # Подтверждение закрытия при несохранённых изменениях
    CONFIRM_CLOSE_MODAL = "text=Не сохранять"
    DONT_SAVE_BUTTON = "button:has-text('Не сохранять')"

    # === Заполнение полей === #

    @allure.step("Заполняю поля склада: название={name}, адрес={address}, город={city}")
    def fill(self, name: str = None, address: str = None, city: str = None):
        if name is not None:
            self.page.locator(self.NAME_INPUT).fill(name)
        if address is not None:
            self.page.locator(self.ADDRESS_INPUT).fill(address)
        if city is not None:
            self.page.locator(self.CITY_INPUT).fill(city)

    @allure.step("Заполняю поля склада случайными данными")
    def fill_random(self) -> tuple:
        name = f"Тестовый склад {fake.random_number(digits=5)}"
        address = fake.street_address()
        city = fake.city()

        self.fill(name, address, city)
        return name, address, city

    @allure.step("Очищаю все поля")
    def clear_all(self):
        self.page.locator(self.NAME_INPUT).fill("")
        self.page.locator(self.ADDRESS_INPUT).fill("")
        self.page.locator(self.CITY_INPUT).fill("")

    # === Автозаполнение адреса (как в AddressModal) === #

    @allure.step("Ввожу адрес в поиск: {query}")
    def search_address(self, query: str):
        self.page.locator(self.ADDRESS_SEARCH_INPUT).fill(query)
        self.page.wait_for_timeout(2000)

    @allure.step("Проверяю, что подсказки адресов отображаются")
    def is_address_suggestions_visible(self) -> bool:
        return self.page.locator(self.SUGGESTION_ITEM).count() > 0

    @allure.step("Выбираю первый адрес из подсказок")
    def select_first_address_suggestion(self):
        self.page.locator(self.SUGGESTION_ITEM).first.click()
        self.page.wait_for_timeout(500)

    # === Кнопки === #

    @allure.step("Нажимаю 'Добавить склад'")
    def click_add(self):
        self.page.locator(self.MODAL).locator(self.ADD_BUTTON).click()
        self.page.wait_for_timeout(1000)

    @allure.step("Нажимаю 'Сохранить изменения'")
    def click_save(self):
        self.page.locator(self.SAVE_BUTTON).click()
        self.page.wait_for_timeout(1000)

    @allure.step("Нажимаю 'Удалить склад'")
    def click_delete(self):
        self.page.locator(self.DELETE_BUTTON).click()
        self.page.wait_for_timeout(500)

    @allure.step("Подтверждаю удаление склада")
    def confirm_delete(self):
        self.page.locator(self.DELETE_CONFIRM_BUTTON).click()
        self.page.wait_for_timeout(1000)

    @allure.step("Отменяю удаление склада")
    def cancel_delete(self):
        self.page.locator(self.CANCEL_DELETE_BUTTON).click()
        self.page.wait_for_timeout(500)

    @allure.step("Закрываю окно через крестик")
    def close(self):
        self.page.locator(self.CLOSE_BUTTON).click()
        self.page.wait_for_timeout(300)

    @allure.step("Нажимаю 'Не сохранять' в окне подтверждения")
    def click_dont_save(self):
        self.page.locator(self.DONT_SAVE_BUTTON).click()
        self.page.wait_for_timeout(500)

    # === Проверки валидации === #

    @allure.step("Проверяю отображение ошибки для поля 'Наименование'")
    def is_name_error_visible(self) -> bool:
        return self.page.locator(self.NAME_HELP).is_visible()

    @allure.step("Проверяю отображение ошибки для поля 'Адрес'")
    def is_address_error_visible(self) -> bool:
        return self.page.locator(self.ADDRESS_HELP).is_visible()

    @allure.step("Проверяю отображение ошибки для поля 'Город'")
    def is_city_error_visible(self) -> bool:
        return self.page.locator(self.CITY_HELP).is_visible()

    @allure.step("Проверяю, что окно подтверждения удаления открыто")
    def is_delete_confirmation_visible(self) -> bool:
        return self.page.locator(self.DELETE_CONFIRM_TEXT).is_visible()

    @allure.step("Проверяю, что окно подтверждения закрытия открыто")
    def is_close_confirmation_visible(self) -> bool:
        return self.page.locator(self.CONFIRM_CLOSE_MODAL).is_visible()

    # === Получение значений полей === #

    @allure.step("Получаю значение поля 'Наименование'")
    def get_name_value(self) -> str:
        return self.page.locator(self.NAME_INPUT).input_value()

    @allure.step("Получаю значение поля 'Адрес'")
    def get_address_value(self) -> str:
        return self.page.locator(self.ADDRESS_INPUT).input_value()

    @allure.step("Получаю значение поля 'Город'")
    def get_city_value(self) -> str:
        return self.page.locator(self.CITY_INPUT).input_value()

    @allure.step("Получаю значение поля 'Почтовый индекс'")
    def get_postal_code_value(self) -> str:
        return self.page.locator(self.POSTAL_CODE_INPUT).input_value()
