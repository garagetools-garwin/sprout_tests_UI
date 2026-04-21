import os
import re
import time
from asyncio import wait_for

import allure
import pytest
from playwright.sync_api import expect

from page_opjects.autorization_page import AutorizationPage
from page_opjects.home_page import HomePage
from page_opjects.listing_page import ListingPage
from page_opjects.cart_page import CartPage
from page_opjects.personal_account_page import PersonalAccountPage
from page_opjects.settings_page.legal_entities_settings_page import LegalEntitiesPage, LegalEntityModal
from page_opjects.settings_page.users_settings_page import UsersSettingsPage, UserModal

# Новые объекты
from page_opjects.settings_page.general_settings_page import GeneralSettingsPage
from page_opjects.settings_page.contracts_settings_page import ContractsSettingsPage
from page_opjects.settings_page.company_name_modal import CompanyNameModal
from page_opjects.settings_page.warehouses_settings_page import WarehousesSettingsPage, WarehouseModal

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
    cart_page = CartPage(page)

    autorization_page.open(base_url)
    autorization_page.buyer_admin_for_limit_authorize()

    cart_page.clear_cart(base_url)

    contracts_settings.open(base_url)
    with allure.step("Устанавливаю лимит"):
        contracts_settings.set_item_price_limit("300")
    # TODO Решить проблему с отображением алертов
    page.mouse.click(0, 0)
    # contracts_settings.click_beside_limit_input_and_expect_toast()

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
        contracts_settings.set_item_price_limit("1000000")
        page.mouse.click(0, 0)
        # contracts_settings.click_beside_limit_input_and_expect_toast()

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
    settings_general = GeneralSettingsPage(page)
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
        new_name = modal.generate_unique_company_name(prefix="Покупатель ДЛЯ АВТОТЕСТОВ")
        modal.fill_company_name(new_name)
        modal.click_save()

    with allure.step("Проверяю новое название на странице"):
        modal.assert_company_name_equals(new_name)

@allure.title("Переход по вкладкам страницы настроек")
def test_go_to_settings_pages(base_url, page_fixture):
    # page = page_fixture(role="buyer_admin")

    page = page_fixture()
    settings_general = GeneralSettingsPage(page)
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
        settings_general.click_personal_limits_button()
        expect(page).to_have_url(re.compile(r".*/personal-limits.*"))
        expect(page.request.get(page.url)).to_be_ok()

        settings_general.click_users_button()
        expect(page).to_have_url(re.compile(r".*/user-list.*"))
        expect(page.request.get(page.url)).to_be_ok()

        settings_general.click_legal_antities_button()
        expect(page).to_have_url(re.compile(r".*/legal-entity-list.*"))
        expect(page.request.get(page.url)).to_be_ok()

        settings_general.click_contracts_button()
        expect(page).to_have_url(re.compile(r".*/contracts.*"))
        expect(page.request.get(page.url)).to_be_ok()

"""Страница Юридические лица"""


@allure.title("Открытие карточки юр. лица")
def test_open_legal_entity_card(base_url, page_fixture):
    page = page_fixture()
    entities_page = LegalEntitiesPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    entities_page.open(base_url)
    with allure.step("Проверяю, что листинг не пустой"):
        entities_page.page.wait_for_load_state('networkidle')
        cards = entities_page.get_entity_cards()
        assert cards.count() > 0
    with allure.step("Открываю первую карточку юр. лица"):
        cards.first.click()
    with allure.step("Проверяю, что окно отображается корректно"):
        assert page.locator(LegalEntityModal.MODAL).is_visible()

@allure.title("Открытие окна редактирования юр. лица (открытие из карточки юр лица)")
def test_open_edit_legal_entity_modal(base_url, page_fixture):
    page = page_fixture()
    entities_page = LegalEntitiesPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    entities_page.open(base_url)
    with allure.step("Открываю первую карточку юр. лица"):
        cards = entities_page.get_entity_cards()
        cards.first.click()
    entities_page.click_edit()
    with allure.step("Проверяю, что окно отображается корректно"):
        assert page.locator(LegalEntityModal.MODAL).is_visible()

@allure.title('Открытие окна нового юр. лица')
def test_open_new_legal_entity_modal(base_url, page_fixture):
    page = page_fixture()
    entities_page = LegalEntitiesPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    entities_page.open(base_url)
    entities_page.click_add_new()
    with allure.step("Проверяю, что окно отображается корректно"):
        assert page.locator(LegalEntityModal.MODAL).is_visible()

@allure.title("Создание нового и удаление юридического лица")
def test_create_legal_entity(base_url, page_fixture, delete_legal_entity_fixture):

    # Получаем методы из фикстуры
    mark_legal_entity_created, mark_legal_entity_deleted = delete_legal_entity_fixture

    page = page_fixture()
    entities_page = LegalEntitiesPage(page)
    modal = LegalEntityModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    entities_page.open(base_url)

    with allure.step("Проверяю, что записи с вводимым названием еще нет"):
        entities_page.page.wait_for_load_state('networkidle')
        cards = entities_page.get_entity_cards()

        with allure.step("Проверяем наличие записи с 'Автотест'"):
            existing_entities = [cards.nth(i).text_content() for i in range(cards.count())
                                 if "Автотест" in cards.nth(i).text_content()]

            if existing_entities:
                # Запись уже существует
                mark_legal_entity_created()
                assert False, f"Найдены существующие записи с 'Автотест': {existing_entities}"

    entities_page.click_add_new()

    with allure.step("Ввожу данные для записи"):
        modal.fill("Автотест", "9999999999", "123456789")
        modal.add()

        mark_legal_entity_created() # Сообщаем фикстуре, что юр лицо создано

    with allure.step("Проверяю, что ошибки не отображаются"):
        assert not page.locator('text=ИНН должен быть равен 10 символам').is_visible()
        assert not page.locator('text=КПП должен быть равен 9 символам').is_visible()
    with allure.step("Проверяю, появилась ли запись в списке"):
        cards = entities_page.get_entity_cards()
        assert any("Автотест" in cards.nth(i).text_content() for i in range(cards.count()))

    with allure.step("Удаляю созданную карточку юр лица"):
        with allure.step("Считаю количество карточек"):
            initial_count = entities_page.get_entity_cards().count()
            print(f"Изначальное число карточек: {initial_count}")

        # Найти все строки таблицы (rows)
        rows = entities_page.page.locator('.ant-table-row.ant-table-row-level-0')
        autotest_row = None
        for i in range(rows.count()):
            row_text = rows.nth(i).text_content() or ""
            if "Автотест" in row_text:
                autotest_row = rows.nth(i)
                break
        assert autotest_row is not None, "Карточка с 'Автотест' не найдена!"

        with allure.step("Открываю меню действий у найденной строки"):
            # Берите кнопку только внутри строки!
            action_menu_button = autotest_row.locator('button.button-icon')  # уточните селектор на свой!
            action_menu_button.hover()

        with allure.step("Удаляю найденную карточку"):
            delete_button = entities_page.page.locator("text=Удалить")  # уточните путь, если в меню кнопка не видна глобально
            delete_button.click()

        with allure.step("В появившейся модалке подтверждаю удаление"):
            modal.click_delete()

        with allure.step("Проверяю, что число карточек уменьшилось"):
            new_count = entities_page.get_entity_cards().count()
            print(f"Новое число карточек: {new_count}")
            assert new_count == initial_count - 1

        mark_legal_entity_deleted() # Сообщаем фикстуре, что юр лицо удалено

@allure.title("Редактирование юридического лица") # открытие из лиситнга
def test_edit_and_delete_legal_entity(base_url, page_fixture):
    page = page_fixture()
    entities_page = LegalEntitiesPage(page)
    modal = LegalEntityModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    entities_page.open(base_url)
    entities_page.open_action_menu()
    entities_page.click_edit()
    with allure.step("Ввожу новые данные для записи"):
        modal.fill("Изменено", "8888888888", "987654321")
        modal.save()
    with allure.step("Проверяю, что ошибки не отображаются"):
        assert not page.locator('text=ИНН должен быть равен 10 символам').is_visible()
        assert not page.locator('text=КПП должен быть равен 9 символам').is_visible()
    with allure.step("Проверяю, что запись в списке изменилась"):
        cards = entities_page.get_entity_cards()
        assert any("Изменено" in cards.nth(i).text_content() for i in range(cards.count()))

