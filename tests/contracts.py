import time

# test_contract_detail.py

import allure
import pytest
from playwright.sync_api import expect

from page_opjects.autorization_page import AutorizationPage
from page_opjects.listing_page import ListingPage
from page_opjects.settings_page.contract_detail_page import (
    ContractDetailPage,
    ContractManagementTab,
    ContractAssortmentTab,
    ContractDiscountsTab,
    ContractDeliveryTab,
)

# ── Константы ──
CONTRACT_URL_SUFFIX = "/settings/contract/6/general"  # подставить реальный ID
CATALOG_URL = "/catalog/9/3076"
TEST_MANAGER_EMAIL = "testgarwin_yur+4@mail.ru"
TEST_MANAGER_NAME = "Тестовый продавец для выбора в контракт"
TEST_BRAND = "Licota"
TEST_CATEGORY = "Автосвет"
TEST_BRAND_DISCOUNT = "10"

# ════════════════════════════════════════════════════════
# Переключение вкладок
# ════════════════════════════════════════════════════════

@allure.title("Переключение вкладок контракта")
def test_switch_tabs(base_url, page_fixture):
    """
    Тест-кейс:
    1. Открыть контракт — по умолчанию «Управление контрактом»
    2. Проверить кнопку «+ Добавить менеджера»
    3. Переключиться на «Ассортимент» — видны кнопки настройки
    4. Переключиться на «Скидки» — видно поле скидки
    5. Переключиться на «Сроки доставки» — видны склады
    6. Вернуться на «Управление контрактом»
    """
    page = page_fixture()
    auth = AutorizationPage(page)
    contract = ContractDetailPage(page)

    auth.open(base_url)
    auth.admin_seller_authorize()
    contract.open(base_url + CONTRACT_URL_SUFFIX)

    with allure.step("По умолчанию — «Управление контрактом»"):
        assert page.locator("text=Менеджер по контракту").is_visible()
        assert page.locator("text=Добавить менеджера").is_visible()

    with allure.step("Переключаюсь на «Ассортимент»"):
        contract.go_to_assortment_tab()
        assert page.locator("text=Ручная настройка ассортимента").is_visible()
        assert page.locator("text=Настроить категории товаров").is_visible()
        assert page.locator("text=Настроить бренды").is_visible()

    with allure.step("Переключаюсь на «Скидки»"):
        contract.go_to_discounts_tab()
        assert page.locator("text=Базовая скидка на ассортимент").is_visible()
        assert page.locator("text=Скидка на бренд").is_visible()

    with allure.step("Переключаюсь на «Сроки доставки»"):
        contract.go_to_delivery_tab()
        delivery = ContractDeliveryTab(page)
        assert delivery.get_warehouses_count() > 0

    with allure.step("Возвращаюсь на «Управление контрактом»"):
        contract.go_to_management_tab()
        assert page.locator("text=Менеджер по контракту").is_visible()


