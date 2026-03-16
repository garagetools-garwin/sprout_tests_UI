# import time
# import allure
# import pytest
# from playwright.sync_api import expect
#
# from page_opjects.autorization_page import AutorizationPage
# from page_opjects.cart_page import CartPage
# from page_opjects.listing_page import ListingPage
# from page_opjects.settings_page.limits_page import LimitsPage
#
# """
# Тесты лимитов на закупку.
#
# ТИП 1 — Лимит на общую сумму заказа:
#   Источники: персональный лимит пользователя, лимит подразделения.
#   Если заданы оба — берётся минимальный.
#   Лимита на сумму на уровне компании — НЕТ.
#
# ТИП 2 — Лимит на цену за единицу товара (maxGoodPrice):
#   Источники: лимит подразделения, лимит компании.
#   Если есть лимит подразделения — он приоритетный.
#   Если нет — берётся лимит компании.
# """
#
# # ============================================================================
# # КОНСТАНТЫ
# # ============================================================================
#
# SUBDIVISION_ID = 136
# CATALOG_PATH = "/catalog/9/3707"
# TEST_SUBDIVISION = "Тестовое подразделение для теста лимитов(не трогать)"
# TEST_USER_EMAIL = "testgarwin_yur@mail.ru"
#
# HIGH = "1000000"
# LOW = "300"
#
#
# # ============================================================================
# # HELPERS
# # ============================================================================
#
#
# def init_all(page):
#     return (
#         AutorizationPage(page),
#         CartPage(page),
#         ListingPage(page),
#         LimitsPage(page),
#     )
#
#
# def auth_and_clear(base_url, page, auth, cart):
#     auth.open(base_url)
#     auth.admin_buyer_authorize()
#     cart.clear_cart(base_url)
#
#
# def add_item(page, base_url, listing, min_price):
#     with allure.step(f"Добавляю товар с ценой > {min_price}₽"):
#         page.goto(base_url + CATALOG_PATH)
#         listing.add_expensive_item_to_cart(min_price=min_price)
#
#
# def open_cart_and_select_subdivision(base_url, cart, page):
#     cart.open(base_url)
#     current = cart.get_selected_subdivision()
#     if current != TEST_SUBDIVISION:
#         cart.select_subdivision(TEST_SUBDIVISION)
#         time.sleep(1)
#
#
# class SavedLimits:
#     """Хранилище исходных значений лимитов для восстановления"""
#     def __init__(self):
#         self.sub_purchase = None
#         self.sub_item_price = None
#         self.company_item_price = None
#         self.personal_limit_value = None
#         self.personal_limit_existed = False
#
#
# def save_all_limits(base_url, limits: LimitsPage, subdivision_id: int, email: str) -> SavedLimits:
#     """Запоминает все текущие лимиты перед тестом"""
#     saved = SavedLimits()
#
#     with allure.step("Запоминаю текущие лимиты"):
#         limits.open_subdivision(base_url, subdivision_id)
#         saved.sub_purchase = limits.get_subdivision_purchase_limit()
#         saved.sub_item_price = limits.get_subdivision_item_price_limit()
#
#         saved.company_item_price = limits.get_company_item_price_limit(base_url)
#
#         limits.open_personal_limits(base_url)
#         saved.personal_limit_existed = limits.is_personal_limit_present(email)
#         if saved.personal_limit_existed:
#             saved.personal_limit_value = limits.get_personal_limit_value(email)
#
#         allure.attach(
#             f"Подразделение закупка: {saved.sub_purchase}\n"
#             f"Подразделение цена товара: {saved.sub_item_price}\n"
#             f"Компания цена товара: {saved.company_item_price}\n"
#             f"Персональный: {'есть (' + saved.personal_limit_value + ')' if saved.personal_limit_existed else 'нет'}",
#             name="Исходные лимиты"
#         )
#
#     return saved
#
#
# def restore_all_limits(base_url, limits: LimitsPage, subdivision_id: int, email: str, saved: SavedLimits):
#     """Восстанавливает все лимиты к исходным значениям после теста"""
#     with allure.step("Восстанавливаю исходные лимиты"):
#         if saved.sub_purchase:
#             limits.set_subdivision_purchase_limit(base_url, subdivision_id, saved.sub_purchase)
#         else:
#             limits.clear_subdivision_purchase_limit(base_url, subdivision_id)
#
#         if saved.sub_item_price:
#             limits.set_subdivision_item_price_limit(base_url, subdivision_id, saved.sub_item_price)
#         else:
#             limits.clear_subdivision_item_price_limit(base_url, subdivision_id)
#
#         if saved.company_item_price:
#             limits.set_company_item_price_limit(base_url, saved.company_item_price)
#         else:
#             limits.clear_company_item_price_limit(base_url)
#
#         if saved.personal_limit_existed and saved.personal_limit_value:
#             limits.set_personal_limit(base_url, email, saved.personal_limit_value)
#         elif not saved.personal_limit_existed:
#             limits.delete_personal_limit(base_url, email)
#
#
# # ============================================================================
# # ТИП 1: ЛИМИТ НА ОБЩУЮ СУММУ ЗАКАЗА
# # ============================================================================
#
#
# @allure.title("L-01: Только лимит подразделения на сумму заказа — блокировка и разблокировка")
# @allure.tag("limits", "subdivision", "order-total", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_only_subdivision_purchase_limit(base_url, page_fixture):
#     """
#     Чек-лист п.1:
#     Персональный лимит НЕ задан. Лимит подразделения задан.
#     а) Маленький лимит → блокировка
#     б) Большой лимит → разблокировка
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#
#     auth_and_clear(base_url, page, auth, cart)
#     saved = save_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL)
#
#     try:
#         with allure.step("Предусловие: убираю персональный лимит, ставлю высокий лимит цены"):
#             limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#             limits.set_subdivision_item_price_limit(base_url, SUBDIVISION_ID, HIGH)
#             limits.set_company_item_price_limit(base_url, HIGH)
#
#         # --- а) Маленький лимит → блокировка ---
#         with allure.step("Устанавливаю маленький лимит подразделения"):
#             limits.set_subdivision_purchase_limit(base_url, SUBDIVISION_ID, LOW)
#
#         add_item(page, base_url, listing, min_price=350)
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ заблокирован"):
#             limits.assert_blocked_by_purchase_limit(cart)
#
#         # --- б) Большой лимит → разблокировка ---
#         with allure.step("Устанавливаю большой лимит подразделения"):
#             limits.set_subdivision_purchase_limit(base_url, SUBDIVISION_ID, HIGH)
#
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ разблокирован"):
#             limits.assert_not_blocked(cart)
#
#     finally:
#         cart.clear_cart(base_url)
#         restore_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL, saved)
#
#
# @allure.title("L-02: Только персональный лимит на сумму заказа — блокировка и разблокировка")
# @allure.tag("limits", "personal", "order-total", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_only_personal_purchase_limit(base_url, page_fixture):
#     """
#     Чек-лист п.2:
#     Лимит подразделения НЕ задан. Персональный лимит задан.
#     а) Маленький → блокировка
#     б) Большой → разблокировка
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#
#     auth_and_clear(base_url, page, auth, cart)
#     saved = save_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL)
#
#     try:
#         with allure.step("Предусловие: убираю лимит подразделения, ставлю высокий лимит цены"):
#             limits.clear_subdivision_purchase_limit(base_url, SUBDIVISION_ID)
#             limits.set_subdivision_item_price_limit(base_url, SUBDIVISION_ID, HIGH)
#             limits.set_company_item_price_limit(base_url, HIGH)
#
#         # --- а) Маленький → блокировка ---
#         with allure.step("Устанавливаю маленький персональный лимит"):
#             limits.set_personal_limit(base_url, TEST_USER_EMAIL, LOW)
#
#         add_item(page, base_url, listing, min_price=350)
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ заблокирован"):
#             limits.assert_blocked_by_purchase_limit(cart)
#
#         # --- б) Большой → разблокировка ---
#         with allure.step("Устанавливаю большой персональный лимит"):
#             limits.set_personal_limit(base_url, TEST_USER_EMAIL, HIGH)
#
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ разблокирован"):
#             limits.assert_not_blocked(cart)
#
#     finally:
#         cart.clear_cart(base_url)
#         restore_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL, saved)
#
#
# @allure.title("L-03: Оба лимита заданы, подразделения меньше — применяется подразделения")
# @allure.tag("limits", "conflict", "order-total", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_both_limits_subdivision_is_stricter(base_url, page_fixture):
#     """
#     Чек-лист п.3:
#     Персональный: 1 000 000₽, подразделение: 300₽.
#     Берётся минимальный → подразделение.
#     а) Товар > 300₽ → блокировка
#     б) Увеличиваем подразделение до 1 000 000₽ → разблокировка
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#
#     auth_and_clear(base_url, page, auth, cart)
#     saved = save_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL)
#
#     try:
#         with allure.step("Предусловие: высокие лимиты цены на товар"):
#             limits.set_subdivision_item_price_limit(base_url, SUBDIVISION_ID, HIGH)
#             limits.set_company_item_price_limit(base_url, HIGH)
#
#         # --- а) Подразделение 300 < персональный 1М → блокировка ---
#         with allure.step("Устанавливаю: подразделение 300₽, персональный 1М₽"):
#             limits.set_subdivision_purchase_limit(base_url, SUBDIVISION_ID, LOW)
#             limits.set_personal_limit(base_url, TEST_USER_EMAIL, HIGH)
#
#         add_item(page, base_url, listing, min_price=350)
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ заблокирован (подразделение строже)"):
#             limits.assert_blocked_by_purchase_limit(cart)
#
#         # --- б) Увеличиваем подразделение → разблокировка ---
#         with allure.step("Увеличиваю лимит подразделения до 1М₽"):
#             limits.set_subdivision_purchase_limit(base_url, SUBDIVISION_ID, HIGH)
#
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ разблокирован"):
#             limits.assert_not_blocked(cart)
#
#     finally:
#         cart.clear_cart(base_url)
#         restore_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL, saved)
#
#
# @allure.title("L-04: Оба лимита заданы, персональный меньше — применяется персональный")
# @allure.tag("limits", "conflict", "order-total", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_both_limits_personal_is_stricter(base_url, page_fixture):
#     """
#     Чек-лист п.4:
#     Персональный: 300₽, подразделение: 1 000 000₽.
#     Берётся минимальный → персональный.
#     а) Товар > 300₽ → блокировка
#     б) Увеличиваем персональный до 1 000 000₽ → разблокировка
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#
#     auth_and_clear(base_url, page, auth, cart)
#     saved = save_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL)
#
#     try:
#         with allure.step("Предусловие: высокие лимиты цены на товар"):
#             limits.set_subdivision_item_price_limit(base_url, SUBDIVISION_ID, HIGH)
#             limits.set_company_item_price_limit(base_url, HIGH)
#
#         # --- а) Персональный 300 < подразделение 1М → блокировка ---
#         with allure.step("Устанавливаю: персональный 300₽, подразделение 1М₽"):
#             limits.set_subdivision_purchase_limit(base_url, SUBDIVISION_ID, HIGH)
#             limits.set_personal_limit(base_url, TEST_USER_EMAIL, LOW)
#
#         add_item(page, base_url, listing, min_price=350)
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ заблокирован (персональный строже)"):
#             limits.assert_blocked_by_purchase_limit(cart)
#
#         # --- б) Увеличиваем персональный → разблокировка ---
#         with allure.step("Увеличиваю персональный лимит до 1М₽"):
#             limits.set_personal_limit(base_url, TEST_USER_EMAIL, HIGH)
#
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ разблокирован"):
#             limits.assert_not_blocked(cart)
#
#     finally:
#         cart.clear_cart(base_url)
#         restore_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL, saved)
#
#
# @allure.title("L-05: Ни один лимит на сумму не задан — ограничений нет")
# @allure.tag("limits", "positive", "order-total", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_no_purchase_limits_set(base_url, page_fixture):
#     """
#     Чек-лист п.5:
#     Персональный лимит не задан, лимит подразделения не задан.
#     Ограничений по сумме нет → заказ проходит.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#
#     auth_and_clear(base_url, page, auth, cart)
#     saved = save_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL)
#
#     try:
#         with allure.step("Убираю все лимиты на сумму заказа"):
#             limits.clear_subdivision_purchase_limit(base_url, SUBDIVISION_ID)
#             limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#         with allure.step("Ставлю высокие лимиты цены на товар (чтобы не мешали)"):
#             limits.set_subdivision_item_price_limit(base_url, SUBDIVISION_ID, HIGH)
#             limits.set_company_item_price_limit(base_url, HIGH)
#
#         add_item(page, base_url, listing, min_price=350)
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ не заблокирован"):
#             limits.assert_not_blocked(cart)
#
#     finally:
#         cart.clear_cart(base_url)
#         restore_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL, saved)
#
#
# # ============================================================================
# # ТИП 2: ЛИМИТ НА ЦЕНУ ЗА ЕДИНИЦУ ТОВАРА
# # ============================================================================
#
#
# @allure.title("L-06: Лимит цены подразделения приоритетнее компании (подразделение строже)")
# @allure.tag("limits", "item-price", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_subdivision_item_price_is_priority_and_stricter(base_url, page_fixture):
#     """
#     Чек-лист п.6:
#     Подразделение: 300₽, компания: 600₽.
#     Товар в диапазоне 300–600₽.
#     Приоритет у подразделения → блокировка.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#
#     auth_and_clear(base_url, page, auth, cart)
#     saved = save_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL)
#
#     try:
#         with allure.step("Предусловие: убираю лимиты на сумму"):
#             limits.set_subdivision_purchase_limit(base_url, SUBDIVISION_ID, HIGH)
#             limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#         with allure.step("Устанавливаю: подразделение 300₽, компания 600₽"):
#             limits.set_subdivision_item_price_limit(base_url, SUBDIVISION_ID, LOW)
#             limits.set_company_item_price_limit(base_url, "600")
#
#         with allure.step("Добавляю товар с ценой в диапазоне 300–600₽"):
#             add_item(page, base_url, listing, min_price=350)
#
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ заблокирован (подразделение приоритетнее)"):
#             limits.assert_blocked_by_item_price_limit(cart)
#
#     finally:
#         cart.clear_cart(base_url)
#         restore_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL, saved)
#
#
# @allure.title("L-07: Лимит цены подразделения приоритетнее компании (подразделение мягче)")
# @allure.tag("limits", "item-price", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_subdivision_item_price_is_priority_and_softer(base_url, page_fixture):
#     """
#     Чек-лист п.7:
#     Подразделение: 600₽, компания: 300₽.
#     Товар в диапазоне 300–600₽.
#     Приоритет у подразделения → НЕ блокируется (подразделение разрешает).
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#
#     auth_and_clear(base_url, page, auth, cart)
#     saved = save_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL)
#
#     try:
#         with allure.step("Предусловие: убираю лимиты на сумму"):
#             limits.set_subdivision_purchase_limit(base_url, SUBDIVISION_ID, HIGH)
#             limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#         with allure.step("Устанавливаю: подразделение 600₽, компания 300₽"):
#             limits.set_subdivision_item_price_limit(base_url, SUBDIVISION_ID, "600")
#             limits.set_company_item_price_limit(base_url, LOW)
#
#         with allure.step("Добавляю товар с ценой в диапазоне 300–600₽"):
#             add_item(page, base_url, listing, min_price=350)
#
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ НЕ заблокирован (подразделение приоритетнее и разрешает)"):
#             limits.assert_not_blocked(cart)
#
#     finally:
#         cart.clear_cart(base_url)
#         restore_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL, saved)
#
#
# @allure.title("L-08: Нет лимита цены подразделения — берётся лимит компании")
# @allure.tag("limits", "item-price", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_no_subdivision_item_price_falls_back_to_company(base_url, page_fixture):
#     """
#     Чек-лист п.8:
#     Подразделение: нет лимита. Компания: 300₽.
#     Товар > 300₽ → блокировка лимитом компании.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#
#     auth_and_clear(base_url, page, auth, cart)
#     saved = save_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL)
#
#     try:
#         with allure.step("Предусловие: убираю лимиты на сумму"):
#             limits.set_subdivision_purchase_limit(base_url, SUBDIVISION_ID, HIGH)
#             limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#         with allure.step("Убираю лимит цены подразделения, ставлю лимит компании 300₽"):
#             limits.clear_subdivision_item_price_limit(base_url, SUBDIVISION_ID)
#             limits.set_company_item_price_limit(base_url, LOW)
#
#         add_item(page, base_url, listing, min_price=350)
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ заблокирован лимитом компании"):
#             limits.assert_blocked_by_item_price_limit(cart)
#
#     finally:
#         cart.clear_cart(base_url)
#         restore_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL, saved)
#
#
# @allure.title("L-09: Нет лимита цены ни в подразделении, ни в компании — ограничений нет")
# @allure.tag("limits", "item-price", "positive", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_no_item_price_limits_at_all(base_url, page_fixture):
#     """
#     Чек-лист п.9:
#     Подразделение: нет лимита. Компания: нет лимита.
#     Ограничений по цене за единицу нет → заказ проходит.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#
#     auth_and_clear(base_url, page, auth, cart)
#     saved = save_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL)
#
#     try:
#         with allure.step("Предусловие: убираю лимиты на сумму"):
#             limits.set_subdivision_purchase_limit(base_url, SUBDIVISION_ID, HIGH)
#             limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#         with allure.step("Убираю все лимиты цены на товар"):
#             limits.clear_subdivision_item_price_limit(base_url, SUBDIVISION_ID)
#             limits.clear_company_item_price_limit(base_url)
#
#         add_item(page, base_url, listing, min_price=350)
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ не заблокирован"):
#             limits.assert_not_blocked(cart)
#
#     finally:
#         cart.clear_cart(base_url)
#         restore_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL, saved)
#
#
#
# @allure.title("L-10: Лимит цены подразделения задан, компании нет — работает подразделение")
# @allure.tag("limits", "item-price", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_only_subdivision_item_price_limit(base_url, page_fixture):
#     """
#     Дополнение к п.6/п.7:
#     Подразделение: 300₽, компания: нет.
#     Товар > 300₽ → блокировка лимитом подразделения.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#
#     auth_and_clear(base_url, page, auth, cart)
#     saved = save_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL)
#
#     try:
#         with allure.step("Предусловие: убираю лимиты на сумму"):
#             limits.set_subdivision_purchase_limit(base_url, SUBDIVISION_ID, HIGH)
#             limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#         with allure.step("Устанавливаю лимит цены подразделения 300₽, убираю лимит компании"):
#             limits.set_subdivision_item_price_limit(base_url, SUBDIVISION_ID, LOW)
#             limits.clear_company_item_price_limit(base_url)
#
#         add_item(page, base_url, listing, min_price=350)
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: заказ заблокирован лимитом подразделения"):
#             limits.assert_blocked_by_item_price_limit(cart)
#
#     finally:
#         cart.clear_cart(base_url)
#         restore_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL, saved)
#
#
# @allure.title("L-11: Оба типа лимитов превышены одновременно — обе плашки")
# @allure.tag("limits", "combined", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_both_limit_types_exceeded_simultaneously(base_url, page_fixture):
#     """
#     Лимит на сумму заказа: 200₽ (подразделение).
#     Лимит на цену за ед.: 300₽ (подразделение).
#     Товар > 300₽.
#     Обе плашки отображаются, кнопка недоступна.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#
#     auth_and_clear(base_url, page, auth, cart)
#     saved = save_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL)
#
#     try:
#         with allure.step("Предусловие: убираю персональный, ставлю высокий лимит компании"):
#             limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#             limits.set_company_item_price_limit(base_url, HIGH)
#
#         with allure.step("Устанавливаю оба лимита подразделения низкими"):
#             limits.set_subdivision_purchase_limit(base_url, SUBDIVISION_ID, "200")
#             limits.set_subdivision_item_price_limit(base_url, SUBDIVISION_ID, LOW)
#
#         add_item(page, base_url, listing, min_price=301)
#         open_cart_and_select_subdivision(base_url, cart, page)
#
#         with allure.step("Проверяю: плашка лимита на сумму заказа"):
#             expect(page.locator(cart.LIMIT_EXCEEDED_BANNER_2)).not_to_be_hidden(timeout=5000)
#
#         with allure.step("Проверяю: плашка лимита цены на товар"):
#             expect(page.locator(cart.LIMIT_EXCEEDED_BANNER)).not_to_be_hidden(timeout=5000)
#
#         with allure.step("Проверяю: кнопка 'Отправить' недоступна"):
#             send_btn = page.locator(cart.SEND_BUTTON)
#             is_hidden = not send_btn.is_visible()
#             is_disabled = send_btn.is_visible() and not send_btn.is_enabled()
#             assert is_hidden or is_disabled, \
#                 "Кнопка 'Отправить' должна быть скрыта или disabled"
#
#     finally:
#         cart.clear_cart(base_url)
#         restore_all_limits(base_url, limits, SUBDIVISION_ID, TEST_USER_EMAIL, saved)





































































