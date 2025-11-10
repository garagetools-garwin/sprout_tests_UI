# subdivisions_settings_page.py
import os
import time
import random
from faker import Faker
import allure
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

fake = Faker('ru_RU')
load_dotenv()
class SubdivisionModal:
    def __init__(self, page: Page):
        self.page = page

    MODAL = "div.ant-drawer-body"
    MODAL_EDIT = ".ant-modal-content"
    NAME_INPUT = "input#name"
    SAVE_BUTTON = "button:has-text('Добавить подразделение')"
    HEAD_SELECT = "span.ant-select-selection-search"
    HEAD_SELECT_G = "#rc_select_6"
    HEAD_SELECT_GG = 'span.ant-select-selection-placeholder:has-text("Выберите из списка юр. лиц компании")'
    LEGAL_ENTITY_SELECT_G = "#rc_select_7"
    LEGAL_ENTITY_SELECT = "span.ant-select-selection-search"
    FIRST_HEAD = ".text-controls-accent.mb-2.select-with-search__custom-option-user-name"
    FIRST_LEGAL_ENTITY = ".rc-virtual-list-holder-inner .ant-select-item.ant-select-item-option.ant-select-item-option-active"
    FIRST_UNSELECTED_HEAD = 'div.ant-select-dropdown.redesign.select-with-search.css-2nkxv5.ant-select-dropdown-placement-bottomLeft:not(.ant-select-dropdown-hidden) :is([role="option"])'
    # FIRST_UNSELECTED_HEAD = 'div.ant-select-dropdown :is([role="option"])'
    # FIRST_UNSELECTED_HEAD = "#rc_select_6_list_0"
    FIRST_UNSELECTED_LEGAL_ENTITY = 'div.ant-select-dropdown.redesign.select-with-search.css-2nkxv5.ant-select-dropdown-placement-bottomLeft:not(.ant-select-dropdown-hidden) :is([role="option"])'
    # FIRST_UNSELECTED_LEGAL_ENTITY = 'div.ant-select-dropdown :is([role="option"])'
    # FIRST_UNSELECTED_LEGAL_ENTITY = "#rc_select_7_list_0"

    DELETE_CONFIRM_BUTTON = ".button-lg.danger"
    NAME_TIP = "#name_help"

    @allure.step("Заполняю название подразделения: {name}")
    def fill_name(self, name):
        self.page.locator(self.NAME_INPUT).fill(name)

    @allure.step("Выбираю руководителя подразделения")
    def select_head(self, index=0):
        self.page.locator(self.HEAD_SELECT).first.click()
        self.page.locator(self.FIRST_HEAD).first.click()

    @allure.step("Выбираю юридическое лицо")
    def select_legal_entity(self, index=0):
        self.page.locator(self.LEGAL_ENTITY_SELECT).nth(1).click()
        self.page.locator(self.FIRST_LEGAL_ENTITY).nth(1).click()

    @allure.step("Заполняю название подразделения: {name}")
    def fill_name_child_subdivision(self, name):
        self.page.locator(self.NAME_INPUT).nth(1).fill(name)

    @allure.step("Выбираю руководителя подразделения")
    def select_head_child_subdivision(self, index=0):
        self.page.locator(self.MODAL).locator(self.HEAD_SELECT_G).nth(0).click(force=True)
        self.page.locator(self.FIRST_UNSELECTED_HEAD).nth(0).click()

    @allure.step("Выбираю юридическое лицо")
    def select_legal_entity_child_subdivision(self, index=0):
        self.page.locator(self.MODAL).locator(self.LEGAL_ENTITY_SELECT_G).nth(0).click(force=True)
        self.page.locator(self.FIRST_UNSELECTED_LEGAL_ENTITY).nth(0).click()

    @allure.step("Нажимаю Сохранить подразделение")
    def click_save(self):
        self.page.locator(self.SAVE_BUTTON).click()

    @allure.step("Нажимаю Сохранить подразделение")
    def click_save_child_subdivision(self):
        self.page.locator(self.SAVE_BUTTON).nth(1).click()

    @allure.step("Подтверждаю удаление подразделения")
    def confirm_delete(self):
        self.page.locator(self.DELETE_CONFIRM_BUTTON).click()

    @allure.step("Заполняю все поля подразделения")
    def fill_all_fields(self, name, head_index=0, legal_entity_index=0):
        self.fill_name(name)
        self.select_head(head_index)
        self.select_legal_entity(legal_entity_index)

    @allure.step("Заполняю все поля дочернего подразделения")
    def fill_all_fields_for_child_subdivision(self, name, head_index=0, legal_entity_index=0):
        self.fill_name_child_subdivision(name)
        self.select_head_child_subdivision(head_index)
        self.select_legal_entity_child_subdivision(legal_entity_index)

class SubdivisionsSettingsPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/settings/account/contracts"

    # Локаторы страницы Подразделения
    ADD_SUBDIVISION_BUTTON = "button.settings-sidebar__btn-create"
    SUBDIVISION_BAR = ".settings-sidebar__btn-title-container"
    SUBDIVISION_LIST_BUTTON = ".settings-sidebar__btn-container .ant-btn-default"
    CHILD_SUBDIVISION_LIST_BUTTON = ".ant-tree-switcher.ant-tree-switcher_close"
    SUBDIVISION_CARD = "span .ant-tree-title"
    ACTION_MENU_BUTTON = ".ant-btn-icon-only.ant-dropdown-trigger"
    DELETE_OPTION = ".ant-dropdown-menu-title-content:has-text('Удалить подразделение')"
    SUBDIVISION_NAME_INPUT = ".ant-modal input"
    SAVE_BUTTON = ".ant-modal-content .button-sm.primary"
    SUBDIVISION_NAME = ".subdivision-settings-name__value"
    USERS_BUTTON = ".ant-menu-title-content:has-text('Пользователи')"
    ADRESSES_BUTTON = ".ant-menu-title-content:has-text('Адреса доставки')"
    EDIT_NAME_BUTTON = ".subdivision-settings-name__edit-btn"


    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    @allure.step("Кликаю на крестик для добавления подразделения")
    def click_add_subdivision_button(self):
        self.page.locator(self.SUBDIVISION_BAR).hover()
        self.page.locator(self.ADD_SUBDIVISION_BUTTON).click()

    @allure.step("Кликаю на стрелочку для раскрытия листа подразделений")
    def click_subdivision_list_button(self):
        self.page.locator(self.SUBDIVISION_LIST_BUTTON).first.click()

    @allure.step("Кликаю на стрелочку для раскрытия листа дочерних подразделений")
    def click_child_subdivision_list_button(self):
        self.page.locator(self.CHILD_SUBDIVISION_LIST_BUTTON).first.click()

    @allure.step("Навожу на экшн меню подразделения")
    def hover_action_menu(self, index=0):
        self.page.locator(self.SUBDIVISION_CARD).nth(index).hover()
        self.page.locator(self.ACTION_MENU_BUTTON).nth(index).click()

    @allure.step("Навожу на экшн меню дочернего подразделения")
    def hover_action_menu_child_subdivision(self, new_name, index=0):
        self.page.locator(self.SUBDIVISION_CARD).filter(has_text=new_name).nth(index).hover()
        self.page.locator(self.ACTION_MENU_BUTTON).filter(visible=True).click()

    @allure.step("Открываю подразделение по индексу {index}")
    def open_subdivision(self, index=0):
        self.page.locator(self.SUBDIVISION_CARD).nth(index).click()

    @allure.step("Кликаю на карандаш редактирования названия")
    def click_edit_name_button(self):
        self.page.locator(self.EDIT_NAME_BUTTON).click()

    @allure.step("Генерирую уникальное название подразделения")
    def generate_unique_subdivision_name(self, prefix: str = "Подразделение") -> str:
        return f"{prefix} {int(time.time())}"

    @allure.step("Заполняю новое название компании")
    def fill_subdivision_name(self, value: str):
        self.page.fill(self.SUBDIVISION_NAME_INPUT, "")
        self.page.type(self.SUBDIVISION_NAME_INPUT, value)

    @allure.step("Сохраняю новое название компании")
    def click_save(self):
        self.page.locator(self.SAVE_BUTTON).click()
        self.page.wait_for_timeout(400)

    @allure.step("Проверяю, что название подразделения обновилось")
    def assert_subdivision_name_equals(self, expected: str):
        expect(self.page.locator(self.SUBDIVISION_NAME)).to_have_text(expected)

    @allure.step("Кликаю на вкладку Пользователи")
    def click_users_tab(self):
        self.page.locator(self.USERS_BUTTON).click()

    @allure.step("Кликаю на вкладку Адреса")
    def click_addresses_tab(self):
        self.page.locator(self.ADRESSES_BUTTON).click()

    @allure.step("Кликаю на опцию Удалить в меню")
    def click_delete_option(self):
        self.page.locator(self.DELETE_OPTION).click()

    def get_subdivision_cards(self):
        return self.page.locator(self.SUBDIVISION_CARD)

    @allure.step("Удаляю подразделение")
    def delete_subdivision(self,base_url):
        modal = SubdivisionModal(self.page)
        self.open(base_url)
        self.click_subdivision_list_button()
        initial_count = self.get_subdivision_cards().count()

        with allure.step("Открываю экшн меню и нажимаю Удалить"):
            self.hover_action_menu(0)
            self.click_delete_option()

        with allure.step("Подтверждаю удаление"):
            modal.confirm_delete()

        with allure.step("Проверяю, что подразделение удалено"):
            self.page.wait_for_timeout(2000)
            new_count = self.get_subdivision_cards().count()
            assert new_count < initial_count


    @allure.step("Удаляю подразделение")
    def delete_child_subdivision(self,base_url, new_name):
        modal = SubdivisionModal(self.page)
        self.open(base_url)
        self.click_subdivision_list_button()
        self.click_child_subdivision_list_button()

        with allure.step("Открываю экшн меню и нажимаю Удалить"):
            self.hover_action_menu_child_subdivision(new_name, 0)
            self.click_delete_option()

        with allure.step("Подтверждаю удаление"):
            modal.confirm_delete()

        with allure.step("Проверяю, что подразделение удалено"):
            self.page.wait_for_timeout(2000)
            time.sleep(3)
            assert not self.page.locator(f"text={new_name}").first.is_visible()

    LEGAL_ENTITY_LABEL = "label[for='legalId']"
    HEAD_LABEL = "label[for='headOfDepartmentId']"
    MANAGER_LABEL = "label[for='managerId']"

    FIRST_UNSELECTED_OPTION = ".ant-select-item.ant-select-item-option[label]:not(.ant-select-item-option-selected)"

    # XPath для подъема к родительскому ant-row
    ANCESTOR_ANT_ROW = "xpath=ancestor::div[contains(@class, 'ant-row')]"

    # Селектор для клика по селекту
    SELECT_SELECTION_ITEM = "span.ant-select-selection-item"

    # Видимый дропдаун
    VISIBLE_DROPDOWN = ".ant-select-dropdown:visible"

    CODE_INPUT = "input#code"
    CHILD_SUBDIVISION_BUTTON = "button:has-text('Дочернее подразделение')"
    DELETE_SUBDIVISION_BUTTON = "button:has-text('Удалить подразделение')"
    PURCHASE_LIMIT_INPUT = "#limit"
    PRICE_LIMIT_INPUT = "#maxGoodPrice"
    FIRST_UNSELECTED_HEAD = ".ant-select-item.ant-select-item-option[label]:not(.ant-select-item-option-selected)"
    FIRST_UNSELECTED_LEGAL_ENTITY = ".ant-select-item.ant-select-item-option[label][title]:not(.ant-select-item-option-selected)"
    FIRST_UNSELECTED_MANAGER_SELECT = ".ant-select-item.ant-select-item-option[label][title]:not(.ant-select-item-option-selected)"
    SUCCESS_MESSAGE = "text=Подразделение успешно изменено"

    @allure.step("Выбираю юридическое лицо")
    def select_legal_entity(self, index=0):
        # Находим label, поднимаемся к родительскому ant-row, затем кликаем по span.ant-select-selection-item
        legal_row = self.page.locator(self.LEGAL_ENTITY_LABEL).locator(self.ANCESTOR_ANT_ROW)
        legal_row.locator(self.SELECT_SELECTION_ITEM).click()
        # Выбираем невыбранный элемент
        self.page.locator(self.FIRST_UNSELECTED_OPTION).nth(index).click()
        # Ждем закрытия дропдауна
        self.page.wait_for_selector(self.SUCCESS_MESSAGE, state="visible", timeout=10000)

    @allure.step("Выбираю руководителя подразделения")
    def select_head(self, index=0):
        head_row = self.page.locator(self.HEAD_LABEL).locator(self.ANCESTOR_ANT_ROW)
        head_row.locator(self.SELECT_SELECTION_ITEM).click()

        # Ждем появления дропдауна и кликаем по опции внутри него
        dropdown = self.page.locator(self.VISIBLE_DROPDOWN)
        option = dropdown.locator(self.FIRST_UNSELECTED_OPTION).nth(index)
        option.wait_for(state="visible", timeout=3000)
        option.click()

    @allure.step("Выбираю менеджера по закупкам")
    def select_manager(self, index=0):
        manager_row = self.page.locator(self.MANAGER_LABEL).locator(self.ANCESTOR_ANT_ROW)
        manager_row.locator(self.SELECT_SELECTION_ITEM).click()

        # Ждем появления дропдауна и кликаем по опции внутри него
        dropdown = self.page.locator(self.VISIBLE_DROPDOWN)
        option = dropdown.locator(self.FIRST_UNSELECTED_OPTION).nth(index)
        option.wait_for(state="visible", timeout=3000)
        option.click()

    @allure.step("Ввожу код подразделения: {code}")
    def fill_code(self, code):
        self.page.locator(self.CODE_INPUT).fill(code)

    @allure.step("Нажимаю Дочернее подразделение")
    def click_add_child_subdivision(self):
        self.page.locator(self.CHILD_SUBDIVISION_BUTTON).click()

    @allure.step("Нажимаю Удалить подразделение")
    def click_delete_subdivision(self):
        self.page.locator(self.DELETE_SUBDIVISION_BUTTON).click()

    @allure.step("Устанавливаю лимит расходов: {limit}")
    def set_purchase_limit(self, limit):
        self.page.locator(self.PURCHASE_LIMIT_INPUT).fill("")
        self.page.locator(self.PURCHASE_LIMIT_INPUT).fill(limit)
        self.page.mouse.click(0, 0)

    @allure.step("Устанавливаю лимит цены за единицу товара")
    def set_item_price_limit(self, value: str):
        self.page.fill(self.PRICE_LIMIT_INPUT, "")
        self.page.fill(self.PRICE_LIMIT_INPUT, value)
        self.page.mouse.click(0, 0)

