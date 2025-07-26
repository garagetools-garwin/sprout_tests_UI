import os

import allure
from playwright.sync_api import Page

class PurchaseOrdersPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "request-list/manager"

    MOVE_TO_ORDER_BUTTON = ".button-circle.secondary"
    SELECT_ALL_PRODUCTS_CHECKBOX = ".request-supply-list__table-group-row .ant-checkbox-input"
    APPROVE_BUTTON_IN_MODAL = ".request-actions__container .ant-btn.request-actions__btn:has-text('Согласовать')"
    REJECT_BUTTON_IN_MODAL = ".request-actions__container .ant-btn.request-actions__btn:has-text('Отклонить')"
    APPROVE_BUTTON_IN_ROW = ""

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    @allure.step("Перехожу в последний созданный заказ")
    def click_move_to_order_button(self):
        self.page.locator(self.MOVE_TO_ORDER_BUTTON).nth(0).click()

    @allure.step("Выделяю весь товар в заказе")
    def select_all_products_in_order(self):
        self.page.locator(self.SELECT_ALL_PRODUCTS_CHECKBOX).click()

    @allure.step("Нажать на Согласовать")
    def click_approve_button_in_modal(self):
        self.page.locator(self.APPROVE_BUTTON_IN_MODAL).click()



    @allure.step("Добавляю товар в корзину")
    def add_to_cart(self):
        self.click_first_product()
        self.click_add_to_cart_button()

    # Карточка товара

    @allure.step("Нажимаю на добавить товар в корзину")
    def click_add_to_cart_button(self):
        self.page.locator(self.ADD_TO_CART_BUTTON).click()







    #TODO перевести карточку товара в отдельный класс

