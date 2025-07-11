from datetime import datetime
import allure
import pytest
from dotenv import load_dotenv
import os
import re
from playwright.sync_api import Browser, Page

from page_opjects.autorization_page import AutorizationPage
from page_opjects.home_page import HomePage
from page_opjects.settings_account_page import SettingsAccountPage

load_dotenv()  # Загружаем переменные из .env

AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")





# @pytest.fixture(scope="function")
# def page_factory(browser: Browser, base_url, request):
#     def _create_page(use_auth=False, use_auth_empty=False):
#         project_root = os.path.dirname(os.path.abspath(__file__))
#         auth_states_dir = os.path.join(project_root, 'auth_states')
#         os.makedirs(auth_states_dir, exist_ok=True)
#
#         auth_state_path = os.path.join(auth_states_dir, "auth_state.json")
#         auth_state_empty_path = os.path.join(auth_states_dir, "auth_state_empty.json")
#
#         if use_auth:
#             context = browser.new_context(storage_state=auth_state_path)
#         elif use_auth_empty:
#             context = browser.new_context(storage_state=auth_state_empty_path)
#         else:
#             context = browser.new_context()
#
#         page = context.new_page()
#         page.set_viewport_size({"width": 1920, "height": 1080})
#
#         # автоавторизация по ссылке
#         if "https://stage.sprout-store.ru" in base_url or "https://review-site" in base_url:
#             auth_url = base_url.replace("https://", f"https://{AUTH_USERNAME}:{AUTH_PASSWORD}@")
#             page.goto(auth_url)
#             context.storage_state(path=auth_state_path)
#
#         return page, context
#
#     return _create_page


# """Основная фикстура для управления браузером, авторизацией и трассировкой (кастомная фикстура, расширяющая стандартную page)."""
# @pytest.fixture(scope="function")
# def page_fixture(browser: Browser, request, base_url) -> Page:
#
#     # Путь к корню проекта и папке auth_states
#     project_root = os.path.dirname(os.path.abspath(__file__))  # Путь к корню проекта
#     auth_states_dir = os.path.join(project_root, 'auth_states')
#     os.makedirs(auth_states_dir, exist_ok=True)
#
#     page = None
#     trace_path = None
#
#     try:
#         auth_state_path = os.path.join(auth_states_dir, "auth_state.json")
#         auth_state_empty_path = os.path.join(auth_states_dir, "auth_state_empty.json")
#
#         # Получаем метку, чтобы определить, нужен ли storage_state
#         # "auth" используется для авторизации через основной тестовый аккаунт, подходит для большенства задач
#         use_auth = request.node.get_closest_marker("auth")
#         # "auth_empty" используется для специального пустого аккаунта, в котором нет ниодного адреса или получателя
#         # / не создавать адреса или получателей в этом аккаунте!
#         use_auth_empty = request.node.get_closest_marker("auth_empty")
#
#         if use_auth:
#             # Создаём новый контекст с сохранённым состоянием авторизации, если метка присутствует
#             context = browser.new_context(storage_state=auth_state_path)
#         elif use_auth_empty:
#             # Создаём новый контекст с сохранённым состоянием авторизации, если метка присутствует
#             context = browser.new_context(storage_state=auth_state_empty_path)
#         else:
#             # Стандартный контекст без авторизации
#             context = browser.new_context()
#
#         # Создаём новую страницу в контексте
#         page = context.new_page()
#
#         # Если платформа тестовая, автоматически авторизуемся через URL
#         if "https://stage.sprout-store.ru" in base_url or "https://review-site" in base_url:
#             auth_url = base_url.replace("https://", f"https://{AUTH_USERNAME}:{AUTH_PASSWORD}@")
#             page.goto(auth_url)
#             context.storage_state(path=auth_state_path)
#
#         # Задаем размер экрана для браузера
#         page.set_viewport_size({"width": 1920, "height": 1080})
#
#         """Настройка трассировки"""
#         # Получение текущей даты и времени
#         current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#
#         # Удаляем все символы, которые нельзя использовать в путях Windows
#         safe_name = re.sub(r'[\\/*?:"<>|\[\]]', '_', request.node.name)
#
#         # Формирование имени файла с трассировкой
#         trace_path = os.path.join(
#             os.getcwd(),
#             f'traces/{safe_name}_{current_time}.zip'
#         )
#
#         os.makedirs(os.path.dirname(trace_path), exist_ok=True)
#         page.context.tracing.start(screenshots=True, snapshots=True)
#
#         yield page
#
#     finally:
#         if page is not None and trace_path is not None:
#             # Проверяем, был ли тест успешным
#             if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
#                 # Сохраняем трассировку
#                 page.context.tracing.stop(path=trace_path)
#
#                 # Добавляем трассировку как артефакт в Allure-отчет
#                 allure.attach.file(
#                     trace_path,
#                     name="trace",
#                     attachment_type='application/zip',
#                     extension='.zip')
#
#                 # Добавляем скриншот как артефакт в Allure-отчет
#                 allure.attach(
#                     name="failure_screenshot",
#                     body=page.screenshot(full_page=True),
#                     attachment_type=allure.attachment_type.PNG
#                 )
#
#                 # Добавляем исходный код страницы как артефакт в Allure-отчет
#                 allure.attach(
#                     name="page_source",
#                     body=page.content(),
#                     attachment_type=allure.attachment_type.HTML
#                 )
#             else:
#                 # Если тест успешен, просто останавливаем трассировку без сохранения
#                 page.context.tracing.stop()
#
#             # Закрываем контекст браузера
#             page.context.close()