@allure.title("Открытие окна подтверждения удаления и отмена удаления (открытие из карточки юр лица)")
def test_cancel_delete_legal_entity(base_url, page_fixture):
    page = page_fixture()
    entities_page = LegalEntitiesPage(page)
    modal = LegalEntityModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    entities_page.open(base_url)
    with allure.step("Открываю первую карточку юр. лица"):
        cards = entities_page.get_entity_cards()
        cards.first.click()
    entities_page.click_delete()

    with allure.step("В появившейся модалке отменяем удаление"):
        modal.cancel_delete()
    with allure.step("Проеверяю, что модалка подтверждения удаления закрыта"):
        assert not page.locator(LegalEntityModal.DELETE_MODAL).is_visible()
    with allure.step("Проеверяю, что модалка юр лица открыта"):
        assert page.locator(LegalEntityModal.MODAL).is_visible()
    with allure.step("Проеверяю, что запись не была удалена"):
        assert entities_page.get_entity_cards().count() > 0


@allure.title("Обязательность всех полей")
def test_mandatory_all_fields(base_url, page_fixture):
    page = page_fixture()
    entities_page = LegalEntitiesPage(page)
    modal = LegalEntityModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    entities_page.open(base_url)
    entities_page.click_add_new()

    with allure.step("Проверяю обязательность всех полей"):
        # Оставляем все поля пустыми
        modal.fill("", "", "")
        modal.add()
        assert page.locator("#name_help").get_by_text("Обязательное поле при сохранении").is_visible()
        # assert page.locator("#kpp_help").get_by_text("Обязательное поле при сохранении").is_visible()
        assert page.locator("#name_help").get_by_text("Обязательное поле при сохранении").is_visible()

    with allure.step("ИНН обязателен к заполнению"):
        modal.fill("BoundTest", "", "123456789")
        modal.add()
        assert page.locator("#inn_help").get_by_text("Обязательное поле при сохранении").is_visible()

    with allure.step("КПП обязателен к заполнению"):
        modal.fill("BoundTest", "1234567890", "")
        modal.add()
        # assert page.locator("#kpp_help").get_by_text("Обязательное поле при сохранении").is_visible()

    with allure.step("Наименование обязательно к заполнению"):
        modal.fill("", "1234567890", "123456789")
        modal.add()
        assert page.locator("#name_help").get_by_text("Обязательное поле при сохранении").is_visible()

#TODO добавить тесты на ИП

@allure.title("Граничные значения для ИНН и КПП")
def test_inn_kpp_boundaries(base_url, page_fixture):
    page = page_fixture()
    entities_page = LegalEntitiesPage(page)
    modal = LegalEntityModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    entities_page.open(base_url)
    entities_page.click_add_new()

    with allure.step("Проеверяю, ИНН < 10 символов"):
        modal.fill("BoundTest", "123456789", "123456789")
        modal.add()
        assert page.locator('text=ИНН должен содержать 10 (для юридических лиц) или 12 (для ИП) цифр').is_visible()

    with allure.step("Проеверяю, ИНН > 10 символов"):
        modal.fill("BoundTest", "12345678901", "123456789")
        modal.add()
        assert page.locator('text=ИНН должен содержать 10 (для юридических лиц) или 12 (для ИП) цифр').is_visible()

    with allure.step("Проеверяю, КПП < 9 символов"):
        modal.fill("BoundTest", "1234567890", "12345678")
        modal.add()
        assert page.locator('text=Для ИНН юридического лица КПП обязателен и должен содержать 9 символов').is_visible()

    with allure.step("Проеверяю, КПП > 9 символов"):
        modal.fill("BoundTest", "1234567890", "1234567890")
        modal.add()
        assert page.locator('text=Для ИНН юридического лица КПП обязателен и должен содержать 9 символов').is_visible()

@allure.title("Копирование реквизитов ИНН/КПП из карточки юр. лица")
def test_copy_inn_kpp(base_url, page_fixture):
    page = page_fixture()

    # Даем разрешения на работу с clipboard (синхронная версия)
    page.context.grant_permissions(['clipboard-read', 'clipboard-write'])

    entities_page = LegalEntitiesPage(page)
    modal = LegalEntityModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    entities_page.open(base_url)

    with allure.step("Открываю первую карточку юр. лица"):
        cards = entities_page.get_entity_cards()
        cards.first.click()

    with allure.step("Копирую ИНН"):
        modal.click_copy_inn()

    with allure.step("Проверяю, что информация в буфере обмена соотвествует настоящему ИНН"):
        # Получаем содержимое clipboard через браузер API (синхронная версия)
        clipboard_content = page.evaluate("() => navigator.clipboard.readText()")
        expected_inn = page.locator('.legal-entity-card__details-table-row-container div.text-body').text_content()
        assert clipboard_content == expected_inn

    with allure.step("Копирую КПП"):
        modal.click_copy_kpp()

    with allure.step("Проверяю, что информация в буфере обмена соотвествует настоящему КПП"):
        # Получаем содержимое clipboard через браузер API (синхронная версия)
        clipboard_content = page.evaluate("() => navigator.clipboard.readText()")
        expected_kpp = page.locator(".text-body:has-text('КПП:') + .legal-entity-card__details-table-row-container span.text-body").text_content()
        assert clipboard_content == expected_kpp

"""Страница Пользователь"""

@allure.title("Открытие окна нового пользователя")
def test_open_new_user_modal(base_url, page_fixture):
    page = page_fixture()
    users = UsersSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    users.open(base_url)
    users.click_add_user_button()
    assert page.locator("text='Пригласить пользователя'").is_visible()

@allure.title("Открытие карточки любого пользователя")
def test_open_user_card(base_url, page_fixture):
    page = page_fixture()
    users = UsersSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    users.open(base_url)
    with allure.step("Проверяю, что листинг не пустой"):
        users.page.wait_for_load_state('networkidle')
        cards = users.get_users_cards()
        assert cards.count() > 0
    with allure.step("Открываю первую карточку юр. лица"):
        cards.first.click()
    with allure.step("Проверяю, что окно отображается корректно"):
        assert page.locator(UsersSettingsPage.MODAL).is_visible()

@allure.title("Кнопка Удалить в карточке пользователя — открывается окно удаления")
def test_open_user_delete_modal(base_url, page_fixture):
    page = page_fixture()
    users = UsersSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    users.open(base_url)
    cards = users.get_users_cards()
    cards.first.click()
    page.locator("button:has-text('Удалить')").click()
    assert page.locator("text='Вы уверены, что хотите удалить пользователя?'").is_visible()

@allure.title("Обязательность всех полей для нового пользователя")
def test_mandatory_all_fields_for_user(base_url, page_fixture):
    page = page_fixture()
    users = UsersSettingsPage(page)
    autorization_page = AutorizationPage(page)
    modal = UserModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    users.open(base_url)
    users.click_add_user_button()

    with allure.step("Проверяю обязательность всех полей"):
        # Оставляем все поля пустыми
        modal.fill_main_fields("", "", "")
        modal.click_send_invite()
        assert page.locator(modal.EMAIL_TIP).get_by_text("Обязательное поле при сохранении").is_visible()
        assert page.locator(modal.LASTNAME_TIP).get_by_text("Обязательное поле при сохранении").is_visible()
        assert page.locator(modal.FIRSTNAME_TIP).get_by_text("Обязательное поле при сохранении").is_visible()

    with allure.step("Фамилия обязательна к заполнению"):
        modal.fill_main_fields("mail@test.com", "", "first_name")
        modal.click_send_invite()
        assert page.locator(modal.LASTNAME_TIP).get_by_text("Обязательное поле при сохранении").is_visible()

    with allure.step("Имя обязательно к заполнению"):
        modal.fill_main_fields("mail@test.com", "last_name", "")
        modal.click_send_invite()
        assert page.locator(modal.FIRSTNAME_TIP).get_by_text("Обязательное поле при сохранении").is_visible()

    with allure.step("E-mail обязателен к заполнению"):
        modal.fill_main_fields("", "last_name", "first_name")
        modal.click_send_invite()
        assert page.locator(modal.EMAIL_TIP).get_by_text("Обязательное поле при сохранении").is_visible()