class SubdivisionUsersPage:
    def __init__(self, page: Page):
        self.page = page

    ADD_USER_BUTTON = ".button-circle.primary"
    ADD_USER_TEXT_BUTTON = "button:has-text('Добавить пользователя')"
    USER_CARD = ".ant-table-row.ant-table-row-level-0"

    @allure.step("Кликаю на + для добавления пользователя")
    def click_add_user_icon(self):
        self.page.locator(self.ADD_USER_BUTTON).click()

    @allure.step("Кликаю на кнопку Добавить пользователя")
    def click_add_user_button(self):
        self.page.locator(self.ADD_USER_TEXT_BUTTON).click()

    @allure.step("Открываю карточку пользователя по индексу {index}")
    def open_user_card(self, index=0):
        self.page.locator(self.USER_CARD).nth(index).click()

    def get_user_cards(self):
        return self.page.locator(self.USER_CARD)

class AddUserToSubdivisionModal:
    def __init__(self, page: Page):
        self.page = page

    MODAL = ".ant-modal-content"
    USER_SELECT = ".user-add-modal__list-item"
    ADD_BUTTON = ".button-sm.primary"
    CONFIRM_BUTTON = "button:has-text('Подтвердить')"
    CANCEL_BUTTON = "button:has-text('Отмена')"

    @allure.step("Выбираю пользователя по индексу {index}")
    def select_user(self, index=0):
        self.page.locator(self.USER_SELECT).nth(index).click()

    @allure.step("Нажимаю Добавить")
    def click_add(self):
        self.page.locator(self.ADD_BUTTON).click()
        if self.page.locator(self.CONFIRM_BUTTON).count() > 0:
            self.page.locator(self.CONFIRM_BUTTON).click()

    @allure.step("Нажимаю Добавить")
    def click_add_without_confirm(self):
        self.page.locator(self.ADD_BUTTON).click()

    @allure.step("Нажимаю Добавить")
    def click_cancel_button(self):
        self.page.locator(self.CANCEL_BUTTON).click()