@allure.title("Добавление и удаление менеджера контракта с проверкой доступа к корзинам")
def test_add_and_delete_contract_manager(base_url, page_fixture):

    page_seller = page_fixture()
    auth_seller = AutorizationPage(page_seller)
    contract = ContractDetailPage(page_seller)
    management = ContractManagementTab(page_seller)

    page_manager = page_fixture()
    auth_manager = AutorizationPage(page_manager)

    BASKETS_URL = "https://sprout-store.ru/active-basket-list"
    BASKET_CELL = ".ant-table-cell"
    EMPTY_MESSAGE = "text=Корзины клиентов не найдены"

    # ── Продавец: подготовка ──
    auth_seller.open(base_url)
    auth_seller.admin_seller_authorize()
    contract.open(base_url + CONTRACT_URL_SUFFIX)

    if management.is_manager_present(TEST_MANAGER_EMAIL):
        management.delete_manager(TEST_MANAGER_EMAIL)
        page_seller.wait_for_timeout(1000)

    initial_count = management.get_managers_count()

    # ── Открытие модалки и отмена ──
    with allure.step("Открываю модалку и отменяю"):
        management.click_add_manager()
        assert management.is_modal_visible(), "Модалка не открылась"
        management.cancel_modal()
        assert not management.is_modal_visible(), "Модалка не закрылась"
        assert management.get_managers_count() == initial_count

    # ── Добавление менеджера ──
    with allure.step("Добавляю менеджера"):
        management.click_add_manager()
        management.search_in_modal(TEST_MANAGER_NAME)
        management.select_first_employee()
        page_seller.wait_for_timeout(1000)

    with allure.step("Менеджер появился в списке"):
        assert management.is_manager_present(TEST_MANAGER_EMAIL)
        assert management.get_managers_count() == initial_count + 1

    # ── Менеджер: проверка доступа к корзинам ──
    with allure.step("Авторизуюсь как менеджер контракта"):
        auth_manager.open(base_url)
        auth_manager.for_contract_manager_authorize()
        page_manager.wait_for_load_state("networkidle")

    with allure.step("Перехожу на страницу активных корзин"):
        forbidden_responses = []

        def capture_403(response):
            if response.status == 403:
                forbidden_responses.append(response.url)

        page_manager.on("response", capture_403)
        page_manager.goto(BASKETS_URL)
        page_manager.wait_for_load_state("networkidle")
        page_manager.wait_for_timeout(2000)
        page_manager.remove_listener("response", capture_403)

    with allure.step("Проверяю: нет 403, нет forbidden resource"):
        assert len(forbidden_responses) == 0, (
            f"Получены 403 при наличии роли менеджера: {forbidden_responses}"
        )
        assert not page_manager.locator("text=/forbidden resource/i").is_visible(), (
            "Нотификация 'forbidden resource' при наличии роли менеджера"
        )

    with allure.step("Проверяю: корзины отображаются"):
        has_baskets = page_manager.locator(BASKET_CELL).count() > 0
        no_empty_msg = not page_manager.locator(EMPTY_MESSAGE).is_visible()
        assert has_baskets and no_empty_msg, (
            "Корзины клиентов не найдены или таблица пуста"
        )

    allure.attach(
        page_manager.screenshot(full_page=True),
        name="baskets-with-manager-role",
        attachment_type=allure.attachment_type.PNG,
    )

    # ── Продавец: удаление менеджера ──
    with allure.step("Удаляю менеджера"):
        management.delete_manager(TEST_MANAGER_EMAIL)
        page_seller.wait_for_timeout(1000)

    with allure.step("Менеджер удалён"):
        assert not management.is_manager_present(TEST_MANAGER_EMAIL)
        assert management.get_managers_count() == initial_count

    # ── Менеджер: проверка что доступ пропал ──
    with allure.step("Обновляю страницу корзин после удаления"):
        forbidden_after = []

        def capture_403_after(response):
            if response.status == 403:
                forbidden_after.append(response.url)

        page_manager.on("response", capture_403_after)
        page_manager.reload()
        page_manager.wait_for_load_state("networkidle")
        page_manager.wait_for_timeout(2000)
        page_manager.remove_listener("response", capture_403_after)

    with allure.step("Проверяю: корзины недоступны"):
        baskets_gone = page_manager.locator(EMPTY_MESSAGE).is_visible() or \
                       len(forbidden_after) > 0 or \
                       page_manager.locator("text=/forbidden resource/i").is_visible() or \
                       page_manager.locator(BASKET_CELL).count() == 0

        assert baskets_gone, (
            "После удаления менеджера корзины всё ещё доступны"
        )

    allure.attach(
        page_manager.screenshot(full_page=True),
        name="baskets-without-manager-role",
        attachment_type=allure.attachment_type.PNG,
    )


# ════════════════════════════════════════════════════════
# TC-03: Категории — модалка, поиск, дерево, снятие/установка
# ════════════════════════════════════════════════════════