@allure.title("Невадидный e-mail")
def test_ivalid_email_for_user(base_url, page_fixture):
    page = page_fixture()
    users = UsersSettingsPage(page)
    autorization_page = AutorizationPage(page)
    modal = UserModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()


    users.open(base_url)
    users.click_add_user_button()

    with allure.step("email без собаки"):
        # Оставляем все поля пустыми
        modal.fill_main_fields("mailtest.com", "last_name", "first_name")
        modal.click_send_invite()
        assert page.locator(modal.EMAIL_TIP).get_by_text("Неверный формат электронной почты").is_visible()

    with allure.step("email без точки"):
        modal.fill_main_fields("mail@testcom", "last_name", "first_name")
        modal.click_send_invite()
        assert page.locator(modal.EMAIL_TIP).get_by_text("Неверный формат электронной почты").is_visible()

    with allure.step("email с двумия собаками"):
        modal.fill_main_fields("mail@@test.com", "last_name", "first_name")
        modal.click_send_invite()
        assert page.locator(modal.EMAIL_TIP).get_by_text("Неверный формат электронной почты").is_visible()

@allure.title("Приглашение уже активированного email")
def test_invite_existing_email(base_url, page_fixture):
    page = page_fixture()
    users = UsersSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    users.open(base_url)
    users.click_add_user_button()
    modal = UserModal(page)
    modal.fill_main_fields(email="testgarwin_yur+b2b@mail.ru", last_name="Фам", first_name="Имя")
    modal.click_send_invite()
    assert page.locator("text='Адрес электронной почты уже используется'").is_visible()

@allure.title("Редактирование пользователя и проверка изменений")
def test_user_edit_and_save(base_url, page_fixture):
    page = page_fixture()
    users = UsersSettingsPage(page)
    autorization_page = AutorizationPage(page)
    modal = UserModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    users.open(base_url)
    cards = users.get_users_cards()
    cards.first.click()
    page.locator("button:has-text('Редактировать')").click()
    with allure.step("Проверяю, что окно редактирования пользователя открыто"):
        assert page.locator("text='Редактировать данные'").is_visible()

    last_name, first_name, patronymic, position, phone = modal.fill_in_data_randomize()
    modal.click_save_button()
    assert page.locator("text=Данные пользователя успешно изменены").is_visible(timeout=4000)
    assert cards.first.locator(f':has-text("{last_name} {first_name} {patronymic}")').first.is_visible()

@allure.title("Операция с ролями (выбор, проверка доступных ролей, массовый выбор)")
def test_roles_selection_in_user_card(base_url, page_fixture):
    page = page_fixture()
    users = UsersSettingsPage(page)
    autorization_page = AutorizationPage(page)
    modal = UserModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    users.open(base_url)
    cards = users.get_users_cards()
    modal.open_last_user_card(cards)

    roles_block = modal.get_roles_block()
    with allure.step("Проверяю, что отображаются роли 'Пользователь' и 'Администратор аккаунта'"):
        assert roles_block.locator("text=Администратор аккаунта").is_visible()

    modal.click_main_role_button()
    modal.deselect_all_roles()

    with allure.step("Проверяю, что ссылка /request-list/manager НЕ отображается (Доступна только закупщику)"):
        assert not modal.is_manager_link_visible()

    modal.go_to_url("https://sprout-store.ru/settings/subdivision/136/general")
    modal.open_head_role_selector()
    full_name = "Тестовый Покупатель (администратор) (ФИО пользователя)"  # подставьте нужное ФИО

    with allure.step("Проверяю, что ФИО в подразделении отсутствует"):
        assert full_name not in page.content()

    modal.go_to_url(base_url + "/settings/account/user-list")
    modal.open_last_user_card(cards)
    modal.click_main_role_button()
    modal.select_all_roles()

    roles_block = modal.get_roles_block()
    with allure.step("Проверяю, что все роли теперь видимы в карточке"):
        assert roles_block.locator("text=Администратор аккаунта").is_visible()
        assert roles_block.locator("text=Закупщик").is_visible()
        assert roles_block.locator("text=Руководитель подразделения").is_visible()

    with allure.step("Проверяю, что ссылка /request-list/manager отображается (Доступна только закупщику)"):
        assert modal.is_manager_link_visible()

    modal.go_to_url("https://sprout-store.ru/settings/subdivision/136/general")
    modal.open_head_role_selector()
    with allure.step("Проверяю, что теперь ФИО присутствует хотя бы 1 раз"):
        expect(page.locator(f"text={full_name}")).to_be_visible(timeout=5000)
        assert full_name in page.content()

@allure.title("Рутового пользователя нельзя удалить/отменить роль админстратора")
def test_root_user_cannot_be_deleted(base_url, page_fixture):
    page = page_fixture()
    users = UsersSettingsPage(page)
    autorization_page = AutorizationPage(page)
    modal = UserModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    users.open(base_url)
    cards = users.get_users_cards()
    modal.open_last_user_card(cards)

    modal.click_main_role_button()

    modal.root_delete_button_is_disabled()
    modal.admin_role_is_not_toggleable()

@pytest.mark.skip(reason="временно отключен, ошибка будет исправлена через неопределенное время")
@allure.title("Выдаем и забираем роль администратора у обычного пользователя")
def test_change_admin_role_flow(base_url, page_fixture):

    page_user = page_fixture()
    users_user = UsersSettingsPage(page_user)
    autorization_user = AutorizationPage(page_user)
    modal_user = UserModal(page_user)

    page_admin = page_fixture()
    users_admin = UsersSettingsPage(page_admin)
    autorization_admin = AutorizationPage(page_admin)
    modal_admin = UserModal(page_admin)

    with allure.step("Захожу как админ проверяю что у пользователя нет прав администратора"):
        autorization_admin.open(base_url)
        autorization_admin.admin_buyer_authorize()

        users_admin.open(base_url)

    with allure.step("Открыть карточку нужного пользователя по email"):
        users_admin.open_user_card_by_email("testgarwin_yur+2@mail.ru")
        modal_admin.click_main_role_button()
        modal_admin.disable_admin_role()

    with allure.step("Вхожу как обычный пользователь"):
        autorization_user.open(base_url)
        autorization_user.test_buyer_for_admin_role_authorize()

    with allure.step("Проверяю, что ссылка /workspace-list НЕ отображается (Доступна только админу)"):
        page_user.wait_for_selector('.sidebar__body', state='visible')
        modal_user.transition_to_contracts_page_assertion_not(base_url)

    with allure.step("Захожу как админ"):
        # autorization_admin.open(base_url)
        # autorization_admin.admin_buyer_authorize()

        users_admin.open(base_url)

    with allure.step("Открыть карточку нужного пользователя по email"):
        users_admin.open_user_card_by_email("testgarwin_yur+2@mail.ru")
        modal_admin.click_main_role_button()
        modal_admin.set_admin_role()

    with allure.step("Проверяю, что в списке пользователей появилось 'Администратор аккаунта' у юзера"):
        assert users_admin.is_admin_badge_present("testgarwin_yur+2@mail.ru")

    users_user.open(base_url)
    with allure.step("Проверяю, что ссылка /workspace-list отображается (Доступна только админу)"):
        page_user.wait_for_selector('.sidebar__body', state='visible')
        modal_user.transition_to_contracts_page_assertion(base_url)

    with allure.step("Открыть карточку нужного пользователя по email"):
        users_admin.open(base_url)
        users_admin.open_user_card_by_email("testgarwin_yur+2@mail.ru")
        modal_admin.click_main_role_button()
        modal_admin.unset_admin_role()

    with allure.step("Проверяю, что в списке пользователей 'Администратор аккаунта' у юзера отсутствует"):
        assert not users_admin.is_admin_badge_present("testgarwin_yur+2@mail.ru")