import time
import allure
import pytest
from playwright.sync_api import expect

from page_opjects.autorization_page import AutorizationPage
from page_opjects.cart_page import CartPage
from page_opjects.listing_page import ListingPage
from page_opjects.settings_page.limits_page import LimitsPage

"""
Тесты лимитов на закупку.

ТИП 1 — Лимит на общую сумму заказа:
  Источники: персональный, подразделение. Берётся min. Компании — нет.

ТИП 2 — Лимит на цену за единицу товара:
  Источники: подразделение (приоритет), компания (fallback).
"""

SUBDIVISION_ID = 136
CATALOG_PATH = "/catalog/9/3707"
TEST_SUBDIVISION = "Тестовое подразделение для теста лимитов(не трогать)"
TEST_USER_EMAIL = "testgarwin_yur@mail.ru"

HIGH = "1000000"
LOW = "300"


def init_all(page):
    return (
        AutorizationPage(page),
        CartPage(page),
        ListingPage(page),
        LimitsPage(page),
    )


def auth_and_clear(base_url, page, auth, cart):
    auth.open(base_url)
    auth.admin_buyer_authorize()
    cart.clear_cart(base_url)


def add_item(page, base_url, listing, min_price):
    with allure.step(f"Добавляю товар с ценой > {min_price}₽"):
        page.goto(base_url + CATALOG_PATH)
        listing.add_expensive_item_to_cart(min_price=min_price)