@allure.title("Настройка категорий — модалка, поиск, дерево, переключение чекбокса")
def test_categories_modal_search_and_toggle(base_url, page_fixture):
    """
    Тест-кейс:
    1. Открыть «Ассортимент» → «Настроить категории товаров» — модалка открылась
    2. Видны «Все категории» и поле поиска
    3. Поиск «Автотовары» — фильтрация работает
    4. Очистка поиска — полный список вернулся
    5. Раскрыть «Автотовары» — дочерние видны (Автосвет, Автоэлектроника)
    6. Снять чекбокс с «Автосвет» → Сохранить
    7. Снова открыть категории → «Автосвет» не отмечен
    8. Вернуть чекбокс → Сохранить (постусловие)
    """
    page = page_fixture()
    auth = AutorizationPage(page)
    contract = ContractDetailPage(page)
    assortment = ContractAssortmentTab(page)

    auth.open(base_url)
    auth.admin_seller_authorize()
    contract.open(base_url + CONTRACT_URL_SUFFIX)
    contract.go_to_assortment_tab()

    # Открытие модалки
    with allure.step("Открываю модалку категорий"):
        assortment.click_categories()
        time.sleep(3)
        assert assortment.is_modal_visible(), "Модалка категорий не открылась"
        assert page.locator("text=Все категории").is_visible()

    # Поиск
    total_count = assortment.get_visible_items_count()

    with allure.step("Ищу «Автотовары»"):
        assortment.search_in_modal("Автотовары")
        filtered = assortment.get_visible_items_count()
        assert filtered > 0, "Поиск не дал результатов"
        assert filtered <= total_count, "Фильтрация не сработала"

    with allure.step("Очищаю поиск"):
        assortment.clear_search()
        restored = assortment.get_visible_items_count()
        assert restored == total_count, "Список не восстановился"

    with allure.step("Закрываю модалку категорий"):
        assortment.click_cancel()
        assert not page.locator("text=Все категории").is_visible()

    # Дерево
    # with allure.step("Раскрываю «Автотовары»"):
    #     assortment.expand_category("Автотовары")
    #     assert page.locator("text=Автоаксессуары").is_visible()
    #     assert page.locator(f"text={TEST_CATEGORY}").is_visible()
    #     assert page.locator("text=Автоэлектроника").is_visible()
    #
    # # Переключение чекбокса
    # with allure.step(f"Запоминаю состояние «{TEST_CATEGORY}»"):
    #     was_checked = assortment.is_item_checked(TEST_CATEGORY)
    #
    # with allure.step(f"Снимаю чекбокс «{TEST_CATEGORY}»"):
    #     assortment.uncheck_item(TEST_CATEGORY)
    #     assert not assortment.is_item_checked(TEST_CATEGORY)
    #
    # with allure.step("Сохраняю"):
    #     assortment.click_save()
    #     page.wait_for_timeout(1000)
    #
    # with allure.step("Повторно открываю и проверяю"):
    #     assortment.click_categories()
    #     assortment.expand_category("Автотовары")
    #     assert not assortment.is_item_checked(TEST_CATEGORY), (
    #         f"«{TEST_CATEGORY}» всё ещё отмечен после сохранения"
    #     )
    #
    # # Постусловие
    # with allure.step("Постусловие: возвращаю чекбокс"):
    #     assortment.check_item(TEST_CATEGORY)
    #     assortment.click_save()
    #     page.wait_for_timeout(1000)


# ════════════════════════════════════════════════════════
# TC-04: Бренды — модалка, поиск, снятие/установка
# ════════════════════════════════════════════════════════

@allure.title("Настройка брендов — модалка, поиск, переключение чекбокса")
def test_brands_modal_search_and_toggle(base_url, page_fixture):
    """
    Тест-кейс:
    1. Открыть «Ассортимент» → «Настроить бренды» — модалка открылась
    2. Видны «Все бренды» и поле поиска
    3. Поиск «3M» — найден
    4. Поиск несуществующего бренда — нет результатов
    5. Очистка — список вернулся
    6. Снять чекбокс «2Hands» → Сохранить
    7. Повторно открыть → «2Hands» не отмечен
    8. Вернуть → Сохранить (постусловие)
    """
    page = page_fixture()
    auth = AutorizationPage(page)
    contract = ContractDetailPage(page)
    assortment = ContractAssortmentTab(page)

    auth.open(base_url)
    auth.admin_seller_authorize()
    contract.open(base_url + CONTRACT_URL_SUFFIX)
    contract.go_to_assortment_tab()

    test_brand = "2Hands"

    with allure.step("Открываю модалку брендов"):
        assortment.click_brands()
        time.sleep(3)
        assert assortment.is_modal_visible(), "Модалка брендов не открылась"
        assert page.locator("text=Все бренды").is_visible()

    # Поиск
    total = assortment.get_visible_items_count()

    with allure.step("Ищу «garwin»"):
        assortment.search_in_modal("garwin")
        assert page.locator(".ant-modal-content:has-text('garwin')").is_visible()

    with allure.step("Очищаю поиск"):
        assortment.clear_search()
        assert assortment.get_visible_items_count() == total

    with allure.step("Закрываю модалку брендов"):
        assortment.click_cancel()
        assert not page.locator("text=Все бренды").is_visible()

    # # Переключение
    # with allure.step(f"Запоминаю состояние «{test_brand}»"):
    #     was_checked = assortment.is_item_checked(test_brand)
    #
    # with allure.step(f"Снимаю чекбокс «{test_brand}»"):
    #     assortment.uncheck_item(test_brand)
    #     assert not assortment.is_item_checked(test_brand)
    #
    # with allure.step("Сохраняю"):
    #     assortment.click_save()
    #     page.wait_for_timeout(1000)
    #
    # with allure.step("Повторно открываю и проверяю"):
    #     assortment.click_brands()
    #     assert not assortment.is_item_checked(test_brand)
    #
    # # Постусловие
    # with allure.step("Постусловие: возвращаю"):
    #     assortment.check_item(test_brand)
    #     assortment.click_save()
    #     page.wait_for_timeout(1000)



