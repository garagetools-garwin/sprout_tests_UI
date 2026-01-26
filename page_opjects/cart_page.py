import os

import time
import allure
from playwright.sync_api import Page
from faker import Faker

fake = Faker('ru_RU')

class CartPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/basket"

    SEND_BUTTON = "button.button-lg.primary"
    MINI_CART_BADGE = "text=добавлен в корзину"
    LIMIT_EXCEEDED_BANNER = "text=Стоимость позиции превышает допустимый лимит на цену товара."
    LIMIT_EXCEEDED_BANNER_2 = "text=Ваш заказ превышает доступный лимит на покупки"
    OPTION_BUTTON = ".ant-dropdown-trigger.button-circle.secondary"
    CLEAR_CART_BUTTON = ".ant-dropdown-menu-item.ant-dropdown-menu-item-only-child"
    CONFIRM_CLEAR_CART_BUTTON = ".button-lg.danger"
    PRODUCT_ROW = ".ant-table-row.ant-table-row-level-0.ant-table-row-selected.expanded"

    ADDRESS_LABEL = "text=Адрес:"
    ADDRESS_CONTAINER = ".."
    ADDRESS_VALUE = ".ant-select-selection-item"

    # Локаторы шапки корзины
    # CART_TITLE = "h1:has-text('Корзина')"
    SELECT_ALL_BUTTON = ".mb-5 .ant-checkbox-input"
    # SELECT_ALL_BUTTON = "button:has-text('Выделить весь товар')"
    #
    # # Локаторы товара в корзине
    CART_ITEM = ".ant-table-row"
    CART_ITEM_CHECKBOX = "input[type='checkbox']"
    EXPANDED_ROW = ".ant-table-expanded-row.ant-table-expanded-row-level-1"
    BUYER_ARTICLE = ".ant-table-expanded-row.ant-table-expanded-row-level-1 .text-tag-accent.color-bright-green.buyer-code__value"
    # CART_ITEM_NAME = ".cart-item__name"
    CART_ITEM_PRICE = ".mb-2.ff-semibold.fs-m.text-nowrap"
    # CART_ITEM_QUANTITY_INPUT = "input[type='number']"
    # CART_ITEM_QUANTITY_PLUS = "button:has-text('+')"
    # CART_ITEM_QUANTITY_MINUS = "button:has-text('-')"
    # CART_ITEM_DELETE_BUTTON = ".ant-btn-icon-only[aria-label='delete']"
    # CART_ITEM_TOTAL_PRICE = ".cart-item__total"
    #
    # # Локаторы счетчика количества
    QUANTITY_INPUT = "input.ant-input-number-input"
    QUANTITY_PLUS_BUTTON = ".ant-btn.css-2nkxv5.ant-btn-default.ant-btn-icon-only.counter__btn"
    QUANTITY_MINUS_BUTTON = ".ant-btn.css-2nkxv5.ant-btn-default.ant-btn-icon-only.counter__btn"
    #
    # Локаторы удаления товара
    DELETE_BUTTON = "button.ant-btn.css-2nkxv5.ant-btn-default.button-text.dark-green"
    DELETE_MODAL = 'div.ant-drawer-content-wrapper  .drawer__title:has-text("Вы уверены, что хотите удалить товар?")'
    # DELETE_CONFIRM_MODAL = ".ant-modal-content"
    DELETE_CONFIRM_BUTTON = ".button-lg.danger"
    DELETE_CANCEL_BUTTON = "button:has-text('Отмена')"
    #
    # Локаторы быстрого добавления
    QUICK_ADD_BUTTON = "button.button-circle.primary"
    QUICK_ADD_MODAL = "div.ant-drawer-wrapper-body"
    QUICK_ADD_SEARCH_INPUT = "input.ant-input.css-2nkxv5"
    QUICK_ADD_ITEM_NAME = ".text-controls-accent.color-black.mb-5"
    QUICK_ADD_ITEM_ADD_BUTTON = "button.add-goods-card__goods"
    DROPDOWN_MENU = ".custom-dropdown"
    QUICK_ADD_ITEM_BUYER_ARTICLE = "div.ant-drawer-wrapper-body .text-tag-accent.color-bright-green.buyer-code__value"
    # QUICK_ADD_ITEM = ".product-list__item"
    #
    # # Локаторы меню корзины (три точки)
    # CART_MENU_BUTTON = "button.ant-dropdown-trigger"
    # CART_CODE_DISPLAY = ".cart-code"
    # COPY_CODE_BUTTON = "button:has-text('Копировать')"
    # CLEAR_CART_BUTTON = "button:has-text('Очистить корзину')"
    # CLEAR_CART_CONFIRM_BUTTON = "button:has-text('Очистить')"
    #
    # Локаторы блока калькуляции
    CALCULATION_BLOCK = "mb-6.ff-medium.fs-m:has-text('Общая информация')"
    GOODS_QUANTITY = ".ff-regular.fs-s:has-text('Товаров в заказе:') + .ff-regular.fs-s"
    GOODS_PRICE = ".ff-regular.fs-s:has-text('Стоимость товаров:') + .ff-regular.fs-s"
    VAT_AMOUNT = ".ff-regular.fs-s:has-text('Сумма НДС:') + .ff-regular.fs-s"
    TOTAL_WITH_VAT = ".ff-regular.fs-s:has-text('Итого с НДС:') + .ff-regular.fs-s"
    #
    # # Локаторы лимита
    # LIMIT_BLOCK = ".cart-limit"
    # LIMIT_TOTAL = ".cart-limit__total"
    # LIMIT_REMAINING = ".cart-limit__remaining"
    # LIMIT_BAR = ".cart-limit__bar"
    # LIMIT_EXCEEDED_BANNER = "text=Ваш заказ превышает доступный лимит на покупки"
    # LIMIT_EXCEEDED_BANNER_2 = ".ant-alert-warning:has-text('Ваш заказ превышает доступный лимит на покупки')"
    #
    # # Локаторы блока доставки
    # SUBDIVISION_SELECT = "#subdivision"
    # SUBDIVISION_OPTION = ".ant-select-item-option"
    # ADDRESS_SELECT = "#address"
    # ADDRESS_OPTION = ".ant-select-item-option"
    # LEGAL_ENTITY_SELECT = "#legalEntity"
    # LEGAL_ENTITY_OPTION = ".ant-select-item-option"
    #
    # # Локаторы комментария и отправки
    # COMMENT_INPUT = "textarea#comment"
    # SEND_BUTTON = "button:has-text('Отправить')"
    # SUCCESS_MESSAGE = "text=Заказ успешно отправлен"

    # Локаторы для лимита
    # LIMIT_BLOCK = ".limit-block"
    LIMIT_TOTAL_LOCATOR = "span.ff-regular.fs-xs.color-dark-grey:has-text('лимит на закупку')"
    LIMIT_REMAINING_LOCATOR = ".mb-4.d-flex.align-center.justify-between .ff-medium.fs-m:last-of-type"
    # ITEM_LINE_TOTAL = ".item-total-price"

    # === Методы для шапки корзины === #

    @allure.step("Нажимаю кнопку 'Выделить весь товар'")
    def click_select_all_button(self):
        self.page.locator(self.SELECT_ALL_BUTTON).click()
    #
    @allure.step("Получаю количество товаров в корзине")
    def get_cart_items_count(self):
        return self.page.locator(self.CART_ITEM).count()
    #
    @allure.step("Получаю состояние чекбокса товара {index}")
    def is_item_checkbox_checked(self, index=0):
        return self.page.locator(self.CART_ITEM).nth(index).locator(self.CART_ITEM_CHECKBOX).is_checked()
    #
    # # === Методы для работы с товаром === #
    #
    @allure.step("Снимаю чекбокс 'Включить в заказ' у товара {index}")
    def uncheck_item_checkbox(self, index=0):
        checkbox = self.page.locator(self.CART_ITEM).nth(index).locator(self.CART_ITEM_CHECKBOX)
        if checkbox.is_checked():
            checkbox.click()
            self.page.mouse.move(0, 0)
    #
    @allure.step("Устанавливаю чекбокс 'Включить в заказ' у товара {index}")
    def check_item_checkbox(self, index=0):
        checkbox = self.page.locator(self.CART_ITEM).nth(index).locator(self.CART_ITEM_CHECKBOX)
        if not checkbox.is_checked():
            checkbox.click()

    # # === Методы для счетчика количества === #
    #
    @allure.step("Увеличиваю количество товара {index} на {count} через кнопку +")
    def increase_quantity_by_button(self, index=0, count=1):
        for _ in range(count):
            self.page.locator(self.CART_ITEM).nth(index).locator(self.QUANTITY_PLUS_BUTTON).nth(1).click()
            time.sleep(0.3)

    @allure.step("Уменьшаю количество товара {index} на {count} через кнопку -")
    def decrease_quantity_by_button(self, index=0, count=1):
        for _ in range(count):
            self.page.locator(self.CART_ITEM).nth(index).locator(self.QUANTITY_MINUS_BUTTON).nth(0).click()
            time.sleep(0.3)

    @allure.step("Устанавливаю количество товара {index} вручную: {quantity}")
    def set_quantity_manually(self, index=0, quantity=1):
        quantity_input = self.page.locator(self.CART_ITEM).nth(index).locator(self.QUANTITY_INPUT)
        quantity_input.click()
        quantity_input.fill("")
        quantity_input.type(str(quantity))
        self.page.keyboard.press("Enter")
        time.sleep(0.5)
    #
    @allure.step("Получаю текущее количество товара {index}")
    def get_item_quantity(self, index=0):
        return int(self.page.locator(self.CART_ITEM).nth(index).locator(self.QUANTITY_INPUT).input_value())
    #
    # # === Методы для удаления товара === #
    #
    @allure.step("Нажимаю кнопку удаления товара {index}")
    def click_delete_item_button(self, index=0):
        self.page.locator(self.DELETE_BUTTON).nth(index).click()
    #
    # @allure.step("Проверяю отображение модального окна подтверждения удаления")
    # def is_delete_confirm_modal_visible(self):
    #     return self.page.locator(self.DELETE_CONFIRM_MODAL).is_visible()
    #
    @allure.step("Подтверждаю удаление товара")
    def confirm_delete_item(self):
        self.page.locator(self.DELETE_CONFIRM_BUTTON).click()

    @allure.step("Отменяю удаление товара")
    def cancel_delete_item(self):
        self.page.locator(self.DELETE_CANCEL_BUTTON).click()
    #
    # # === Методы для быстрого добавления === #

    @allure.step("Добавляю товар из окна быстрого добавления")
    def add_product_from_quick_add_modal(self):
        self.open_quick_add_modal()
        self.add_product_from_opened_quick_add_modal()

    @allure.step("Открываю модальное окно быстрого добавления")
    def open_quick_add_modal(self):
        self.page.locator(self.QUICK_ADD_BUTTON).click()

    @allure.step("Проверяю отображение модального окна быстрого добавления")
    def is_quick_add_modal_visible(self):
        return self.page.locator(self.QUICK_ADD_MODAL).is_visible()

    @allure.step("Проверяю что товар отображается в корзине")
    def is_product_row_visible(self):
        return self.page.locator(self.PRODUCT_ROW).is_visible()

    @allure.step("Ищу товар в модальном окне быстрого добавления: {query}")
    def search_in_quick_add(self, query):
        self.page.locator(self.QUICK_ADD_SEARCH_INPUT).fill(query)

    @allure.step("Получаю название первого товара в результатах поиска")
    def get_first_product_name(self):
        return self.page.locator(self.QUICK_ADD_ITEM_NAME).first.inner_text()

    @allure.step("Получаю артикул покупателя первого товара в результатах поиска")
    def get_first_buyer_articl(self):
        return self.page.locator(self.QUICK_ADD_ITEM_BUYER_ARTICLE).first.inner_text()

    @allure.step("Получаю локатор названия товара по индексу {index}")
    def get_product_name_locator(self, index=0):
        return self.page.locator(self.QUICK_ADD_ITEM_NAME).nth(index)

    @allure.step("Получаю локатор названия товара по индексу {index}")
    def add_product_from_opened_quick_add_modal(self, index=0):
        self.page.locator(self.QUICK_ADD_ITEM_ADD_BUTTON).nth(index).click()

    @allure.step("Получаю локатор артикула покупателя товара по индексу {index}")
    def get_product_buyer_article_locator(self, index=0):
        return self.page.locator(self.QUICK_ADD_ITEM_BUYER_ARTICLE).nth(index)
    #
    # @allure.step("Добавляю товар из модального окна быстрого добавления по индексу {index}")
    # def add_item_from_quick_add(self, index=0):
    #     self.page.locator(self.QUICK_ADD_ITEM).nth(index).click()
    #     time.sleep(1)
    #
    # # === Методы для меню корзины === #
    #
    # @allure.step("Открываю меню корзины")
    # def open_cart_menu(self):
    #     self.page.locator(self.CART_MENU_BUTTON).click()
    #
    # @allure.step("Нажимаю 'Очистить корзину'")
    # def click_clear_cart(self):
    #     self.page.locator(self.CLEAR_CART_BUTTON).click()
    #
    # @allure.step("Подтверждаю очистку корзины")
    # def confirm_clear_cart(self):
    #     self.page.locator(self.CLEAR_CART_CONFIRM_BUTTON).click()
    #     time.sleep(1)
    #
    # @allure.step("Очищаю корзину полностью")
    # def clear_cart(self, base_url):
    #     self.open(base_url)
    #     if self.get_cart_items_count() > 0:
    #         self.open_cart_menu()
    #         self.click_clear_cart()
    #         self.confirm_clear_cart()
    #
    # # === Методы для блока калькуляции === #
    #
    @allure.step("Получаю количество товаров из блока калькуляции")
    def get_calculation_quantity(self):
        text = self.page.locator(self.GOODS_QUANTITY).inner_text()
        return int(text.replace(" шт", "").strip())
    #
    @allure.step("Получаю стоимость товаров из блока калькуляции")
    def get_calculation_goods_price(self):
        text = self.page.locator(self.GOODS_PRICE).inner_text()
        return float(text.replace(" ₽", "").replace(" ", "").strip())

    @allure.step("Получаю сумму НДС из блока калькуляции")
    def get_calculation_vat(self):
        text = self.page.locator(self.VAT_AMOUNT).inner_text()
        return float(text.replace(" ₽", "").replace(" ", "").strip())

    @allure.step("Получаю итоговую сумму с НДС из блока калькуляции")
    def get_calculation_total(self):
        text = self.page.locator(self.TOTAL_WITH_VAT).inner_text()
        return float(text.replace(" ₽", "").replace(" ", "").strip())
    #
    # # === Методы для лимита === #
    #
    # @allure.step("Получаю общую сумму лимита")
    # def get_limit_total(self):
    #     text = self.page.locator(self.LIMIT_TOTAL).inner_text()
    #     return float(text.replace(" ₽", "").replace(" ", "").strip())
    #
    # @allure.step("Получаю оставшуюся сумму лимита")
    # def get_limit_remaining(self):
    #     text = self.page.locator(self.LIMIT_REMAINING).inner_text()
    #     return float(text.replace(" ₽", "").replace(" ", "").strip())
    #
    # @allure.step("Проверяю цвет полоски лимита (красная при превышении)")
    # def is_limit_exceeded(self):
    #     limit_bar_class = self.page.locator(self.LIMIT_BAR).get_attribute("class")
    #     return "red" in limit_bar_class or "exceeded" in limit_bar_class
    #
    # # === Методы для блока доставки === #
    #
    # @allure.step("Выбираю подразделение {index}")
    # def select_subdivision(self, index=0):
    #     self.page.locator(self.SUBDIVISION_SELECT).click()
    #     self.page.locator(self.SUBDIVISION_OPTION).nth(index).click()
    #     time.sleep(1)
    #
    # @allure.step("Выбираю адрес {index}")
    # def select_address(self, index=0):
    #     self.page.locator(self.ADDRESS_SELECT).click()
    #     self.page.locator(self.ADDRESS_OPTION).nth(index).click()
    #     time.sleep(0.5)
    #
    # @allure.step("Выбираю юридическое лицо {index}")
    # def select_legal_entity(self, index=0):
    #     self.page.locator(self.LEGAL_ENTITY_SELECT).click()
    #     self.page.locator(self.LEGAL_ENTITY_OPTION).nth(index).click()
    #     time.sleep(0.5)
    #
    # @allure.step("Проверяю, что адрес {address_text} отображается в корзине")
    # def verify_primary_address(self, address_text):
    #     expect(self.page.locator(self.ADDRESS_SELECT)).to_contain_text(address_text)
    #
    # # === Методы для отправки заказа === #
    #
    # @allure.step("Ввожу комментарий к заказу: {comment}")
    # def fill_comment(self, comment):
    #     self.page.locator(self.COMMENT_INPUT).fill(comment)
    #
    # @allure.step("Нажимаю кнопку 'Отправить'")
    # def click_send_button(self):
    #     self.page.locator(self.SEND_BUTTON).click()
    #
    @allure.step("Проверяю, что кнопка 'Отправить' активна")
    def is_send_button_enabled(self):
        return self.page.locator(self.SEND_BUTTON).is_enabled()
    #
    # @allure.step("Проверяю, что кнопка 'Отправить' неактивна")
    # def is_send_button_disabled(self):
    #     return self.page.locator(self.SEND_BUTTON).is_disabled()

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    @allure.step("Нажимаю на отправить")
    def click_send_button(self):
        self.page.locator(self.SEND_BUTTON).click()

    @allure.step("Очищаю корзину")
    def clear_cart(self, base_url):
        self.open(base_url)
        self.click_option_button()
        if self.page.locator(self.CLEAR_CART_BUTTON).is_enabled():
            self.click_clear_cart_button()
            self.clear_confirm__clear_cart_button()
        else:
            pass

    @allure.step("Нажимаю на кнопку меню")
    def click_option_button(self):
        self.page.locator(self.OPTION_BUTTON).click()

    @allure.step("Нажимаю на Очистить корзину")
    def click_clear_cart_button(self):
        self.page.locator(self.CLEAR_CART_BUTTON).click()

    @allure.step("Подтверждаю очистку корзины")
    def clear_confirm__clear_cart_button(self):
        self.page.locator(self.CONFIRM_CLEAR_CART_BUTTON).click()

    def get_primary_address_text(self):
        """Получить текст основного адреса из корзины"""
        container = self.page.locator(self.ADDRESS_LABEL).locator(self.ADDRESS_CONTAINER)
        return container.locator(self.ADDRESS_VALUE).inner_text()

    def verify_primary_address(self, expected_address):
        """Проверить, что в корзине отображается ожидаемый основной адрес"""
        actual_address = self.get_primary_address_text()
        assert actual_address == expected_address, \
            f"В корзине отображается неверный адрес. Ожидалось: '{expected_address}', Получено: '{actual_address}'"

    #
    # @allure.step("Добавляю товар в корзину")
    # def get_primary_address_text(self):
    #     adress =



    @allure.step("Добавляю товар в корзину")
    def add_to_cart(self):
        self.click_first_product()
        self.click_add_to_cart_button()

    # Карточка товара

    @allure.step("Нажимаю на добавить товар в корзину")
    def click_add_to_cart_button(self):
        self.page.locator(self.ADD_TO_CART_BUTTON).click()

    @allure.step("Получаю общую сумму лимита")
    def get_limit_total(self):
        text = self.page.locator(self.LIMIT_TOTAL_LOCATOR).inner_text()
        return float(text.replace(" ₽", "").replace(" ", "").replace("₽", "").replace("лимитназакупку", "").strip())

    @allure.step("Получаю оставшуюся сумму лимита")
    def get_limit_remaining(self):
        text = self.page.locator(self.LIMIT_REMAINING_LOCATOR).inner_text()
        return float(text.replace(" ₽", "").replace(" ", "").replace("₽", "").strip())

    @allure.step("Получаю итоговую стоимость товара {index}")
    def get_item_line_total(self, index=0):
        text = self.page.locator(self.CART_ITEM).nth(index).locator(self.CART_ITEM_PRICE).inner_text()
        return float(text.replace(" ₽", "").replace(" ", "").strip())



    #TODO перевести карточку товара в отдельный класс


