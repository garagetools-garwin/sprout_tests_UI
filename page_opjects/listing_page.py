import os
import re
import time
from asyncio import wait_for

import allure
from playwright.sync_api import Page, expect


class ListingPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/catalog/9/3052"

    # Листинг

    PRODUCT = "tr.ant-table-row"
    PRICE_IN_CARD = ".text-accent"

    # Карточка товара
    ADD_TO_CART_BUTTON = ".goods-card__btn button.ant-btn"

    # Листинг

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    @allure.step("Открываю указанный URL листинга")
    def open_url(self, url: str):
        return self.page.goto(url)

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

    def open_vs(self, base_url):
        self.page.goto("https://www.vseinstrumenti.ru/product/bolgarka-ushm-sturm-ag9012t-711829/")

    @allure.step("Получаю тексты цен из видимых карточек")
    def get_visible_prices_text(self):
        self.page.wait_for_selector(self.PRICE_IN_CARD)
        loc = self.page.locator(self.PRICE_IN_CARD)
        return [loc.nth(i).inner_text().strip() for i in range(loc.count())]

    @allure.step("Извлекаю структурированные данные о ценах (рубли, копейки)")
    def get_price_data(self):
        """
        Возвращает список словарей с данными о ценах:
        [{"full_price": "1234,56", "rubles": 1234, "kopecks": 56}, ...]
        """
        price_texts = self.get_visible_prices_text()
        price_data = []

        for price_text in price_texts:
            # Ищем числа с разделителями копеек (точка или запятая)
            match = re.search(r'(\d{1,})[.,](\d{2})', price_text)
            if match:
                rubles = int(match.group(1))
                kopecks = int(match.group(2))
                price_data.append({
                    "full_price": price_text,
                    "rubles": rubles,
                    "kopecks": kopecks
                })

        return price_data

    @allure.step("Проверяю, что в ценах есть ненулевые копейки (до округления)")
    def has_non_zero_kopecks(self):
        """Проверяет, что есть цены с копейками != 00"""
        price_data = self.get_price_data()
        return any(item["kopecks"] != 0 for item in price_data)

    @allure.step("Проверяю, что все цены округлены (копейки = 00, рубли увеличены)")
    def are_prices_rounded_up(self, original_price_data):
        """
        Сравнивает текущие цены с исходными и проверяет:
        1. Все копейки стали 00
        2. Рубли округлились до ближайшего большего (если копейки были > 0)
        """
        current_price_data = self.get_price_data()

        # Проверяем, что все копейки стали 00
        all_kopecks_zero = all(item["kopecks"] == 0 for item in current_price_data)
        if not all_kopecks_zero:
            return False, "Не все копейки стали 00"

        # Проверяем округление рублей
        for i, current in enumerate(current_price_data):
            if i < len(original_price_data):
                original = original_price_data[i]
                expected_rubles = original["rubles"]

                # Если копейки были > 0, рубли должны увеличиться на 1
                if original["kopecks"] > 0:
                    expected_rubles += 1

                if current["rubles"] != expected_rubles:
                    return False, f"Цена {i}: ожидали {expected_rubles} руб, получили {current['rubles']} руб"

        return True, "Все цены корректно округлены"

    @allure.step("Добавляю товар дороже {min_price} в корзину")
    def add_expensive_item_to_cart(self, min_price: int):
        self.page.wait_for_selector(self.PRODUCT, timeout=10000)
        # time.sleep(5)
        cards = self.page.locator(self.PRODUCT)
        total = cards.count()
        assert total > 0, "Нет карточек товаров в листинге"

        for i in range(total):
            text = cards.nth(i).locator(self.PRICE_IN_CARD).inner_text()
            digits = re.findall(r"\d+", text.replace(" ", ""))
            if not digits:
                continue
            value = int(digits[0])
            if value > min_price:
                cards.nth(i).click()
                self.page.locator(self.ADD_TO_CART_BUTTON).click()
                return
        raise AssertionError(f"Не найден товар дороже {min_price}")





    #TODO перевести карточку товара в отдельный класс

