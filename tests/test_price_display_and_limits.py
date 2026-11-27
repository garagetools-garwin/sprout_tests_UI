"""
UI-приёмка MR front !8 / back !10: режимы отображения цен по договору и персональные лимиты.

Тесты написаны по итогам ручной приёмки 25–26.11.2026 (sprout-ui-handoff-2026-11-26.md).
Каждый тест возвращает стенд в исходное состояние в finally: договор №6 — «С НДС»,
временные персональные лимиты удаляются.
"""
import re

import allure
import pytest
from playwright.sync_api import expect

from page_opjects.autorization_page import AutorizationPage, TEST_BUYER_EMAIL
from page_opjects.cart_page import CartPage
from page_opjects.my_orders_page import MyOrdersPage
from page_opjects.settings_page.contract_detail_page import ContractPriceDisplayMode
from page_opjects.settings_page.personal_limits_settings_page import (
    PersonalLimitsSettingsPage,
    SelectEmployeeModal,
    SetLimitModal,
    DeleteLimitModal,
)

CONTRACT_ID = 6
CONTRACT_GENERAL_PATH = f"/settings/contract/{CONTRACT_ID}/general"
# Исходный режим договора №6 на стенде — к нему возвращаемся после каждого теста
DEFAULT_MODE = ContractPriceDisplayMode.WITH_VAT

# Пользователь без персонального лимита: на нём проверяем создание нулевого лимита,
# чтобы не трогать лимиты, которыми пользуются другие тесты (+3, +b2b, основной админ)
ZERO_LIMIT_USER_EMAIL = TEST_BUYER_EMAIL


def _open_contract_as_seller(page_fixture, base_url):
    page = page_fixture()
    auth = AutorizationPage(page)
    auth.open(base_url)
    auth.admin_seller_authorize()
    with allure.step(f"Открываю договор №{CONTRACT_ID}"):
        page.goto(base_url + CONTRACT_GENERAL_PATH)
    return page, ContractPriceDisplayMode(page)


@allure.title("Продавец: режим отображения цен по договору сохраняется после перезагрузки")
@allure.tag("AI", "claude", "price-display-mode", "regression")
@pytest.mark.ai
@pytest.mark.claude
@pytest.mark.parametrize("mode", ContractPriceDisplayMode.ALL_MODES)
def test_contract_price_display_mode_is_saved(base_url, page_fixture, mode):
    page, price_mode = _open_contract_as_seller(page_fixture, base_url)
    initial_mode = price_mode.get_mode()

    try:
        if initial_mode == mode:
            # Чтобы проверить именно сохранение, сначала уходим в другой режим
            other = next(m for m in ContractPriceDisplayMode.ALL_MODES if m != mode)
            assert price_mode.set_mode(other), f"Не сохранился промежуточный режим «{other}»"

        with allure.step(f"Выбираю режим «{mode}»"):
            price_mode.select_mode(mode)

        with allure.step("Проверяю toast о сохранении"):
            assert price_mode.is_saved_toast_visible(), \
                "Нет уведомления «Режим отображения цен сохранён»"

        with allure.step("Перезагружаю страницу и проверяю сохранённый режим"):
            page.reload()
            assert price_mode.get_mode() == mode, \
                f"После перезагрузки режим «{price_mode.get_mode()}», ожидался «{mode}»"
    finally:
        with allure.step(f"Возвращаю договору режим «{DEFAULT_MODE}»"):
            page.goto(base_url + CONTRACT_GENERAL_PATH)
            price_mode.set_mode(DEFAULT_MODE)


