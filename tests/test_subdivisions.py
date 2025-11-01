import random
import re
import time
import allure
from faker import Faker
from playwright.sync_api import expect
from page_opjects.autorization_page import AutorizationPage
from page_opjects.cart_page import CartPage
from page_opjects.listing_page import ListingPage
from page_opjects.settings_page.subdivisions_page.subdivisions_settings_page import (
    SubdivisionsSettingsPage,
    SubdivisionModal,
    SubdivisionUsersPage, AddUserToSubdivisionModal, SubdivisionUserCard, SubdivisionAddressesPage, AddressModal,

)
from page_opjects.settings_page.users_settings_page import UsersSettingsPage, UserModal

fake = Faker('ru_RU')

"""Тесты страницы Подразделения"""

"""Тесты виджета Подразделения"""

@allure.title("Открытие окна нового подразделения")
def test_open_new_subdivision_modal(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)

    with allure.step("Нажимаю на крестик для добавления подразделения"):
        subdivisions.click_add_subdivision_button()

    with allure.step("Проверяю, что окно нового подразделения отображается"):
        assert page.locator(SubdivisionModal.MODAL).is_visible()


@allure.title("Отображение экшн меню подразделения")
def test_action_menu_display(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)

    with allure.step("Открываю список подразделенией"):
        subdivisions.click_subdivision_list_button()

    with allure.step("Навожу на экшн меню"):
        subdivisions.hover_action_menu(0)

    with allure.step("Проверяю, что экшн меню отображается"):
        assert page.locator(subdivisions.DELETE_OPTION).is_visible()


@allure.title("Открытие страницы настроек подразделения")
def test_open_subdivision_settings(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)

    with allure.step("Открываю список подразделенией"):
        subdivisions.click_subdivision_list_button()

    with allure.step("Открываю подразделение"):
        subdivisions.open_subdivision(0)

    with allure.step("Проверяю, что страница настроек подразделения отображается"):
        expect(page).to_have_url(re.compile(r".*/subdivision/\d+.*"))


@allure.title("Редактирование названия подразделения")
def test_edit_subdivision_name(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    modal = SubdivisionModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)

    with allure.step("Открываю список подразделенией"):
        subdivisions.click_subdivision_list_button()

    subdivisions.open_subdivision(0)

    with allure.step("Нажимаю на карандаш редактирования названия"):
        subdivisions.click_edit_name_button()

    with allure.step("Отображается окно редактирования названия"):
        assert page.locator(modal.MODAL_EDIT).is_visible()

    with allure.step("Ввожу новое название и сохраняю"):
        new_name = subdivisions.generate_unique_subdivision_name(prefix="Тестовое подразделение")
        subdivisions.fill_subdivision_name(new_name)
        subdivisions.click_save()

    with allure.step("Проверяю новое название на странице"):
        subdivisions.assert_subdivision_name_equals(new_name)


@allure.title("Переход по вкладкам настроек подразделения")
def test_navigate_subdivision_tabs(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)

    with allure.step("Проверяю, что нахожусь в настройках подразделения"):
        expect(page).to_have_url(re.compile(r".*/general"))
        expect(page.request.get(page.url)).to_be_ok()

    with allure.step("Переключаюсь на вкладку Пользователи"):
        subdivisions.click_users_tab()
        expect(page).to_have_url(re.compile(r".*/user-list"))
        expect(page.request.get(page.url)).to_be_ok()

    with allure.step("Переключаюсь на вкладку Адреса"):
        subdivisions.click_addresses_tab()
        expect(page).to_have_url(re.compile(r".*/address-list"))
        expect(page.request.get(page.url)).to_be_ok()


@allure.title("Открытие окна подтверждения удаления подразделения")
def test_open_delete_confirmation(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)

    subdivisions.click_subdivision_list_button()

    with allure.step("Навожу на экшн меню и нажимаю Удалить"):
        subdivisions.hover_action_menu(0)
        subdivisions.click_delete_option()

    with allure.step("Проверяю, что окно подтверждения удаления отображается"):
        assert page.locator("text=Вы уверены").is_visible()


"""Тесты окна нового подразделения"""


