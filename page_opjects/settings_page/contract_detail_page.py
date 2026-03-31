# contract_detail_page.py

import allure
from playwright.sync_api import Page


class ContractDetailPage:
    """Навигация по вкладкам контракта + общие элементы."""

    def __init__(self, page: Page):
        self.page = page

    # Путь контракта — подставьте реальный ID
    PATH = "/settings/seller/contracts"  # + /CONTRACT_ID

    TAB_MANAGEMENT = "text=Управление контрактом"
    TAB_ASSORTMENT = "text=Ассортимент"
    TAB_DISCOUNTS = ".ant-menu-title-content:has-text('Скидки')"
    TAB_DELIVERY = "text=Сроки доставки"

    APPLYING_BANNER = "text=/Изменения применяются/"

    @allure.step("Открываю страницу контракта")
    def open(self, url: str):
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    @allure.step("Переключаюсь на «Управление контрактом»")
    def go_to_management_tab(self):
        self.page.locator(self.TAB_MANAGEMENT).click()
        self.page.wait_for_timeout(500)

    @allure.step("Переключаюсь на «Ассортимент»")
    def go_to_assortment_tab(self):
        self.page.locator(self.TAB_ASSORTMENT).click()
        self.page.wait_for_timeout(500)

    @allure.step("Переключаюсь на «Скидки»")
    def go_to_discounts_tab(self):
        self.page.locator(self.TAB_DISCOUNTS).click()
        self.page.wait_for_timeout(500)

    @allure.step("Переключаюсь на «Сроки доставки»")
    def go_to_delivery_tab(self):
        self.page.locator(self.TAB_DELIVERY).click()
        self.page.wait_for_timeout(500)

    @allure.step("Проверяю баннер 'Изменения применяются'")
    def is_applying_banner_visible(self) -> bool:
        return self.page.locator(self.APPLYING_BANNER).is_visible()

    def wait_for_applying_banner_gone(self, timeout: int = 300000):
        """Ждёт пока баннер 'Изменения применяются' исчезнет (до 5 мин)."""
        try:
            self.page.wait_for_selector(
                self.APPLYING_BANNER, state="hidden", timeout=timeout
            )
        except Exception:
            pass


class ContractManagementTab:
    """Вкладка «Управление контрактом»."""

    def __init__(self, page: Page):
        self.page = page

    ADD_MANAGER_BUTTON = "button:has-text('Добавить менеджера')"
    MANAGER_ROW = ".ant-table-row.ant-table-row-level-0"
    MANAGER_DELETE_ICON = "svg, button.button-icon"

    # Модалка выбора
    MODAL = ".ant-modal-content, .ant-drawer-content-wrapper"
    MODAL_SEARCH = ".ant-modal-content input, .ant-drawer-content input"
    MODAL_EMPLOYEE_ROW = ".user-add-modal__list-item"
    MODAL_SELECT_BUTTON = ".ant-modal-footer button.primary:has-text('Добавить')"
    MODAL_CANCEL_BUTTON = "button:has-text('Отмена')"

    MANAGER_ADDED_TOAST = "text=/менеджер.*добавлен/i"
    MANAGER_DELETED_TOAST = "text=/менеджер.*удал/i"

    @allure.step("Нажимаю «+ Добавить менеджера»")
    def click_add_manager(self):
        self.page.locator(self.ADD_MANAGER_BUTTON).click()
        self.page.wait_for_timeout(500)

    def get_managers_count(self) -> int:
        self.page.wait_for_timeout(500)
        return self.page.locator(self.MANAGER_ROW).count()

    def is_manager_present(self, email: str) -> bool:
        return self.page.locator(f"text={email}").is_visible()

    @allure.step("Удаляю менеджера «{email}»")
    def delete_manager(self, email: str):
        row = self.page.locator(f"{self.MANAGER_ROW}:has-text('{email}')")
        row.locator(self.MANAGER_DELETE_ICON).last.click()
        self.page.wait_for_timeout(500)

    def is_modal_visible(self) -> bool:
        return self.page.locator(self.MODAL).is_visible()

    @allure.step("Ищу «{query}» в модалке")
    def search_in_modal(self, query: str):
        self.page.locator(self.MODAL_SEARCH).first.fill(query)
        self.page.wait_for_timeout(500)

    @allure.step("Выбираю первого сотрудника")
    def select_first_employee(self):
        self.page.locator(self.MODAL_EMPLOYEE_ROW).first.click()
        self.page.wait_for_timeout(300)
        btn = self.page.locator(self.MODAL_SELECT_BUTTON)
        if btn.is_visible():
            btn.click()

    @allure.step("Отменяю")
    def cancel_modal(self):
        self.page.locator(self.MODAL_CANCEL_BUTTON).click()
        self.page.wait_for_timeout(300)

    def is_toast_added(self) -> bool:
        try:
            self.page.wait_for_selector(self.MANAGER_ADDED_TOAST, state="visible", timeout=5000)
            return True
        except Exception:
            return False

    def is_toast_deleted(self) -> bool:
        try:
            self.page.wait_for_selector(self.MANAGER_DELETED_TOAST, state="visible", timeout=5000)
            return True
        except Exception:
            return False