@allure.title("Персональный лимит 0 ₽ можно установить и он сохраняется как 0, а не 1 ₽ (дефект D3)")
@allure.tag("AI", "claude", "personal-limits", "bug-D3")
@allure.description(
    "D3: в PersonalLimitChangeModal.tsx 0 трактуется как «пусто» (`balance ? ... : null`, "
    "`disabled={!balance}`, `min={DEFAULT_VALUE_1}`). Кнопка «Сохранить» неактивна для 0, "
    "в существующем лимите 0 превращается в 1. Тест помечен xfail(strict): "
    "после исправления он начнёт проходить и xfail нужно снять."
)
@pytest.mark.ai
@pytest.mark.claude
@pytest.mark.xfail(strict=True, reason="D3: нулевой персональный лимит нельзя сохранить через UI (решено исправить 26.11)")
def test_personal_limit_zero_can_be_saved(base_url, page_fixture):
    page = page_fixture()
    auth = AutorizationPage(page)
    personal_limits = PersonalLimitsSettingsPage(page)
    select_modal = SelectEmployeeModal(page)
    limit_modal = SetLimitModal(page)
    delete_modal = DeleteLimitModal(page)

    auth.open(base_url)
    auth.admin_buyer_authorize()
    personal_limits.open(base_url)
    personal_limits.wait_for_any_limit()

    if personal_limits.is_user_present(ZERO_LIMIT_USER_EMAIL):
        pytest.skip(f"У {ZERO_LIMIT_USER_EMAIL} уже есть персональный лимит — тест не трогает чужие данные")

    try:
        with allure.step("Открываю создание лимита и выбираю сотрудника"):
            personal_limits.click_add_new()
            assert select_modal.is_visible(), "Модалка выбора сотрудника не открылась"
            # Поиск в модалке по email не находит сотрудников («Список пользователей пуст»),
            # поэтому выбираем из полного списка
            select_modal.select_and_confirm_by_email(ZERO_LIMIT_USER_EMAIL)
            assert limit_modal.is_visible(), "Модалка установки лимита не открылась"

        with allure.step("Ввожу лимит 0"):
            limit_modal.set_limit("0")

        with allure.step("Проверяю, что «Сохранить» доступна для 0"):
            expect(page.locator(limit_modal.SAVE_BUTTON)).to_be_enabled(timeout=3000)

        with allure.step("Сохраняю и проверяю toast"):
            limit_modal.click_save()
            assert personal_limits.is_limit_set_toast_visible(), "Нет toast об установке лимита"

        with allure.step("Проверяю, что в списке остаток 0,00 ₽, а не 1,00 ₽"):
            page.reload()
            personal_limits.wait_for_any_limit()
            limit_text = personal_limits.get_user_limit_text(ZERO_LIMIT_USER_EMAIL)
            amount = re.search(r"(\d[\d\s\u00a0]*[.,]\d{2})\s*₽", limit_text)
            assert amount, f"Не нашёл сумму лимита в строке: «{limit_text}»"
            value = float(re.sub(r"[\s\u00a0]", "", amount.group(1)).replace(",", "."))
            assert value == 0, f"Ожидался лимит 0, в списке: «{amount.group(0)}»"
    finally:
        with allure.step("Удаляю созданный в тесте лимит"):
            page.keyboard.press("Escape")
            personal_limits.open(base_url)
            personal_limits.wait_for_any_limit()
            if personal_limits.is_user_present(ZERO_LIMIT_USER_EMAIL):
                personal_limits.click_delete_user_limit(ZERO_LIMIT_USER_EMAIL)
                if delete_modal.is_visible():
                    delete_modal.confirm_delete()


# Товар договора №6 из ручной приёмки: категория «Динамометрические ключи», НДС 22%
PRICE_CHECK_CATEGORY_PATH = "/catalog/9/2988"
PRICE_CHECK_ARTICLE = "501523-600-1500-1"
VAT_RATE = 0.22
PRICE_RE = re.compile(r"(\d[\d\s ]*[.,]\d{2})\s*₽")


def _parse_price(text: str) -> float:
    return float(re.sub(r"[\s ]", "", text).replace(",", "."))


def _get_catalog_price_lines(page, base_url) -> list:
    """Строки цен (текст с ₽) из ячейки цены строки товара в табличном листинге, по порядку.

    Разметка ячейки `td.catalog-good-offer-cell`: первая цена — `div > span`,
    в режиме «Без НДС и с НДС» вторая — `div` с текстом «с НДС: … ₽»;
    блок наличия/доставки `.catalog-good-offer` в подсчёт не входит.
    """
    page.goto(base_url + PRICE_CHECK_CATEGORY_PATH)
    row = page.locator("tr.ant-table-row.ant-table-row-level-0", has_text=PRICE_CHECK_ARTICLE).first
    row.wait_for(state="visible", timeout=20000)
    price_lines = row.locator("td.catalog-good-offer-cell > div:not(.catalog-good-offer)")
    return [t.strip() for t in price_lines.all_inner_texts() if PRICE_RE.search(t)]


def _get_catalog_prices(page, base_url) -> list:
    """Все цены (₽) из ячейки цены строки товара в табличном листинге, по порядку."""
    lines = _get_catalog_price_lines(page, base_url)
    return [_parse_price(PRICE_RE.search(t).group(1)) for t in lines]