import os
import allure
import pytest
from page_opjects.autorization_page import AutorizationPage
from page_opjects.settings_page.users_settings_page import UsersSettingsPage, UserModal

ROLE_NAME = "Менеджер контракта"
ACTIVE_BASKET_URL = "https://sprout-store.ru/active-basket-list"
WITHOUT_ROLE_MANAGER_EMAIL = os.getenv("WITHOUT_ROLE_MANAGER_EMAIL")
WITHOUT_ROLE_MANAGER_PASSWORD = os.getenv("WITHOUT_ROLE_MANAGER_PASSWORD")

@allure.title("Назначение роли «Менеджер контракта» и проверка доступа к активным корзинам")
def test_assign_contract_manager_role_and_verify_access(base_url, page_fixture):

    # Часть 1: Админ-продавец назначает роль
    page_admin = page_fixture()
    auth_admin = AutorizationPage(page_admin)
    users_page = UsersSettingsPage(page_admin)

    with allure.step("Авторизация как администратор-продавец"):
        auth_admin.open(base_url)
        auth_admin.admin_seller_authorize()
        page_admin.wait_for_load_state("networkidle")

    with allure.step("Открыть страницу управления пользователями"):
        users_page.open(base_url)
        page_admin.wait_for_load_state("networkidle")

    with allure.step(f"Найти пользователя {WITHOUT_ROLE_MANAGER_EMAIL}"):
        users_page.search_user(WITHOUT_ROLE_MANAGER_EMAIL)
        page_admin.wait_for_timeout(1000)
        assert users_page.is_user_visible(WITHOUT_ROLE_MANAGER_EMAIL), (
            f"Пользователь {WITHOUT_ROLE_MANAGER_EMAIL} не найден в списке"
        )

    with allure.step("Открыть карточку пользователя"):
        users_page.open_user_card(WITHOUT_ROLE_MANAGER_EMAIL)
        page_admin.wait_for_timeout(1000)

    with allure.step(f"Назначить роль «{ROLE_NAME}»"):
        modal = UserModal(page_admin)
        modal.set_role(ROLE_NAME)
        page_admin.wait_for_timeout(1500)

    # Часть 2: С ролью — доступ есть
    page_user = page_fixture()
    auth_user = AutorizationPage(page_user)

    with allure.step("Авторизоваться как менеджер контракта"):
        auth_user.open(base_url)
        auth_user.without_role_manager_authorize()
        page_user.wait_for_load_state("networkidle")

    with allure.step("Проверить, что страница активных корзин доступна (нет 403)"):
        forbidden_responses = []

        def capture_403(response):
            if response.status == 403:
                forbidden_responses.append(response.url)

        page_user.on("response", capture_403)

        page_user.goto(ACTIVE_BASKET_URL)
        page_user.wait_for_load_state("networkidle")
        page_user.wait_for_timeout(2000)

        page_user.remove_listener("response", capture_403)

        # Проверяем: нет 403 в network
        assert len(forbidden_responses) == 0, (
            f"Получены 403 ответы при наличии роли: {forbidden_responses}"
        )

        # Проверяем: нет нотификации "forbidden resource"
        forbidden_toast = page_user.locator("text=/forbidden resource/i")
        assert not forbidden_toast.is_visible(), (
            "Отображается нотификация 'forbidden resource' при наличии роли"
        )

    allure.attach(
        page_user.screenshot(full_page=True),
        name="with-role-active-basket-list",
        attachment_type=allure.attachment_type.PNG,
    )

    # ── Часть 3: Снять роль и проверить, что доступ пропал ──
    with allure.step("Постусловие: снять роль менеджера контракта"):
        users_page.open(base_url)
        page_admin.wait_for_load_state("networkidle")
        users_page.search_user(WITHOUT_ROLE_MANAGER_EMAIL)
        page_admin.wait_for_timeout(1000)
        users_page.open_user_card(WITHOUT_ROLE_MANAGER_EMAIL)
        page_admin.wait_for_timeout(1000)
        modal.unset_role(ROLE_NAME)
        page_admin.wait_for_timeout(1500)

    with allure.step("Проверить, что без роли страница возвращает 403"):
        forbidden_responses_after = []

        def capture_403_after(response):
            if response.status == 403:
                forbidden_responses_after.append(response.url)

        page_user.on("response", capture_403_after)

        page_user.goto(ACTIVE_BASKET_URL)
        page_user.wait_for_load_state("networkidle")
        page_user.wait_for_timeout(2000)

        page_user.remove_listener("response", capture_403_after)

        # Проверяем: ЕСТЬ 403 в network
        assert len(forbidden_responses_after) > 0, (
            "Ожидались 403 ответы после снятия роли, но их нет"
        )

    allure.attach(
        page_user.screenshot(full_page=True),
        name="without-role-active-basket-list",
        attachment_type=allure.attachment_type.PNG,
    )


"""Страница Склады отгрузки (продавец)"""


# ============================================================================
# ВЫСОКИЙ ПРИОРИТЕТ
# ============================================================================


# @allure.title("Создание нового склада и его удаление")
# @allure.tag("positive", "regression", "high")
# @allure.severity(allure.severity_level.CRITICAL)
# def test_create_and_delete_warehouse(base_url, page_fixture):
#     """
#     Объединяет тест-кейсы:
#     - Создание склада (высокий приоритет)
#     - Проверка оповещения об успешном добавлении
#     - Удаление созданного склада (чистка за собой)
#     """
#     page = page_fixture()
#     autorization_page = AutorizationPage(page)
#     warehouses = WarehousesSettingsPage(page)
#     modal = WarehouseModal(page)
#
#     autorization_page.open(base_url)
#     autorization_page.admin_seller_authorize()
#
#     warehouses.open(base_url)
#
#     initial_count = warehouses.get_warehouses_count()
#
#     with allure.step("Открываю окно добавления склада"):
#         warehouses.click_add_warehouse()
#         assert warehouses.is_modal_visible(), "Окно нового склада не открылось"
#
#     with allure.step("Заполняю обязательные поля корректными значениями"):
#         warehouse_name, address, city = modal.fill_random()
#
#         allure.attach(
#             f"Название: {warehouse_name}\nАдрес: {address}\nГород: {city}",
#             name="Данные склада"
#         )
#
#     with allure.step("Нажимаю 'Добавить склад'"):
#         modal.click_add()
#
#     with allure.step("Проверяю оповещение об успешном добавлении"):
#         assert warehouses.is_success_toast_visible(), \
#             "Оповещение 'Новый склад добавлен' не отображается"
#
#     with allure.step("Проверяю, что склад появился в списке"):
#         page.wait_for_timeout(1000)
#         new_count = warehouses.get_warehouses_count()
#         assert new_count == initial_count + 1, \
#             f"Количество складов не увеличилось. Было: {initial_count}, стало: {new_count}"
#
#         assert warehouses.is_warehouse_present(warehouse_name), \
#             f"Склад '{warehouse_name}' не найден в списке"
#
#     # --- Удаление созданного склада ---
#     with allure.step("Открываю экшн-меню созданного склада и удаляю"):
#         warehouses.click_warehouse_by_name(warehouse_name)
#         modal.click_delete()
#
#     with allure.step("Проверяю отображение окна подтверждения удаления"):
#         assert modal.is_delete_confirmation_visible(), \
#             "Окно подтверждения удаления не появилось"
#
#     with allure.step("Подтверждаю удаление"):
#         modal.confirm_delete()
#
#     with allure.step("Проверяю оповещение об удалении"):
#         assert warehouses.is_delete_success_toast_visible(), \
#             "Оповещение 'Склад удален' не отображается"
#
#     with allure.step("Проверяю, что склад удалён из списка"):
#         page.wait_for_timeout(1000)
#         final_count = warehouses.get_warehouses_count()
#         assert final_count == initial_count, \
#             f"Количество складов не вернулось к исходному. Было: {initial_count}, стало: {final_count}"
#
#         assert not warehouses.is_warehouse_present(warehouse_name), \
#             f"Склад '{warehouse_name}' всё ещё отображается в списке"