# TODO расскоментировать когда доделаю

#
# # ════════════════════════════════════════════════════════
# # TC-05: Базовая скидка — E2E с проверкой в каталоге покупателя
# # ════════════════════════════════════════════════════════
#
# @allure.title("Базовая скидка — изменение и проверка цены в каталоге покупателя")
# def test_base_discount_e2e(base_url, page_fixture):
#     """
#     Тест-кейс:
#     1. Продавец: открыть «Скидки», запомнить текущую скидку
#     2. Установить скидку 0% → сохранить
#     3. Покупатель: открыть каталог, запомнить цену товара (без скидки)
#     4. Продавец: установить скидку 10%
#     5. Покупатель: обновить каталог, проверить что цена стала на 10% ниже
#     6. Постусловие: вернуть исходную скидку
#     """
#     page_seller = page_fixture()
#     auth_seller = AutorizationPage(page_seller)
#     contract = ContractDetailPage(page_seller)
#     discounts = ContractDiscountsTab(page_seller)
#
#     page_buyer = page_fixture()
#     auth_buyer = AutorizationPage(page_buyer)
#     listing = ListingPage(page_buyer)
#
#     def parse_price(price_str: str) -> float:
#         """Парсит '1 151.00 ₽' → 1151.0"""
#         cleaned = price_str.replace("₽", "").replace(" ", "").strip()
#         # Остаётся '1151.00'
#         return float(cleaned)
#
#     # ── Продавец: обнуляю скидку ──
#     auth_seller.open(base_url)
#     auth_seller.admin_seller_authorize()
#     contract.open(base_url + CONTRACT_URL_SUFFIX)
#     contract.go_to_discounts_tab()
#
#     with allure.step("Запоминаю исходную скидку"):
#         original_discount = discounts.get_base_discount()
#         allure.attach(original_discount, name="Исходная скидка")
#
#     with allure.step("Устанавливаю скидку 0%"):
#         discounts.set_base_discount("0")
#         page_seller.wait_for_timeout(1000)
#
#     # ── Покупатель: цена без скидки ──
#     auth_buyer.open(base_url)
#     auth_buyer.admin_buyer_authorize()
#
#     with allure.step("Открываю каталог и запоминаю цену без скидки"):
#         listing.open_url(base_url + CATALOG_URL)
#         page_buyer.wait_for_timeout(1000)
#         prices_without_discount = listing.get_price_data()
#         assert len(prices_without_discount) > 0, "Нет товаров в каталоге"
#
#         first_price_original = parse_price(prices_without_discount[0]["full_price"])
#         allure.attach(str(first_price_original), name="Цена без скидки")
#
#     # ── Продавец: устанавливаю 10% ──
#     with allure.step("Устанавливаю скидку 10%"):
#         contract.open(base_url + CONTRACT_URL_SUFFIX)
#         contract.go_to_discounts_tab()
#         discounts.set_base_discount("10")
#         page_seller.wait_for_timeout(1000)
#
#     # ── Покупатель: проверяю пересчёт ──
#     with allure.step("Обновляю каталог и проверяю цену со скидкой"):
#         page_buyer.reload()
#         page_buyer.wait_for_load_state("networkidle")
#         page_buyer.wait_for_timeout(1000)
#
#         prices_with_discount = listing.get_price_data()
#         first_price_discounted = parse_price(prices_with_discount[0]["full_price"])
#         allure.attach(str(first_price_discounted), name="Цена со скидкой 10%")
#
#         expected = round(first_price_original * 0.9, 2)
#         assert abs(first_price_discounted - expected) <= 1, (
#             f"Цена не пересчиталась. "
#             f"Исходная: {first_price_original}, "
#             f"ожидал ~{expected}, получил {first_price_discounted}"
#         )
#
#     # ── Постусловие ──
#     with allure.step("Возвращаю исходную скидку"):
#         contract.open(base_url + CONTRACT_URL_SUFFIX)
#         contract.go_to_discounts_tab()
#         discounts.set_base_discount(original_discount)
#         page_seller.wait_for_timeout(1000)
#
#
# # ════════════════════════════════════════════════════════
# # TC-06: Скидка на бренд — CRUD + drawer
# # ════════════════════════════════════════════════════════
#
# @allure.title("Скидка на бренд — создание, редактирование через drawer, удаление")
# def test_brand_discount_crud(base_url, page_fixture):
#     """
#     Тест-кейс:
#     1. Открыть «Скидки», запомнить количество скидок на бренд
#     2. Нажать «+ Скидка на бренд» — drawer открылся
#     3. Выбрать бренд Licota, установить 10%, сохранить
#     4. Скидка появилась в списке
#     5. Открыть экшн-меню → «Настроить» → drawer с данными Licota 10%
#     6. Изменить скидку на 15%, сохранить
#     7. Удалить скидку через экшн-меню → «Удалить скидку»
#     8. Количество вернулось к исходному
#     """
#     page = page_fixture()
#     auth = AutorizationPage(page)
#     contract = ContractDetailPage(page)
#     discounts = ContractDiscountsTab(page)
#
#     auth.open(base_url)
#     auth.admin_seller_authorize()
#     contract.open(base_url + CONTRACT_URL_SUFFIX)
#     contract.go_to_discounts_tab()
#
#     initial_count = discounts.get_brand_discounts_count()
#
#     # Создание
#     with allure.step("Создаю скидку на бренд"):
#         discounts.click_add_brand_discount()
#         assert discounts.is_drawer_visible(), "Drawer не открылся"
#
#     with allure.step("Выбираю бренд и устанавливаю скидку"):
#         discounts.select_brand_in_drawer(TEST_BRAND)
#         discounts.set_discount_in_drawer(TEST_BRAND_DISCOUNT)
#         discounts.save_drawer()
#         page.wait_for_timeout(1000)
#
#     with allure.step("Скидка появилась в списке"):
#         assert page.locator(f"text=/{TEST_BRAND}.*{TEST_BRAND_DISCOUNT}%/").is_visible() or \
#                page.locator(f"text={TEST_BRAND} {TEST_BRAND_DISCOUNT}%").is_visible(), (
#             "Скидка на бренд не отображается в списке"
#         )
#         assert discounts.get_brand_discounts_count() == initial_count + 1
#
#     # Редактирование через «Настроить»
#     with allure.step("Открываю drawer через «Настроить»"):
#         discounts.open_brand_discount_menu(initial_count)  # последняя добавленная
#         discounts.click_configure()
#         assert discounts.is_drawer_visible(), "Drawer не открылся"
#
#     with allure.step("Проверяю данные в drawer"):
#         assert TEST_BRAND in discounts.get_drawer_brand_value()
#         assert discounts.get_drawer_discount_value() == TEST_BRAND_DISCOUNT
#
#     with allure.step("Меняю скидку на 15%"):
#         discounts.set_discount_in_drawer("15")
#         discounts.save_drawer()
#         page.wait_for_timeout(1000)
#
#     # Удаление
#     with allure.step("Удаляю скидку через экшн-меню"):
#         discounts.open_brand_discount_menu(initial_count)
#         discounts.click_delete_discount()
#         page.wait_for_timeout(1000)
#
#     with allure.step("Количество вернулось к исходному"):
#         assert discounts.get_brand_discounts_count() == initial_count