# cart_page.py - добавить локаторы и методы

    # ... существующие локаторы ...

    # Локаторы для блока "Детали доставки"
    # SUBDIVISION_SELECT = ".ant-select:has(.ant-select-selection-item):near(:text('Подразделение'))"
    # SUBDIVISION_DROPDOWN = ".ant-select-dropdown"
    # SUBDIVISION_OPTION = ".ant-select-item-option"
    SUBDIVISION_SELECTED_VALUE = ".ant-select-selection-item"
    #
    # ADDRESS_SELECT = ".ant-select:has(.ant-select-selection-item):near(:text('Адрес'))"
    # ADDRESS_DROPDOWN = ".ant-select-dropdown"
    # ADDRESS_OPTION = ".ant-select-item-option"
    # ADDRESS_SELECTED_VALUE = ".ant-select-selection-item"
    #
    # LEGAL_ENTITY_SELECT = ".ant-select:has(.ant-select-selection-item):near(:text('Юридическое лицо'))"
    # LEGAL_ENTITY_DROPDOWN = ".ant-select-dropdown"
    # LEGAL_ENTITY_OPTION = ".ant-select-item-option"
    # LEGAL_ENTITY_SELECTED_VALUE = ".ant-select-selection-item"
    #
    # # Локаторы для подразделения в шапке
    # DELIVERY_DETAILS_BLOCK = "text=Детали доставки"
    # SUBDIVISION_FIELD = "text=Подразделение (место возникновения затрат):"
    # ADDRESS_FIELD = "text=Адрес:"
    # LEGAL_ENTITY_FIELD = "text=Юридическое лицо:"
    #
    # # === Методы для работы с подразделениями === #
    #
    @allure.step("Получаю текущее выбранное подразделение")
    def get_selected_subdivision(self):
        return self.page.locator(self.SUBDIVISION_SELECT).locator(self.SUBDIVISION_SELECTED_VALUE).inner_text()
    #
    # @allure.step("Открываю список подразделений")
    # def open_subdivision_dropdown(self):
    #     self.page.locator(self.SUBDIVISION_SELECT).click()
    #     self.page.wait_for_selector(self.SUBDIVISION_DROPDOWN, state="visible")
    #
    # @allure.step("Проверяю, что список подразделений отображается")
    # def is_subdivision_dropdown_visible(self):
    #     return self.page.locator(self.SUBDIVISION_DROPDOWN).is_visible()
    #
    # @allure.step("Получаю список подразделений из выпадающего списка")
    # def get_subdivision_options(self):
    #     options = self.page.locator(f"{self.SUBDIVISION_DROPDOWN} {self.SUBDIVISION_OPTION}")
    #     return [opt.inner_text() for opt in options.all()]
    #
    # @allure.step("Выбираю подразделение: {subdivision_name}")
    # def select_subdivision(self, subdivision_name: str):
    #     self.open_subdivision_dropdown()
    #     self.page.locator(f"{self.SUBDIVISION_DROPDOWN} {self.SUBDIVISION_OPTION}").filter(
    #         has_text=subdivision_name).click()
    #     time.sleep(1)
    #
    # @allure.step("Выбираю подразделение по индексу: {index}")
    # def select_subdivision_by_index(self, index: int):
    #     self.open_subdivision_dropdown()
    #     self.page.locator(f"{self.SUBDIVISION_DROPDOWN} {self.SUBDIVISION_OPTION}").nth(index).click()
    #     time.sleep(1)
    #
    # # === Методы для работы с адресами === #
    #
    # @allure.step("Получаю текущий выбранный адрес")
    # def get_selected_address(self):
    #     return self.page.locator(self.ADDRESS_SELECT).locator(self.ADDRESS_SELECTED_VALUE).inner_text()
    #
    # @allure.step("Открываю список адресов")
    # def open_address_dropdown(self):
    #     self.page.locator(self.ADDRESS_SELECT).click()
    #     self.page.wait_for_selector(self.ADDRESS_DROPDOWN, state="visible")
    #
    # @allure.step("Проверяю, что список адресов отображается")
    # def is_address_dropdown_visible(self):
    #     return self.page.locator(self.ADDRESS_DROPDOWN).is_visible()
    #
    # @allure.step("Получаю список адресов из выпадающего списка")
    # def get_address_options(self):
    #     options = self.page.locator(f"{self.ADDRESS_DROPDOWN} {self.ADDRESS_OPTION}")
    #     return [opt.inner_text() for opt in options.all()]
    #
    # @allure.step("Выбираю адрес: {address_name}")
    # def select_address(self, address_name: str):
    #     self.open_address_dropdown()
    #     self.page.locator(f"{self.ADDRESS_DROPDOWN} {self.ADDRESS_OPTION}").filter(has_text=address_name).click()
    #     time.sleep(1)
    #
    # @allure.step("Выбираю адрес по индексу: {index}")
    # def select_address_by_index(self, index: int):
    #     self.open_address_dropdown()
    #     self.page.locator(f"{self.ADDRESS_DROPDOWN} {self.ADDRESS_OPTION}").nth(index).click()
    #     time.sleep(1)
    #
    # # === Методы для работы с юридическими лицами === #
    #
    # @allure.step("Получаю текущее выбранное юридическое лицо")
    # def get_selected_legal_entity(self):
    #     return self.page.locator(self.LEGAL_ENTITY_SELECT).locator(self.LEGAL_ENTITY_SELECTED_VALUE).inner_text()
    #
    # @allure.step("Открываю список юридических лиц")
    # def open_legal_entity_dropdown(self):
    #     self.page.locator(self.LEGAL_ENTITY_SELECT).click()
    #     self.page.wait_for_selector(self.LEGAL_ENTITY_DROPDOWN, state="visible")
    #
    # @allure.step("Проверяю, что список юридических лиц отображается")
    # def is_legal_entity_dropdown_visible(self):
    #     return self.page.locator(self.LEGAL_ENTITY_DROPDOWN).is_visible()
    #
    # @allure.step("Получаю список юридических лиц из выпадающего списка")
    # def get_legal_entity_options(self):
    #     options = self.page.locator(f"{self.LEGAL_ENTITY_DROPDOWN} {self.LEGAL_ENTITY_OPTION}")
    #     return [opt.inner_text() for opt in options.all()]
    #
    # @allure.step("Выбираю юридическое лицо: {entity_name}")
    # def select_legal_entity(self, entity_name: str):
    #     self.open_legal_entity_dropdown()
    #     self.page.locator(f"{self.LEGAL_ENTITY_DROPDOWN} {self.LEGAL_ENTITY_OPTION}").filter(
    #         has_text=entity_name).click()
    #     time.sleep(1)
    #
    # @allure.step("Выбираю юридическое лицо по индексу: {index}")
    # def select_legal_entity_by_index(self, index: int):
    #     self.open_legal_entity_dropdown()
    #     self.page.locator(f"{self.LEGAL_ENTITY_DROPDOWN} {self.LEGAL_ENTITY_OPTION}").nth(index).click()
    #     time.sleep(1)
