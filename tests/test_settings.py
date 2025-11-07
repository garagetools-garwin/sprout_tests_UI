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
        new_name = modal.generate_unique_company_name(prefix="Тестовый Покупатель")
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
        assert page.locator("#kpp_help").get_by_text("Обязательное поле при сохранении").is_visible()
        assert page.locator("#name_help").get_by_text("Обязательное поле при сохранении").is_visible()

    with allure.step("ИНН обязателен к заполнению"):
        modal.fill("BoundTest", "", "123456789")
        modal.add()
        assert page.locator("#inn_help").get_by_text("Обязательное поле при сохранении").is_visible()

    with allure.step("КПП обязателен к заполнению"):
        modal.fill("BoundTest", "1234567890", "")
        modal.add()
        assert page.locator("#kpp_help").get_by_text("Обязательное поле при сохранении").is_visible()

    with allure.step("Наименование обязательно к заполнению"):
        modal.fill("", "1234567890", "123456789")
        modal.add()
        assert page.locator("#name_help").get_by_text("Обязательное поле при сохранении").is_visible()

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
        assert page.locator('text=ИНН должен быть равен 10 символам').is_visible()

    with allure.step("Проеверяю, ИНН > 10 символов"):
        modal.fill("BoundTest", "12345678901", "123456789")
        modal.add()
        assert page.locator('text=ИНН должен быть равен 10 символам').is_visible()

    with allure.step("Проеверяю, КПП < 9 символов"):
        modal.fill("BoundTest", "1234567890", "12345678")
        modal.add()
        assert page.locator('text=КПП должен быть равен 9 символам').is_visible()

    with allure.step("Проеверяю, КПП > 9 символов"):
        modal.fill("BoundTest", "1234567890", "1234567890")
        modal.add()
        assert page.locator('text=КПП должен быть равен 9 символам').is_visible()


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
        expected_kpp = page.locator('.legal-entity-card__details-table-row-container span.text-body').text_content()
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

@allure.title("Обязательность всех полей")
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