def open_cart_and_select_subdivision(base_url, cart, page):
    cart.open(base_url)
    current = cart.get_selected_subdivision()
    if current != TEST_SUBDIVISION:
        cart.select_subdivision(TEST_SUBDIVISION)
        time.sleep(1)


# # ============================================================================
# # ТИП 1: ЛИМИТ НА ОБЩУЮ СУММУ ЗАКАЗА
# # ============================================================================
#
#
# @allure.title("L-01: Только лимит подразделения на сумму заказа — блокировка и разблокировка")
# @allure.tag("limits", "subdivision", "order-total", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_only_subdivision_purchase_limit(base_url, page_fixture):
#     """
#     Чек-лист п.1:
#     Персональный НЕ задан. Лимит подразделения задан.
#     а) 300₽ → блокировка
#     б) 1М₽ → разблокировка
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#     auth_and_clear(base_url, page, auth, cart)
#
#     with allure.step("Убираю персональный лимит"):
#         limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#     with allure.step("Устанавливаю: закупка 300₽, цена товара HIGH"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=LOW, item_price=HIGH)
#         limits.set_company_item_price_limit(base_url, HIGH)
#
#     add_item(page, base_url, listing, min_price=350)
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("а) Проверяю: заказ заблокирован"):
#         limits.assert_blocked_by_purchase_limit(cart)
#
#     with allure.step("Устанавливаю большой лимит подразделения"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH)
#
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("б) Проверяю: заказ разблокирован"):
#         limits.assert_not_blocked(cart)
#
#
# @allure.title("L-02: Только персональный лимит на сумму заказа — блокировка и разблокировка")
# @allure.tag("limits", "personal", "order-total", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_only_personal_purchase_limit(base_url, page_fixture):
#     """
#     Чек-лист п.2:
#     Лимит подразделения НЕ задан. Персональный задан.
#     а) 300₽ → блокировка
#     б) 1М₽ → разблокировка
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#     auth_and_clear(base_url, page, auth, cart)
#
#     with allure.step("Убираю лимит подразделения на закупку, ставлю высокие лимиты цены"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase="", item_price=HIGH)
#         limits.set_company_item_price_limit(base_url, HIGH)
#
#     with allure.step("Устанавливаю маленький персональный лимит"):
#         limits.set_personal_limit(base_url, TEST_USER_EMAIL, LOW)
#
#     add_item(page, base_url, listing, min_price=350)
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("а) Проверяю: заказ заблокирован"):
#         limits.assert_blocked_by_purchase_limit(cart)
#
#     with allure.step("Устанавливаю большой персональный лимит"):
#         limits.set_personal_limit(base_url, TEST_USER_EMAIL, HIGH)
#
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("б) Проверяю: заказ разблокирован"):
#         limits.assert_not_blocked(cart)
#
#
# @allure.title("L-03: Оба лимита заданы, подразделение меньше — применяется подразделение")
# @allure.tag("limits", "conflict", "order-total", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_both_limits_subdivision_is_stricter(base_url, page_fixture):
#     """
#     Чек-лист п.3:
#     Персональный: 1М₽, подразделение: 300₽.
#     Берётся min → подразделение.
#     а) Блокировка
#     б) Увеличиваем подразделение → разблокировка
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#     auth_and_clear(base_url, page, auth, cart)
#
#     with allure.step("Устанавливаю высокие лимиты цены"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=LOW, item_price=HIGH)
#         limits.set_company_item_price_limit(base_url, HIGH)
#
#     with allure.step("Устанавливаю персональный 1М₽"):
#         limits.set_personal_limit(base_url, TEST_USER_EMAIL, HIGH)
#
#     add_item(page, base_url, listing, min_price=350)
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("а) Проверяю: заказ заблокирован (подразделение строже)"):
#         limits.assert_blocked_by_purchase_limit(cart)
#
#     with allure.step("Увеличиваю лимит подразделения"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH)
#
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("б) Проверяю: заказ разблокирован"):
#         limits.assert_not_blocked(cart)
#
#
# @allure.title("L-04: Оба лимита заданы, персональный меньше — применяется персональный")
# @allure.tag("limits", "conflict", "order-total", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_both_limits_personal_is_stricter(base_url, page_fixture):
#     """
#     Чек-лист п.4:
#     Персональный: 300₽, подразделение: 1М₽.
#     Берётся min → персональный.
#     а) Блокировка
#     б) Увеличиваем персональный → разблокировка
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#     auth_and_clear(base_url, page, auth, cart)
#
#     with allure.step("Устанавливаю высокие лимиты цены и подразделения"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)
#         limits.set_company_item_price_limit(base_url, HIGH)
#
#     with allure.step("Устанавливаю маленький персональный лимит"):
#         limits.set_personal_limit(base_url, TEST_USER_EMAIL, LOW)
#
#     add_item(page, base_url, listing, min_price=350)
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("а) Проверяю: заказ заблокирован (персональный строже)"):
#         limits.assert_blocked_by_purchase_limit(cart)
#
#     with allure.step("Увеличиваю персональный лимит"):
#         limits.set_personal_limit(base_url, TEST_USER_EMAIL, HIGH)
#
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("б) Проверяю: заказ разблокирован"):
#         limits.assert_not_blocked(cart)
#
#
# @allure.title("L-05: Ни один лимит на сумму не задан — ограничений нет")
# @allure.tag("limits", "positive", "order-total", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_no_purchase_limits_set(base_url, page_fixture):
#     """
#     Чек-лист п.5:
#     Персональный НЕ задан, подразделение НЕ задан.
#     Ограничений по сумме нет.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#     auth_and_clear(base_url, page, auth, cart)
#
#     with allure.step("Убираю все лимиты на сумму"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase="", item_price=HIGH)
#         limits.set_company_item_price_limit(base_url, HIGH)
#         limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#     add_item(page, base_url, listing, min_price=350)
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("Проверяю: заказ не заблокирован"):
#         limits.assert_not_blocked(cart)
#
#
# # ============================================================================
# # ТИП 2: ЛИМИТ НА ЦЕНУ ЗА ЕДИНИЦУ ТОВАРА
# # ============================================================================
#
#
# @allure.title("L-06: Подразделение приоритетнее компании (подразделение строже)")
# @allure.tag("limits", "item-price", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_subdivision_item_price_priority_stricter(base_url, page_fixture):
#     """
#     Чек-лист п.6:
#     Подразделение: 300₽, компания: 600₽.
#     Товар 300–600₽. Подразделение приоритетнее → блокировка.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#     auth_and_clear(base_url, page, auth, cart)
#
#     with allure.step("Убираю лимиты на сумму"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=LOW)
#         limits.set_company_item_price_limit(base_url, "600")
#         limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#     add_item(page, base_url, listing, min_price=350)
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("Проверяю: заказ заблокирован (подразделение приоритетнее)"):
#         limits.assert_blocked_by_item_price_limit(cart)
#
#
# @allure.title("L-07: Подразделение приоритетнее компании (подразделение мягче)")
# @allure.tag("limits", "item-price", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_subdivision_item_price_priority_softer(base_url, page_fixture):
#     """
#     Чек-лист п.7:
#     Подразделение: 600₽, компания: 300₽.
#     Товар 300–600₽. Подразделение приоритетнее → пропускает.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#     auth_and_clear(base_url, page, auth, cart)
#
#     with allure.step("Устанавливаю лимиты"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price="600")
#         limits.set_company_item_price_limit(base_url, LOW)
#         limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#     add_item(page, base_url, listing, min_price=350)
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("Проверяю: заказ НЕ заблокирован (подразделение приоритетнее и разрешает)"):
#         limits.assert_not_blocked(cart)
#
#
# @allure.title("L-08: Нет лимита цены подразделения — берётся лимит компании")
# @allure.tag("limits", "item-price", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_no_subdivision_item_price_fallback_to_company(base_url, page_fixture):
#     """
#     Чек-лист п.8:
#     Подразделение: нет. Компания: 300₽.
#     Товар > 300₽ → блокировка лимитом компании.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#     auth_and_clear(base_url, page, auth, cart)
#
#     with allure.step("Убираю лимит цены подразделения, ставлю лимит компании"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price="")
#         limits.set_company_item_price_limit(base_url, LOW)
#         limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#     add_item(page, base_url, listing, min_price=350)
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("Проверяю: заказ заблокирован лимитом компании"):
#         limits.assert_blocked_by_item_price_limit(cart)
#
#
# @allure.title("L-09: Нет лимита цены ни в подразделении ни в компании — ограничений нет")
# @allure.tag("limits", "item-price", "positive", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_no_item_price_limits_at_all(base_url, page_fixture):
#     """
#     Чек-лист п.9:
#     Подразделение: нет. Компания: нет.
#     Ограничений нет.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#     auth_and_clear(base_url, page, auth, cart)
#
#     with allure.step("Убираю все лимиты цены на товар"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price="")
#         limits.clear_company_item_price_limit(base_url)
#         limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#     add_item(page, base_url, listing, min_price=350)
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("Проверяю: заказ не заблокирован"):
#         limits.assert_not_blocked(cart)
#
#
# @allure.title("L-10: Только лимит цены подразделения задан, компании нет — работает подразделение")
# @allure.tag("limits", "item-price", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_only_subdivision_item_price_limit(base_url, page_fixture):
#     """
#     Подразделение: 300₽, компания: нет.
#     Товар > 300₽ → блокировка подразделением.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#     auth_and_clear(base_url, page, auth, cart)
#
#     with allure.step("Устанавливаю лимит цены подразделения, убираю компанию"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=LOW)
#         limits.clear_company_item_price_limit(base_url)
#         limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#     add_item(page, base_url, listing, min_price=350)
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("Проверяю: заказ заблокирован лимитом подразделения"):
#         limits.assert_blocked_by_item_price_limit(cart)
#
#
# @allure.title("L-11: Оба типа лимитов превышены — отображается только плашка цены на товар")
# @allure.tag("limits", "combined", "critical")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_both_limit_types_exceeded(base_url, page_fixture):
#     """
#     Лимит на сумму заказа: 200₽ (подразделение).
#     Лимит на цену за ед.: 300₽ (подразделение).
#     Товар > 300₽.
#     Отображается только плашка лимита цены на товар, кнопка disabled.
#     """
#     page = page_fixture()
#     auth, cart, listing, limits = init_all(page)
#     auth_and_clear(base_url, page, auth, cart)
#
#     with allure.step("Устанавливаю оба лимита подразделения низкими"):
#         limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase="200", item_price=LOW)
#         limits.set_company_item_price_limit(base_url, HIGH)
#         limits.delete_personal_limit(base_url, TEST_USER_EMAIL)
#
#     add_item(page, base_url, listing, min_price=301)
#     open_cart_and_select_subdivision(base_url, cart, page)
#
#     with allure.step("Проверяю: отображается только плашка лимита цены на товар"):
#         limits.assert_blocked_by_item_price_limit(cart)


















