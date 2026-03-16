# import time
# import allure
# from playwright.sync_api import Page, expect
#
#
# class LimitsPage:
#     """
#     Page Object для работы со всеми тремя уровнями лимитов.
#     Инкапсулирует навигацию и установку лимитов:
#       - Персональный лимит (страница personal-limits)
#       - Лимит подразделения (страница subdivision/{id}/general)
#       - Лимит компании (страница contracts)
#     """
#
#     def __init__(self, page: Page):
#         self.page = page
#
#     # ============================================================================
#     # ПУТИ
#     # ============================================================================
#
#     PERSONAL_LIMITS_PATH = "/settings/account/personal-limits"
#     CONTRACTS_PATH = "/settings/account/contracts"
#
#     # ============================================================================
#     # ЛОКАТОРЫ: ПЕРСОНАЛЬНЫЕ ЛИМИТЫ
#     # ============================================================================
#
#     PL_ADD_NEW_BUTTON = "button:has-text('Установить новый')"
#     PL_SEARCH_INPUT = "input[placeholder*='Введите имя, фамилию или e-mail']"
#     PL_USER_ROW = ".ant-list-item, tr.ant-table-row.ant-table-row-level-0"
#     PL_EMPTY_LIST = "text=Список пользователей пуст"
#     PL_ACTION_BUTTON = ".ant-btn.ant-btn-default.ant-btn-icon-only.button-icon"
#
#     # Модалка выбора сотрудника
#     PL_SELECT_MODAL_TITLE = "text=Выберите сотрудника"
#     PL_SELECT_SEARCH = "input[placeholder*='Поиск по сотрудникам']"
#     PL_SELECT_USER_ITEM = ".ant-modal-content .ant-list-item, .ant-modal-content .user-add-modal__list-item"
#     PL_SELECT_BUTTON = ".ant-modal-content button:has-text('Выбрать')"
#     PL_SELECT_CANCEL = ".ant-modal-content button:has-text('Отмена')"
#
#     # Модалка установки лимита
#     PL_LIMIT_MODAL_TITLE = "text=Изменение персонального лимита"
#     PL_LIMIT_INPUT = ".ant-modal-content input[type='text'], .ant-modal-content input.ant-input-number-input"
#     PL_LIMIT_SAVE = ".ant-modal-content button:has-text('Сохранить')"
#     PL_LIMIT_CANCEL = ".ant-modal-content button:has-text('Отмена')"
#     PL_LIMIT_CLOSE = ".ant-modal-content .ant-modal-close"
#     PL_REMAINING_LABEL = "text=Остаток за период"
#
#     # Модалка подтверждения удаления
#     PL_DELETE_CONFIRM_TEXT = "text=Вы уверены"
#     PL_DELETE_CONFIRM_BUTTON = "button:has-text('Снять лимит')"
#     PL_DELETE_CANCEL_BUTTON = "button:has-text('Отмена')"
#
#     # Toast
#     PL_TOAST_SET = "text=/Персональный лимит сотрудника.*установлен/"
#     PL_TOAST_DELETED = "text=/Персональный лимит сотрудника.*удален/"
#
#     # ============================================================================
#     # ЛОКАТОРЫ: ПОДРАЗДЕЛЕНИЕ
#     # ============================================================================
#
#     SUB_CHANGE_LIMIT_BUTTON = "text=Изменить лимиты"
#     SUB_PURCHASE_LIMIT_INPUT = "#balance"
#     SUB_ITEM_PRICE_LIMIT_INPUT = "#maxGoodPrice"
#     SUB_SAVE_BUTTON = ".ant-modal-content .button-sm.primary"
#     SUB_REMAINING_VALUE = "//span[contains(text(), 'Остаток за период')]/preceding-sibling::div"
#     SUB_TOTAL_VALUE = "//span[contains(text(), 'Общий лимит подразделения')]/preceding-sibling::div"
#     SUB_ITEM_PRICE_VALUE = "//span[contains(text(), 'Лимит цены на товар (включительно)')]/preceding-sibling::div"
#
#     # ============================================================================
#     # ЛОКАТОРЫ: КОМПАНИЯ (КОНТРАКТЫ)
#     # ============================================================================
#
#     COMPANY_ITEM_PRICE_INPUT = "#maxGoodPrice"
#
#     # ============================================================================
#     # ПЕРСОНАЛЬНЫЕ ЛИМИТЫ — МЕТОДЫ
#     # ============================================================================
#
#     @allure.step("Открываю страницу персональных лимитов")
#     def open_personal_limits(self, base_url: str):
#         self.page.goto(base_url + self.PERSONAL_LIMITS_PATH)
#         self.page.wait_for_load_state('networkidle')
#
#     @allure.step("Проверяю наличие пользователя с email: {email}")
#     def is_personal_limit_present(self, email: str) -> bool:
#         if self.page.locator(self.PL_EMPTY_LIST).is_visible():
#             return False
#         return self.page.locator(f"{self.PL_USER_ROW}:has-text('{email}')").count() > 0
#
#     @allure.step("Получаю количество пользователей с лимитами")
#     def get_personal_limits_count(self) -> int:
#         if self.page.locator(self.PL_EMPTY_LIST).is_visible():
#             return 0
#         return self.page.locator(self.PL_USER_ROW).count()
#
#     @allure.step("Получаю текущее значение персонального лимита для {email}")
#     def get_personal_limit_value(self, email: str) -> str:
#         """Нажимает карандаш, читает значение из модалки, закрывает модалку"""
#         row = self.page.locator(f"{self.PL_USER_ROW}:has-text('{email}')")
#         row.locator(self.PL_ACTION_BUTTON).nth(0).click()
#         self.page.wait_for_timeout(500)
#
#         value = self.page.locator(self.PL_LIMIT_INPUT).input_value()
#
#         self.page.locator(self.PL_LIMIT_CANCEL).click()
#         self.page.wait_for_timeout(300)
#         return value
#
#     @allure.step("Устанавливаю персональный лимит {value}₽ для {email}")
#     def set_personal_limit(self, base_url: str, email: str, value: str):
#         """Создаёт или обновляет персональный лимит"""
#         self.open_personal_limits(base_url)
#
#         if self.is_personal_limit_present(email):
#             # Редактирование — нажимаем карандаш (первая кнопка)
#             row = self.page.locator(f"{self.PL_USER_ROW}:has-text('{email}')")
#             row.locator(self.PL_ACTION_BUTTON).nth(0).click()
#             self.page.wait_for_timeout(500)
#         else:
#             # Создание
#             self.page.locator(self.PL_ADD_NEW_BUTTON).click()
#             self.page.wait_for_timeout(500)
#
#             # Выбираем сотрудника
#             self.page.locator(f"{self.PL_SELECT_USER_ITEM}:has-text('{email}')").click()
#             self.page.wait_for_timeout(300)
#             self.page.locator(self.PL_SELECT_BUTTON).click()
#             self.page.wait_for_timeout(500)
#
#         # Заполняем и сохраняем
#         limit_input = self.page.locator(self.PL_LIMIT_INPUT)
#         limit_input.click()
#         limit_input.fill("")
#         limit_input.fill(value)
#         self.page.locator(self.PL_LIMIT_SAVE).click()
#         self.page.wait_for_timeout(1000)
#
#     @allure.step("Удаляю персональный лимит для {email}")
#     def delete_personal_limit(self, base_url: str, email: str):
#         self.open_personal_limits(base_url)
#
#         if not self.is_personal_limit_present(email):
#             return
#
#         row = self.page.locator(f"{self.PL_USER_ROW}:has-text('{email}')")
#         row.locator(self.PL_ACTION_BUTTON).nth(1).click()
#         self.page.wait_for_timeout(500)
#
#         if self.page.locator(self.PL_DELETE_CONFIRM_TEXT).is_visible():
#             self.page.locator(self.PL_DELETE_CONFIRM_BUTTON).click()
#             self.page.wait_for_timeout(1000)
#
#     # ============================================================================
#     # ПОДРАЗДЕЛЕНИЕ — МЕТОДЫ
#     # ============================================================================
#
#     @allure.step("Открываю настройки подразделения {subdivision_id}")
#     def open_subdivision(self, base_url: str, subdivision_id: int):
#         self.page.goto(f"{base_url}/settings/subdivision/{subdivision_id}/general")
#         self.page.wait_for_load_state('networkidle')
#
#     @allure.step("Получаю текущий лимит на закупку подразделения")
#     def get_subdivision_purchase_limit(self) -> str:
#         text = self.page.locator(self.SUB_TOTAL_VALUE).inner_text()
#         return text.replace(" ₽", "").replace(" ", "").replace("\xa0", "").strip()
#
#     @allure.step("Получаю текущий лимит цены на товар подразделения")
#     def get_subdivision_item_price_limit(self) -> str:
#         text = self.page.locator(self.SUB_ITEM_PRICE_VALUE).inner_text()
#         return text.replace(" ₽", "").replace(" ", "").replace("\xa0", "").strip()
#
#     @allure.step("Получаю остаток лимита подразделения")
#     def get_subdivision_remaining(self) -> str:
#         text = self.page.locator(self.SUB_REMAINING_VALUE).inner_text()
#         return text.replace(" ₽", "").replace(" ", "").replace("\xa0", "").strip()
#
#     @allure.step("Устанавливаю лимит на закупку подразделения: {value}")
#     def set_subdivision_purchase_limit(self, base_url: str, subdivision_id: int, value: str):
#         self.open_subdivision(base_url, subdivision_id)
#         self.page.locator(self.SUB_CHANGE_LIMIT_BUTTON).click()
#         self.page.wait_for_timeout(300)
#         input_el = self.page.locator(self.SUB_PURCHASE_LIMIT_INPUT)
#         input_el.fill("")
#         input_el.fill(value)
#         self.page.locator(self.SUB_SAVE_BUTTON).click()
#         self.page.wait_for_timeout(1000)
#
#     @allure.step("Устанавливаю лимит цены на товар подразделения: {value}")
#     def set_subdivision_item_price_limit(self, base_url: str, subdivision_id: int, value: str):
#         self.open_subdivision(base_url, subdivision_id)
#         self.page.locator(self.SUB_CHANGE_LIMIT_BUTTON).click()
#         self.page.wait_for_timeout(300)
#         input_el = self.page.locator(self.SUB_ITEM_PRICE_LIMIT_INPUT)
#         input_el.fill("")
#         input_el.fill(value)
#         self.page.locator(self.SUB_SAVE_BUTTON).click()
#         self.page.wait_for_timeout(1000)
#
#     @allure.step("Очищаю лимит на закупку подразделения (пустое значение)")
#     def clear_subdivision_purchase_limit(self, base_url: str, subdivision_id: int):
#         self.open_subdivision(base_url, subdivision_id)
#         self.page.locator(self.SUB_CHANGE_LIMIT_BUTTON).click()
#         self.page.wait_for_timeout(300)
#         self.page.locator(self.SUB_PURCHASE_LIMIT_INPUT).fill("")
#         self.page.locator(self.SUB_SAVE_BUTTON).click()
#         self.page.wait_for_timeout(1000)
#
#     @allure.step("Очищаю лимит цены на товар подразделения (пустое значение)")
#     def clear_subdivision_item_price_limit(self, base_url: str, subdivision_id: int):
#         self.open_subdivision(base_url, subdivision_id)
#         self.page.locator(self.SUB_CHANGE_LIMIT_BUTTON).click()
#         self.page.wait_for_timeout(300)
#         self.page.locator(self.SUB_ITEM_PRICE_LIMIT_INPUT).fill("")
#         self.page.locator(self.SUB_SAVE_BUTTON).click()
#         self.page.wait_for_timeout(1000)
#
#     # ============================================================================
#     # КОМПАНИЯ (КОНТРАКТЫ) — МЕТОДЫ
#     # ============================================================================
#
#     @allure.step("Открываю страницу контрактов")
#     def open_contracts(self, base_url: str):
#         self.page.goto(base_url + self.CONTRACTS_PATH)
#         self.page.wait_for_load_state('networkidle')
#
#     @allure.step("Получаю текущий лимит цены за ед. товара компании")
#     def get_company_item_price_limit(self, base_url: str) -> str:
#         self.open_contracts(base_url)
#         return self.page.locator(self.COMPANY_ITEM_PRICE_INPUT).input_value()
#
#     @allure.step("Устанавливаю лимит цены за ед. товара компании: {value}")
#     def set_company_item_price_limit(self, base_url: str, value: str):
#         self.open_contracts(base_url)
#         input_el = self.page.locator(self.COMPANY_ITEM_PRICE_INPUT)
#         input_el.fill("")
#         input_el.fill(value)
#         self.page.mouse.click(0, 0)
#         self.page.wait_for_timeout(1000)
#
#     @allure.step("Очищаю лимит цены за ед. товара компании")
#     def clear_company_item_price_limit(self, base_url: str):
#         self.open_contracts(base_url)
#         self.page.locator(self.COMPANY_ITEM_PRICE_INPUT).fill("")
#         self.page.mouse.click(0, 0)
#         self.page.wait_for_timeout(1000)
#
#     # ============================================================================
#     # ПРОВЕРКИ В КОРЗИНЕ (АССЕРТЫ)
#     # ============================================================================
#
#     @allure.step("Проверяю: заказ заблокирован лимитом на сумму заказа")
#     def assert_blocked_by_purchase_limit(self, cart):
#         """Кнопка 'Отправить' скрыта + плашка 'превышает лимит на покупки'"""
#         expect(self.page.locator(cart.SEND_BUTTON)).not_to_be_visible()
#         expect(self.page.locator(cart.LIMIT_EXCEEDED_BANNER_2)).not_to_be_hidden(timeout=5000)
#
#     @allure.step("Проверяю: заказ заблокирован лимитом цены на товар")
#     def assert_blocked_by_item_price_limit(self, cart):
#         """Кнопка 'Отправить' disabled + плашка 'превышает лимит на цену товара'"""
#         expect(self.page.locator(cart.SEND_BUTTON)).to_be_disabled()
#         expect(self.page.locator(cart.LIMIT_EXCEEDED_BANNER)).not_to_be_hidden(timeout=5000)
#
#     @allure.step("Проверяю: заказ НЕ заблокирован")
#     def assert_not_blocked(self, cart):
#         """Кнопка enabled, обе плашки скрыты"""
#         self.page.wait_for_selector(cart.SEND_BUTTON, timeout=5000)
#         expect(self.page.locator(cart.SEND_BUTTON)).to_be_enabled()
#         expect(self.page.locator(cart.LIMIT_EXCEEDED_BANNER_2)).to_be_hidden(timeout=5000)
#         expect(self.page.locator(cart.LIMIT_EXCEEDED_BANNER)).to_be_hidden(timeout=5000)




