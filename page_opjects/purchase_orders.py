import os

import allure
from playwright.sync_api import Page, expect


class PurchaseOrdersPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/request-list/manager"

    MOVE_TO_ORDER_BUTTON = ".button-circle.secondary"
    SELECT_ALL_PRODUCTS_CHECKBOX = ".request-supply-list__table-group-row .ant-checkbox-input"
    APPROVE_BUTTON_IN_MODAL = ".request-actions__container .ant-btn.request-actions__btn:has-text('Согласовать')"
    REJECT_BUTTON_IN_MODAL = ".request-actions__container .ant-btn.request-actions__btn:has-text('Отклонить')"
    APPROVE_BUTTON_IN_ROW = ""
    ORDER_NUMBER_CELL = ".ant-table-row.ant-table-row-level-0:has(.ant-table-cell .text-controls-accent.ellipsis)"
    ORDERS_LIST_LOCATOR = "tbody.ant-table-tbody"
    ORDER_ROW = "tr.ant-table-row.ant-table-row-level-0"
    NUM_CELL = ".ant-table-cell .text-controls-accent.ellipsis"

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    def open_ready_orders(self, base_url):
        with allure.step(f"Открываю {base_url + "/request-list/seller_manager/requests"}"):
            return self.page.goto(base_url + "/request-list/seller_manager/requests")

    def has_order_number(self, order_number: str) -> bool:
        # Найдём все строки заказов, а не только первую!
        order_rows = self.page.locator(self.ORDER_ROW)
        rows_count = order_rows.count()
        for i in range(rows_count):
            row = order_rows.nth(i)
            # Локатор номера заказа внутри ряда
            num_cells = row.locator(self.NUM_CELL)
            # Может быть несколько — ищем среди них
            for j in range(num_cells.count()):
                num_text = num_cells.nth(j).inner_text().strip()
                if order_number in num_text:
                    print(f"Найден заказ с номером: {order_number}")
                    return True
        print(f"Заказ с номером {order_number} не найден")
        return False

    @allure.step("Перехожу в последний созданный заказ")
    def move_to_first_order_in_list(self):
        self.page.locator(self.MOVE_TO_ORDER_BUTTON).nth(0).click()

    @allure.step("Нахожу заказ по номеру, перехожу в него")
    def move_to_order_with_number(self, order_number):
        with allure.step("Проверяю, что номер заказа есть в списке"):
            order_number_in_list = self.page.locator(f'{self.ORDER_NUMBER_CELL}:has-text("{order_number}")')
            assert order_number_in_list is not None
        with allure.step("Прехожу в заказ"):
            order_number_in_list.locator(self.MOVE_TO_ORDER_BUTTON).click()
        return order_number_in_list

    @allure.step("Выделяю весь товар в заказе")
    def select_all_products_in_order(self):
        self.page.locator(self.SELECT_ALL_PRODUCTS_CHECKBOX).click()

    @allure.step("Нажать на Согласовать")
    def click_approve_button_in_modal(self):
        self.page.locator(self.APPROVE_BUTTON_IN_MODAL).click()

