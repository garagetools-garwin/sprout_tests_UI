import os

import allure
from playwright.sync_api import Page

class ListingPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/catalog/9/3052"

    # Листинг

    PRODUCT = "tr.ant-table-row"

    # Карточка товара
    ADD_TO_CART_BUTTON = ".goods-card__btn button.ant-btn"

    # Листинг

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    @allure.step("Выбираю первый товар")
    def click_first_product(self):
        self.page.locator(self.PRODUCT).nth(0).click()

    @allure.step("Добавляю товар в корзину")
    def add_to_cart(self):
        self.click_first_product()
        self.click_add_to_cart_button()

    # Карточка товара

    @allure.step("Нажимаю на добавить товар в корзину")
    def click_add_to_cart_button(self):
        self.page.locator(self.ADD_TO_CART_BUTTON).click()







    #TODO перевести карточку товара в отдельный класс

