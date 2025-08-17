import re
from asyncio import wait_for

import allure
from playwright.sync_api import expect

from page_opjects.autorization_page import AutorizationPage
from page_opjects.home_page import HomePage
from page_opjects.listing_page import ListingPage
from page_opjects.cart_page import CartPage
from page_opjects.settings_page.users_settings_page import UsersSettingsPage

# Новые объекты
from page_opjects.settings_page.account_settings_general_page import AccountSettingsGeneralPage
from page_opjects.settings_page.contracts_settings_page import ContractsSettingsPage
from page_opjects.settings_page.company_name_modal import CompanyNameModal

"""Страница Контракты"""
@allure.title("Округление копеек в листинге через настройку в Контрактах")
def test_rounding_toggle_affects_listing_prices(base_url, page_fixture):
    # page = page_fixture(role="buyer_admin")

    page = page_fixture()
    listing = ListingPage(page)
    contracts = ContractsSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    with allure.step("Проверяю, что округление выключено"):
        contracts.open(base_url)
        # Если тумблер по умолчанию включён, выключаем его
        contracts.disable_total_rounding()
        assert not contracts.is_total_rounding_enabled(), "Тумблер округления должен быть выключен перед проверкой листинга"

    with allure.step("Проверяю, что цены содержат ненулевые копейки"):
        listing.open_url(f"{base_url}/catalog/9/3707")
        assert listing.has_non_zero_kopecks(), "В листинге не найдено цен с ненулевыми копейками"
        original_prices = listing.get_price_data()
        # allure.attach(
        #     str(original_prices),
        #     name="Исходные цены",
        #     attachment_type=allure.attachment_type.TEXT
        # )


    with allure.step("Включаю округление"):
        contracts.open(base_url)
        contracts.enable_total_rounding()
        assert contracts.is_total_rounding_enabled(), "Тумблер округления не включился"

    with allure.step("Возвращаюсь в листинг и проверяю правильность округления"):
        listing.open_url(f"{base_url}/catalog/9/3707")

        is_rounded, message = listing.are_prices_rounded_up(original_prices)

        # current_prices = listing.get_price_data()

        # allure.attach(
        #     str(current_prices),
        #     name="Цены после округления",
        #     attachment_type=allure.attachment_type.TEXT
        # )

        assert is_rounded, f"Округление работает некорректно: {message}"

    with allure.step("Дополнительная проверка: все копейки равны 00"):
        current_prices = listing.get_price_data()
        kopecks_list = [p["kopecks"] for p in current_prices]
        assert all(k == 0 for k in kopecks_list), f"Найдены ненулевые копейки: {kopecks_list}"


@allure.title("Проверка работы блока «Лимиты на закупку»")
def test_purchase_limits_banner_and_cart_behavior(base_url, page_fixture):
    # page = page_fixture(role="buyer_admin")

    page = page_fixture()
    listing = ListingPage(page)
    cart = CartPage(page)
    contracts_settings = ContractsSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    contracts_settings.open(base_url)
    with allure.step("Устанавливаю лимит"):
        contracts_settings.set_item_price_limit("300")
    # TODO Решить проблему с отображением алертов
    contracts_settings.click_beside_limit_input_and_expect_toast()

    # with allure.step("Информационная плашка о том, что лимит изменен — отображается"):
    #     expect(page.locator(contracts_settings.ALERT_LIMIT_CHANGED)).to_be_visible()

    with allure.step("Добавляю в корзину товар дороже лимита"):
        page.goto(base_url + "/catalog/9/3707")
        listing.add_expensive_item_to_cart(min_price=350)  # подбирает 1 товар с ценой > 300

    # with allure.step("Товар успешно добавлен в корзину"):
    #     expect(page.locator(cart.MINI_CART_BADGE)).not_to_be_hidden(timeout=5000)

    cart.open(base_url)

    with allure.step("Проверяю, что кнопка Отправить заказ недоступна"):
        expect(page.locator(cart.SEND_BUTTON)).to_be_disabled()
    with allure.step("Отображается плашка 'Стоимость позиции превышает допустимый лимит на цену товара'"):
        expect(page.locator(cart.LIMIT_EXCEEDED_BANNER)).not_to_be_hidden(timeout=5000)

    with allure.step("Устанавливаю лимит выше стоимости добавленого товара"):
        contracts_settings.open(base_url)
        contracts_settings.set_item_price_limit("100000")
        contracts_settings.click_beside_limit_input_and_expect_toast()

    cart.open(base_url)

    with allure.step("Проверяю, что кнопка Отправить заказ доступна"):
        page.wait_for_selector(cart.SEND_BUTTON, timeout=5000)
        expect(page.locator(cart.SEND_BUTTON)).to_be_enabled()
    with allure.step("Плашка 'Стоимость позиции превышает допустимый лимит на цену товара' не отображается"):
        expect(page.locator(cart.LIMIT_EXCEEDED_BANNER)).to_be_hidden(timeout=5000)

"""Оснавная страница настроек"""
@allure.title("Редактирование названия компании")
def test_edit_company_name(base_url, page_fixture):
    # page = page_fixture(role="buyer_admin")

    page = page_fixture()
    settings_general = AccountSettingsGeneralPage(page)
    modal = CompanyNameModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    settings_general.open(base_url)

    with allure.step("Редактирую название компании"):
        modal.click_edit_company_name()

    with allure.step("Открылось окно редактирования названия"):
        modal.assert_opened()

    with allure.step("Ввожу новое название и сохраняю"):
        new_name = modal.generate_unique_company_name(prefix="Тестовый Покупатель")
        modal.fill_company_name(new_name)
        modal.click_save()

    with allure.step("Проверяю новое название на странице"):
        modal.assert_company_name_equals(new_name)

@allure.title("Переход по вкладкам страницы настроек")
def test_go_to_settings_pages(base_url, page_fixture):
    # page = page_fixture(role="buyer_admin")

    page = page_fixture()
    settings_general = AccountSettingsGeneralPage(page)
    home_page = HomePage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    home_page.open(base_url)
    home_page.click_settings_button()

    with allure.step("Проверяю, что нахожусь на странице настроек"):
        expect(page).to_have_url(re.compile(r".*/settings.*"))

    with allure.step("По умолчанию открыта вкладка Контракты"):
        expect(page).to_have_url(re.compile(r".*/contracts.*"))

    with allure.step("Переключаю вкладки, проверяю их состояние"):
        settings_general.click_users_button()
        expect(page).to_have_url(re.compile(r".*/user-list.*"))
        expect(page.request.get(page.url)).to_be_ok()

        settings_general.click_legal_antities_button()
        expect(page).to_have_url(re.compile(r".*/legal-entity-list.*"))
        expect(page.request.get(page.url)).to_be_ok()

        settings_general.click_contracts_button()
        expect(page).to_have_url(re.compile(r".*/contracts.*"))
        expect(page.request.get(page.url)).to_be_ok()