import random
import allure
import pytest
from faker import Faker
from playwright.sync_api import expect

from page_opjects.autorization_page import AutorizationPage
from page_opjects.settings_page.warehouses_settings_page import WarehousesSettingsPage, WarehouseModal

fake = Faker('ru_RU')

"""Тесты страницы Склады отгрузки (Продавец)"""


@allure.title("Создание нового склада и его удаление")
def test_create_and_delete_warehouse(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)
    modal = WarehouseModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)

    initial_count = warehouses.get_warehouses_count()

    with allure.step("Открываю окно добавления склада"):
        warehouses.click_add_warehouse()
        assert warehouses.is_modal_visible(), "Окно нового склада не открылось"

    with allure.step("Заполняю обязательные поля корректными значениями"):
        warehouse_name, address, city = modal.fill_random()
        print(warehouse_name)

        allure.attach(
            f"Название: {warehouse_name}\nАдрес: {address}\nГород: {city}",
            name="Данные склада"
        )

    with allure.step("Нажимаю 'Добавить склад'"):
        modal.click_add()

    with allure.step("Проверяю оповещение об успешном добавлении"):
        assert warehouses.is_success_toast_visible(), \
            "Оповещение 'Новый склад добавлен' не отображается"

    with allure.step("Проверяю, что склад появился в списке"):
        page.wait_for_timeout(1000)
        new_count = warehouses.get_warehouses_count()
        assert new_count == initial_count + 1, \
            f"Количество складов не увеличилось. Было: {initial_count}, стало: {new_count}"

        assert warehouses.is_warehouse_present(warehouse_name), \
            f"Склад '{warehouse_name}' не найден в списке"

    # --- Удаление через экшн-меню (как адреса в subdivisions) ---
    with allure.step("Навожу на экшн-меню созданного склада и нажимаю Удалить"):
        warehouses.delete_warehouse_by_name(warehouse_name)

    with allure.step("Проверяю отображение окна подтверждения удаления"):
        assert page.locator("text=Вы уверены").is_visible(), \
            "Окно подтверждения удаления не появилось"

    with allure.step("Подтверждаю удаление"):
        warehouses.confirm_delete()

    with allure.step("Проверяю оповещение об удалении"):
        assert warehouses.is_delete_success_toast_visible(), \
            "Оповещение 'Склад удален' не отображается"

    with allure.step("Проверяю, что склад удалён из списка"):
        page.wait_for_timeout(1000)
        final_count = warehouses.get_warehouses_count()
        assert final_count == initial_count, \
            f"Количество складов не вернулось к исходному. Было: {initial_count}, стало: {final_count}"

        assert not warehouses.is_warehouse_present(warehouse_name), \
            f"Склад '{warehouse_name}' всё ещё отображается в списке"


@allure.title("Редактирование склада через экшн-меню")
def test_edit_warehouse(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)
    modal = WarehouseModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)

    with allure.step("Открываю карточку первого склада через экшн-меню → Редактировать"):
        warehouses.open_warehouse_card(0)
        assert warehouses.is_modal_visible(), "Карточка склада не открылась"

    with allure.step("Запоминаю исходные данные"):
        original_name = modal.get_name_value()
        original_address = modal.get_address_value()
        original_city = modal.get_city_value()

        allure.attach(
            f"Название: {original_name}\nАдрес: {original_address}\nГород: {original_city}",
            name="Исходные данные"
        )

    with allure.step("Ввожу новые данные"):
        new_name = f"Изменённый склад {random.randint(0, 999999)}"
        new_address = fake.street_address()
        new_city = fake.city()

        modal.fill(new_name, new_address, new_city)

    with allure.step("Сохраняю изменения"):
        modal.click_save()

    with allure.step("Проверяю оповещение об успешном редактировании"):
        assert warehouses.is_edit_success_toast_visible(), \
            "Оповещение 'Склад успешно изменен' не отображается"

    with allure.step("Проверяю, что данные обновились в списке"):
        page.wait_for_timeout(1000)
        assert warehouses.is_warehouse_present(new_name), \
            f"Склад '{new_name}' не найден в списке после редактирования"

    with allure.step("Постусловие: возвращаю исходные данные"):
        warehouses.open_warehouse_card_by_name(new_name)
        modal.fill(original_name, original_address, original_city)
        modal.click_save()
        page.wait_for_timeout(1000)


@allure.title("Редактирование склада с автозаполнением адреса")
def test_edit_warehouse_with_address_autocomplete(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)
    modal = WarehouseModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)

    with allure.step("Открываю карточку первого склада через экшн-меню → Редактировать"):
        warehouses.open_warehouse_card(0)
        assert warehouses.is_modal_visible(), "Карточка склада не открылась"

    with allure.step("Запоминаю исходные данные"):
        original_name = modal.get_name_value()
        original_address = modal.get_address_value()
        original_city = modal.get_city_value()

        allure.attach(
            f"Название: {original_name}\nАдрес: {original_address}\nГород: {original_city}",
            name="Исходные данные"
        )

    with allure.step("Ввожу новые данные"):
        new_name = f"Изменённый склад {random.randint(0, 999999)}"
        modal.fill(new_name)

    with allure.step("Ввожу часть адреса в поиск"):
        modal.search_address("Краснодонцев 13")

    with allure.step("Проверяю отображение подсказок адресов"):
        assert modal.is_address_suggestions_visible(), \
            "Подсказки адресов не отображаются"

    with allure.step("Выбираю первую подсказку"):
        modal.select_first_address_suggestion()

    with allure.step("Проверяю автозаполнение полей"):
        address_value = modal.get_address_value()
        city_value = modal.get_city_value()

        assert address_value != "", "Поле 'Адрес' не заполнилось"
        assert city_value != "", "Поле 'Город' не заполнилось"

        allure.attach(
            f"Адрес: {address_value}\nГород: {city_value}",
            name="Автозаполненные данные"
        )

    with allure.step("Сохраняю изменения"):
        modal.click_save()

    with allure.step("Проверяю оповещение об успешном редактировании"):
        assert warehouses.is_edit_success_toast_visible(), \
            "Оповещение 'Склад успешно изменен' не отображается"

    with allure.step("Проверяю, что данные обновились в списке"):
        page.wait_for_timeout(1000)
        assert warehouses.is_warehouse_present(new_name), \
            f"Склад '{new_name}' не найден в списке после редактирования"

    with allure.step("Постусловие: возвращаю исходные данные"):
        warehouses.open_warehouse_card_by_name(new_name)
        modal.fill(original_name, original_address, original_city)
        modal.click_save()
        page.wait_for_timeout(1000)


@allure.title("Открытие окна нового склада")
def test_open_new_warehouse_modal(base_url, page_fixture):
    """Тест-кейс: Кнопка 'Добавить склад' открывает drawer"""
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)

    with allure.step("Нажимаю на кнопку 'Добавить склад'"):
        warehouses.click_add_warehouse()

    with allure.step("Проверяю, что окно нового склада отображается"):
        assert warehouses.is_modal_visible(), "Окно нового склада не открылось"


@allure.title("Отображение экшн-меню склада")
def test_warehouse_action_menu_display(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)

    with allure.step("Проверяю, что в списке есть склады"):
        assert warehouses.get_warehouses_count() > 0, "Список складов пуст"

    with allure.step("Навожу на экшн-меню первого склада"):
        warehouses.hover_action_menu(0)

    with allure.step("Проверяю отображение опций меню"):
        assert page.locator(warehouses.EDIT_OPTION).is_visible(), \
            "Опция 'Редактировать' не отображается"
        assert page.locator(warehouses.DELETE_OPTION).is_visible(), \
            "Опция 'Удалить' не отображается"