class ContractAssortmentTab:
    """Вкладка «Ассортимент»."""

    def __init__(self, page: Page):
        self.page = page

    CATEGORIES_BUTTON = "button:has-text('Настроить категории товаров')"
    BRANDS_BUTTON = "button:has-text('Настроить бренды')"
    RESET_BUTTON = "button:has-text('Сбросить настройки')"
    ADD_FEED_BUTTON = "button:has-text('Добавить кастомный фид')"

    # Модалки (общее)
    MODAL = ".ant-modal-content"
    SEARCH_INPUT = ".ant-modal-content input[type='text']"
    SAVE_BUTTON = ".ant-modal-content button:has-text('Сохранить')"
    CANCEL_BUTTON = ".ant-modal-content button:has-text('Отмена')"

    # Категории
    ALL_CATEGORIES_CHECKBOX = "text=Все категории"
    CATEGORY_NODE = ".ant-tree-treenode"
    CATEGORY_EXPAND = ".ant-tree-switcher"

    # Бренды
    ALL_BRANDS_CHECKBOX = "text=Все бренды"
    BRAND_ITEM = ".ant-modal-content .ant-checkbox-wrapper"

    @allure.step("Нажимаю «Настроить категории товаров»")
    def click_categories(self):
        self.page.locator(self.CATEGORIES_BUTTON).click()
        self.page.wait_for_timeout(500)

    @allure.step("Нажимаю «Настроить бренды»")
    def click_brands(self):
        self.page.locator(self.BRANDS_BUTTON).click()
        self.page.wait_for_timeout(500)

    def is_modal_visible(self) -> bool:
        return self.page.locator(self.MODAL).is_visible()

    @allure.step("Ищу «{query}» в модалке")
    def search_in_modal(self, query: str):
        inp = self.page.locator(self.SEARCH_INPUT).first
        inp.fill("")
        inp.fill(query)
        self.page.wait_for_timeout(500)

    def clear_search(self):
        inp = self.page.locator(self.SEARCH_INPUT).first
        inp.fill("")
        self.page.wait_for_timeout(500)

    @allure.step("Снимаю чекбокс «{name}»")
    def uncheck_item(self, name: str):
        item = self.page.locator(f".ant-modal-content .ant-checkbox-wrapper:has-text('{name}')")
        checkbox_input = item.locator(".ant-checkbox-input")
        if checkbox_input.is_checked():
            item.click()
        self.page.wait_for_timeout(300)

    @allure.step("Устанавливаю чекбокс «{name}»")
    def check_item(self, name: str):
        item = self.page.locator(f".ant-modal-content .ant-checkbox-wrapper:has-text('{name}')")
        checkbox_input = item.locator(".ant-checkbox-input")
        if not checkbox_input.is_checked():
            item.click()
        self.page.wait_for_timeout(300)

    def is_item_checked(self, name: str) -> bool:
        item = self.page.locator(f".ant-modal-content .ant-checkbox-wrapper:has-text('{name}')")
        return item.locator(".ant-checkbox-input").is_checked()

    @allure.step("Раскрываю категорию «{name}»")
    def expand_category(self, name: str):
        node = self.page.locator(f".ant-tree-treenode:has-text('{name}')")
        switcher = node.locator(self.CATEGORY_EXPAND)
        if switcher.is_visible():
            switcher.click()
        self.page.wait_for_timeout(300)

    def get_visible_items_count(self) -> int:
        return self.page.locator(
            f"{self.CATEGORY_NODE}, {self.BRAND_ITEM}"
        ).count()

    @allure.step("Сохраняю")
    def click_save(self):
        self.page.locator(self.SAVE_BUTTON).click()
        self.page.wait_for_timeout(500)

    @allure.step("Отменяю")
    def click_cancel(self):
        self.page.locator(self.CANCEL_BUTTON).click()
        self.page.wait_for_timeout(300)