class SubdivisionUserCard:
    def __init__(self, page: Page):
        self.page = page

    MODAL = "div.ant-drawer-content-wrapper"
    ROLE_BUTTON = ".user-card-role-selector"
    ALL_CHECKBOX = "input[type='checkbox']"
    UNBIND_BUTTON = "button:has-text('Отвязать')"
    EDIT_BUTTON = "button:has-text('Редактировать')"
    ADMIN_ROLE = "span.text=Администратор аккаунта"

    @allure.step("Нажимаю на кнопку выбора ролей")
    def click_role_button(self):
        self.page.locator(self.ROLE_BUTTON).click()

    @allure.step("Выбираю все роли")
    def select_all_roles(self):
        all_checkbox = self.page.locator(self.ALL_CHECKBOX).first
        if not all_checkbox.is_checked():
            all_checkbox.click()

    @allure.step("Нажимаю Отвязать")
    def click_unbind(self):
        self.page.locator(self.UNBIND_BUTTON).click()

    @allure.step("Нажимаю Редактировать")
    def click_edit(self):
        self.page.locator(self.EDIT_BUTTON).click()

    def is_admin_role_visible(self):
        return self.page.locator(self.ADMIN_ROLE).is_visible()

class SubdivisionAddressesPage:
    def __init__(self, page: Page):
        self.page = page

    ADD_ADDRESS_BUTTON = "button:has-text('Добавить адрес')"
    ADDRESS_CARD = "tr.ant-table-row.ant-table-row-level-0"
    ACTION_MENU = ".ant-table-content button.ant-btn-icon-only.ant-dropdown-trigger"
    EDIT_OPTION = "text=Редактировать"
    DELETE_OPTION = "text=Удалить"
    MAKE_PRIMARY_OPTION = "text=Сделать основным"
    PRIMARY_BADGE = ".text-tag.color-dark-grey:has-text('Основной адрес')"
    DELETE_CONFIRM_BUTTON = ".button-lg.danger"

    def get_all_address_cards(self):
        """Получить все адресные карточки"""
        return self.page.locator(self.ADDRESS_CARD)

    @allure.step("Нажимаю Добавить адрес")
    def click_add_address(self):
        self.page.locator(self.ADD_ADDRESS_BUTTON).click()

    @allure.step("Навожу на экшн меню адреса")
    def hover_address_action_menu(self, index=0):
        self.page.locator(self.ADDRESS_CARD).nth(index).hover()
        self.page.locator(self.ACTION_MENU).nth(index).click()

    @allure.step("Кликаю Редактировать")
    def click_edit_option(self):
        self.page.locator(self.EDIT_OPTION).click()

    @allure.step("Кликаю Удалить")
    def click_delete_option(self):
        self.page.locator(self.DELETE_OPTION).click()

    @allure.step("Кликаю Сделать основным")
    def click_make_primary_option(self):
        self.page.locator(self.MAKE_PRIMARY_OPTION).click()

    @allure.step("Подтверждаю удаление подразделения")
    def confirm_delete(self):
        self.page.locator(self.DELETE_CONFIRM_BUTTON).click()

    def get_address_cards(self):
        return self.page.locator(self.ADDRESS_CARD)

    def is_primary_badge_visible(self, card_index):  # ← ДОБАВЛЕН ПАРАМЕТР card_index
        """Проверить видимость плашки 'Основной адрес' у карточки"""
        card = self.get_all_address_cards().nth(card_index)
        return card.locator(self.PRIMARY_BADGE).is_visible()

    def get_address_cards_count(self):
        """Получить количество адресных карточек"""
        return self.get_all_address_cards().count()

    def get_card_text(self, card_index):
        """Получить текст карточки адреса"""
        card = self.get_all_address_cards().nth(card_index)
        return card.inner_text().strip()

    def find_current_primary_address(self):
        """Найти текущий основной адрес (с плашкой)"""
        count = self.get_address_cards_count()
        for i in range(count):
            if self.is_primary_badge_visible(i):
                return {
                    'index': i,
                    'text': self.get_card_text(i)
                }
        return None

    def find_first_non_primary_address(self):
        """Найти первый адрес без плашки 'Основной адрес'"""
        count = self.get_address_cards_count()
        for i in range(count):
            if not self.is_primary_badge_visible(i):
                return {
                    'index': i,
                    'text': self.get_card_text(i)
                }
        return None

    def set_address_as_primary(self, card_index):
        """Сделать адрес основным"""
        with allure.step(f"Устанавливаю адрес с индексом {card_index} как основной"):
            self.hover_address_action_menu(card_index)
            self.click_make_primary_option()

    def get_updated_address_text(self, card_index):
        """Получить обновлённый текст адреса (вторая строка)"""
        card = self.get_all_address_cards().nth(card_index)
        full_text = card.inner_text()
        return full_text.split("\n")[1].strip() if "\n" in full_text else full_text.strip()

    def verify_primary_badge_visible(self, card_index):
        """Проверить наличие плашки 'Основной адрес' у карточки"""
        card = self.get_all_address_cards().nth(card_index)
        badge_visible = card.locator(self.PRIMARY_BADGE).is_visible()
        assert badge_visible, f"Плашка 'Основной адрес' не отображается у карточки с индексом {card_index}"