# ============================================================================
# ТИП 1: ЛИМИТ НА ОБЩУЮ СУММУ ЗАКАЗА
# ============================================================================


@allure.title("Только лимит подразделения на сумму заказа — блокировка и разблокировка")
def test_only_subdivision_purchase_limit(base_url, page_fixture):
    page = page_fixture()
    auth, cart, listing, limits = init_all(page)
    auth_and_clear(base_url, page, auth, cart)

    try:
        with allure.step("Убираю персональный лимит"):
            limits.delete_personal_limit(base_url, TEST_USER_EMAIL)

        with allure.step("Устанавливаю: закупка 300₽, цена товара HIGH"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=LOW, item_price=HIGH)
            limits.set_company_item_price_limit(base_url, HIGH)

        add_item(page, base_url, listing, min_price=350)
        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("а) Проверяю: заказ заблокирован"):
            limits.assert_blocked_by_purchase_limit(cart)

        with allure.step("Устанавливаю большой лимит подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH)

        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("б) Проверяю: заказ разблокирован"):
            limits.assert_not_blocked(cart)

    finally:
        with allure.step("Постусловие: возвращаю высокие лимиты подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)


@allure.title("Только персональный лимит на сумму заказа — блокировка и разблокировка")
def test_only_personal_purchase_limit(base_url, page_fixture):
    page = page_fixture()
    auth, cart, listing, limits = init_all(page)
    auth_and_clear(base_url, page, auth, cart)

    try:
        with allure.step("Убираю лимит подразделения на закупку, ставлю высокие лимиты цены"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase="", item_price=HIGH)
            limits.set_company_item_price_limit(base_url, HIGH)

        with allure.step("Устанавливаю маленький персональный лимит"):
            limits.set_personal_limit(base_url, TEST_USER_EMAIL, LOW)

        add_item(page, base_url, listing, min_price=350)
        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("а) Проверяю: заказ заблокирован"):
            limits.assert_blocked_by_purchase_limit(cart)

        with allure.step("Устанавливаю большой персональный лимит"):
            limits.set_personal_limit(base_url, TEST_USER_EMAIL, HIGH)

        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("б) Проверяю: заказ разблокирован"):
            limits.assert_not_blocked(cart)

    finally:
        with allure.step("Постусловие: возвращаю высокие лимиты подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)


@allure.title("Оба лимита заданы, подразделение меньше — применяется подразделение")
def test_both_limits_subdivision_is_stricter(base_url, page_fixture):
    page = page_fixture()
    auth, cart, listing, limits = init_all(page)
    auth_and_clear(base_url, page, auth, cart)

    try:
        with allure.step("Устанавливаю: подразделение 300₽ закупка, HIGH цена товара"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=LOW, item_price=HIGH)
            limits.set_company_item_price_limit(base_url, HIGH)

        with allure.step("Устанавливаю персональный 1М₽"):
            limits.set_personal_limit(base_url, TEST_USER_EMAIL, HIGH)

        add_item(page, base_url, listing, min_price=350)
        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("а) Проверяю: заказ заблокирован (подразделение строже)"):
            limits.assert_blocked_by_purchase_limit(cart)

        with allure.step("Увеличиваю лимит подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH)

        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("б) Проверяю: заказ разблокирован"):
            limits.assert_not_blocked(cart)

    finally:
        with allure.step("Постусловие: возвращаю высокие лимиты подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)


@allure.title("Оба лимита заданы, персональный меньше — применяется персональный")
def test_both_limits_personal_is_stricter(base_url, page_fixture):
    page = page_fixture()
    auth, cart, listing, limits = init_all(page)
    auth_and_clear(base_url, page, auth, cart)

    try:
        with allure.step("Устанавливаю высокие лимиты подразделения и компании"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)
            limits.set_company_item_price_limit(base_url, HIGH)

        with allure.step("Устанавливаю маленький персональный лимит"):
            limits.set_personal_limit(base_url, TEST_USER_EMAIL, LOW)

        add_item(page, base_url, listing, min_price=350)
        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("а) Проверяю: заказ заблокирован (персональный строже)"):
            limits.assert_blocked_by_purchase_limit(cart)

        with allure.step("Увеличиваю персональный лимит"):
            limits.set_personal_limit(base_url, TEST_USER_EMAIL, HIGH)

        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("б) Проверяю: заказ разблокирован"):
            limits.assert_not_blocked(cart)

    finally:
        with allure.step("Постусловие: возвращаю высокие лимиты подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)


@allure.title("Ни один лимит на сумму не задан — ограничений нет")
def test_no_purchase_limits_set(base_url, page_fixture):
    page = page_fixture()
    auth, cart, listing, limits = init_all(page)
    auth_and_clear(base_url, page, auth, cart)

    try:
        with allure.step("Убираю все лимиты на сумму"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase="", item_price=HIGH)
            limits.set_company_item_price_limit(base_url, HIGH)
            limits.delete_personal_limit(base_url, TEST_USER_EMAIL)

        add_item(page, base_url, listing, min_price=350)
        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("Проверяю: заказ не заблокирован"):
            limits.assert_not_blocked(cart)

    finally:
        with allure.step("Постусловие: возвращаю высокие лимиты подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)


# ============================================================================
# ТИП 2: ЛИМИТ НА ЦЕНУ ЗА ЕДИНИЦУ ТОВАРА
# ============================================================================


@allure.title("Подразделение приоритетнее компании (лимит подразделения меньше компании)")
def test_subdivision_item_price_priority_stricter(base_url, page_fixture):
    page = page_fixture()
    auth, cart, listing, limits = init_all(page)
    auth_and_clear(base_url, page, auth, cart)

    try:
        with allure.step("Устанавливаю лимиты"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=LOW)
            limits.set_company_item_price_limit(base_url, "600")
            limits.delete_personal_limit(base_url, TEST_USER_EMAIL)

        add_item(page, base_url, listing, min_price=350)
        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("Проверяю: заказ заблокирован (лимит подразделения больше компании)"):
            limits.assert_blocked_by_item_price_limit(cart)

    finally:
        with allure.step("Постусловие: возвращаю высокие лимиты подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)


@allure.title("Подразделение приоритетнее компании (подразделение мягче)")
def test_subdivision_item_price_priority_softer(base_url, page_fixture):
    page = page_fixture()
    auth, cart, listing, limits = init_all(page)
    auth_and_clear(base_url, page, auth, cart)

    try:
        with allure.step("Устанавливаю лимиты"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price="600")
            limits.set_company_item_price_limit(base_url, LOW)
            limits.delete_personal_limit(base_url, TEST_USER_EMAIL)

        add_item(page, base_url, listing, min_price=350)
        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("Проверяю: заказ НЕ заблокирован (подразделение приоритетнее и разрешает)"):
            limits.assert_not_blocked(cart)

    finally:
        with allure.step("Постусловие: возвращаю высокие лимиты подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)


@allure.title("Нет лимита цены подразделения — берётся лимит компании")
def test_no_subdivision_item_price_fallback_to_company(base_url, page_fixture):
    page = page_fixture()
    auth, cart, listing, limits = init_all(page)
    auth_and_clear(base_url, page, auth, cart)

    try:
        with allure.step("Убираю лимит цены подразделения, ставлю лимит компании"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price="")
            limits.set_company_item_price_limit(base_url, LOW)
            limits.delete_personal_limit(base_url, TEST_USER_EMAIL)

        add_item(page, base_url, listing, min_price=350)
        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("Проверяю: заказ заблокирован лимитом компании"):
            limits.assert_blocked_by_item_price_limit(cart)

    finally:
        with allure.step("Постусловие: возвращаю высокие лимиты подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)


@allure.title("L-09: Нет лимита цены ни в подразделении ни в компании — ограничений нет")
def test_no_item_price_limits_at_all(base_url, page_fixture):
    page = page_fixture()
    auth, cart, listing, limits = init_all(page)
    auth_and_clear(base_url, page, auth, cart)

    try:
        with allure.step("Убираю все лимиты цены на товар"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price="")
            limits.clear_company_item_price_limit(base_url)
            limits.delete_personal_limit(base_url, TEST_USER_EMAIL)

        add_item(page, base_url, listing, min_price=350)
        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("Проверяю: заказ не заблокирован"):
            limits.assert_not_blocked(cart)

    finally:
        with allure.step("Постусловие: возвращаю высокие лимиты подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)


@allure.title("Только лимит цены подразделения задан, компании нет — работает подразделение")
def test_only_subdivision_item_price_limit(base_url, page_fixture):
    page = page_fixture()
    auth, cart, listing, limits = init_all(page)
    auth_and_clear(base_url, page, auth, cart)

    try:
        with allure.step("Устанавливаю лимит цены подразделения, убираю компанию"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=LOW)
            limits.clear_company_item_price_limit(base_url)
            limits.delete_personal_limit(base_url, TEST_USER_EMAIL)

        add_item(page, base_url, listing, min_price=350)
        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("Проверяю: заказ заблокирован лимитом подразделения"):
            limits.assert_blocked_by_item_price_limit(cart)

    finally:
        with allure.step("Постусловие: возвращаю высокие лимиты подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)


@allure.title("Оба типа лимитов превышены — отображается только плашка цены на товар")
def test_both_limit_types_exceeded(base_url, page_fixture):
    page = page_fixture()
    auth, cart, listing, limits = init_all(page)
    auth_and_clear(base_url, page, auth, cart)

    try:
        with allure.step("Устанавливаю оба лимита подразделения низкими"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase="200", item_price=LOW)
            limits.set_company_item_price_limit(base_url, HIGH)
            limits.delete_personal_limit(base_url, TEST_USER_EMAIL)

        add_item(page, base_url, listing, min_price=301)
        open_cart_and_select_subdivision(base_url, cart, page)

        with allure.step("Проверяю: только плашка лимита цены на товар"):
            limits.assert_blocked_by_item_price_limit(cart)

    finally:
        with allure.step("Постусловие: возвращаю высокие лимиты подразделения"):
            limits.set_subdivision_limits(base_url, SUBDIVISION_ID, purchase=HIGH, item_price=HIGH)