class ContractDiscountsTab:
    """Вкладка «Скидки»."""

    def __init__(self, page: Page):
        self.page = page

    # Базовая скидка
    BASE_DISCOUNT_INPUT = "input[id*='discount'], input[type='number']"

    # Скидка на бренд — список
    ADD_BRAND_DISCOUNT_BUTTON = "button:has-text('Скидка на бренд')"
    BRAND_DISCOUNT_ROW = ".ant-table-row.ant-table-row-level-0"
    BRAND_DISCOUNT_ACTION_MENU = "button.button-icon"  # три точки

    # Меню: Настроить / Удалить скидку
    CONFIGURE_OPTION = "text=Настроить"
    DELETE_DISCOUNT_OPTION = "text=Удалить скидку"

    # Drawer «Настроить скидку»
    DRAWER = ".ant-drawer-content-wrapper"
    BRAND_SELECT = ".ant-drawer-content-wrapper .ant-select"
    BRAND_SEARCH_INPUT = ".ant-select-dropdown input, .ant-select-selection-search-input"
    BRAND_OPTION = ".ant-select-item.ant-select-item-option"
    DISCOUNT_VALUE_INPUT = ".ant-drawer-content-wrapper input[type='number'], .ant-drawer-content-wrapper input"
    SAVE_CHANGES_BUTTON = "button:has-text('Сохранить изменения')"
    DELETE_BUTTON_IN_DRAWER = "button:has-text('Удалить')"
    CLOSE_DRAWER = "button.ant-drawer-close"

    DISCOUNT_SAVED_TOAST = "text=/скидк.*сохран|сохран.*скидк|изменени.*сохран/i"

    def parse_price(price_str: str) -> float:
        """Парсит '1 151.00 ₽' → 1151.0"""
        cleaned = price_str.replace("₽", "").replace(" ", "").strip()
        # Остаётся '1151.00'
        return float(cleaned)

    @allure.step("Получаю значение базовой скидки")
    def get_base_discount(self) -> str:
        return self.page.locator(self.BASE_DISCOUNT_INPUT).first.input_value()

    @allure.step("Устанавливаю базовую скидку {value}%")
    def set_base_discount(self, value: str):
        inp = self.page.locator(self.BASE_DISCOUNT_INPUT).first
        inp.fill("")
        inp.fill(value)
        self.page.mouse.click(0, 0)
        self.page.wait_for_timeout(500)

    @allure.step("Нажимаю «+ Скидка на бренд»")
    def click_add_brand_discount(self):
        self.page.locator(self.ADD_BRAND_DISCOUNT_BUTTON).click()
        self.page.wait_for_timeout(500)

    def get_brand_discounts_count(self) -> int:
        return self.page.locator(self.BRAND_DISCOUNT_ROW).count()

    @allure.step("Открываю экшн-меню скидки на бренд (индекс {index})")
    def open_brand_discount_menu(self, index: int = 0):
        self.page.locator(self.BRAND_DISCOUNT_ROW).nth(index).locator(
            self.BRAND_DISCOUNT_ACTION_MENU
        ).click()
        self.page.wait_for_timeout(300)

    @allure.step("Нажимаю «Настроить»")
    def click_configure(self):
        self.page.locator(self.CONFIGURE_OPTION).click()
        self.page.wait_for_timeout(500)

    @allure.step("Нажимаю «Удалить скидку»")
    def click_delete_discount(self):
        self.page.locator(self.DELETE_DISCOUNT_OPTION).click()
        self.page.wait_for_timeout(500)

    def is_drawer_visible(self) -> bool:
        return self.page.locator(self.DRAWER).is_visible()

    @allure.step("Выбираю бренд «{brand}» в drawer")
    def select_brand_in_drawer(self, brand: str):
        self.page.locator(self.BRAND_SELECT).click()
        self.page.wait_for_timeout(300)
        search = self.page.locator(self.BRAND_SEARCH_INPUT).last
        search.fill(brand)
        self.page.wait_for_timeout(500)
        self.page.locator(f"{self.BRAND_OPTION}:has-text('{brand}')").click()
        self.page.wait_for_timeout(300)

    @allure.step("Устанавливаю скидку {value}% в drawer")
    def set_discount_in_drawer(self, value: str):
        inputs = self.page.locator(self.DISCOUNT_VALUE_INPUT)
        # Берём последний input (скидка), первый — это бренд
        discount_input = inputs.last
        discount_input.fill("")
        discount_input.fill(value)

    @allure.step("Сохраняю изменения в drawer")
    def save_drawer(self):
        self.page.locator(self.SAVE_CHANGES_BUTTON).click()
        self.page.wait_for_timeout(500)

    @allure.step("Удаляю скидку через drawer")
    def delete_in_drawer(self):
        self.page.locator(self.DELETE_BUTTON_IN_DRAWER).click()
        self.page.wait_for_timeout(500)

    @allure.step("Закрываю drawer")
    def close_drawer(self):
        self.page.locator(self.CLOSE_DRAWER).click()
        self.page.wait_for_timeout(300)

    def get_drawer_brand_value(self) -> str:
        return self.page.locator(self.BRAND_SELECT).text_content().strip()

    def get_drawer_discount_value(self) -> str:
        return self.page.locator(self.DISCOUNT_VALUE_INPUT).last.input_value()


