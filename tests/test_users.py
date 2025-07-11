import os

import allure
import pytest
from playwright.sync_api import expect

from page_opjects.autorization_page import AutorizationPage
from page_opjects.home_page import HomePage
from page_opjects.settings_account_page import SettingsAccountPage


@allure.title("Приглашение пользователя и проверка активации")
def test_user_invitation(base_url, page_factory_fixture, delete_user_fixture):
    mark_user_created, mark_user_deleted = delete_user_fixture  # Получаем оба метода

    # Путь к auth_states
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auth_states_dir = os.path.join(project_root, 'auth_states')
    auth_state_path = os.path.join(auth_states_dir, "auth_state.json")

    # === Админ: создаёт пользователя ===
    admin_page = page_factory_fixture()
    autorization_page = AutorizationPage(admin_page)
    home_page = HomePage(admin_page)
    settings_account_page = SettingsAccountPage(admin_page)
    autorization_page.open(base_url)
    autorization_page.admin_buyer_authorize()
    admin_page.context.storage_state(path=auth_state_path)
    home_page.click_settings_button()
    settings_account_page.click_users_button()
    settings_account_page.add_user()

    mark_user_created()  # Сообщаем фикстуре, что пользователь создан

    admin_page.reload()

    with allure.step("Проверяем, что пользователь уже есть, но не активирован"):
        settings_account_page.click_first_user_table_row()
        notification_text = autorization_page.get_notification_text()
        assert notification_text == "Пользователь не активирован"

    # === Новый пользователь: активирует аккаунт ===
    user_page = page_factory_fixture()
    user_autorization = AutorizationPage(user_page)
    user_autorization.activate_account_directly()

    with allure.step("Проверяю, что пользователь перешел на страницу настроек профиля"):
        expect(user_page).to_have_url(f"{base_url}/profile")

    # === Админ: проверяет статус и удаляет ===
    with allure.step("Проверяем, что пользователь активирован"):
        admin_page.reload()
        settings_account_page.click_first_user_table_row()
        notification_text = autorization_page.get_notification_text()
        assert notification_text != "Пользователь не активирован"
        settings_account_page.click_close_button()

    with allure.step("Удаляем созданного пользователя"):
        settings_account_page.delete_last_created_user()
        mark_user_deleted()

    with allure.step("Проверяем, что пользователь отсутствует в списке"):
        assert not settings_account_page.is_user_present()

    with allure.step("Проверка, что по логину и паролю нельзя войти"):
        temp_page = page_factory_fixture()
        temp_auth = AutorizationPage(temp_page)
        temp_auth.open(base_url)
        temp_auth.test_buyer_authorize()
        with allure.step("Проверяю, что пользователь остался на странице логина и не перешел на странцу настроек"):
            expect(temp_page).to_have_url(f"{base_url}/login")

























    # with allure.step("Удаляем созданного пользователя"):
    #     settings_account_page.delete_user_by_email(TESTMAIL_ADRESS_)












# @allure.title("Приглашение пользователя")
# def test_user_invitation(page_fixture, base_url, browser):
#     autorization_page = AutorizationPage(page_fixture)
#     home_page = HomePage(page_fixture)
#     settings_account_page = SettingsAccountPage(page_fixture)
#
#     autorization_page.open(base_url)
#     autorization_page.authorize()
#     home_page.click_settings_button()
#     settings_account_page.click_users_button()
#     settings_account_page.add_user()
#
#     with allure.step("Проверяем, что пользователь уже есть в списке, но еще не активирован"):
#         settings_account_page.click_first_user_table_row()
#         notification_text = autorization_page.get_notification_text()
#         assert notification_text == "Пользователь не активирован"
#
#     autorization_page.activate_account(browser)
#     with allure.step("Проверяю, что пользователь перешел на страницу настроек профиля"):
#         expect(page_fixture).to_have_url(f"{base_url}/profile")
#
# #TODO Переключится на первый контекст
#
#     with allure.step("Проверяем, что пользователь активирован"):
#         settings_account_page.click_first_user_table_row()
#         notification_text = autorization_page.get_notification_text()
#         assert notification_text != "Пользователь не активирован"
# #TODO Удалить запись
#     settings_account_page.delete_last_created_user()
# #TODO Убедится, что ее нет в списке
# #TODO Убедится, по логину паролю зайти нельзя
# #TODO Фикстура удаления должна проходится по всему списку юзеров в поиске созданного имейла, если он есть происходит удаление, если нет не происходит








    #ПЕРЕХОД ПО ССЫЛКЕ ПОЛУЧЕНОЙ В ПОСЛЕДНЕМ МЕТОДЕ


    # Какаято проверка на то что кнопка была нажата?
    # Залезть в на фейковую почту, скопировать ссылку
    # Открыть новый контекст
    # Перейти по ссылке
    # Сверится с тем, что ФИО те же*
    # Отредактировать ФИО*
    # Нажать на активировать
    # Убедится, что я нахожусь в настройках
    # Перейти в первый контекст
    # Удалить пользователя
    # Перейти во втлорой контекст обновить страницу
    # Попробовать авторизоватся

# @pytest.mark.auth
# @allure.title("Удаление поьзователя")
# def test_user_deletion(page_factory_fixture, base_url):
#     admin_page = page_factory_fixture(use_auth=True)
#     autorization_page = AutorizationPage(admin_page)
#     home_page = HomePage(admin_page)
#     settings_account_page = SettingsAccountPage(admin_page)
#     settings_account_page.open(base_url)
    # autorization_page.admin_buyer_authorize()
    # home_page.click_settings_button()
    # settings_account_page.click_users_button()
    # settings_account_page.delete_last_created_user()















    # Проверить "с возвращением"
    # проверить что введенная почта соответствует той, что была введена #email to have value=USER_EMAIL
    #TODO Написать фикстуру на уровне сессии, которая будет смотреть конкретного пользователя и удалять его.
