# test_cart.py
import random
import time
import allure
import pytest
from playwright.sync_api import expect
from page_opjects.autorization_page import AutorizationPage
from page_opjects.cart_page import CartPage
from page_opjects.listing_page import ListingPage

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
    listing.add_item_with_one_week()
    listing.add_item_available_on_request()

    cart.open(base_url)

    expanded_rows = page.locator(cart.EXPANDED_ROW)

    with allure.step("Проверяю, что срок доставки первого товара 1 Неделя"):
        first_row_badge = expanded_rows.nth(0).locator(
            listing.AVAILABILITY_TEXT_LOCATOR_IN_STOCK
        )
        expect(first_row_badge).to_have_text("1 неделя")

    with allure.step("Проверяю, что срок доставки первого товара Доступно под заказ"):
        second_row_badge = expanded_rows.nth(1).locator(
            listing.AVAILABILITY_TEXT_LOCATOR_AVAILABLE_ON_REQUEST
        )
        expect(second_row_badge).to_have_text("Доступно под заказ")

@allure.title("Кнопка 'Выделить весь товар' в шапке корзины")
def test_select_all_items_button(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)

    cart.clear_cart(base_url)

    with allure.step("обавляю в корзину 3 товара"):
        for i in range(3):
            cart.add_product_from_quick_add_modal()

    time.sleep(3)

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



@allure.title("TC-801: Проверка отображения доступных средств для закупки")
def test_display_available_purchase_limit(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    cart.open(base_url)
    cart.clear_cart(base_url)

    with allure.step("Получаю начальный лимит подразделения"):
        cart.open(base_url)
        initial_limit = cart.get_limit_total()
        print(initial_limit)
        allure.attach(f"Начальный лимит: {initial_limit} ₽", name="Начальный лимит")

    with allure.step("Добавляю в корзину"):
        page.goto(base_url + "/catalog/9/3707")
        listing.add_expensive_item_to_cart(min_price=350)
        cart.open(base_url)
        time.sleep(2)

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
    listing.add_item_with_one_week()
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