import time
import allure
from playwright.sync_api import Page, expect


class LimitsPage:
    """
    Page Object для работы со всеми тремя уровнями лимитов.
    """

    def __init__(self, page: Page):
        self.page = page

    # ============================================================================
    # ПУТИ
    # ============================================================================

    PERSONAL_LIMITS_PATH = "/settings/account/personal-limits"
    CONTRACTS_PATH = "/settings/account/contracts"

    # ============================================================================
    # ЛОКАТОРЫ: ПЕРСОНАЛЬНЫЕ ЛИМИТЫ
    # ============================================================================

    PL_ADD_NEW_BUTTON = "button:has-text('Установить новый')"
    PL_SEARCH_INPUT = "input[placeholder*='Введите имя, фамилию или e-mail']"
    PL_USER_ROW = ".ant-list-item, tr.ant-table-row.ant-table-row-level-0"
    PL_EMPTY_LIST = "text=Список пользователей пуст"
    PL_ACTION_BUTTON = ".ant-btn.ant-btn-default.ant-btn-icon-only.button-icon"

    # Модалка выбора сотрудника
    PL_SELECT_MODAL_TITLE = "text=Выберите сотрудника"
    PL_SELECT_SEARCH = "input[placeholder*='Поиск по сотрудникам']"
    PL_SELECT_USER_ITEM = ".ant-modal-content .ant-list-item, .ant-modal-content .user-add-modal__list-item"
    PL_SELECT_BUTTON = ".ant-modal-content button:has-text('Выбрать')"
    PL_SELECT_CANCEL = ".ant-modal-content button:has-text('Отмена')"

    # Модалка установки лимита
    PL_LIMIT_MODAL_TITLE = "text=Изменение персонального лимита"
    PL_LIMIT_INPUT = ".ant-modal-content input[type='text'], .ant-modal-content input.ant-input-number-input"
    PL_LIMIT_SAVE = ".ant-modal-content button:has-text('Сохранить')"
    PL_LIMIT_CANCEL = ".ant-modal-content button:has-text('Отмена')"
    PL_LIMIT_CLOSE = ".ant-modal-content .ant-modal-close"
    PL_REMAINING_LABEL = "text=Остаток за период"

    # Модалка подтверждения удаления
    PL_DELETE_CONFIRM_TEXT = "text=Вы уверены"
    PL_DELETE_CONFIRM_BUTTON = "button:has-text('Снять лимит')"
    PL_DELETE_CANCEL_BUTTON = "button:has-text('Отмена')"

    # Toast
    PL_TOAST_SET = "text=/Персональный лимит сотрудника.*установлен/"
    PL_TOAST_DELETED = "text=/Персональный лимит сотрудника.*удален/"

    # ============================================================================
    # ЛОКАТОРЫ: ПОДРАЗДЕЛЕНИЕ
    # ============================================================================

    SUB_CHANGE_LIMIT_BUTTON = "text=Изменить лимиты"
    SUB_PURCHASE_LIMIT_INPUT = "#balance"
    SUB_ITEM_PRICE_LIMIT_INPUT = "#maxGoodPrice"
    SUB_SAVE_BUTTON = ".ant-modal-content .button-sm.primary"

    # ============================================================================
    # ЛОКАТОРЫ: КОМПАНИЯ (КОНТРАКТЫ)
    # ============================================================================

    COMPANY_ITEM_PRICE_INPUT = "#maxGoodPrice"

    # ============================================================================
    # ПЕРСОНАЛЬНЫЕ ЛИМИТЫ — МЕТОДЫ
    # ============================================================================

    @allure.step("Открываю страницу персональных лимитов")
    def open_personal_limits(self, base_url: str):
        self.page.goto(base_url + self.PERSONAL_LIMITS_PATH)
        self.page.wait_for_load_state('networkidle')

    @allure.step("Проверяю наличие пользователя с email: {email}")
    def is_personal_limit_present(self, email: str) -> bool:
        if self.page.locator(self.PL_EMPTY_LIST).is_visible():
            return False
        return self.page.locator(f"{self.PL_USER_ROW}:has-text('{email}')").count() > 0

    @allure.step("Получаю количество пользователей с лимитами")
    def get_personal_limits_count(self) -> int:
        if self.page.locator(self.PL_EMPTY_LIST).is_visible():
            return 0
        return self.page.locator(self.PL_USER_ROW).count()

    @allure.step("Устанавливаю персональный лимит {value}₽ для {email}")
    def set_personal_limit(self, base_url: str, email: str, value: str):
        """Создаёт или обновляет персональный лимит"""
        self.open_personal_limits(base_url)

        if self.is_personal_limit_present(email):
            row = self.page.locator(f"{self.PL_USER_ROW}:has-text('{email}')")
            row.locator(self.PL_ACTION_BUTTON).nth(0).click()
            self.page.wait_for_timeout(500)
        else:
            self.page.locator(self.PL_ADD_NEW_BUTTON).click()
            self.page.wait_for_timeout(500)
            self.page.locator(f"{self.PL_SELECT_USER_ITEM}:has-text('{email}')").click()
            self.page.wait_for_timeout(300)
            self.page.locator(self.PL_SELECT_BUTTON).click()
            self.page.wait_for_timeout(500)

        limit_input = self.page.locator(self.PL_LIMIT_INPUT)
        limit_input.click()
        limit_input.fill("")
        limit_input.fill(value)
        self.page.locator(self.PL_LIMIT_SAVE).click()
        self.page.wait_for_timeout(1000)

    @allure.step("Удаляю персональный лимит для {email}")
    def delete_personal_limit(self, base_url: str, email: str):
        self.open_personal_limits(base_url)

        if not self.is_personal_limit_present(email):
            return

        row = self.page.locator(f"{self.PL_USER_ROW}:has-text('{email}')")
        row.locator(self.PL_ACTION_BUTTON).nth(1).click()
        self.page.wait_for_timeout(500)

        if self.page.locator(self.PL_DELETE_CONFIRM_TEXT).is_visible():
            self.page.locator(self.PL_DELETE_CONFIRM_BUTTON).click()
            self.page.wait_for_timeout(1000)

    # ============================================================================
    # ПОДРАЗДЕЛЕНИЕ — МЕТОДЫ
    # ============================================================================

    @allure.step("Открываю настройки подразделения {subdivision_id}")
    def open_subdivision(self, base_url: str, subdivision_id: int):
        self.page.goto(f"{base_url}/settings/subdivision/{subdivision_id}/general")
        self.page.wait_for_load_state('networkidle')

    @allure.step("Устанавливаю лимиты подразделения: закупка={purchase}, цена товара={item_price}")
    def set_subdivision_limits(self, base_url: str, subdivision_id: int,
                                purchase: str = None, item_price: str = None):
        """
        Открывает одно модальное окно, заполняет оба поля и сохраняет один раз.
        Если значение None — поле не трогается.
        Если значение "" — поле очищается.
        """
        self.open_subdivision(base_url, subdivision_id)
        self.page.locator(self.SUB_CHANGE_LIMIT_BUTTON).click()
        self.page.wait_for_timeout(300)

        if purchase is not None:
            purchase_input = self.page.locator(self.SUB_PURCHASE_LIMIT_INPUT)
            purchase_input.fill("")
            purchase_input.fill(purchase)

        if item_price is not None:
            item_price_input = self.page.locator(self.SUB_ITEM_PRICE_LIMIT_INPUT)
            item_price_input.fill("")
            item_price_input.fill(item_price)

        self.page.locator(self.SUB_SAVE_BUTTON).click()
        self.page.wait_for_timeout(1000)

    # ============================================================================
    # КОМПАНИЯ (КОНТРАКТЫ) — МЕТОДЫ
    # ============================================================================

    @allure.step("Открываю страницу контрактов")
    def open_contracts(self, base_url: str):
        self.page.goto(base_url + self.CONTRACTS_PATH)
        self.page.wait_for_load_state('networkidle')

    @allure.step("Устанавливаю лимит цены за ед. товара компании: {value}")
    def set_company_item_price_limit(self, base_url: str, value: str):
        self.open_contracts(base_url)
        input_el = self.page.locator(self.COMPANY_ITEM_PRICE_INPUT)
        input_el.fill("")
        input_el.fill(value)
        self.page.mouse.click(0, 0)
        self.page.wait_for_timeout(1000)

    @allure.step("Очищаю лимит цены за ед. товара компании")
    def clear_company_item_price_limit(self, base_url: str):
        self.open_contracts(base_url)
        self.page.locator(self.COMPANY_ITEM_PRICE_INPUT).fill("")
        self.page.mouse.click(0, 0)
        self.page.wait_for_timeout(1000)

    # ============================================================================
    # ПРОВЕРКИ В КОРЗИНЕ
    # ============================================================================

    @allure.step("Проверяю: заказ заблокирован лимитом на сумму заказа")
    def assert_blocked_by_purchase_limit(self, cart):
        expect(self.page.locator(cart.SEND_BUTTON)).not_to_be_visible()
        expect(self.page.locator(cart.LIMIT_EXCEEDED_BANNER_2)).not_to_be_hidden(timeout=5000)

    @allure.step("Проверяю: заказ заблокирован лимитом цены на товар")
    def assert_blocked_by_item_price_limit(self, cart):
        expect(self.page.locator(cart.SEND_BUTTON)).to_be_disabled()
        expect(self.page.locator(cart.LIMIT_EXCEEDED_BANNER)).not_to_be_hidden(timeout=5000)

    @allure.step("Проверяю: заказ НЕ заблокирован")
    def assert_not_blocked(self, cart):
        self.page.wait_for_selector(cart.SEND_BUTTON, timeout=5000)
        expect(self.page.locator(cart.SEND_BUTTON)).to_be_enabled()
        expect(self.page.locator(cart.LIMIT_EXCEEDED_BANNER_2)).to_be_hidden(timeout=5000)
        expect(self.page.locator(cart.LIMIT_EXCEEDED_BANNER)).to_be_hidden(timeout=5000)