@allure.title("Покупатель видит цены в каталоге в режиме, выбранном продавцом в договоре")
@allure.tag("AI", "claude", "price-display-mode", "regression")
@allure.description(
    "Продавец по очереди включает режимы «Только без НДС», «Без НДС и с НДС», «С НДС». "
    "Покупатель после перезагрузки видит одну цену без НДС, обе цены (первой — без НДС) "
    "и одну цену с НДС. Сравниваются цены между режимами и с НДС 22%, "
    "поэтому тест не зависит от текущих цен прайса."
)
@pytest.mark.ai
@pytest.mark.claude
def test_buyer_catalog_prices_follow_contract_mode(base_url, page_fixture):
    seller_page, price_mode = _open_contract_as_seller(page_fixture, base_url)

    buyer_page = page_fixture()
    buyer_auth = AutorizationPage(buyer_page)
    buyer_auth.open(base_url)
    buyer_auth.admin_buyer_authorize()

    def switch(mode):
        seller_page.goto(base_url + CONTRACT_GENERAL_PATH)
        assert price_mode.set_mode(mode), f"Режим «{mode}» не сохранился"

    try:
        with allure.step("Режим «Только без НДС»: одна цена — без НДС"):
            switch(ContractPriceDisplayMode.WITHOUT_VAT)
            prices = _get_catalog_prices(buyer_page, base_url)
            assert len(prices) == 1, f"Ожидалась одна цена, получено: {prices}"
            price_without_vat = prices[0]

        with allure.step("Режим «Без НДС и с НДС»: две цены, первая — без НДС"):
            switch(ContractPriceDisplayMode.BOTH)
            lines = _get_catalog_price_lines(buyer_page, base_url)
            assert len(lines) == 2, f"Ожидались две цены, получено: {lines}"
            assert lines[1].lower().startswith("с ндс"), \
                f"Вторая цена должна быть подписана «с НДС», показано: «{lines[1]}»"
            prices = [_parse_price(PRICE_RE.search(t).group(1)) for t in lines]
            assert prices[0] == price_without_vat, \
                f"Первая цена {prices[0]} не совпадает с ценой без НДС {price_without_vat}"
            price_with_vat_both = prices[1]

        with allure.step("Режим «С НДС»: одна цена — с НДС"):
            switch(ContractPriceDisplayMode.WITH_VAT)
            prices = _get_catalog_prices(buyer_page, base_url)
            assert len(prices) == 1, f"Ожидалась одна цена, получено: {prices}"
            price_with_vat = prices[0]
            assert price_with_vat == price_with_vat_both, \
                f"Цена с НДС {price_with_vat} не совпадает со второй ценой режима «обе» {price_with_vat_both}"

        with allure.step("Цена с НДС = цена без НДС × 1,22 (с точностью до копейки)"):
            expected = round(price_without_vat * (1 + VAT_RATE), 2)
            assert abs(price_with_vat - expected) <= 0.01, \
                f"{price_without_vat} × 1,22 = {expected}, а показано {price_with_vat}"
    finally:
        with allure.step(f"Возвращаю договору режим «{DEFAULT_MODE}»"):
            seller_page.goto(base_url + CONTRACT_GENERAL_PATH)
            price_mode.set_mode(DEFAULT_MODE)


# D1: заявки «На согласовании» автора +b2b (подразделение «Еще одно тестовое подразделение»).
# Вкладка «На согласовании» открывается в «Моих заказах» по умолчанию.
ORDER_NUMBER_RE = re.compile(r"#\d{8}-(\d+)")
SUPPLY_NOT_FOUND_TOAST = "text=Поставка не найдена"


