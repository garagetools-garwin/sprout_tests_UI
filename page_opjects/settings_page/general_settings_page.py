import allure
from playwright.sync_api import Page, expect


class GeneralSettingsPage:
    PATH = "/settings/account"

    # Иконка профиля/вход в карточку "Настройки аккаунта"
    PROFILE_AVATAR = "header:has-text('Тестовый П.') img, header .ant-avatar, header [role='img']"
    SETTINGS_ENTRY_CARD = "main a:has-text('Настройки аккаунта'), main:has-text('Настройки аккаунта')"
    USERS_BUTTON = ".ant-menu-title-content:has-text('Пользователи')"
    CONTRACTS_BUTTON = ".ant-menu-title-content:has-text('Контракты')"
    LEGAL_ENTITIES_BUTTON = ".ant-menu-title-content:has-text('Юридические лица')"

    def __init__(self, page: Page):
        self.page = page

    @allure.step("Открываю страницу настроек аккаунта")
    def open(self, base_url: str):
        return self.page.goto(base_url + self.PATH)

    @allure.step("Открываю настройки через иконку личного кабинета")
    def open_via_profile_icon(self, base_url: str):
        self.page.goto(base_url)
        self.page.locator(self.PROFILE_AVATAR).click()
        self.page.locator(self.SETTINGS_ENTRY_CARD).click()

    @allure.step("Кликаю на иконку Пользователи")
    def click_users_button(self):
        self.page.locator(self.USERS_BUTTON).click()

    @allure.step("Кликаю на иконку Контракты")
    def click_contracts_button(self):
        self.page.locator(self.CONTRACTS_BUTTON).click()

    @allure.step("Кликаю на иконку Юридические лица")
    def click_legal_antities_button(self):
        self.page.locator(self.LEGAL_ENTITIES_BUTTON).click()