# === ФАБРИКА СТРАНИЦ === #
def page_factory(browser: Browser, base_url: str, use_auth=False, use_auth_empty=False, use_manual_login=False) -> Page:
    project_root = os.path.dirname(os.path.abspath(__file__))
    auth_states_dir = os.path.join(project_root, 'auth_states')
    os.makedirs(auth_states_dir, exist_ok=True)

    auth_state_path = os.path.join(auth_states_dir, "auth_state.json")
    auth_state_empty_path = os.path.join(auth_states_dir, "auth_state_empty.json")

    if use_auth:
        context = browser.new_context(storage_state=auth_state_path)
    elif use_auth_empty:
        context = browser.new_context(storage_state=auth_state_empty_path)
    else:
        context = browser.new_context()

    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})

    if not use_manual_login and ("stage.sprout-store.ru" in base_url or "review-site" in base_url):
        auth_url = base_url.replace("https://", f"https://{AUTH_USERNAME}:{AUTH_PASSWORD}@")
        page.goto(auth_url)
        context.storage_state(path=auth_state_path)

    return page


# === ЕДИНАЯ ФИКСТУРА С ТРАССИРОВКОЙ === #
@pytest.fixture()
def page_factory_fixture(browser: Browser, request, base_url):
    pages = []

    def _factory(use_auth=False, use_auth_empty=False, use_manual_login=False):
        page = page_factory(
            browser=browser,
            base_url=base_url,
            use_auth=use_auth,
            use_auth_empty=use_auth_empty,
            use_manual_login=use_manual_login
        )
        pages.append(page)

        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = re.sub(r'[\\/*?:"<>|\[\]]', '_', request.node.name)
        trace_path = os.path.join(os.getcwd(), f'traces/{safe_name}_{current_time}_{len(pages)}.zip')
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)

        page.context.tracing.start(screenshots=True, snapshots=True)
        page._trace_path = trace_path
        return page

    yield _factory

    for page in pages:
        trace_path = getattr(page, "_trace_path", None)
        if trace_path:
            if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
                page.context.tracing.stop(path=trace_path)
                allure.attach.file(trace_path, name="trace", attachment_type='application/zip', extension='.zip')
                allure.attach(name="failure_screenshot", body=page.screenshot(full_page=True), attachment_type=allure.attachment_type.PNG)
                allure.attach(name="page_source", body=page.content(), attachment_type=allure.attachment_type.HTML)
            else:
                page.context.tracing.stop()
        page.context.close()

import pytest
import allure


@pytest.fixture
def delete_user_fixture(base_url, page_factory_fixture):
    """Фикстура для удаления пользователя после теста, если он был создан, но не удалён вручную."""

    state = {
        "user_created": False,
        "user_deleted": False
    }

    def mark_user_created():
        state["user_created"] = True
        print("=== USER CREATED ===")
        allure.attach("Пользователь создан", name="DEBUG", attachment_type=allure.attachment_type.TEXT)

    def mark_user_deleted():
        state["user_deleted"] = True
        print("=== USER DELETED MANUALLY ===")
        allure.attach("Пользователь удалён вручную", name="DEBUG", attachment_type=allure.attachment_type.TEXT)

    yield mark_user_created, mark_user_deleted

    print("=== TEARDOWN STARTED ===")
    allure.attach("Teardown начался", name="DEBUG", attachment_type=allure.attachment_type.TEXT)

    if state["user_created"] and not state["user_deleted"]:
        try:
            with allure.step("Удаляю пользователя в teardown"):
                # Создаём новый контекст страницы
                admin_page = page_factory_fixture()
                authorization_page = AutorizationPage(admin_page)
                settings_account_page = SettingsAccountPage(admin_page)
                home_page = HomePage(admin_page)

                settings_account_page.open(base_url)
                authorization_page.admin_buyer_authorize()
                home_page.click_settings_button()
                settings_account_page.click_users_button()
                settings_account_page.delete_last_created_user()

                print("=== USER DELETED IN TEARDOWN ===")
                allure.attach("Пользователь удалён в teardown", name="DEBUG",
                              attachment_type=allure.attachment_type.TEXT)

        except Exception as e:
            print(f"=== TEARDOWN CRASHED: {e} ===")
            allure.attach(str(e), "Ошибка в teardown при удалении пользователя", allure.attachment_type.TEXT)


"""Добавляет опции"""
def pytest_addoption(parser):
    # Добавляет опцию --url для выбора окружения
    parser.addoption(
        "--url", default="https://sprout-store.ru"
    )

"""Фикстура для подмены нового контекста авторизованным"""
@pytest.fixture(scope="function")
def authorized_context(browser):
    # Передает состояние авторизации для создания контекста
    return {
        "storage_state": "auth_state.json"
    }

"""Возвращает базовый URL из параметров командной строки через --url"""
@pytest.fixture(scope="session")
def base_url(request):
    url = request.config.getoption('--url')
    return url

"""Хук для фильтрации отчётов Allure (Перехватывает результат и выводит метку rerun в отчет, если тест был перезапущен)"""
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    # Добавляем информацию о результате теста в запрос
    setattr(item, "rep_" + report.when, report)
    # Добавляем метку "Test Rerun" для перезапущенных тестов
    if report.outcome == "failed" and item.get_closest_marker("rerun"):
        allure.dynamic.label("rerun", "Test Rerun")