class ContractDeliveryTab:
    """Вкладка «Сроки доставки»."""

    def __init__(self, page: Page):
        self.page = page

    WAREHOUSE_ITEM = ".ant-collapse-item, [class*='warehouse-item']"
    WAREHOUSE_HEADER = ".ant-collapse-header"
    ADDRESS_ROW = "[class*='address-item'], [class*='delivery-address']"

    DELIVERY_SELECT = ".ant-select, [class*='delivery-select']"
    DELIVERY_OPTION = ".ant-select-item.ant-select-item-option"

    ALL_OPTIONS = [
        "Не доставляется", "24 часа", "72 часа", "1 неделя",
        "2-3 недели", "1 месяц", "2-3 месяца", "4-6 месяцев",
    ]

    @allure.step("Получаю количество складов")
    def get_warehouses_count(self) -> int:
        self.page.wait_for_timeout(500)
        return self.page.locator(self.WAREHOUSE_ITEM).count()

    @allure.step("Раскрываю склад #{index}")
    def expand_warehouse(self, index: int = 0):
        self.page.locator(self.WAREHOUSE_HEADER).nth(index).click()
        self.page.wait_for_timeout(500)

    def get_addresses_count(self) -> int:
        return self.page.locator(self.ADDRESS_ROW).count()

    @allure.step("Открываю dropdown срока (адрес #{index})")
    def click_delivery_select(self, index: int = 0):
        self.page.locator(self.DELIVERY_SELECT).nth(index).click()
        self.page.wait_for_timeout(300)

    @allure.step("Выбираю «{option}»")
    def select_option(self, option: str):
        self.page.locator(f"{self.DELIVERY_OPTION}:has-text('{option}')").click()
        self.page.wait_for_timeout(300)

    def get_current_term(self, index: int = 0) -> str:
        return self.page.locator(self.DELIVERY_SELECT).nth(index).text_content().strip()

    @allure.step("Проверяю наличие всех опций сроков")
    def are_all_options_visible(self) -> bool:
        for opt in self.ALL_OPTIONS:
            if not self.page.locator(f"{self.DELIVERY_OPTION}:has-text('{opt}')").is_visible():
                return False
        return True