@allure.title("Автор открывает позицию заявки на согласовании без ошибки «Поставка не найдена» (дефект D1)")
@allure.tag("AI", "claude", "approval", "bug-D1")
@allure.description(
    "D1: клик по позиции заявки в статусе «На согласовании» показывает toast «Поставка не найдена»: "
    "фронт запрашивает GET /api/supply/{id строки}, а у заявки на согласовании поставки ещё нет → 404. "
    "Тест только читает данные: кликает по названию позиции, кнопку «Согласовать» не трогает. "
    "Помечен xfail(strict): после исправления начнёт проходить — xfail снять."
)
@pytest.mark.ai
@pytest.mark.claude
@pytest.mark.xfail(strict=True, reason="D1: GET /api/supply/{id} → 404 для заявки на согласовании")
def test_pending_request_item_opens_without_error(base_url, page_fixture):
    page = page_fixture()
    auth = AutorizationPage(page)
    auth.open(base_url)
    auth.buyer_admin_for_limit_authorize()

    with allure.step("Беру первую заявку со вкладки «На согласовании» в «Моих заказах»"):
        page.goto(base_url + MyOrdersPage.PATH)
        numbers = page.locator(MyOrdersPage.ORDER_NUMBER)
        numbers.first.wait_for(state="visible", timeout=20000)
        match = ORDER_NUMBER_RE.search(numbers.first.inner_text())
        if not match:
            pytest.skip("У автора нет заявок на согласовании — проверять D1 не на чем")
        request_id = match.group(1)
        allure.attach(match.group(0), "Заявка", allure.attachment_type.TEXT)

    with allure.step(f"Открываю заявку {request_id}"):
        page.goto(f"{base_url}/request/{request_id}")
        expect(page.get_by_text("На согласовании").first).to_be_visible(timeout=20000)
        item_name = page.locator("tr.ant-table-row .request-supply-list__table-item-name").first
        item_name.wait_for(state="visible", timeout=20000)

    with allure.step("Кликаю по названию позиции и жду запрос поставки"):
        with page.expect_response(
            lambda r: "/api/supply/" in r.url and r.request.method == "GET", timeout=15000
        ) as supply_response:
            item_name.click()
        status = supply_response.value.status

    with allure.step("Проверяю ответ API и отсутствие toast «Поставка не найдена»"):
        assert status < 400, f"GET {supply_response.value.url} вернул {status}"
        expect(page.locator(SUPPLY_NOT_FOUND_TOAST)).to_have_count(0, timeout=3000)


# D4: лимит при оформлении проверяется без умножения на количество.
# Товар и количество подобраны так, что цена за штуку (148 ₽) укладывается в остаток 500 ₽,
# а сумма заказа (740 ₽) — нет.
D4_ARTICLE = "644-955"
D4_QTY = 5
D4_INITIAL_BALANCE = "1000"
D4_LOWERED_BALANCE = "500"
REQUEST_NUMBER_RE = re.compile(r"#(\d{8})-(\d+)")


def _set_personal_balance(personal_limits, select_modal, limit_modal, base_url, email, value):
    """Создаёт или меняет персональный лимит («Остаток за период») сотрудника."""
    personal_limits.open(base_url)
    personal_limits.wait_for_any_limit()
    if personal_limits.is_user_present(email):
        personal_limits.click_edit_user_limit(email)
    else:
        personal_limits.click_add_new()
        select_modal.select_and_confirm_by_email(email)
    limit_modal.set_limit(value)
    limit_modal.click_save()
    personal_limits.page.wait_for_timeout(1500)


def _find_request_by_comment(page, base_url, comment):
    """Ищет заявку пользователя по уникальному комментарию среди последних в «Моих заказах»."""
    for tab in ("/requests/processing", ""):
        page.goto(base_url + MyOrdersPage.PATH + tab)
        page.wait_for_load_state("networkidle")
        for match in REQUEST_NUMBER_RE.finditer(page.locator("body").inner_text()):
            request_id = match.group(2)
            with page.expect_response(
                lambda r: r.url.rstrip("/").endswith(f"/api/request/{request_id}") and r.request.method == "GET",
                timeout=20000,
            ) as response:
                page.goto(f"{base_url}/request/{request_id}")
            if comment in (response.value.json().get("comment") or ""):
                return request_id
            break  # сверяем только самую свежую заявку вкладки
    return None


def _cancel_request(page, base_url, request_id):
    page.goto(f"{base_url}/request/{request_id}")
    page.locator("button.ant-dropdown-trigger").first.click()
    page.locator(".ant-dropdown:not(.ant-dropdown-hidden)").get_by_text("Отменить заказ").click()
    with page.expect_response(lambda r: "/api/request/cancel/" in r.url, timeout=15000):
        page.get_by_role("button", name="Отменить", exact=True).click()