# # ════════════════════════════════════════════════════════
# # TC-07: Скидка на бренд — E2E с каталогом покупателя
# # ════════════════════════════════════════════════════════
#
# CATALOG_URL = "/catalog/9/3076"
#
#
# @allure.suite("Настройки контракта")
# @allure.title("TC-07: Скидка на бренд — Licota со скидкой, GARWIN без изменений")
# @allure.severity(allure.severity_level.BLOCKER)
# def test_brand_discount_e2e(base_url, page_fixture):
#     """
#     1. Продавец: базовая скидка 0%
#     2. Покупатель: фильтр Licota → запомнить цену; фильтр GARWIN → запомнить цену
#     3. Продавец: создать скидку Licota 10%
#     4. Покупатель: Licota -10%, GARWIN без изменений
#     5. Продавец: удалить скидку
#     6. Покупатель: Licota вернулась, GARWIN та же
#     """
#
#     page_seller = page_fixture()
#     auth_seller = AutorizationPage(page_seller)
#     contract = ContractDetailPage(page_seller)
#     discounts = ContractDiscountsTab(page_seller)
#
#     page_buyer = page_fixture()
#     auth_buyer = AutorizationPage(page_buyer)
#     listing = ListingPage(page_buyer)
#
#     def parse_price(price_str: str) -> float:
#         cleaned = price_str.replace("₽", "").replace("\xa0", "").replace(" ", "").strip()
#         return float(cleaned)
#
#     # ══════════════════════════════════════════════
#     # Продавец: подготовка
#     # ══════════════════════════════════════════════
#     auth_seller.open(base_url)
#     auth_seller.admin_seller_authorize()
#     contract.open(base_url + CONTRACT_URL_SUFFIX)
#     contract.go_to_discounts_tab()
#
#     with allure.step("Запоминаю исходную скидку и обнуляю"):
#         original_base = discounts.get_base_discount()
#         discounts.set_base_discount("0")
#         page_seller.wait_for_timeout(1000)
#
#     # ══════════════════════════════════════════════
#     # Покупатель: цены без скидки
#     # ══════════════════════════════════════════════
#     auth_buyer.open(base_url)
#     auth_buyer.admin_buyer_authorize()
#     listing.open_url(base_url + CATALOG_URL)
#     page_buyer.wait_for_timeout(1000)
#
#     with allure.step("Фильтрую по Licota и запоминаю цену"):
#         listing.filter_by_brand("Licota")
#         licota_raw = listing.get_first_product_price()
#         licota_before = parse_price(licota_raw)
#         allure.attach(str(licota_before), name="Licota — до скидки")
#
#     with allure.step("Сбрасываю фильтр, фильтрую по GARWIN и запоминаю цену"):
#         listing.clear_brand_filter()
#         listing.filter_by_brand("GARWIN")
#         garwin_raw = listing.get_first_product_price()
#         garwin_before = parse_price(garwin_raw)
#         allure.attach(str(garwin_before), name="GARWIN — до скидки")
#         listing.clear_brand_filter()
#
#     # ══════════════════════════════════════════════
#     # Продавец: скидка Licota 10%
#     # ══════════════════════════════════════════════
#     with allure.step("Создаю скидку Licota 10%"):
#         contract.open(base_url + CONTRACT_URL_SUFFIX)
#         contract.go_to_discounts_tab()
#         discounts.click_add_brand_discount()
#         discounts.select_brand_in_drawer("Licota")
#         discounts.set_discount_in_drawer("10")
#         discounts.save_drawer()
#         page_seller.wait_for_timeout(1000)
#
#     # ══════════════════════════════════════════════
#     # Покупатель: Licota подешевел, GARWIN — нет
#     # ══════════════════════════════════════════════
#     with allure.step("Обновляю каталог"):
#         listing.open_url(base_url + CATALOG_URL)
#         page_buyer.wait_for_load_state("networkidle")
#         page_buyer.wait_for_timeout(1000)
#
#     with allure.step("Проверяю: цена Licota снизилась на 10%"):
#         listing.filter_by_brand("Licota")
#         licota_after_raw = listing.get_first_product_price()
#         licota_after = parse_price(licota_after_raw)
#         allure.attach(str(licota_after), name="Licota — со скидкой")
#
#         expected_licota = round(licota_before * 0.9, 2)
#         assert abs(licota_after - expected_licota) <= 1, (
#             f"Скидка на Licota не применилась. "
#             f"Было: {licota_before}, ожидал ~{expected_licota}, факт: {licota_after}"
#         )
#
#     with allure.step("Проверяю: цена GARWIN НЕ изменилась"):
#         listing.clear_brand_filter()
#         listing.filter_by_brand("GARWIN")
#         garwin_after_raw = listing.get_first_product_price()
#         garwin_after = parse_price(garwin_after_raw)
#         allure.attach(str(garwin_after), name="GARWIN — после скидки на Licota")
#
#         assert abs(garwin_after - garwin_before) <= 1, (
#             f"Цена GARWIN изменилась, хотя скидка только на Licota! "
#             f"Было: {garwin_before}, стало: {garwin_after}"
#         )
#         listing.clear_brand_filter()
#
#     allure.attach(
#         page_buyer.screenshot(full_page=True),
#         name="catalog-with-licota-discount",
#         attachment_type=allure.attachment_type.PNG,
#     )
#
#     # ══════════════════════════════════════════════
#     # Продавец: удаляю скидку
#     # ══════════════════════════════════════════════
#     with allure.step("Удаляю скидку на Licota"):
#         contract.open(base_url + CONTRACT_URL_SUFFIX)
#         contract.go_to_discounts_tab()
#         discounts.open_brand_discount_menu(0)
#         discounts.click_delete_discount()
#         page_seller.wait_for_timeout(1000)
#
#     # ══════════════════════════════════════════════
#     # Покупатель: всё вернулось
#     # ══════════════════════════════════════════════
#     with allure.step("Обновляю каталог"):
#         listing.open_url(base_url + CATALOG_URL)
#         page_buyer.wait_for_load_state("networkidle")
#         page_buyer.wait_for_timeout(1000)
#
#     with allure.step("Цена Licota вернулась"):
#         listing.filter_by_brand("Licota")
#         licota_restored_raw = listing.get_first_product_price()
#         licota_restored = parse_price(licota_restored_raw)
#         allure.attach(str(licota_restored), name="Licota — после удаления скидки")
#
#         assert abs(licota_restored - licota_before) <= 1, (
#             f"Цена Licota не вернулась. Было: {licota_before}, факт: {licota_restored}"
#         )
#
#     with allure.step("Цена GARWIN по-прежнему та же"):
#         listing.clear_brand_filter()
#         listing.filter_by_brand("GARWIN")
#         garwin_restored_raw = listing.get_first_product_price()
#         garwin_restored = parse_price(garwin_restored_raw)
#
#         assert abs(garwin_restored - garwin_before) <= 1, (
#             f"Цена GARWIN изменилась! Было: {garwin_before}, стало: {garwin_restored}"
#         )
#         listing.clear_brand_filter()
#
#     allure.attach(
#         page_buyer.screenshot(full_page=True),
#         name="catalog-after-discount-removed",
#         attachment_type=allure.attachment_type.PNG,
#     )
#
#     # ══════════════════════════════════════════════
#     # Постусловие
#     # ══════════════════════════════════════════════
#     with allure.step("Возвращаю исходную базовую скидку"):
#         contract.open(base_url + CONTRACT_URL_SUFFIX)
#         contract.go_to_discounts_tab()
#         discounts.set_base_discount(original_base)
#         page_seller.wait_for_timeout(500)