class AddressModal:
    def __init__(self, page: Page):
        self.page = page

    MODAL = "div.ant-drawer-content-wrapper"
    SEARCH_ADRESS_INPUT = ".ant-input.css-2nkxv5.ant-select-selection-search-input"
    ADDRESS_INPUT = "textarea#name"
    CITY_INPUT = "input#city"
    POSTAL_CODE_INPUT = "input#postalCode"
    ADD_BUTTON = "button:has-text('Добавить адрес')"
    SAVE_BUTTON = "button:has-text('Сохранить изменения')"
    VALIDATION_ERROR = "text=Обязательное поле при сохранении."
    SUGGESTION_ITEM = ".ant-select-item.ant-select-item-option"

    @allure.step("Заполняю адрес: {address}")
    def fill_address(self, address):
        self.page.locator(self.ADDRESS_INPUT).fill(address)

    @allure.step("Заполняю адрес: {address}")
    def fill_all_fields_empty_data(self, address):
        self.page.locator(self.ADDRESS_INPUT).fill(address)
        self.page.locator(self.CITY_INPUT).fill(address)
        self.page.locator(self.POSTAL_CODE_INPUT).fill(address)

    @allure.step("Заполняю адрес: {address}")
    def fill_address_search(self, address):
        self.page.locator(self.SEARCH_ADRESS_INPUT).fill(address)

    @allure.step("Заполняю город: {city}")
    def fill_city(self, city):
        self.page.locator(self.CITY_INPUT).fill(city)

    @allure.step("Заполняю индекс: {postal_code}")
    def fill_postal_code(self, postal_code):
        self.page.locator(self.POSTAL_CODE_INPUT).fill(postal_code)

    @allure.step("Нажимаю Добавить адрес")
    def click_add(self):
        self.page.locator(self.MODAL).locator(self.ADD_BUTTON).click()

    @allure.step("Нажимаю Сохранить изменения")
    def click_save(self):
        self.page.locator(self.SAVE_BUTTON).click()

    @allure.step("Заполняю все поля адреса")
    def fill_all_fields(self, address, city, postal_code):
        self.fill_address(address)
        self.fill_city(city)
        self.fill_postal_code(postal_code)

    @allure.step("Выбираю первую подсказку адреса")
    def select_first_suggestion(self):
        self.page.locator(self.SUGGESTION_ITEM).first.click()

    def is_validation_error_visible(self):
        return self.page.locator(self.VALIDATION_ERROR).is_visible()