@allure.title("Заказ сверх остатка личного лимита отклоняется сервером, если остаток уменьшился при открытой корзине (дефект D4)")
@allure.tag("AI", "claude", "personal-limits", "bug-D4")
@allure.description(
    "D4: basket.service.ts (createRequest) для аккаунтов вне LIMIT_APPROVAL_ACCOUNT_IDS сравнивает с лимитом "
    "сумму цен за единицу без умножения на количество. Фронт проверяет лимит правильно, но по остатку, "
    "загруженному вместе с корзиной. Сценарий без инструментов разработчика: у сотрудника остаток 1 000 ₽, "
    "в корзине 5 × 148 ₽ = 740 ₽; пока корзина открыта, администратор снижает остаток до 500 ₽; сотрудник "
    "нажимает «Отправить». Ожидается отказ сервера, фактически создаётся заказ на 740 ₽. "
    "Тест создаёт заказ только при наличии дефекта и сразу отменяет его; лимит и корзина возвращаются в finally."
)
@pytest.mark.ai
@pytest.mark.claude
@pytest.mark.xfail(strict=True, reason="D4: сервер проверяет лимит без умножения на количество")
def test_order_over_personal_limit_is_rejected_by_server(base_url, page_fixture):
    comment = f"UI QA D4 {re.sub(r'[^0-9]', '', str(__import__('time').time()))[:10]} — не исполнять"

    admin_page = page_fixture()
    AutorizationPage(admin_page).open(base_url)
    AutorizationPage(admin_page).admin_buyer_authorize()
    personal_limits = PersonalLimitsSettingsPage(admin_page)
    select_modal = SelectEmployeeModal(admin_page)
    limit_modal = SetLimitModal(admin_page)

    buyer_page = page_fixture()
    AutorizationPage(buyer_page).open(base_url)
    AutorizationPage(buyer_page).test_buyer_for_admin_role_authorize()
    cart = CartPage(buyer_page)

    personal_limits.open(base_url)
    personal_limits.wait_for_any_limit()
    if personal_limits.is_user_present(TEST_BUYER_EMAIL):
        pytest.skip(f"У {TEST_BUYER_EMAIL} уже есть персональный лимит — тест не трогает чужие данные")
    cart.open(base_url)
    buyer_page.wait_for_load_state("networkidle")
    if cart.get_cart_items_count() > 0:
        pytest.skip(f"Корзина {TEST_BUYER_EMAIL} не пустая — тест не трогает чужие данные")

    created_request_id = None
    try:
        with allure.step(f"Администратор выдаёт сотруднику остаток {D4_INITIAL_BALANCE} ₽"):
            _set_personal_balance(personal_limits, select_modal, limit_modal, base_url, TEST_BUYER_EMAIL, D4_INITIAL_BALANCE)

        with allure.step(f"Сотрудник кладёт в корзину {D4_ARTICLE} × {D4_QTY}, выбирает адрес и пишет комментарий"):
            cart.open(base_url)
            cart.open_quick_add_modal()
            cart.search_in_quick_add(D4_ARTICLE)
            cart.add_product_from_opened_quick_add_modal(0)
            buyer_page.keyboard.press("Escape")
            cart.open(base_url)
            buyer_page.wait_for_load_state("networkidle")
            cart.set_quantity_manually(0, D4_QTY)
            buyer_page.wait_for_timeout(2000)
            selected_address = buyer_page.locator(cart.ADDRESS_SELECT).locator(cart.SELECT_VALUE)
            if selected_address.count() == 0 or not selected_address.inner_text().strip():
                cart.open_address_dropdown()
                cart.select_option_by_index(0)
            buyer_page.locator(cart.COMMENT_TEXTAREA).fill(comment)
            expect(buyer_page.locator(cart.SEND_BUTTON)).to_be_enabled(timeout=10000)

        with allure.step(f"Пока корзина открыта, администратор снижает остаток до {D4_LOWERED_BALANCE} ₽"):
            _set_personal_balance(personal_limits, select_modal, limit_modal, base_url, TEST_BUYER_EMAIL, D4_LOWERED_BALANCE)

        with allure.step("Сотрудник, не обновляя страницу, нажимает «Отправить»"):
            with buyer_page.expect_response(
                lambda r: "/api/basket/request" in r.url and r.request.method == "POST", timeout=20000
            ) as response:
                cart.click_send_button()
            status = response.value.status
            allure.attach(response.value.text()[:500], "Ответ POST /api/basket/request", allure.attachment_type.TEXT)
            if response.value.ok:
                created_request_id = _find_request_by_comment(buyer_page, base_url, comment)

        with allure.step("Проверяю, что сервер отклонил заказ сверх остатка"):
            assert status == 400, (
                f"Сервер принял заказ {D4_QTY} × 148 ₽ = 740 ₽ при остатке {D4_LOWERED_BALANCE} ₽ "
                f"(HTTP {status}, заявка {created_request_id})"
            )
    finally:
        with allure.step("Возвращаю данные: отменяю созданную заявку, очищаю корзину, снимаю лимит"):
            if created_request_id:
                _cancel_request(buyer_page, base_url, created_request_id)
            cart.clear_cart(base_url)
            personal_limits.open(base_url)
            personal_limits.wait_for_any_limit()
            if personal_limits.is_user_present(TEST_BUYER_EMAIL):
                personal_limits.click_delete_user_limit(TEST_BUYER_EMAIL)
                DeleteLimitModal(admin_page).confirm_delete()