@allure.title("Обязательность поля Название при создании подразделения")
def test_subdivision_name_required(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    modal = SubdivisionModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_add_subdivision_button()

    with allure.step("Не вводя название, нажимаю Сохранить"):
        modal.click_save()

    with allure.step("Проверяю отображение подсказки об обязательном поле"):
        assert page.locator(modal.NAME_TIP).get_by_text("Обязательное поле при сохранении").is_visible()


@allure.title("Создание и удаление нового подразделения с заполнением всех полей")
def test_create_new_subdivision(base_url, page_fixture, delete_subdivision_fixture):

    mark_subdivision_created, mark_subdivision_deleted = delete_subdivision_fixture

    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    modal = SubdivisionModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_add_subdivision_button()

    with allure.step("Заполняю все поля корректными данными"):
        new_name = f"Автотест подразделение {random.randint(0, 999999)}"
        modal.fill_all_fields(new_name, 0, 0)

    with allure.step("Сохраняю подразделение"):
        modal.click_save()

    with allure.step("Проверяю, что подразделение создано"):
        print(new_name)
        assert page.locator("text=Новое подразделение добавлено в аккаунт").is_visible()
        assert page.locator(f"text={new_name}").first.is_visible()

        mark_subdivision_created()

    initial_count = subdivisions.get_subdivision_cards().count()

    with allure.step("Открываю экшн меню и нажимаю Удалить"):
        subdivisions.hover_action_menu(0)
        subdivisions.click_delete_option()

    with allure.step("Подтверждаю удаление"):
        modal.confirm_delete()

    with allure.step("Проверяю, что подразделение удалено"):
        page.wait_for_timeout(2000)
        new_count = subdivisions.get_subdivision_cards().count()
        assert new_count < initial_count
        mark_subdivision_deleted()


"""Тесты настроек подразделения"""


@allure.title("Редактирование настроек подразделения")
def test_edit_subdivision_settings(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    page.goto("https://sprout-store.ru/settings/subdivision/153/general")

    with allure.step("Выбираю юридическое лицо"):
        subdivisions.select_legal_entity()
        assert page.locator("text=Подразделение успешно изменено").is_visible()

    with allure.step("Выбираю руководителя"):
        subdivisions.select_head()
        assert page.locator("text=Подразделение успешно изменено").is_visible()

    with allure.step("Выбираю менеджера по закупкам"):
        subdivisions.select_manager()
        assert page.locator("text=Подразделение успешно изменено").is_visible()

    with allure.step("Ввожу код подразделения"):
        subdivisions.fill_code(f"TEST{random.randint(0, 999)}")
        assert page.locator("text=Подразделение успешно изменено").is_visible()


@allure.title("Добавление и удаление дочернего подразделения")
def test_add_and_deletion_child_subdivision(base_url, page_fixture, delete_child_subdivision_fixture):

    mark_subdivision_created, mark_subdivision_deleted = delete_child_subdivision_fixture

    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    modal = SubdivisionModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)

    with allure.step("Нажимаю Дочернее подразделение"):
        subdivisions.click_add_child_subdivision()

    with allure.step("Заполняю все поля корректными данными"):
        new_name = f"Автотест подразделение {random.randint(0, 999999)}"
        modal.fill_all_fields_for_child_subdivision(new_name, 0, 0)

    with allure.step("Сохраняю подразделение"):
        modal.click_save_child_subdivision()

    with allure.step("Проверяю, что подразделение создано"):
        print(new_name)
        assert page.locator("text=Новое подразделение добавлено в аккаунт.").is_visible()
        time.sleep(1)
        assert page.locator(f"text={new_name}").first.is_visible()

        mark_subdivision_created(new_name)

    with allure.step("Открываю экшн меню и нажимаю Удалить"):
        subdivisions.hover_action_menu_child_subdivision(new_name, 0)
        subdivisions.click_delete_option()

    with allure.step("Подтверждаю удаление"):
        modal.confirm_delete()

    with allure.step("Проверяю, что подразделение удалено"):
        page.wait_for_timeout(2000)
        time.sleep(3)
        assert not page.locator(f"text={new_name}").first.is_visible()
        mark_subdivision_deleted()


@allure.title("Открытие окна удаления подразделения из настроек")
def test_open_delete_from_settings(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)

    with allure.step("Нажимаю Удалить подразделение"):
        subdivisions.click_delete_subdivision()

    with allure.step("Проверяю, что окно подтверждения удаления открыто"):
        assert page.locator("text=Вы уверены").is_visible()


@allure.title("Проверка работы лимита расходов на закупку")
def test_purchase_limit_in_cart(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    page.goto(f"{base_url}/settings/subdivision/134/general")

    with allure.step("Устанавливаю лимит"):
        subdivisions.set_purchase_limit("300")
    page.mouse.click(0, 0)

    with allure.step("Добавляю в корзину товар дороже лимита"):
        page.goto(base_url + "/catalog/9/3707")
        listing.add_expensive_item_to_cart(min_price=350)  # подбирает 1 товар с ценой > 300

    cart.open(base_url)

    with allure.step("Проверяю, что кнопка Отправить заказ недоступна"):
        expect(page.locator(cart.SEND_BUTTON)).not_to_be_visible()
    with allure.step("Отображается плашка 'Ваш заказ превышает доступный лимит на покупки'"):
        expect(page.locator(cart.LIMIT_EXCEEDED_BANNER_2)).not_to_be_hidden(timeout=5000)

    with allure.step("Устанавливаю лимит выше стоимости добавленого товара"):
        page.goto(f"{base_url}/settings/subdivision/134/general")
        subdivisions.set_purchase_limit("100000")
        page.mouse.click(0, 0)

    cart.open(base_url)

    with allure.step("Проверяю, что кнопка Отправить заказ доступна"):
        page.wait_for_selector(cart.SEND_BUTTON, timeout=5000)
        expect(page.locator(cart.SEND_BUTTON)).to_be_enabled()
    with allure.step("Плашка 'Ваш заказ превышает доступный лимит на покупки' не отображается"):
        expect(page.locator(cart.LIMIT_EXCEEDED_BANNER_2)).to_be_hidden(timeout=5000)


@allure.title("Проверка работы лимита цены на товар")
def test_item_price_limit_in_cart(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    page.goto(f"{base_url}/settings/subdivision/134/general")

    with allure.step("Устанавливаю лимит"):
        subdivisions.set_item_price_limit("300")
    page.mouse.click(0, 0)

    with allure.step("Добавляю в корзину товар дороже лимита"):
        page.goto(base_url + "/catalog/9/3707")
        listing.add_expensive_item_to_cart(min_price=350)  # подбирает 1 товар с ценой > 300

    cart.open(base_url)

    with allure.step("Проверяю, что кнопка Отправить заказ недоступна"):
        expect(page.locator(cart.SEND_BUTTON)).to_be_disabled()
    with allure.step("Отображается плашка 'Стоимость позиции превышает допустимый лимит на цену товара'"):
        expect(page.locator(cart.LIMIT_EXCEEDED_BANNER)).not_to_be_hidden(timeout=5000)

    with allure.step("Устанавливаю лимит выше стоимости добавленого товара"):
        page.goto(f"{base_url}/settings/subdivision/134/general")
        subdivisions.set_item_price_limit("100000")
        page.mouse.click(0, 0)

    cart.open(base_url)

    with allure.step("Проверяю, что кнопка Отправить заказ доступна"):
        page.wait_for_selector(cart.SEND_BUTTON, timeout=5000)
        expect(page.locator(cart.SEND_BUTTON)).to_be_enabled()
    with allure.step("Плашка 'Стоимость позиции превышает допустимый лимит на цену товара' не отображается"):
        expect(page.locator(cart.LIMIT_EXCEEDED_BANNER)).to_be_hidden(timeout=5000)


"""Тесты страницы Пользователи подразделения"""


@allure.title("Открытие окна добавления пользователя через иконку +")
def test_open_add_user_modal_icon(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    users_page = SubdivisionUsersPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_users_tab()

    with allure.step("Нажимаю на +"):
        users_page.click_add_user_icon()

    with allure.step("Проверяю, что окно добавления пользователя открыто"):
        assert page.locator(AddUserToSubdivisionModal.MODAL).is_visible()

@allure.title("Открытие окна добавления пользователя через кнопку Добавить пользователя")
def test_open_add_user_modal_button(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    users_page = SubdivisionUsersPage(page)
    autorization_page = AutorizationPage(page)
    user_card = SubdivisionUserCard(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    page.goto(f"{base_url}/settings/subdivision/137/general")
    subdivisions.click_users_tab()

    with allure.step("Удаляю пользователей пока не появится кнопка"):
        initial_count = users_page.get_user_cards().count()

        while initial_count > 0:
            with allure.step(f"Удаляю пользователя. Осталось: {initial_count}"):
                users_page.open_user_card(0)

                with allure.step("Проверяю, что карточка отображается"):
                    assert page.locator(SubdivisionUserCard.MODAL).is_visible()

                with allure.step("Отвязываю пользователя"):
                    user_card.click_unbind()

                with allure.step("Проверяю, что пользователь отвязан"):
                    page.wait_for_timeout(2000)
                    new_count = users_page.get_user_cards().count()
                    assert new_count < initial_count

                initial_count = new_count  # пересчитываем количество оставшихся пользователей

    with allure.step("Нажимаю Добавить пользователя"):
        users_page.click_add_user_button()

    with allure.step("Проверяю, что окно добавления пользователя открыто"):
        assert page.locator(AddUserToSubdivisionModal.MODAL).is_visible()

@allure.title("Добавление пользователя в подразделение и его отвязка")
def test_add_user_to_subdivision_and_unbind(base_url, page_fixture, unbind_user_fixture):

    mark_user_created, mark_user_deleted = unbind_user_fixture
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    users_page = SubdivisionUsersPage(page)
    add_modal = AddUserToSubdivisionModal(page)
    autorization_page = AutorizationPage(page)
    user_card = SubdivisionUserCard(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_users_tab()

    initial_count = users_page.get_user_cards().count()

    with allure.step("Добавляю пользователя"):
        users_page.click_add_user_icon()
        add_modal.select_user(0)
        add_modal.click_add()

    with allure.step("Проверяю, что пользователь добавлен"):
        page.wait_for_timeout(2000)
        new_count = users_page.get_user_cards().count()
        assert new_count > initial_count
        mark_user_created()

        initial_count = users_page.get_user_cards().count()

        users_page.open_user_card(0)

        with allure.step("Проверяю, что карточка отображается"):
            assert page.locator(SubdivisionUserCard.MODAL).is_visible()

        with allure.step("Отвязываю пользователя"):
            user_card.click_unbind()

        with allure.step("Проверяю, что пользователь отвязан"):
            page.wait_for_timeout(2000)
            new_count = users_page.get_user_cards().count()
            assert new_count < initial_count

            mark_user_deleted()


@allure.title("Назначение ролей пользователю в подразделении")
def test_assign_roles_to_user(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    users_page = SubdivisionUsersPage(page)
    user_card = SubdivisionUserCard(page)
    autorization_page = AutorizationPage(page)

    page_user = page_fixture()
    page_user_2 = page_fixture()
    autorization_user = AutorizationPage(page_user)
    autorization_user_2 = AutorizationPage(page_user_2)

    modal_admin = UserModal(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    page.goto("https://sprout-store.ru/settings/subdivision/138/user-list")
    users_page.open_user_card(0)

    with allure.step("Проверяю что у пользователя нет прав администратора, если есть отключаю"):
        with allure.step("Открываю окно ролей"):
            user_card.click_role_button()
            modal_admin.disable_admin_role()

    with allure.step("Вхожу как обычный пользователь"):
        autorization_user.open(base_url)
        autorization_user.test_buyer_for_admin_role_authorize()
        page_user.goto("https://sprout-store.ru/settings/account/user-list")
        time.sleep(2)
        assert not page_user.url == "https://sprout-store.ru/settings/account/user-list"

    with allure.step("Открыть карточку нужного пользователя по email и задаю роль администратора"):
        modal_admin.set_admin_role()

    with allure.step("Вхожу как обычный пользователь"):
        autorization_user_2.open(base_url)
        autorization_user_2.test_buyer_for_admin_role_authorize()
        page_user_2.goto("https://sprout-store.ru/settings/account/user-list")
        time.sleep(2)
        assert page_user_2.url == "https://sprout-store.ru/settings/account/user-list"


@allure.title("Открытие окна редактирования пользователя из подразделения")
def test_open_edit_user_from_subdivision(base_url, page_fixture):

    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    users_page = SubdivisionUsersPage(page)
    user_card = SubdivisionUserCard(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_users_tab()
    users_page.open_user_card(0)

    with allure.step("Нажимаю Редактировать"):
        user_card.click_edit()

    with allure.step("Проверяю, что окно редактирования открыто"):
        assert page.locator("text=Редактировать данные").is_visible()


@allure.title("Подтверждение добаления пользователя который есть в другом подразделениии")
def test_confirmation_of_adding_a_user_from_another_subdivisions(base_url, page_fixture, unbind_user_fixture):

    mark_user_created, mark_user_deleted = unbind_user_fixture

    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    users_page = SubdivisionUsersPage(page)
    add_modal = AddUserToSubdivisionModal(page)
    autorization_page = AutorizationPage(page)
    user_card = SubdivisionUserCard(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_users_tab()

    with allure.step("Добавляю пользователей пока не появится модальное окно"):
        while not page.locator("text=Добавление в подразделение").is_visible():
            users_page.click_add_user_icon()
            add_modal.select_user(0)
            add_modal.click_add_without_confirm()

            try:
                page.wait_for_selector("text=Добавление в подразделение", timeout=2000)
            except Exception:
                pass

    with allure.step("Проверяю отображение окна подтверждения добавления"):
        assert page.locator("text=Добавление в подразделение").is_visible()

        add_modal.click_cancel_button()

    with allure.step("Проверяю, что окно подтверждения добавления больше не отображается"):
        assert not page.locator("text=Добавление в подразделение").is_visible()

        initial_count = users_page.get_user_cards().count()
        users_page.click_add_user_icon()
        add_modal.select_user(0)
        add_modal.click_add()
        new_count = users_page.get_user_cards().count()
        assert initial_count < new_count

        mark_user_created()

        initial_count = users_page.get_user_cards().count()

        users_page.open_user_card(0)

        with allure.step("Проверяю, что карточка отображается"):
            assert page.locator(SubdivisionUserCard.MODAL).is_visible()

        # with allure.step("Отвязываю пользователя"):
        #     user_card.click_unbind()

        with allure.step("Проверяю, что пользователь отвязан"):
            page.wait_for_timeout(2000)
            new_count = users_page.get_user_cards().count()
            assert new_count < initial_count

            mark_user_deleted()


"""Тесты страницы Адреса доставки"""


@allure.title("Открытие окна добавления нового адреса")
def test_open_add_address_modal(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    addresses_page = SubdivisionAddressesPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_addresses_tab()

    with allure.step("Нажимаю Добавить адрес"):
        addresses_page.click_add_address()

    with allure.step("Проверяю, что окно добавления адреса открыто"):
        assert page.locator(AddressModal.MODAL).is_visible()


@allure.title("Создание нового адреса доставки")
def test_create_and_delete_new_address(base_url, page_fixture, delete_adress_fixture):
    mark_adress_created, mark_adress_deleted = delete_adress_fixture
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    addresses_page = SubdivisionAddressesPage(page)
    address_modal = AddressModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_addresses_tab()

    addresses_page.click_add_address()
    address = fake.address()
    city = fake.city()
    postcode = fake.postcode()

    with allure.step("Заполняю все поля адреса"):
        address_modal.fill_all_fields(f"{address}", f"{city}", f"{postcode}")

    with allure.step("Добавляю адрес"):
        address_modal.click_add()

    with allure.step("Проверяю, что адрес добавлен"):
        assert page.locator(f"text={address}").is_visible()

    mark_adress_created()

    old_adress_count = addresses_page.get_address_cards().count()

    with allure.step("Открываю меню и выбираю Удалить"):
        addresses_page.hover_address_action_menu(0)
        addresses_page.click_delete_option()

    with allure.step("Проверяю, что окно подтверждения удаления открыто"):
        assert page.locator("text=Вы уверены").is_visible()

    with allure.step("Подтверждаю удаление"):
        addresses_page.confirm_delete()

    new_adress_count = addresses_page.get_address_cards().count()
    assert old_adress_count > new_adress_count

    mark_adress_deleted()


@allure.title("Отображение экшн меню адреса")
def test_address_action_menu(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    addresses_page = SubdivisionAddressesPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_addresses_tab()

    with allure.step("Навожу на экшн меню адреса"):
        addresses_page.hover_address_action_menu(0)

    with allure.step("Проверяю отображение опций меню"):
        assert page.locator(addresses_page.EDIT_OPTION).is_visible()
        assert page.locator(addresses_page.DELETE_OPTION).is_visible()
        assert page.locator(addresses_page.MAKE_PRIMARY_OPTION).is_visible()


@allure.title("Открытие окна редактирования адреса")
def test_open_edit_address_modal(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    addresses_page = SubdivisionAddressesPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_addresses_tab()

    with allure.step("Открываю меню и выбираю Редактировать"):
        addresses_page.hover_address_action_menu(0)
        addresses_page.click_edit_option()

    with allure.step("Проверяю, что окно редактирования открыто"):
        assert page.locator(AddressModal.MODAL).is_visible()


@allure.title("Открытие окна подтверждения удаления адреса")
def test_open_delete_address_confirmation(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    addresses_page = SubdivisionAddressesPage(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_addresses_tab()

    with allure.step("Открываю меню и выбираю Удалить"):
        addresses_page.hover_address_action_menu(0)
        addresses_page.click_delete_option()

    with allure.step("Проверяю, что окно подтверждения удаления открыто"):
        assert page.locator("text=Вы уверены").is_visible()


@allure.title("Установка основного адреса доставки")
def test_set_primary_address(base_url, page_fixture):
    # Инициализация страниц
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    addresses_page = SubdivisionAddressesPage(page)
    cart = CartPage(page)
    listing = ListingPage(page)
    autorization_page = AutorizationPage(page)

    # Авторизация
    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()

    # Добавление товара в корзину
    with allure.step("Добавляю товар в корзину"):
        listing.open_url(f"{base_url}/catalog/9/3707")
        listing.add_expensive_item_to_cart(min_price=100)

    # Переход на страницу настроек подразделения
    page.goto(f"{base_url}/settings/subdivision/134/general")
    subdivisions.click_addresses_tab()

    # Получение текущего основного адреса
    with allure.step("Получаю текущий основной адрес"):
        old_primary = addresses_page.find_current_primary_address()
        old_main_address = old_primary['text']
        old_main_index = old_primary['index']
        allure.attach(old_main_address, name="Старый основной адрес", attachment_type=allure.attachment_type.TEXT)

    # Получение первого не основного адреса
    with allure.step("Нахожу адрес для установки как основной"):
        new_primary = addresses_page.find_first_non_primary_address()
        new_main_index = new_primary['index']
        new_main_address = new_primary['text']
        allure.attach(new_main_address, name="Новый основной адрес", attachment_type=allure.attachment_type.TEXT)

    # Установка нового основного адреса
    with allure.step("Делаю адрес основным"):
        addresses_page.set_address_as_primary(new_main_index)
        updated_main_address = addresses_page.get_updated_address_text(new_main_index)
        assert old_main_address != updated_main_address, "Основной адрес не изменился"

    # Проверка отображения плашки
    with allure.step("Проверяю отображение плашки 'Основной адрес'"):
        addresses_page.verify_primary_badge_visible(new_main_index)

    # Проверка адреса в корзине
    with allure.step("Проверяю, что основной адрес отображается в корзине"):
        cart.open(base_url)
        cart.verify_primary_address(updated_main_address)


@allure.title("Автозаполнение адреса по подсказке")
def test_address_autocomplete(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    addresses_page = SubdivisionAddressesPage(page)
    address_modal = AddressModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_addresses_tab()
    addresses_page.click_add_address()

    with allure.step("Ввожу часть адреса"):
        address_modal.fill_address_search("Краснодонцев 13")

    time.sleep(3)

    with allure.step("Проверяю отображение подсказок"):
        assert page.locator(address_modal.SUGGESTION_ITEM).count() > 0

    with allure.step("Выбираю первую подсказку"):
        address_modal.select_first_suggestion()

    with allure.step("Проверяю автозаполнение полей"):
        expect(page.locator(address_modal.ADDRESS_INPUT)).to_contain_text('Краснодонцев')
        expect(page.locator(address_modal.ADDRESS_INPUT)).to_contain_text('13')
        assert page.locator(address_modal.ADDRESS_INPUT).input_value() != ""
        assert page.locator(address_modal.CITY_INPUT).input_value() != ""
        assert page.locator(address_modal.POSTAL_CODE_INPUT).input_value() != ""


@allure.title("Валидация обязательных полей адреса")
def test_address_required_fields_validation(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    addresses_page = SubdivisionAddressesPage(page)
    address_modal = AddressModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_addresses_tab()
    addresses_page.click_add_address()

    with allure.step("Не заполняя поля, нажимаю Добавить адрес"):
        address_modal.click_add()

    with allure.step("Проверяю отображение ошибки валидации во всех обязательных полях"):
        assert page.locator(address_modal.ADDRESS_INPUT).locator(address_modal.VALIDATION_ERROR)
        assert page.locator(address_modal.CITY_INPUT).locator(address_modal.VALIDATION_ERROR)
        assert page.locator(address_modal.POSTAL_CODE_INPUT).locator(address_modal.VALIDATION_ERROR)

    with allure.step("Заполняю только адрес и город"):
        address_modal.fill_all_fields_empty_data("")
        address_modal.fill_address("Краснодонцев 13")
        address_modal.fill_city("Череповец")
        address_modal.click_add()

    with allure.step("Проверяю, что ошибка отображается только в поле Почтовый индекс"):
        assert not page.locator(address_modal.ADDRESS_INPUT).locator(address_modal.VALIDATION_ERROR).is_visible()
        assert not page.locator(address_modal.CITY_INPUT).locator(address_modal.VALIDATION_ERROR).is_visible()
        assert page.locator(address_modal.POSTAL_CODE_INPUT).locator(address_modal.VALIDATION_ERROR)

    with allure.step("Заполняю все обязательные поля"):
        address_modal.fill_all_fields_empty_data("")
        address_modal.fill_postal_code("162600")
        address_modal.fill_address("Краснодонцев 13")
        address_modal.click_add()

    with allure.step("Проверяю, что ошибка отображается только в поле Адрес"):
        assert page.locator(address_modal.ADDRESS_INPUT).locator(address_modal.VALIDATION_ERROR)
        assert not page.locator(address_modal.CITY_INPUT).locator(address_modal.VALIDATION_ERROR).is_visible()
        assert not page.locator(address_modal.POSTAL_CODE_INPUT).locator(address_modal.VALIDATION_ERROR).is_visible()

    with allure.step("Заполняю только адрес и город"):
        address_modal.fill_all_fields_empty_data("")
        address_modal.fill_address("Краснодонцев 13")
        address_modal.fill_postal_code("162600")
        address_modal.click_add()

    with allure.step("Проверяю, что ошибка отображается только в поле Город"):
        assert not page.locator(address_modal.ADDRESS_INPUT).locator(address_modal.VALIDATION_ERROR).is_visible()
        assert page.locator(address_modal.CITY_INPUT).locator(address_modal.VALIDATION_ERROR)
        assert not page.locator(address_modal.POSTAL_CODE_INPUT).locator(address_modal.VALIDATION_ERROR).is_visible()


@allure.title("Редактирование адреса доставки")
def test_edit_address(base_url, page_fixture):
    page = page_fixture()
    subdivisions = SubdivisionsSettingsPage(page)
    addresses_page = SubdivisionAddressesPage(page)
    address_modal = AddressModal(page)
    autorization_page = AutorizationPage(page)

    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    subdivisions.open(base_url)
    subdivisions.click_subdivision_list_button()
    subdivisions.open_subdivision(0)
    subdivisions.click_addresses_tab()

    addresses_page.hover_address_action_menu(0)
    addresses_page.click_edit_option()

    with allure.step("Редактирую данные адреса"):
        address = fake.address()
        city = fake.city()
        postcode = fake.postcode()

        with allure.step("Заполняю все поля адреса"):
            address_modal.fill_all_fields(f"{address}", f"{city}", f"{postcode}")

    with allure.step("Сохраняю изменения"):
        address_modal.click_save()

    with allure.step("Проверяю, что изменения сохранены"):
        assert page.locator(f"text={address}").is_visible()
