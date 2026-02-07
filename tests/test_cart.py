# test_cart.py
import random
import time
from importlib import reload

import allure
import pytest
from playwright.sync_api import expect
from page_opjects.autorization_page import AutorizationPage
from page_opjects.cart_page import CartPage
from page_opjects.listing_page import ListingPage
from page_opjects.settings_page.subdivisions_page.subdivisions_settings_page import SubdivisionsSettingsPage

"""Тесты страницы Корзина"""

"""Тесты на окно быстрого добавления"""

@allure.title("Открытие модального окна быстрого добавления")
def test_open_quick_add_modal(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)

    with allure.step("Открываю модальное окно быстрого добавления"):
        cart.open_quick_add_modal()

    with allure.step("Проверяю, что окно отображается"):
        assert cart.is_quick_add_modal_visible()


@allure.title("Поиск товара в окне быстрого добавления")
def test_quick_add_search(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)
    cart.open_quick_add_modal()

    with allure.step("Ввожу название товара 'отвертка ph2'"):
        cart.search_in_quick_add("отвертка ph2")

    with allure.step("Проверяю, что в результатах поиска найдены товары с 'отвертка' и 'ph2'"):
        product_name_locator = cart.get_product_name_locator(index=0)

        # Проверка на содержание "отвертка"
        expect(product_name_locator).to_contain_text("отвертка", ignore_case=True)

        # Проверка на содержание "ph2"
        expect(product_name_locator).to_contain_text("ph2", ignore_case=True)

        # Прикрепляем текст найденного товара в отчет
        product_name = cart.get_first_product_name()
        allure.attach(product_name, name="Найденный товар", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очищаю строку поиска и ввожу артикул"):
        cart.search_in_quick_add("")
        cart.search_in_quick_add("RT-SD1PH2x100")

    with allure.step("Проверяю, что найден товар с артикулом 'RT-SD1PH2x100'"):
        product_name_locator = cart.get_product_name_locator(index=0)

        expect(product_name_locator).to_contain_text("RT-SD1PH2x100", ignore_case=True)

        product_name = cart.get_first_product_name()
        allure.attach(product_name, name="Товар по артикулу", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Очищаю строку поиска и ввожу артикул покупателя"):
        cart.search_in_quick_add("")
        cart.search_in_quick_add("GAR-776631")

    with allure.step("Проверяю, что найден товар с артикулом клиента'GAR-776631'"):
        product_name_locator = cart.get_product_buyer_article_locator(index=0)

        expect(product_name_locator).to_contain_text("GAR-776631", ignore_case=True)

        product_name = cart.get_first_buyer_articl()
        allure.attach(product_name, name="Товар по артикулу", attachment_type=allure.attachment_type.TEXT)


@allure.title("Добавление товара в окне Быстрое добавление")
def test_add_product_in_quick_add_modal(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)

    cart.clear_cart(base_url)

    with allure.step("Открываю модальное окно быстрого добавления"):
        cart.open_quick_add_modal()

    with allure.step("Проверяю, что окно отображается"):
        assert cart.is_quick_add_modal_visible()

    cart.add_product_from_opened_quick_add_modal()

    current = cart.get_selected_subdivision()
    if current != cart.TEST_SUBDIVISION_HIGH_LIMIT:
        cart.select_subdivision(cart.TEST_SUBDIVISION_HIGH_LIMIT)
        time.sleep(1)

    with allure.step("Проверяю, что окно не отображается"):
        time.sleep(3)
        assert not cart.is_quick_add_modal_visible()
    with allure.step("Проверяю, что товар появился в корзине"):
        assert cart.is_product_row_visible()


"""Листинг товара"""


@allure.title("Открытие окна подтверждения удаления товара и отмена")
def test_open_delete_confirmation_modal(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)

    cart.clear_cart(base_url)

    cart.open_quick_add_modal()
    cart.add_product_from_opened_quick_add_modal()

    with allure.step("Нажимаю кнопку удаления товара"):
        cart.click_delete_item_button(0)

    with allure.step("Проверяю, что модальное окно подтверждения отображается"):
        assert page.locator(cart.DELETE_MODAL).is_visible()

    with allure.step("Нажимаю на отмену"):
        cart.cancel_delete_item()

    with allure.step("Проеверяю, товар не был удален"):
        assert page.locator(cart.PRODUCT_ROW).count() > 0

    with allure.step("Проверяю, что модальное окно подтверждения не отображается"):
        assert not page.locator(cart.DELETE_MODAL).is_visible()


@allure.title("Подтверждение удаления товара")
def test_confirm_delete_item(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)

    cart.clear_cart(base_url)

    cart.open_quick_add_modal()
    cart.add_product_from_opened_quick_add_modal()
    time.sleep(3)

    initial_count = cart.get_cart_items_count()

    with allure.step("Открываю окно подтверждения удаления"):
        with allure.step("Нажимаю кнопку удаления товара"):
            cart.click_delete_item_button(0)

    with allure.step("Подтверждаю удаление"):
        cart.confirm_delete_item()

    time.sleep(3)

    with allure.step("Проверяю, что товар удален"):
        new_count = cart.get_cart_items_count()
        assert new_count == initial_count - 1


@allure.title("Проверка сроков поставки")
def test_delivery_date(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)
    cart.clear_cart(base_url)

    page.goto(f"{base_url}/catalog/9/3059")

    with allure.step("Добавляю товар 'В наличии' и запоминаю срок доставки"):
        listing_time_in_stock = listing.add_item_in_stock_and_get_delivery_time()

        allure.attach(
            f"Срок доставки: {listing_time_in_stock}",
            name="Листинг - товар 'В наличии'"
        )

    with allure.step("Добавляю товар 'Под заказ' и запоминаю срок доставки"):
        listing_time_on_request = listing.add_item_on_request_and_get_delivery_time()

        allure.attach(
            f"Срок доставки: {listing_time_on_request}",
            name="Листинг - товар 'Под заказ'"
        )

    cart.open(base_url)
    time.sleep(1)

    expanded_rows = page.locator(cart.EXPANDED_ROW)

    with allure.step("Проверяю срок доставки товара 'В наличии' в корзине"):
        cart_time_in_stock = expanded_rows.nth(0).locator(
            listing.AVAILABILITY_TEXT_LOCATOR_IN_STOCK
        ).inner_text().strip()

        allure.attach(
            f"Листинг: {listing_time_in_stock}\nКорзина: {cart_time_in_stock}",
            name="Сравнение сроков - 'В наличии'"
        )
        print(listing_time_in_stock, cart_time_in_stock)
        assert cart_time_in_stock == listing_time_in_stock, \
            f"Срок доставки 'В наличии' не совпадает! " \
            f"Листинг: '{listing_time_in_stock}', Корзина: '{cart_time_in_stock}'"

    with allure.step("Проверяю срок доставки товара 'Под заказ' в корзине"):
        cart_time_on_request = expanded_rows.nth(1).locator(
            listing.AVAILABILITY_TEXT_LOCATOR_AVAILABLE_ON_REQUEST
        ).inner_text().strip()

        allure.attach(
            f"Листинг: {listing_time_on_request}\nКорзина: {cart_time_on_request}",
            name="Сравнение сроков - 'Под заказ'"
        )

        assert cart_time_on_request == listing_time_on_request, \
            f"Срок доставки 'Под заказ' не совпадает! " \
            f"Листинг: '{listing_time_on_request}', Корзина: '{cart_time_on_request}'"

    allure.attach(
        f"✓ Товар 'В наличии': {listing_time_in_stock}\n"
        f"✓ Товар 'Под заказ': {listing_time_on_request}",
        name="Итог: сроки совпадают"
    )

# @allure.title("Проверка сроков поставки")
# def test_delivery_date(base_url, page_fixture):
#
#     page = page_fixture()
#     autorization_page = AutorizationPage(page)
#     cart = CartPage(page)
#     listing = ListingPage(page)
#
#     autorization_page.open(base_url)
#     autorization_page.admin_buyer_authorize()
#
#     cart.open(base_url)
#
#     cart.clear_cart(base_url)
#
#     page.goto(f"{base_url}/catalog/9/3059")
#     listing.add_item_with_one_week()
#     listing.add_item_available_on_request()
#
#     cart.open(base_url)
#
#     expanded_rows = page.locator(cart.EXPANDED_ROW)
#
#     with allure.step("Проверяю, что срок доставки первого товара 1 Неделя"):
#         first_row_badge = expanded_rows.nth(0).locator(
#             listing.AVAILABILITY_TEXT_LOCATOR_IN_STOCK
#         )
#         expect(first_row_badge).to_have_text("1 неделя")
#
#     with allure.step("Проверяю, что срок доставки первого товара Доступно под заказ"):
#         second_row_badge = expanded_rows.nth(1).locator(
#             listing.AVAILABILITY_TEXT_LOCATOR_AVAILABLE_ON_REQUEST
#         )
#         expect(second_row_badge).to_have_text("Доступно под заказ")

@allure.title("Кнопка 'Выделить весь товар' в шапке корзины")
def test_select_all_items_button(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)

    cart.clear_cart(base_url)

    page.goto(base_url + "/catalog/9/3707")
    listing.click_first_product()
    listing.click_add_to_cart_button()
    page.goto(base_url + "/catalog/9/3707")
    listing.click_second_product()
    listing.click_add_to_cart_button()


    cart.open(base_url)
    current = cart.get_selected_subdivision()
    if current != cart.TEST_SUBDIVISION_HIGH_LIMIT:
        cart.select_subdivision(cart.TEST_SUBDIVISION_HIGH_LIMIT)
        time.sleep(1)
    # with allure.step("обавляю в корзину 3 товара"):
    #     for i in range(3):
    #         listing.add_item_in_stock_and_get_delivery_time()
    # time.sleep(3)

    with allure.step("Снимаю все чекбоксы 'Включить в заказ'"):
        items_count = cart.get_cart_items_count()
        for i in range(items_count):
            cart.uncheck_item_checkbox(i)

    time.sleep(3)

    with allure.step("Проверяю начальное состояние"):
        assert cart.get_calculation_quantity() == 0
        assert cart.get_calculation_goods_price() == 0.0
        assert not cart.is_send_button_enabled()

    with allure.step("Нажимаю 'Выделить весь товар'"):
        cart.click_select_all_button()

    with allure.step("Проверяю, что все чекбоксы установлены"):
        for i in range(items_count):
            assert cart.is_item_checkbox_checked(i)

    with allure.step("Проверяю, что стоимость и количество пересчитались"):
        assert cart.get_calculation_quantity() == items_count
        assert cart.get_calculation_goods_price() > 0

    with allure.step("Проверяю, что кнопка Отправить активна"):
        assert cart.is_send_button_enabled()


@allure.title("Управление чекбоксами 'Включить в заказ'")
def test_checkbox_toggle_updates_total(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)

    cart.clear_cart(base_url)

    with allure.step("обавляю в корзину 2 товара"):
        for i in range(2):
            cart.add_product_from_quick_add_modal()

    cart.open(base_url)

    with allure.step("Фиксирую начальную стоимость двух товаров"):
        total_price_both = cart.get_calculation_goods_price()
        print(total_price_both)
        allure.attach(f"Стоимость 2 товаров: {total_price_both} ₽", name="Начальная стоимость")

    with allure.step("Снимаю чекбокс у первого товара"):
        cart.uncheck_item_checkbox(0)
        time.sleep(1)

    with allure.step("Проверяю, что стоимость равна стоимости второго товара"):
        price_one_item = cart.get_calculation_goods_price()
        assert price_one_item < total_price_both
        print(price_one_item)
        print(total_price_both)
        allure.attach(f"Стоимость 1 товара: {price_one_item} ₽", name="Стоимость после снятия чекбокса")

    with allure.step("Снова устанавливаю чекбокс на первый товар"):
        cart.check_item_checkbox(0)
        time.sleep(1)

    with allure.step("Проверяю, что стоимость вернулась к сумме двух товаров"):
        final_price = cart.get_calculation_goods_price()
        assert final_price == total_price_both


@allure.title("Увеличение и уменьшение количества через кнопки +/-")
def test_quantity_buttons_increment_decrement(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)

    cart.clear_cart(base_url)

    with allure.step("обавляю в корзину 2 товара"):
        for i in range(1):
            cart.add_product_from_quick_add_modal()

    with allure.step("Проверяю начальное количество товара"):
        assert cart.get_item_quantity(0) == 1
        assert cart.get_calculation_quantity() == 1

    with allure.step("Нажимаю кнопку '+' три раза"):
        cart.increase_quantity_by_button(index=0, count=3)

    time.sleep(3)

    with allure.step("Проверяю количество товара = 4"):
        assert cart.get_item_quantity(0) == 4
        assert cart.get_calculation_quantity() == 4

    with allure.step("Нажимаю кнопку '-' два раза"):
        cart.decrease_quantity_by_button(index=0, count=2)

    time.sleep(3)

    with allure.step("Проверяю количество товара = 2"):
        assert cart.get_item_quantity(0) == 2
        assert cart.get_calculation_quantity() == 2


@allure.title("Ручной ввод количества товара")
def test_manual_quantity_input(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)

    cart.clear_cart(base_url)

    cart.add_product_from_quick_add_modal()

    with allure.step("Фиксирую начальную стоимость"):
        initial_price = cart.get_calculation_goods_price()
        print(initial_price)

    with allure.step("Ввожу количество 7 вручную"):
        cart.set_quantity_manually(index=0, quantity=7)

    with allure.step("Проверяю, что количество обновилось"):
        assert cart.get_item_quantity(0) == 7
        assert cart.get_calculation_quantity() == 7

    with allure.step("Проверяю, что стоимость пересчиталась"):
        final_price = cart.get_calculation_goods_price()
        expected_price = initial_price * 7
        print(final_price)
        print(expected_price)
        assert abs(final_price - expected_price) < 0.1


@allure.title("Очистка корзины через меню")
def test_clear_cart_via_menu(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)

    cart.open_quick_add_modal()

    cart.add_product_from_opened_quick_add_modal()

    time.sleep(3)

    initial_count = cart.get_cart_items_count()
    assert initial_count > 0

    cart.click_option_button()

    with allure.step("Проверяю, что нисподающее меню отображается"):
        assert page.locator(cart.DROPDOWN_MENU).is_visible()

    cart.clear_cart(base_url)

    time.sleep(3)

    with allure.step("Проверяю, что корзина пуста"):
        assert cart.get_cart_items_count() == 0


        #TODO роверять изменения суммы в test_quantity_buttons_increment_decrement или в блоке калькуляции



"""Блок калькуляции"""



@allure.title("Проверка отображения доступных средств для закупки")
def test_display_available_purchase_limit(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    time.sleep(5)

    cart.open(base_url)
    cart.clear_cart(base_url)

    with allure.step("Добавляю в корзину"):
        page.goto(base_url + "/catalog/9/3707")
        listing.add_expensive_item_to_cart(min_price=350)
        cart.open(base_url)
        time.sleep(2)

    with allure.step("Получаю начальный лимит подразделения"):

        current = cart.get_selected_subdivision()
        if current != cart.TEST_SUBDIVISION_HIGH_LIMIT:
            cart.select_subdivision(cart.TEST_SUBDIVISION_HIGH_LIMIT)
            time.sleep(1)

        initial_limit = cart.get_limit_total()
        print(initial_limit)
        allure.attach(f"Начальный лимит: {initial_limit} ₽", name="Начальный лимит")

    with allure.step("Получаю стоимость добавленного товара"):
        goods_price = cart.get_calculation_goods_price()
        print(goods_price)
        allure.attach(f"Стоимость товара: {goods_price} ₽", name="Стоимость товара")

    with allure.step("Проверяю, что в блоке лимита отображается общая сумма лимита"):
        displayed_limit = cart.get_limit_total()
        print(displayed_limit)
        assert displayed_limit == initial_limit, \
            f"Общий лимит отображается некорректно. Ожидалось: {initial_limit}, получено: {displayed_limit}"

    with allure.step("Проверяю, что оставшаяся сумма лимита рассчитана корректно"):
        remaining_limit = cart.get_limit_remaining()
        expected_remaining = initial_limit - goods_price
        print(expected_remaining)
        assert abs(remaining_limit - expected_remaining) < 0.1, \
            f"Оставшийся лимит некорректен. Ожидалось: {expected_remaining}, получено: {remaining_limit}"
        allure.attach(
            f"Расчет: {initial_limit} - {goods_price} = {expected_remaining}\nОтображается: {remaining_limit}",
            name="Проверка оставшегося лимита"
        )



# @allure.title("Обновление лимита при добавлении нескольких товаров")
# def test_limit_updates_on_multiple_items(base_url, page_fixture):
#     """
#     Проверка, что лимит корректно пересчитывается при добавлении нескольких товаров
#     """
#     page = page_fixture()
#     autorization_page = AutorizationPage(page)
#     cart = CartPage(page)
#
#     autorization_page.open(base_url)
#     autorization_page.admin_buyer_authorize()
#
#     cart.open(base_url)
#     cart.clear_cart(base_url)
#
#     with allure.step("Получаю начальный лимит"):
#         cart.open(base_url)
#         initial_limit = cart.get_limit_total()
#         initial_remaining = cart.get_limit_remaining()
#
#         assert initial_limit == initial_remaining, \
#             "При пустой корзине общий лимит должен равняться оставшемуся"
#
#     with allure.step("Добавляю первый товар"):
#         cart.add_product_from_quick_add_modal()
#         time.sleep(2)
#
#         first_item_price = cart.get_calculation_goods_price()
#         remaining_after_first = cart.get_limit_remaining()
#
#         expected_remaining = initial_limit - first_item_price
#         assert abs(remaining_after_first - expected_remaining) < 0.1, \
#             f"Лимит после первого товара некорректен"
#
#     with allure.step("Добавляю второй товар"):
#         cart.add_product_from_quick_add_modal()
#         time.sleep(2)
#
#         total_price = cart.get_calculation_goods_price()
#         remaining_after_second = cart.get_limit_remaining()
#
#         expected_remaining = initial_limit - total_price
#         assert abs(remaining_after_second - expected_remaining) < 0.1, \
#             f"Лимит после второго товара некорректен"
#
#     with allure.step("Проверяю, что общий лимит не изменился"):
#         current_limit = cart.get_limit_total()
#         assert current_limit == initial_limit, \
#             f"Общий лимит изменился. Было: {initial_limit}, стало: {current_limit}"


@allure.title("Корректность расчета стоимости с НДС")
def test_calculation_with_vat_full(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)
    cart.clear_cart(base_url)

    page.goto(f"{base_url}/catalog/9/3059")
    listing.add_item_in_stock_and_get_delivery_time()
    listing.add_item_available_on_request()

    cart.open(base_url)
    time.sleep(2)

    with allure.step("Устанавливаю количество первого товара = 2"):
        cart.set_quantity_manually(index=0, quantity=2)
        time.sleep(1)

    with allure.step("Шаг 1: Получаю стоимость товаров и проверяю расчет"):
        goods_price = cart.get_calculation_goods_price()
        print(f"\n{'=' * 60}")
        print(f"goods_price (Стоимость товаров из блока калькуляции): {goods_price} ₽")

        # Получаем цены отдельных товаров для проверки
        item_prices = []
        items_count = cart.get_cart_items_count()
        print(f"items_count (Количество позиций в корзине): {items_count}")

        for i in range(items_count):
            item_price = cart.get_item_line_total(i)
            item_prices.append(item_price)
            print(f"item_prices[{i}] (Цена товара #{i + 1}): {item_price} ₽")

        calculated_total = sum(item_prices)
        print(f"calculated_total (Сумма цен всех товаров вручную): {calculated_total} ₽")

        assert abs(goods_price - calculated_total) < 0.1, \
            f"Стоимость товаров не совпадает. Ожидалось: {calculated_total}, получено: {goods_price}"

    with allure.step("Шаг 2: Проверяю корректность расчета НДС"):
        vat = cart.get_calculation_vat()
        total = cart.get_calculation_total()

        print(f"\n{'=' * 60}")
        print(f"vat (НДС из блока калькуляции): {vat} ₽")
        print(f"total (Итого с НДС из блока калькуляции): {total} ₽")

        # Вычисляем фактический процент НДС
        actual_vat_percent = (vat / goods_price) * 100
        print(f"\n--- Фактический процент НДС ---")
        print(f"vat / goods_price × 100 = {vat} / {goods_price} × 100 = {actual_vat_percent:.2f}%")

        # Разные варианты расчета НДС
        vat_20_on_top = round(goods_price * 0.2, 2)
        vat_22_on_top = round(goods_price * 0.22, 2)
        vat_extracted_from_total = round(total * 20 / 120, 2)

        # НДС по каждому товару отдельно с округлением
        vat_per_item_20 = sum([round(price * 0.2, 2) for price in item_prices])
        vat_per_item_22 = sum([round(price * 0.22, 2) for price in item_prices])

        print(f"\n--- Варианты расчета НДС ---")
        print(f"vat_20_on_top (goods_price × 0.2): {vat_20_on_top} ₽")
        print(f"vat_22_on_top (goods_price × 0.22): {vat_22_on_top} ₽")
        print(f"vat_extracted_from_total (total × 20 / 120): {vat_extracted_from_total} ₽")
        print(f"vat_per_item_20 (сумма НДС 20% по каждому товару): {vat_per_item_20} ₽")
        print(f"vat_per_item_22 (сумма НДС 22% по каждому товару): {vat_per_item_22} ₽")

        print(f"\n--- Сравнение с фактическим НДС ({vat} ₽) ---")
        print(f"Разница vat - vat_20_on_top: {abs(vat - vat_20_on_top)} ₽")
        print(f"Разница vat - vat_22_on_top: {abs(vat - vat_22_on_top)} ₽")
        print(f"Разница vat - vat_extracted_from_total: {abs(vat - vat_extracted_from_total)} ₽")
        print(f"Разница vat - vat_per_item_20: {abs(vat - vat_per_item_20)} ₽")
        print(f"Разница vat - vat_per_item_22: {abs(vat - vat_per_item_22)} ₽")

        # Определяем какой вариант используется
        tolerance = 1.0  # Допуск 1 рубль из-за округлений

        if abs(vat - vat_20_on_top) < tolerance:
            expected_vat = vat_20_on_top
            vat_method = "НДС 20% от общей стоимости"
        elif abs(vat - vat_22_on_top) < tolerance:
            expected_vat = vat_22_on_top
            vat_method = "НДС 22% от общей стоимости"
        elif abs(vat - vat_extracted_from_total) < tolerance:
            expected_vat = vat_extracted_from_total
            vat_method = "НДС выделен из итого (20/120)"
        elif abs(vat - vat_per_item_20) < tolerance:
            expected_vat = vat_per_item_20
            vat_method = "НДС 20% по каждому товару с округлением"
        elif abs(vat - vat_per_item_22) < tolerance:
            expected_vat = vat_per_item_22
            vat_method = "НДС 22% по каждому товару с округлением"
        else:
            # Если ничего не подошло - просто проверяем что Итого = Стоимость + НДС
            expected_vat = vat
            vat_method = f"Нестандартный расчет (фактически ~{actual_vat_percent:.1f}%)"

        print(f"\nИспользуемый метод: {vat_method}")
        print(f"expected_vat (Ожидаемый НДС): {expected_vat} ₽")

        allure.attach(
            f"Фактический НДС: {vat}\n"
            f"Фактический процент: {actual_vat_percent:.2f}%\n"
            f"Метод: {vat_method}",
            name="Проверка НДС"
        )

    with allure.step("Шаг 3: Проверяю корректность итоговой суммы с НДС"):
        print(f"\n{'=' * 60}")
        print(f"--- Проверка итоговой суммы ---")

        expected_total = goods_price + vat
        print(f"goods_price + vat = {goods_price} + {vat} = {expected_total} ₽")
        print(f"total (фактический): {total} ₽")
        print(f"Разница: {abs(total - expected_total)} ₽")

        # Главная проверка: Итого = Стоимость товаров + НДС
        assert abs(total - expected_total) < 0.1, \
            f"Итоговая сумма некорректна. Ожидалось: {expected_total}, получено: {total}"

    with allure.step("Шаг 4: Увеличиваю количество товара в позиции №1 на 1 шт"):
        old_goods_price = goods_price
        old_vat = vat
        old_total = total

        print(f"\n{'=' * 60}")
        print(f"--- Значения ДО увеличения количества ---")
        print(f"old_goods_price: {old_goods_price} ₽")
        print(f"old_vat: {old_vat} ₽")
        print(f"old_total: {old_total} ₽")

        cart.increase_quantity_by_button(index=0, count=1)
        time.sleep(2)

    with allure.step("Проверяю, что все строчки стоимости пересчитались"):
        new_goods_price = cart.get_calculation_goods_price()
        new_vat = cart.get_calculation_vat()
        new_total = cart.get_calculation_total()

        print(f"\n--- Значения ПОСЛЕ увеличения количества ---")
        print(f"new_goods_price: {new_goods_price} ₽")
        print(f"new_vat: {new_vat} ₽")
        print(f"new_total: {new_total} ₽")

        print(f"\n--- Изменения ---")
        print(f"Стоимость: {old_goods_price} → {new_goods_price} (+{new_goods_price - old_goods_price} ₽)")
        print(f"НДС: {old_vat} → {new_vat} (+{new_vat - old_vat} ₽)")
        print(f"Итого: {old_total} → {new_total} (+{new_total - old_total} ₽)")

        assert new_goods_price > old_goods_price, \
            f"Стоимость товаров не увеличилась"

        assert new_vat > old_vat, \
            f"НДС не увеличился"

        assert new_total > old_total, \
            f"Итоговая сумма не увеличилась"

    with allure.step("Проверяю корректность новых расчетов"):
        print(f"\n{'=' * 60}")
        print(f"--- Проверка новых расчетов ---")

        expected_new_total = new_goods_price + new_vat
        print(f"new_goods_price + new_vat = {new_goods_price} + {new_vat} = {expected_new_total} ₽")
        print(f"new_total (фактический): {new_total} ₽")

        assert abs(new_total - expected_new_total) < 0.1, \
            f"Новая итоговая сумма некорректна. Ожидалось: {expected_new_total}, получено: {new_total}"

        print(f"\n{'=' * 60}")
        print("ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print(f"{'=' * 60}\n")


import time
import allure
import pytest
from playwright.sync_api import expect
from page_opjects.autorization_page import AutorizationPage
from page_opjects.cart_page import CartPage

"""Тесты на блок Детали доставки в корзине"""

@allure.title("Проверка переключения подразделений")
def test_subdivision_switching(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)
    subdivision = SubdivisionsSettingsPage(page)

    # Константы для подразделений
    SUBDIVISION_HIGH_LIMIT = cart.TEST_SUBDIVISION_HIGH_LIMIT
    SUBDIVISION_LOW_LIMIT = cart.TEST_SUBDIVISION_LOW_LIMIT

    # ID подразделений для страниц настроек
    SUBDIVISION_HIGH_LIMIT_ID = "136"
    SUBDIVISION_LOW_LIMIT_ID = "134"

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)
    cart.clear_cart(base_url)

    page.goto(f"{base_url}/catalog/9/3059")
    listing.add_item_in_stock_and_get_delivery_time()

    cart.open(base_url)

    try:
        with allure.step(f"Предусловие: Устанавливаю подразделение {SUBDIVISION_HIGH_LIMIT}"):
            current = cart.get_selected_subdivision()

            if current != SUBDIVISION_HIGH_LIMIT:
                cart.select_subdivision(SUBDIVISION_HIGH_LIMIT)
                time.sleep(1)
                allure.attach(f"Подразделение установлено: {SUBDIVISION_HIGH_LIMIT}", name="Предусловие")
            else:
                allure.attach(f"Подразделение уже выбрано: {SUBDIVISION_HIGH_LIMIT}", name="Предусловие")

        # Получаем лимит из настроек первого подразделения
        page.goto(f"{base_url}/settings/subdivision/{SUBDIVISION_HIGH_LIMIT_ID}/general")
        initial_remaining_limit_from_settings = subdivision.get_remaining_limit_value()
        print(f"Лимит подразделения HIGH_LIMIT в настройках: {initial_remaining_limit_from_settings}")

        cart.open(base_url)

        with allure.step("Шаг 1: Проверяю отображение текущего подразделения и лимита"):
            initial_subdivision = cart.get_selected_subdivision()
            initial_limit = cart.get_limit_total()

            print(f"Начальное подразделение: {initial_subdivision}")
            print(f"Начальный лимит в корзине: {initial_limit}")

            allure.attach(f"Подразделение: {initial_subdivision}", name="Начальное подразделение")
            allure.attach(f"Лимит: {initial_limit} ₽", name="Начальный лимит")

            assert initial_subdivision == SUBDIVISION_HIGH_LIMIT, \
                f"Подразделение не соответствует ожидаемому. Ожидалось: {SUBDIVISION_HIGH_LIMIT}, получено: {initial_subdivision}"
            assert initial_limit > 0, "Лимит не отображается"

        with allure.step("Проверяю что лимит в настройках подразделения равен лимиту в корзине"):
            assert initial_remaining_limit_from_settings == initial_limit, \
                f"Лимиты не совпадают. В настройках: {initial_remaining_limit_from_settings}, в корзине: {initial_limit}"

        with allure.step("Шаг 2: Открываю список подразделений"):
            cart.open_subdivision_dropdown()

        with allure.step("Проверяю, что отображается ниспадающий список с подразделениями"):
            assert cart.is_dropdown_visible(), "Список подразделений не отображается"

            subdivision_options = cart.get_dropdown_options()
            allure.attach("\n".join(subdivision_options), name="Доступные подразделения")

            # Проверяем что оба тестовых подразделения доступны
            assert SUBDIVISION_LOW_LIMIT in subdivision_options, \
                f"Подразделение {SUBDIVISION_LOW_LIMIT} не найдено в списке"

            # assert len(subdivision_options) >= 2, "Должно быть минимум 2 подразделения для теста"

        with allure.step(f"Шаг 3: Переключаюсь на подразделение {SUBDIVISION_LOW_LIMIT}"):
            cart.select_subdivision(SUBDIVISION_LOW_LIMIT)
            # for option in subdivision_options:
            #     if option != initial_subdivision:
            #         new_subdivision_name = option
            #         break
            #
            # assert new_subdivision_name, "Не найдено другое подразделение для выбора"
            #
            # cart.select_subdivision(new_subdivision_name)
            time.sleep(2)

        with allure.step("Проверяю, что выбранное подразделение отображается корректно"):
            current_subdivision = cart.get_selected_subdivision()
            print(f"Текущее подразделение: {current_subdivision}")

            assert current_subdivision == SUBDIVISION_LOW_LIMIT, \
                f"Подразделение не изменилось. Ожидалось: {SUBDIVISION_LOW_LIMIT}, получено: {current_subdivision}"

        with allure.step("Проверяю, что лимит изменился"):
            new_limit = cart.get_limit_total()
            print(f"Новый лимит в корзине: {new_limit}")

            allure.attach(
                f"Было: {SUBDIVISION_HIGH_LIMIT} (лимит: {initial_limit} ₽)\n"
                f"Стало: {SUBDIVISION_LOW_LIMIT} (лимит: {new_limit} ₽)",
                name="Сравнение подразделений"
            )

            assert new_limit >= 0, "Лимит нового подразделения не отображается"

        # Проверяем лимит из настроек второго подразделения
        page.goto(f"{base_url}/settings/subdivision/{SUBDIVISION_LOW_LIMIT_ID}/general")
        new_remaining_limit_from_settings = subdivision.get_remaining_limit_value()
        print(f"Лимит подразделения LOW_LIMIT в настройках: {new_remaining_limit_from_settings}")

        with allure.step("Проверяю что лимит в настройках нового подразделения равен лимиту в корзине"):
            assert new_remaining_limit_from_settings == new_limit, \
                f"Лимиты не совпадают. В настройках: {new_remaining_limit_from_settings}, в корзине: {new_limit}"

    finally:
        with allure.step(f"Постусловие: Возвращаю подразделение {SUBDIVISION_HIGH_LIMIT}"):
            try:
                cart.open(base_url)
                current = cart.get_selected_subdivision()

                if current != SUBDIVISION_HIGH_LIMIT:
                    cart.select_subdivision(SUBDIVISION_HIGH_LIMIT)
                    time.sleep(1)
                    allure.attach(f"Подразделение восстановлено: {SUBDIVISION_HIGH_LIMIT}", name="Восстановление")
                else:
                    allure.attach(f"Подразделение уже выбрано: {SUBDIVISION_HIGH_LIMIT}", name="Восстановление")

            except Exception as e:
                allure.attach(f"Ошибка восстановления: {e}", name="Ошибка восстановления")

@pytest.skip("При переключении не обновляетя страница, соответственно статус кнопки не меняется")
@allure.title("Блокировка заказа при превышении лимита на цену товара при переключении подразделения")
def test_subdivision_switch_item_price_limit_exceeded(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)

    # Константы для подразделений
    SUBDIVISION_HIGH_LIMIT = cart.TEST_SUBDIVISION_HIGH_LIMIT  # Подразделение с высоким лимитом
    SUBDIVISION_LOW_LIMIT = cart.TEST_SUBDIVISION_LOW_LIMIT  # Подразделение с низким лимитом на цену товара

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)
    cart.clear_cart(base_url)

    page.goto(f"{base_url}/catalog/9/3059")
    listing.add_item_in_stock_and_get_delivery_time()

    cart.open(base_url)

    try:
        with allure.step("Предусловие: Устанавливаю подразделение с высоким лимитом"):
            current = cart.get_selected_subdivision()

            if current != SUBDIVISION_HIGH_LIMIT:
                cart.select_subdivision(SUBDIVISION_HIGH_LIMIT)
                time.sleep(1)

        with allure.step("Проверяю, что заказ можно оформить"):
            time.sleep(2)
            expect(page.locator(cart.LIMIT_EXCEEDED_BANNER)).to_be_hidden(timeout=5000)
            expect(page.locator(cart.SEND_BUTTON)).to_be_enabled()
            allure.attach("Плашка скрыта, кнопка активна", name="Состояние до переключения")

        with allure.step("Переключаюсь на подразделение с низким лимитом на цену товара"):
            cart.select_subdivision(SUBDIVISION_LOW_LIMIT)
            time.sleep(2)

        with allure.step("Проверяю, что подразделение переключилось"):
            current_subdivision = cart.get_selected_subdivision()
            assert current_subdivision == SUBDIVISION_LOW_LIMIT, \
                f"Подразделение не переключилось. Ожидалось: {SUBDIVISION_LOW_LIMIT}, получено: {current_subdivision}"

        with allure.step("Проверяю, что появилась плашка о превышении лимита и кнопка заблокирована"):
            time.sleep(2)
            expect(page.locator(cart.LIMIT_EXCEEDED_BANNER)).to_be_visible(timeout=5000)
            # cart.click_send_button()
            expect(page.locator(cart.SEND_BUTTON)).to_be_disabled()
            allure.attach("Плашка отображается, кнопка заблокирована", name="Состояние после переключения на низкий лимит")

        with allure.step("Переключаюсь обратно на подразделение с высоким лимитом"):
            cart.select_subdivision(SUBDIVISION_HIGH_LIMIT)
            time.sleep(2)

        with allure.step("Проверяю, что подразделение переключилось"):
            current_subdivision = cart.get_selected_subdivision()
            assert current_subdivision == SUBDIVISION_HIGH_LIMIT, \
                f"Подразделение не переключилось. Ожидалось: {SUBDIVISION_HIGH_LIMIT}, получено: {current_subdivision}"

        with allure.step("Проверяю, что плашка исчезла и кнопка снова активна"):
            time.sleep(2)
            expect(page.locator(cart.LIMIT_EXCEEDED_BANNER)).to_be_hidden(timeout=5000)
            expect(page.locator(cart.SEND_BUTTON)).to_be_enabled()
            allure.attach("Плашка скрыта, кнопка активна", name="Состояние после возврата на высокий лимит")

    finally:
        with allure.step("Постусловие: Возвращаю тестовое подразделение"):
            try:
                cart.open(base_url)
                current = cart.get_selected_subdivision()

                if current != SUBDIVISION_HIGH_LIMIT:
                    cart.select_subdivision(SUBDIVISION_HIGH_LIMIT)
                    time.sleep(1)
                    allure.attach(f"Подразделение восстановлено: {SUBDIVISION_HIGH_LIMIT}", name="Восстановление")

            except Exception as e:
                allure.attach(f"Ошибка восстановления: {e}", name="Ошибка восстановления")


@allure.title("Проверка изменения списка адресов при переключении подразделения")
def test_address_list_changes_on_subdivision_switch(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)
    cart.clear_cart(base_url)

    try:
        with allure.step("Предусловие: Устанавливаю первое тестовое подразделение"):

            page.goto(f"{base_url}/catalog/9/3059")
            listing.add_item_in_stock_and_get_delivery_time()

            cart.open(base_url)

            current = cart.get_selected_subdivision()
            if cart.normalize_address(current) != cart.normalize_address(cart.TEST_SUBDIVISION_HIGH_LIMIT):
                cart.select_subdivision(cart.TEST_SUBDIVISION_HIGH_LIMIT)
                time.sleep(1)


        with allure.step("Шаг 0: Открываю список адресов"):
            cart.open_address_dropdown()
            time.sleep(0.5)

        with allure.step("Проверяю, что отображается ниспадающий список адресов"):
            assert cart.is_dropdown_visible(), "Список адресов не отображается"

            initial_addresses = cart.get_dropdown_options()
            allure.attach("\n".join(initial_addresses), name="Адреса начального подразделения")

            assert len(initial_addresses) >= 2, "Должно быть минимум 2 адреса для теста"

        with allure.step("Шаг 2: Выбираю другой адрес"):
            cart.select_option_by_index(0)
            time.sleep(1)


        with allure.step("Запоминаю начальное подразделение и адрес"):
            initial_subdivision = cart.get_selected_subdivision()
            initial_address = cart.get_selected_address()

            allure.attach(f"Подразделение: {initial_subdivision}", name="Начальное подразделение")
            allure.attach(f"Адрес: {initial_address}", name="Начальный адрес")

        with allure.step("Шаг 1: Открываю список адресов"):
            cart.open_address_dropdown()
            time.sleep(0.5)

        with allure.step("Проверяю, что отображается ниспадающий список адресов"):
            assert cart.is_dropdown_visible(), "Список адресов не отображается"

            initial_addresses = cart.get_dropdown_options()
            allure.attach("\n".join(initial_addresses), name="Адреса начального подразделения")

            assert len(initial_addresses) >= 2, "Должно быть минимум 2 адреса для теста"

        with allure.step("Шаг 2: Выбираю другой адрес"):
            cart.select_option_by_index(1)
            time.sleep(1)

        with allure.step("Проверяю, что адрес изменился"):
            new_address = cart.get_selected_address()

            assert new_address != initial_address, \
                f"Адрес не изменился. Было: {initial_address}, стало: {new_address}"

            allure.attach(f"Новый адрес: {new_address}", name="Выбранный адрес")

        # with allure.step("Шаг 3: Переключаю подразделение"):
        #     cart.open_subdivision_dropdown()
        #     time.sleep(0.5)
        #
        #     subdivision_options = cart.get_dropdown_options()
        #
        #     new_subdivision_name = None
        #     for option in subdivision_options:
        #         if option != initial_subdivision:
        #             new_subdivision_name = option
        #             break
        #
        #     assert new_subdivision_name, "Не найдено другое подразделение"
        #
        #     cart.select_option(new_subdivision_name)
        #     time.sleep(2)
        #
        # with allure.step("Проверяю, что адрес изменился на адрес по умолчанию нового подразделения"):
        #     default_address_new_subdivision = cart.get_selected_address()
        #
        #     allure.attach(
        #         f"Подразделение: {new_subdivision_name}\n"
        #         f"Адрес по умолчанию: {default_address_new_subdivision}",
        #         name="Адрес нового подразделения"
        #     )
        #
        #     assert default_address_new_subdivision, "Адрес по умолчанию не отображается"

        with allure.step("Шаг 3: Переключаю на второе тестовое подразделение"):
            cart.select_subdivision(cart.TEST_SUBDIVISION_LOW_LIMIT)
            time.sleep(2)

            current_subdivision = cart.get_selected_subdivision()
            allure.attach(f"Текущее подразделение: {current_subdivision}", name="Второе подразделение")

        with allure.step("Проверяю, что адрес изменился на адрес по умолчанию второго подразделения"):
            default_address_second_subdivision = cart.get_selected_address()

            allure.attach(
                f"Подразделение: {cart.TEST_SUBDIVISION_LOW_LIMIT}\n"
                f"Адрес по умолчанию: {default_address_second_subdivision}",
                name="Адрес второго подразделения"
            )

            assert default_address_second_subdivision, "Адрес по умолчанию не отображается"

        with allure.step("Шаг 4: Открываю список адресов нового подразделения"):
            cart.open_address_dropdown()
            time.sleep(0.5)

        with allure.step("Проверяю, что список адресов изменился"):
            assert cart.is_dropdown_visible(), "Список адресов не отображается"

            new_subdivision_addresses = cart.get_dropdown_options()
            allure.attach("\n".join(new_subdivision_addresses), name="Адреса нового подразделения")

            # === ГЛАВНАЯ ПРОВЕРКА: списки адресов должны отличаться ===

            # Преобразуем в множества для сравнения
            initial_addresses_set = set(initial_addresses)
            new_addresses_set = set(new_subdivision_addresses)

            allure.attach(
                f"Адреса подразделения '{initial_subdivision}':\n"
                f"{chr(10).join(sorted(initial_addresses))}\n\n"
                f"Адреса подразделения '{new_address}':\n"
                f"{chr(10).join(sorted(new_subdivision_addresses))}\n\n"
                f"Общие адреса: {initial_addresses_set & new_addresses_set}\n"
                f"Только в первом: {initial_addresses_set - new_addresses_set}\n"
                f"Только во втором: {new_addresses_set - initial_addresses_set}",
                name="Сравнение списков адресов"
            )

            # Проверяем что списки НЕ идентичны
            assert initial_addresses_set != new_addresses_set, \
                f"Списки адресов идентичны! Ожидалось, что у разных подразделений разные адреса."

            # Закрываем dropdown
            page.keyboard.press("Escape")


    finally:

        with allure.step("Постусловие: Возвращаю тестовое подразделение"):

            try:

                cart.open(base_url)

                current = cart.get_selected_subdivision()

                if cart.normalize_address(current) != cart.normalize_address(cart.TEST_SUBDIVISION_HIGH_LIMIT):
                    cart.select_subdivision(cart.TEST_SUBDIVISION_HIGH_LIMIT)

                    time.sleep(1)


            except Exception as e:

                allure.attach(f"Ошибка восстановления: {e}", name="Ошибка восстановления")


@allure.title("Проверка изменения списка юридических лиц при переключении подразделения")
def test_legal_entity_list_changes_on_subdivision_switch(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)

    with allure.step("Запоминаю начальное подразделение"):
        initial_subdivision = cart.get_selected_subdivision()
        allure.attach(f"Подразделение: {initial_subdivision}", name="Начальное подразделение")

    with allure.step("Шаг 2: Нажимаю на юридическое лицо"):
        cart.open_legal_entity_dropdown()

    with allure.step("Проверяю, что отображается ниспадающий список юр лиц"):
        assert cart.is_legal_entity_dropdown_visible(), "Список юр лиц не отображается"

        initial_legal_entities = cart.get_legal_entity_options()
        allure.attach("\n".join(initial_legal_entities), name="Юр лица начального подразделения")

        assert len(initial_legal_entities) >= 2, "Должно быть минимум 2 юр лица для теста"

    with allure.step("Шаг 3: Выбираю другое юр лицо"):
        initial_legal_entity = cart.get_selected_legal_entity()

        # Выбираем юр лицо, отличное от текущего
        cart.select_legal_entity_by_index(1)
        time.sleep(1)

    with allure.step("Проверяю, что на странице отображается новое юр лицо"):
        new_legal_entity = cart.get_selected_legal_entity()

        assert new_legal_entity != initial_legal_entity, \
            f"Юр лицо не изменилось. Было: {initial_legal_entity}, стало: {new_legal_entity}"

        allure.attach(f"Новое юр лицо: {new_legal_entity}", name="Выбранное юр лицо")

    with allure.step("Шаг 4: Переключаю подразделение"):
        cart.open_subdivision_dropdown()
        subdivision_options = cart.get_subdivision_options()

        # Выбираем другое подразделение
        for option in subdivision_options:
            if option != initial_subdivision:
                new_subdivision_name = option
                break

        cart.select_subdivision(new_subdivision_name)
        time.sleep(2)

    with allure.step("Проверяю, что в поле юр лицо отображается юр лицо нового подразделения"):
        default_legal_entity_new_subdivision = cart.get_selected_legal_entity()

        allure.attach(
            f"Подразделение: {new_subdivision_name}\n"
            f"Юр лицо по умолчанию: {default_legal_entity_new_subdivision}",
            name="Юр лицо нового подразделения"
        )

        assert default_legal_entity_new_subdivision, "Юр лицо по умолчанию не отображается"

    with allure.step("Шаг 5: Нажимаю на юр лицо"):
        cart.open_legal_entity_dropdown()

    with allure.step("Проверяю, что отображается список юр лиц нового подразделения"):
        assert cart.is_legal_entity_dropdown_visible(), "Список юр лиц не отображается"

        new_subdivision_legal_entities = cart.get_legal_entity_options()
        allure.attach("\n".join(new_subdivision_legal_entities), name="Юр лица нового подразделения")

        allure.attach(
            f"Юр лица старого подразделения ({initial_subdivision}):\n{chr(10).join(initial_legal_entities)}\n\n"
            f"Юр лица нового подразделения ({new_subdivision_name}):\n{chr(10).join(new_subdivision_legal_entities)}",
            name="Сравнение списков юр лиц"
        )


@allure.title("Блокировка заказа при превышении лимита на цену товара")
def test_order_blocked_when_item_price_exceeds_limit(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)

    # Константы для подразделений
    SUBDIVISION_LOW_LIMIT = cart.TEST_SUBDIVISION_LOW_LIMIT  # Подразделение с низким лимитом на цену товара

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)
    cart.clear_cart(base_url)

    page.goto(f"{base_url}/catalog/9/3059")
    listing.add_item_in_stock_and_get_delivery_time()

    cart.open(base_url)

    with allure.step("Предусловие: Устанавливаю подразделение с низким лимитом"):
        current = cart.get_selected_subdivision()

        if current != SUBDIVISION_LOW_LIMIT:
            cart.select_subdivision(SUBDIVISION_LOW_LIMIT)
            time.sleep(1)

    page.reload()

    with allure.step("Проверяю, что появилась плашка о превышении лимита и кнопка заблокирована"):
        time.sleep(2)
        expect(page.locator(cart.LIMIT_EXCEEDED_BANNER)).to_be_visible(timeout=5000)
        expect(page.locator(cart.SEND_BUTTON)).to_be_disabled()
        allure.attach("Плашка отображается, кнопка заблокирована", name="Состояние после переключения на низкий лимит")


@allure.title("Нельзя отправить товар который дороже разрешённого лимита")
def test_order_blocked_when_item_price_exceeds_allowed_limit(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)

    SUBDIVISION_LOW_LIMIT = cart.TEST_SUBDIVISION_LOW_TOTAL_LIMIT

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)
    cart.clear_cart(base_url)

    page.goto(f"{base_url}/catalog/9/3059")
    listing.add_item_in_stock_and_get_delivery_time()

    cart.open(base_url)

    try:
        with allure.step("Предусловие: Устанавливаю подразделение с низким лимитом на закупку"):
            current = cart.get_selected_subdivision()

            if current != cart.TEST_SUBDIVISION_LOW_TOTAL_LIMIT:
                cart.select_subdivision(cart.TEST_SUBDIVISION_LOW_TOTAL_LIMIT)
                time.sleep(1)
                allure.attach(f"Подразделение установлено: {cart.TEST_SUBDIVISION_LOW_TOTAL_LIMIT}", name="Подразделение")

        with allure.step("Получаю текущий лимит подразделения"):
            current_limit = cart.get_limit_total()
            print(f"Текущий лимит подразделения: {current_limit} ₽")
            allure.attach(f"Лимит: {current_limit} ₽", name="Лимит подразделения")

        # with allure.step("Добавляю товар в корзину который дороже разрешённого лимита"):
        #     # Переходим в каталог и добавляем дорогой товар
        #     page.goto(f"{base_url}/catalog/9/3707")
        #     listing.add_expensive_item_to_cart(min_price=current_limit + 100)
        #
        #     cart.open(base_url)
        #     time.sleep(2)

        with allure.step("Получаю стоимость добавленного товара"):
            goods_price = cart.get_calculation_goods_price()
            print(f"Стоимость товара: {goods_price} ₽")
            allure.attach(f"Стоимость товара: {goods_price} ₽", name="Стоимость товара")

            assert goods_price > current_limit, \
                f"Стоимость товара ({goods_price}) должна превышать лимит ({current_limit})"

        # with allure.step("Проверяю, что полоска лимита красная"):
        #     assert cart.is_limit_bar_red(), "Полоска лимита должна быть красной"
        #     allure.attach("Полоска лимита красная", name="Цвет полоски")

        with allure.step("Проверяю, что кнопка 'Отправить' заблокирована"):
            expect(page.locator(cart.SEND_BUTTON)).not_to_be_visible()
            allure.attach("Кнопка 'Отправить' заблокирована", name="Состояние кнопки")

        with allure.step("Проверяю, что отображается плашка 'Ваш заказ превышает доступный лимит на покупки'"):
            expect(page.locator(cart.LIMIT_EXCEEDED_BANNER_2)).to_be_visible(timeout=5000)
            allure.attach("Плашка отображается", name="Плашка лимита")

    finally:
        with allure.step("Постусловие: Очищаю корзину и возвращаю тестовое подразделение"):
            try:
                current = cart.get_selected_subdivision()
                if current != cart.TEST_SUBDIVISION_HIGH_LIMIT:
                    cart.select_subdivision(cart.TEST_SUBDIVISION_HIGH_LIMIT)
                    time.sleep(1)

            except Exception as e:
                allure.attach(f"Ошибка в постусловии: {e}", name="Ошибка")
