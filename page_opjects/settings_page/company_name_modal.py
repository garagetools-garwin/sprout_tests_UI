import time
import allure
from playwright.sync_api import Page, expect


class CompanyNameModal:
    MODAL = ".ant-modal"
    COMPANY_NAME_INPUT = ".ant-modal input"
    SAVE_BUTTON = ".button-sm.primary"
    # Название компании (берём из заголовка страницы настроек)
    COMPANY_NAME = ".account-settings-name__value"
    EDIT_BUTTON = ".account-settings-name__edit-btn"

    def __init__(self, page: Page):
        self.page = page

    @allure.step("Проверяю, что модалка редактирования открыта")
    def assert_opened(self):
        expect(self.page.locator(self.MODAL)).to_be_visible()

    @allure.step("Генерирую уникальное название компании")
    def generate_unique_company_name(self, prefix: str = "Компания") -> str:
        return f"{prefix} {int(time.time())}"

    @allure.step("Заполняю новое название компании")
    def fill_company_name(self, value: str):
        self.page.fill(self.COMPANY_NAME_INPUT, "")
        self.page.type(self.COMPANY_NAME_INPUT, value)

    @allure.step("Сохраняю новое название компании")
    def click_save(self):
        self.page.locator(self.SAVE_BUTTON).click()
        self.page.wait_for_timeout(400)

    @allure.step("Название компании видно")
    def assert_company_name_visible(self):
        expect(self.page.locator(self.COMPANY_NAME)).to_be_visible()

    @allure.step("Открываю модалку редактирования названия компании (карандаш рядом с заголовком)")
    def click_edit_company_name(self):
        self.page.locator(self.EDIT_BUTTON).click()

    @allure.step("Проверяю, что название компании обновилось")
    def assert_company_name_equals(self, expected: str):
        expect(self.page.locator(self.COMPANY_NAME)).to_have_text(expected)
