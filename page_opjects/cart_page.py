import os

import allure
from playwright.sync_api import Page

class CartPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/basket"

    SEND_BUTTON = "button.button-lg.primary"
    MINI_CART_BADGE = "text=добавлен в корзину"
    LIMIT_EXCEEDED_BANNER = "text=Стоимость позиции превышает допустимый лимит на цену товара."
    LIMIT_EXCEEDED_BANNER_2 = "text=Ваш заказ превышает доступный лимит на покупки"

    ADDRESS_LABEL = "text=Адрес:"
    ADDRESS_CONTAINER = ".."
    ADDRESS_VALUE = ".ant-select-selection-item"

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    @allure.step("Нажимаю на отправить")
    def click_send_button(self):
        self.page.locator(self.SEND_BUTTON).click()


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







    #TODO перевести карточку товара в отдельный класс