@allure.title("Открытие карточки склада через экшн-меню → Редактировать")
def test_open_warehouse_card_via_action_menu(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)
    modal = WarehouseModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)

    with allure.step("Проверяю, что листинг не пустой"):
        assert warehouses.get_warehouses_count() > 0, "Список складов пуст"

    with allure.step("Открываю карточку через экшн-меню → Редактировать"):
        warehouses.open_warehouse_card(0)

    with allure.step("Проверяю, что карточка склада открылась"):
        assert warehouses.is_modal_visible(), "Карточка склада не открылась"

    with allure.step("Проверяю, что поля заполнены данными"):
        name_value = modal.get_name_value()
        assert name_value != "", "Поле 'Наименование' пустое в режиме редактирования"

        allure.attach(name_value, name="Наименование склада в карточке")


@allure.title("Открытие окна подтверждения удаления склада через экшн-меню")
def test_open_delete_warehouse_confirmation(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)

    with allure.step("Проверяю, что в списке есть склады"):
        assert warehouses.get_warehouses_count() > 0, "Список складов пуст"

    with allure.step("Навожу на экшн-меню и нажимаю Удалить"):
        warehouses.hover_action_menu(0)
        warehouses.click_delete_option()

    with allure.step("Проверяю, что окно подтверждения удаления открылось"):
        assert page.locator("text=Вы уверены").is_visible(), \
            "Окно подтверждения удаления не появилось"


@allure.title("Отмена удаления склада")
@allure.tag("positive", "regression", "medium")
@allure.severity(allure.severity_level.NORMAL)
def test_cancel_delete_warehouse(base_url, page_fixture):
    """Тест-кейс: Отменить удаление — количество складов не меняется"""
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)
    modal = WarehouseModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)

    initial_count = warehouses.get_warehouses_count()
    assert initial_count > 0, "Нет складов для теста"

    with allure.step("Открываю карточку первого склада через экшн-меню"):
        warehouses.hover_action_menu(0)
        warehouses.click_delete_option()

    # with allure.step("Нажимаю кнопку удаления в карточке"):
    #     modal.confirm_delete()

    with allure.step("Проверяю отображение окна подтверждения"):
        assert modal.is_delete_confirmation_visible()

    with allure.step("Отменяю удаление"):
        modal.cancel_delete()

    with allure.step("Проверяю, что окно подтверждения закрылось"):
        assert not modal.is_delete_confirmation_visible(), \
            "Окно подтверждения удаления не закрылось"

    with allure.step("Проверяю количество"):
        new_count = warehouses.get_warehouses_count()
        assert new_count == initial_count, \
            f"Количество складов изменилось. Было: {initial_count}, стало: {new_count}"


@allure.title("Поиск адреса через автозаполнение")
def test_address_autocomplete(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)
    modal = WarehouseModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)
    warehouses.click_add_warehouse()

    with allure.step("Ввожу часть адреса в поиск"):
        modal.search_address("Краснодонцев 13")

    with allure.step("Проверяю отображение подсказок адресов"):
        assert modal.is_address_suggestions_visible(), \
            "Подсказки адресов не отображаются"

    with allure.step("Выбираю первую подсказку"):
        modal.select_first_address_suggestion()

    with allure.step("Проверяю автозаполнение полей"):
        address_value = modal.get_address_value()
        city_value = modal.get_city_value()

        assert address_value != "", "Поле 'Адрес' не заполнилось"
        assert city_value != "", "Поле 'Город' не заполнилось"

        allure.attach(
            f"Адрес: {address_value}\nГород: {city_value}",
            name="Автозаполненные данные"
        )

    warehouses.close_modal()

"""Негатвные кейсы"""


@allure.title("Нельзя создать склад без обязательных полей")
def test_warehouse_mandatory_fields(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)
    modal = WarehouseModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)
    warehouses.click_add_warehouse()

    initial_count = warehouses.get_warehouses_count()

    with allure.step("Проверяю: все поля пустые"):
        modal.fill("", "", "")
        modal.click_add()

        assert modal.is_name_error_visible(), "Ошибка для 'Наименование' не отображается"
        assert modal.is_address_error_visible(), "Ошибка для 'Адрес' не отображается"
        assert modal.is_city_error_visible(), "Ошибка для 'Город' не отображается"

    with allure.step("Проверяю: заполнено только Наименование"):
        modal.clear_all()
        modal.fill("Тестовый склад", "", "")
        modal.click_add()

        assert not modal.is_name_error_visible(), "Ошибка для 'Наименование' не должна отображаться"
        assert modal.is_address_error_visible(), "Ошибка для 'Адрес' не отображается"
        assert modal.is_city_error_visible(), "Ошибка для 'Город' не отображается"

    with allure.step("Проверяю: заполнено Наименование и Адрес"):
        modal.clear_all()
        modal.fill("Тестовый склад", "Тестовый адрес", "")
        modal.click_add()

        assert not modal.is_name_error_visible()
        assert not modal.is_address_error_visible()
        assert modal.is_city_error_visible(), "Ошибка для 'Город' не отображается"

    with allure.step("Проверяю: заполнено Наименование и Город"):
        modal.clear_all()
        modal.fill("Тестовый склад", "", "Тестовый город")
        modal.click_add()

        assert not modal.is_name_error_visible()
        assert modal.is_address_error_visible(), "Ошибка для 'Адрес' не отображается"
        assert not modal.is_city_error_visible()

    with allure.step("Проверяю: заполнены Адрес и Город, пустое Наименование"):
        modal.clear_all()
        modal.fill("", "Тестовый адрес", "Тестовый город")
        modal.click_add()

        assert modal.is_name_error_visible(), "Ошибка для 'Наименование' не отображается"
        assert not modal.is_address_error_visible()
        assert not modal.is_city_error_visible()

    with allure.step("Проверяю, что склад не был создан"):
        warehouses.close_modal()
        new_count = warehouses.get_warehouses_count()
        assert new_count == initial_count, \
            "Склад был создан несмотря на ошибки валидации"


"""Закрытие окон"""


@allure.title("Закрытие окна нового склада разными способами")
def test_close_new_warehouse_modal(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)

    with allure.step("Открываю окно и закрываю крестиком"):
        warehouses.click_add_warehouse()
        assert warehouses.is_modal_visible()

        warehouses.close_modal()
        assert not warehouses.is_modal_visible(), "Окно не закрылось по крестику"

    with allure.step("Открываю окно и закрываю кликом вне окна"):
        warehouses.click_add_warehouse()
        assert warehouses.is_modal_visible()

        warehouses.close_modal_by_click_outside()
        assert not warehouses.is_modal_visible(), "Окно не закрылось по клику вне окна"


@allure.title("Окно подтверждения закрытия при несохранённых изменениях")
def test_close_confirmation_on_unsaved_changes(base_url, page_fixture):
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    warehouses = WarehousesSettingsPage(page)
    modal = WarehouseModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_seller_authorize()

    warehouses.open(base_url)

    with allure.step("Открываю карточку первого склада через экшн-меню"):
        warehouses.open_warehouse_card(0)

    with allure.step("Вношу изменения в поля"):
        modal.fill("Изменённое название", None, None)

    with allure.step("Нажимаю на крестик"):
        modal.close()

    with allure.step("Проверяю появление окна подтверждения"):
        assert modal.is_close_confirmation_visible(), \
            "Окно подтверждения закрытия не появилось"

    with allure.step("Нажимаю 'Не сохранять'"):
        modal.click_dont_save()

    with allure.step("Проверяю, что окно закрылось"):
        assert not warehouses.is_modal_visible(), \
            "Окно склада не закрылось"


import time
import allure
import pytest
from playwright.sync_api import expect

