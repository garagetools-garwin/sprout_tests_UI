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



@allure.title("TC-800: Корректность расчета стоимости с НДС")
@allure.tag("positive", "regression", "non-automated")
def test_calculation_with_vat(base_url, page_fixture):
    """
    Предусловия:
    - В корзину добавлены 3 разных товара с разным количеством

    Шаги:
    1. Посчитать вручную стоимость всех товаров
    2. Посчитать вручную НДС
    3. Посчитать вручную Итого с НДС
    4. Увеличить количество товара в позиции №1 на 1 шт

    Ожидаемый результат:
    - Все расчеты корректны
    - После изменения количества стоимость пересчиталась
    """
    page = page_fixture(role="buyer_admin")
    cart = CartPage(page)

    cart.clear_cart(base_url)
    # ... добавление 3 товаров
    cart.open(base_url)

    with allure.step("Получаю данные из блока калькуляции"):
        goods_price = cart.get_calculation_goods_price()
        vat = cart.get_calculation_vat()
        total = cart.get_calculation_total()

    with allure.step("Проверяю корректность расчета НДС (20%)"):
        expected_vat = round(goods_price * 0.2, 2)
        assert abs(vat - expected_vat) < 0.1

    with allure.step("Проверяю корректность итоговой суммы"):
        expected_total = goods_price + vat
        assert abs(total - expected_total) < 0.1

    with allure.step("Увеличиваю количество первого товара на 1"):
        cart.increase_quantity_by_button(0, 1)

    with allure.step("Проверяю, что все строчки стоимости пересчитались"):
        new_goods_price = cart.get_calculation_goods_price()
        new_vat = cart.get_calculation_vat()
        new_total = cart.get_calculation_total()

        assert new_goods_price > goods_price
        assert new_vat > vat
        assert new_total > total


@allure.title("TC-812: Отправка заказа")
@allure.tag("positive", "regression", "smoke", "non-automated")
@allure.severity(allure.severity_level.CRITICAL)
def test_send_order(base_url, page_fixture):
    """
    Предусловия:
    - В корзину добавлен товар
    - Все необходимые поля заполнены

    Шаги:
    1. Нажать Отправить

    Ожидаемый результат:
    - Заказ отправлен
    """
    page = page_fixture(role="buyer_admin")
    cart = CartPage(page)

    cart.clear_cart(base_url)
    # ... добавление товара
    cart.open(base_url)

    with allure.step("Проверяю, что кнопка Отправить активна"):
        assert cart.is_send_button_enabled()

    with allure.step("Нажимаю кнопку Отправить"):
        cart.click_send_button()

    with allure.step("Проверяю успешную отправку заказа"):
        expect(page.locator(cart.SUCCESS_MESSAGE)).to_be_visible(timeout=10000)



@allure.title("TC-780: Расчет общей стоимости при увеличении количества товара")
@allure.tag("positive", "regression", "manual_artefact")
def test_calculate_total_price_on_quantity_increase(base_url, page_fixture):
    """
    Предусловия:
    - В корзине один товар с ценой, например 471 ₽

    Шаги:
    1. Увеличить количество товара до 3 штук через кнопку "+"

    Ожидаемый результат:
    - Общая стоимость товара рассчитывается корректно (471 × 3 = 1413)
    """
    page = page_fixture(role="buyer_admin")
    cart = CartPage(page)

    # Подготовка: добавляем товар в корзину
    cart.clear_cart(base_url)
    # ... добавление товара с ценой 471 ₽

    cart.open(base_url)

    with allure.step("Фиксирую начальную цену товара"):
        initial_price = cart.get_calculation_goods_price()
        allure.attach(f"Начальная цена: {initial_price} ₽", name="Начальная цена")

    with allure.step("Увеличиваю количество товара до 3 штук"):
        cart.increase_quantity_by_button(index=0, count=2)
        time.sleep(1)

    with allure.step("Проверяю корректность расчета общей стоимости"):
        final_price = cart.get_calculation_goods_price()
        expected_price = initial_price * 3
        assert final_price == expected_price, f"Ожидалось {expected_price}, получено {final_price}"