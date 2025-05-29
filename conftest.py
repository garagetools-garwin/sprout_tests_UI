from datetime import datetime
import allure
import pytest
from dotenv import load_dotenv
import os
import re
from playwright.sync_api import Browser, Page

load_dotenv()  # Загружаем переменные из .env

AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")


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


"""Основная фикстура для управления браузером, авторизацией и трассировкой (кастомная фикстура, расширяющая стандартную page)."""
@pytest.fixture(scope="function")
def page_fixtur(browser: Browser, request, base_url) -> Page:

    # Путь к корню проекта и папке auth_states
    project_root = os.path.dirname(os.path.abspath(__file__))  # Путь к корню проекта
    auth_states_dir = os.path.join(project_root, 'auth_states')
    os.makedirs(auth_states_dir, exist_ok=True)

    page = None
    trace_path = None

    try:
        auth_state_path = os.path.join(auth_states_dir, "auth_state.json")
        auth_state_empty_path = os.path.join(auth_states_dir, "auth_state_empty.json")

        # Получаем метку, чтобы определить, нужен ли storage_state
        # "auth" используется для авторизации через основной тестовый аккаунт, подходит для большенства задач
        use_auth = request.node.get_closest_marker("auth")
        # "auth_empty" используется для специального пустого аккаунта, в котором нет ниодного адреса или получателя
        # / не создавать адреса или получателей в этом аккаунте!
        use_auth_empty = request.node.get_closest_marker("auth_empty")

        if use_auth:
            # Создаём новый контекст с сохранённым состоянием авторизации, если метка присутствует
            context = browser.new_context(storage_state=auth_state_path)
        elif use_auth_empty:
            # Создаём новый контекст с сохранённым состоянием авторизации, если метка присутствует
            context = browser.new_context(storage_state=auth_state_empty_path)
        else:
            # Стандартный контекст без авторизации
            context = browser.new_context()

        # Создаём новую страницу в контексте
        page = context.new_page()

        # Если платформа тестовая, автоматически авторизуемся через URL
        if "https://stage.sprout-store.ru" in base_url or "https://review-site" in base_url:
            auth_url = base_url.replace("https://", f"https://{AUTH_USERNAME}:{AUTH_PASSWORD}@")
            page.goto(auth_url)
            context.storage_state(path=auth_state_path)

        # Задаем размер экрана для браузера
        page.set_viewport_size({"width": 1920, "height": 1080})

        """Настройка трассировки"""
        # Получение текущей даты и времени
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Удаляем все символы, которые нельзя использовать в путях Windows
        safe_name = re.sub(r'[\\/*?:"<>|\[\]]', '_', request.node.name)

        # Формирование имени файла с трассировкой
        trace_path = os.path.join(
            os.getcwd(),
            f'traces/{safe_name}_{current_time}.zip'
        )

        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        page.context.tracing.start(screenshots=True, snapshots=True)

        yield page

    finally:
        if page is not None and trace_path is not None:
            # Проверяем, был ли тест успешным
            if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
                # Сохраняем трассировку
                page.context.tracing.stop(path=trace_path)

                # Добавляем трассировку как артефакт в Allure-отчет
                allure.attach.file(
                    trace_path,
                    name="trace",
                    attachment_type='application/zip',
                    extension='.zip')

                # Добавляем скриншот как артефакт в Allure-отчет
                allure.attach(
                    name="failure_screenshot",
                    body=page.screenshot(full_page=True),
                    attachment_type=allure.attachment_type.PNG
                )

                # Добавляем исходный код страницы как артефакт в Allure-отчет
                allure.attach(
                    name="page_source",
                    body=page.content(),
                    attachment_type=allure.attachment_type.HTML
                )
            else:
                # Если тест успешен, просто останавливаем трассировку без сохранения
                page.context.tracing.stop()

            # Закрываем контекст браузера
            page.context.close()

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