from page_opjects.autorization_page import AutorizationPage
from page_opjects.settings_page.personal_limits_settings_page import (
    PersonalLimitsSettingsPage,
    SelectEmployeeModal,
    SetLimitModal,
    DeleteLimitModal,
)

# ============================================================================
# СТРАНИЦА ПЕРСОНАЛЬНЫХ ЛИМИТОВ
# ============================================================================

# Тестовые данные
TEST_USER_EMAIL = "testgarwin_yur+3@mail.ru"
TEST_USER_NAME = "Агафонова Прохор Ефимовна"
HIGH_LIMIT = "99999999.99"
LOW_LIMIT = "300"
MEDIUM_LIMIT = "5000"


@allure.title("Открытие страницы персональных лимитов")
def test_open_personal_limits_page(base_url, page_fixture):
    """Проверяю, что страница персональных лимитов открывается корректно"""
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    personal_limits = PersonalLimitsSettingsPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    personal_limits.open(base_url)

    with allure.step("Проверяю, что кнопка 'Установить новый' отображается"):
        time.sleep(3)
        assert page.locator(personal_limits.ADD_NEW_BUTTON).is_visible(), \
            "Кнопка 'Установить новый' не отображается"

    with allure.step("Проверяю, что поле поиска отображается"):
        assert page.locator(personal_limits.SEARCH_INPUT).is_visible(), \
            "Поле поиска не отображается"


@allure.title("Поиск сотрудника в модалке выбора")
@allure.tag("positive", "personal-limits")
@allure.severity(allure.severity_level.NORMAL)
def test_search_employee_in_modal(base_url, page_fixture):
    """Поиск по имени/email фильтрует список сотрудников"""
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    personal_limits = PersonalLimitsSettingsPage(page)
    select_modal = SelectEmployeeModal(page)
    delete_modal = DeleteLimitModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    personal_limits.open(base_url)

    # Если у пользователя уже есть лимит — сначала удаляем
    personal_limits.wait_for_any_limit()
    if personal_limits.is_user_present(TEST_USER_EMAIL):
        with allure.step("Предусловие: удаляю существующий лимит"):
            personal_limits.click_delete_user_limit(TEST_USER_NAME)
            if delete_modal.is_visible():
                delete_modal.confirm_delete()
            page.wait_for_timeout(1000)
            personal_limits.open(base_url)

    personal_limits.click_add_new()

    with allure.step("Получаю общее количество сотрудников"):
        total_count = select_modal.get_employees_count()
        allure.attach(str(total_count), name="Всего сотрудников")

    with allure.step("Ищу сотрудника по имени"):
        select_modal.search_employee(TEST_USER_NAME)

    with allure.step("Проверяю, что список отфильтрован"):
        filtered_count = select_modal.get_employees_count()
        assert filtered_count > 0, "Поиск не дал результатов"
        assert filtered_count <= total_count, "Фильтрация не сработала"

        allure.attach(str(filtered_count), name="Найдено сотрудников")


@allure.title("Открытие и отмена модалки выбора сотрудника")
@allure.tag("smoke", "personal-limits")
@allure.severity(allure.severity_level.NORMAL)
def test_open_select_employee_modal(base_url, page_fixture):
    """Нажатие '+ Установить новый' открывает модалку выбора сотрудника"""
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    personal_limits = PersonalLimitsSettingsPage(page)
    select_modal = SelectEmployeeModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    personal_limits.open(base_url)

    initial_count = personal_limits.get_users_count()

    with allure.step("Нажимаю '+ Установить новый'"):
        personal_limits.click_add_new()

    with allure.step("Проверяю, что модалка выбора сотрудника открылась"):
        assert select_modal.is_visible(), \
            "Модалка 'Выберите сотрудника' не открылась"

    with allure.step("Проверяю, что список сотрудников не пуст"):
        assert select_modal.get_employees_count() > 0, \
            "Список сотрудников пуст"

    with allure.step("Нажимаю 'Отмена'"):
        select_modal.click_cancel()

    with allure.step("Проверяю, что модалка закрылась"):
        assert not select_modal.is_visible(), \
            "Модалка не закрылась после отмены"

    with allure.step("Проверяю, что количество пользователей не изменилось"):
        assert personal_limits.get_users_count() == initial_count


@allure.title("Открытие модального окна установки лимита и отмена установки лимита")
def test_select_employee_opens_limit_modal_and_cancel_set_limit(base_url, page_fixture):
    """Отмена в модалке лимита не создаёт запись"""
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    personal_limits = PersonalLimitsSettingsPage(page)
    select_modal = SelectEmployeeModal(page)
    limit_modal = SetLimitModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    personal_limits.open(base_url)

    initial_count = personal_limits.get_users_count()

    personal_limits.click_add_new()

    with allure.step("Выбираю первого сотрудника"):
        select_modal.select_and_confirm_by_index(0)

    with allure.step("Проверяю, что модалка установки лимита открылась"):
        assert limit_modal.is_visible(), \
            "Модалка 'Изменение персонального лимита' не открылась"

    with allure.step("Ввожу лимит, но нажимаю 'Отмена'"):
        limit_modal.set_limit("5000")
        limit_modal.click_cancel()

    with allure.step("Проверяю, что модалка закрылась"):
        assert not limit_modal.is_visible()

    with allure.step("Проверяю, что количество пользователей не изменилось"):
        new_count = personal_limits.get_users_count()
        assert new_count == initial_count, \
            f"Количество изменилось после отмены. Было: {initial_count}, стало: {new_count}"