# # ════════════════════════════════════════════════════════
# # TC-08: Сроки доставки — склады, адреса, dropdown, изменение
# # ════════════════════════════════════════════════════════
#
# @allure.suite("Настройки контракта")
# @allure.title("TC-08: Сроки доставки — раскрытие склада, все опции, изменение срока")
# @allure.severity(allure.severity_level.NORMAL)
# def test_delivery_terms_full(base_url, page_fixture):
#     """
#     Тест-кейс:
#     1. Открыть «Сроки доставки» — список складов не пуст
#     2. Раскрыть первый склад — адреса видны
#     3. Открыть dropdown — все 8 опций отображаются
#     4. Запомнить текущий срок
#     5. Изменить срок на «72 часа» (или «1 неделя» если уже 72ч)
#     6. Проверить что срок изменился
#     7. Вернуть исходный срок
#     """
#     page = page_fixture()
#     auth = AutorizationPage(page)
#     contract = ContractDetailPage(page)
#     delivery = ContractDeliveryTab(page)
#
#     auth.open(base_url)
#     auth.admin_seller_authorize()
#     contract.open(base_url + CONTRACT_URL_SUFFIX)
#     contract.go_to_delivery_tab()
#
#     with allure.step("Список складов не пуст"):
#         count = delivery.get_warehouses_count()
#         allure.attach(str(count), name="Складов")
#         assert count > 0
#
#     with allure.step("Раскрываю первый склад"):
#         delivery.expand_warehouse(0)
#         addr_count = delivery.get_addresses_count()
#         allure.attach(str(addr_count), name="Адресов")
#         assert addr_count > 0
#
#     with allure.step("Открываю dropdown — все опции видны"):
#         delivery.click_delivery_select(0)
#         assert delivery.are_all_options_visible(), "Не все опции сроков видны"
#
#     with allure.step("Запоминаю текущий срок"):
#         page.keyboard.press("Escape")
#         original = delivery.get_current_term(0)
#         allure.attach(original, name="Исходный срок")
#
#     new_term = "72 часа" if original != "72 часа" else "1 неделя"
#
#     with allure.step(f"Меняю срок на «{new_term}»"):
#         delivery.click_delivery_select(0)
#         delivery.select_option(new_term)
#         page.wait_for_timeout(1000)
#
#     with allure.step("Срок изменился"):
#         current = delivery.get_current_term(0)
#         assert new_term in current, f"Ожидал {new_term}, получил {current}"
#
#     with allure.step("Постусловие: возвращаю срок"):
#         delivery.click_delivery_select(0)
#         delivery.select_option(original if original else "24 часа")
#         page.wait_for_timeout(1000)
#
#
# # ════════════════════════════════════════════════════════
# # TC-09 и TC-10: Тест-кейсы БЕЗ автотестов (применение
# # категорий/брендов в каталоге — занимает несколько минут)
# # ════════════════════════════════════════════════════════
#
# # Эти тест-кейсы выполняются вручную, код — заглушки для документации
#
# @allure.suite("Настройки контракта")
# @allure.title("TC-09: [РУЧНОЙ] Снятие категории → товары исчезают из каталога покупателя")
# @allure.severity(allure.severity_level.CRITICAL)
# @pytest.mark.manual
# @pytest.mark.skip(reason="Применение занимает несколько минут — ручной тест-кейс")
# def test_category_removal_affects_catalog():
#     """
#     Тест-кейс (ручной):
#     ПРЕДУСЛОВИЕ: все категории включены, покупатель видит товары «Автосвет»
#
#     ШАГИ:
#     1. Продавец: Ассортимент → Настроить категории → снять «Автосвет» → Сохранить
#     2. Дождаться исчезновения баннера «Изменения применяются» (~2-5 мин)
#     3. Покупатель: открыть каталог → категория «Автосвет» отсутствует в дереве
#     4. Покупатель: поиск товара из «Автосвет» → не найден
#
#     ПОСТУСЛОВИЕ:
#     5. Продавец: вернуть чекбокс «Автосвет» → Сохранить
#     6. Дождаться применения
#     7. Покупатель: товары снова видны
#
#     ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:
#     - После снятия категории товары не отображаются у покупателя
#     - После возврата категории товары снова видны
#     """
#     pass
#
#
# @allure.suite("Настройки контракта")
# @allure.title("TC-10: [РУЧНОЙ] Снятие бренда → товары бренда исчезают из каталога покупателя")
# @allure.severity(allure.severity_level.CRITICAL)
# @pytest.mark.manual
# @pytest.mark.skip(reason="Применение занимает несколько минут — ручной тест-кейс")
# def test_brand_removal_affects_catalog():
#     """
#     Тест-кейс (ручной):
#     ПРЕДУСЛОВИЕ: все бренды включены, покупатель видит товары «2Hands»
#
#     ШАГИ:
#     1. Продавец: Ассортимент → Настроить бренды → снять «2Hands» → Сохранить
#     2. Дождаться исчезновения баннера «Изменения применяются» (~2-5 мин)
#     3. Покупатель: фильтр по бренду «2Hands» → нет результатов
#     4. Покупатель: товары бренда не отображаются в каталоге
#
#     ПОСТУСЛОВИЕ:
#     5. Продавец: вернуть чекбокс «2Hands» → Сохранить
#     6. Дождаться применения
#     7. Покупатель: товары «2Hands» снова видны
#
#     ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:
#     - После снятия бренда его товары не видны покупателю
#     - После возврата бренда товары снова доступны
#     """
#     pass