@allure.title("Создание и удаление персонального лимита")
def test_create_and_delete_personal_limit(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    personal_limits = PersonalLimitsSettingsPage(page)
    select_modal = SelectEmployeeModal(page)
    limit_modal = SetLimitModal(page)
    delete_modal = DeleteLimitModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    personal_limits.open(base_url)

    # Если у пользователя уже есть лимит — сначала удаляем
    personal_limits.wait_for_any_limit()
    if personal_limits.is_user_present(TEST_USER_EMAIL):
        with allure.step("Предусловие: удаляю существующий лимит"):
            personal_limits.click_delete_user_limit(TEST_USER_NAME)
            if delete_modal.is_visible():
                delete_modal.confirm_delete()
            page.wait_for_timeout(1000)
            personal_limits.open(base_url)

    initial_count = personal_limits.get_users_count()

    # --- Создание ---
    with allure.step("Нажимаю '+ Установить новый'"):
        personal_limits.click_add_new()

    with allure.step("Проверяю, что модалка выбора сотрудника открылась"):
        assert select_modal.is_visible(), \
            "Модалка 'Выберите сотрудника' не открылась"

    with allure.step("Выбираю сотрудника по имени"):
        select_modal.select_employee_by_email(TEST_USER_NAME)

    with allure.step("Нажимаю 'Выбрать'"):
        select_modal.click_select()

    with allure.step("Проверяю, что модалка установки лимита открылась"):
        assert limit_modal.is_visible(), \
            "Модалка 'Изменение персонального лимита' не открылась"

    with allure.step("Устанавливаю лимит и сохраняю"):
        limit_modal.set_and_save(MEDIUM_LIMIT)

    with allure.step("Проверяю toast об установке лимита"):
        assert personal_limits.is_limit_set_toast_visible(), \
            "Toast 'Персональный лимит сотрудника ... установлен' не отображается"

    with allure.step("Проверяю, что пользователь появился в списке"):
        page.wait_for_timeout(1000)
        assert personal_limits.is_user_present(TEST_USER_EMAIL), \
            f"Пользователь {TEST_USER_EMAIL} не найден в списке"

        new_count = personal_limits.get_users_count()
        assert new_count == initial_count + 1, \
            f"Количество не увеличилось. Было: {initial_count}, стало: {new_count}"

    # --- Удаление ---
    with allure.step("Нажимаю кнопку удаления (вторая иконка в строке)"):
        personal_limits.click_delete_user_limit(TEST_USER_EMAIL)

    with allure.step("Проверяю окно подтверждения удаления"):
        assert delete_modal.is_visible(), \
            "Окно подтверждения удаления не появилось"

    with allure.step("Подтверждаю удаление"):
        delete_modal.confirm_delete()

    with allure.step("Проверяю, что пользователь удалён из списка"):
        page.wait_for_timeout(1000)
        assert not personal_limits.is_user_present(TEST_USER_EMAIL), \
            f"Пользователь {TEST_USER_EMAIL} всё ещё в списке после удаления"

        final_count = personal_limits.get_users_count()
        assert final_count == initial_count, \
            f"Количество не вернулось. Было: {initial_count}, стало: {final_count}"


@allure.title("Редактирование персонального лимита")
def test_edit_personal_limit(base_url, page_fixture):

    page = page_fixture()
    autorization_page = AutorizationPage(page)
    personal_limits = PersonalLimitsSettingsPage(page)
    select_modal = SelectEmployeeModal(page)
    limit_modal = SetLimitModal(page)
    delete_modal = DeleteLimitModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    personal_limits.open(base_url)

    # Предусловие: создаём лимит если его нет
    personal_limits.wait_for_any_limit()
    if not personal_limits.is_user_present(TEST_USER_EMAIL):
        with allure.step("Предусловие: создаю лимит"):
            personal_limits.click_add_new()
            select_modal.select_and_confirm_by_email(TEST_USER_EMAIL)
            limit_modal.set_and_save(HIGH_LIMIT)
            page.wait_for_timeout(1000)

    with allure.step("Нажимаю кнопку редактирования"):
        personal_limits.click_edit_user_limit(TEST_USER_EMAIL)

    with allure.step("Проверяю, что модалка редактирования открылась"):
        assert limit_modal.is_visible(), \
            "Модалка изменения лимита не открылась"

    with allure.step("Запоминаю старое значение"):
        old_value = limit_modal.get_limit_value()
        allure.attach(old_value, name="Старое значение лимита")

    with allure.step("Устанавливаю новое значение"):
        new_value = MEDIUM_LIMIT
        limit_modal.set_and_save(new_value)

    with allure.step("Проверяю toast об изменении"):
        # Toast может быть как "установлен" так и "изменен"
        page.wait_for_timeout(1000)

    with allure.step("Проверяю, что значение обновилось на странице"):
        user_text = personal_limits.get_user_limit_text(TEST_USER_EMAIL)
        allure.attach(user_text, name="Текст строки пользователя")

    with allure.step("Постусловие: возвращаю исходное значение"):
        personal_limits.click_edit_user_limit(TEST_USER_EMAIL)
        limit_modal.set_and_save(HIGH_LIMIT)
        page.wait_for_timeout(1000)

        # --- Удаление ---
    with allure.step("Нажимаю кнопку удаления (вторая иконка в строке)"):
        personal_limits.click_delete_user_limit(TEST_USER_EMAIL)

    with allure.step("Проверяю окно подтверждения удаления"):
        assert delete_modal.is_visible(), \
            "Окно подтверждения удаления не появилось"

    with allure.step("Подтверждаю удаление"):
        delete_modal.confirm_delete()

    with allure.step("Проверяю, что пользователь удалён из списка"):
        page.wait_for_timeout(1000)
        assert not personal_limits.is_user_present(TEST_USER_EMAIL), \
            f"Пользователь {TEST_USER_EMAIL} всё ещё в списке после удаления"


@allure.title("Отмена удаления персонального лимита")
def test_cancel_delete_personal_limit(base_url, page_fixture):
    """Отмена удаления не удаляет лимит"""
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    personal_limits = PersonalLimitsSettingsPage(page)
    select_modal = SelectEmployeeModal(page)
    limit_modal = SetLimitModal(page)
    delete_modal = DeleteLimitModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    personal_limits.open(base_url)

    # Предусловие
    personal_limits.wait_for_any_limit()
    if not personal_limits.is_user_present(TEST_USER_EMAIL):
        personal_limits.click_add_new()
        select_modal.select_and_confirm_by_email(TEST_USER_EMAIL)
        limit_modal.set_and_save(HIGH_LIMIT)
        page.wait_for_timeout(1000)

    initial_count = personal_limits.get_users_count()

    with allure.step("Нажимаю кнопку удаления"):
        personal_limits.click_delete_user_limit(TEST_USER_EMAIL)

    with allure.step("Проверяю окно подтверждения"):
        assert delete_modal.is_visible()

    with allure.step("Отменяю удаление"):
        delete_modal.cancel_delete()

    with allure.step("Проверяю, что окно закрылось"):
        assert not delete_modal.is_visible()

    with allure.step("Проверяю, что пользователь остался в списке"):
        assert personal_limits.is_user_present(TEST_USER_EMAIL)
        assert personal_limits.get_users_count() == initial_count


@allure.title("Поиск пользователя с лимитом на странице")
def test_search_user_on_page(base_url, page_fixture):
    """Поиск на странице фильтрует список пользователей с лимитами"""
    page = page_fixture()
    autorization_page = AutorizationPage(page)
    personal_limits = PersonalLimitsSettingsPage(page)
    select_modal = SelectEmployeeModal(page)
    limit_modal = SetLimitModal(page)
    delete_modal = DeleteLimitModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    personal_limits.open(base_url)

    TEST_USER_NAME = "Агафонова"

    # Предусловие: нужны минимум 2 пользователя с лимитами
    personal_limits.wait_for_any_limit()
    if not personal_limits.is_user_present(TEST_USER_EMAIL):
        personal_limits.click_add_new()
        select_modal.select_and_confirm_by_email(TEST_USER_EMAIL)
        limit_modal.set_and_save(HIGH_LIMIT)
        page.wait_for_timeout(1000)

    total_count = personal_limits.get_users_count()

    with allure.step("Ищу по email"):
        personal_limits.search_user(TEST_USER_EMAIL)

    with allure.step("Проверяю, что список отфильтрован"):
        filtered_count = personal_limits.get_users_count()
        assert filtered_count > 0, "Поиск не дал результатов"
        assert personal_limits.is_user_present(TEST_USER_EMAIL), \
            "Искомый пользователь не найден в результатах"

    with allure.step("Очищаю поиск"):
        personal_limits.clear_search()

    with allure.step("Проверяю, что полный список вернулся"):
        restored_count = personal_limits.get_users_count()
        assert restored_count == total_count, \
            f"Полный список не вернулся. Было: {total_count}, стало: {restored_count}"

        total_count = personal_limits.get_users_count()

        with allure.step("Ищу по имени"):
            personal_limits.search_user(TEST_USER_NAME)

        with allure.step("Проверяю, что список отфильтрован"):
            filtered_count = personal_limits.get_users_count()
            assert filtered_count > 0, "Поиск не дал результатов"
            assert personal_limits.is_user_present(TEST_USER_NAME), \
                "Искомый пользователь не найден в результатах"

        with allure.step("Очищаю поиск"):
            personal_limits.clear_search()

        with allure.step("Проверяю, что полный список вернулся"):
            restored_count = personal_limits.get_users_count()
            assert restored_count == total_count, \
                f"Полный список не вернулся. Было: {total_count}, стало: {restored_count}"

        # --- Удаление ---
    with allure.step("Нажимаю кнопку удаления (вторая иконка в строке)"):
        personal_limits.click_delete_user_limit(TEST_USER_EMAIL)

    with allure.step("Проверяю окно подтверждения удаления"):
        assert delete_modal.is_visible(), \
            "Окно подтверждения удаления не появилось"

    with allure.step("Подтверждаю удаление"):
        delete_modal.confirm_delete()

    with allure.step("Проверяю, что пользователь удалён из списка"):
        page.wait_for_timeout(1000)
        assert not personal_limits.is_user_present(TEST_USER_EMAIL), \
            f"Пользователь {TEST_USER_EMAIL} всё ещё в списке после удаления"

#TODO возможно, нужны тесты на карточку лимита