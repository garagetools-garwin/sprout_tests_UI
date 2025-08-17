import allure
from playwright.sync_api import Page, expect


class ContractsSettingsPage:

    PATH = "/settings/account/contracts"

    # Тумблер "Округление итоговой суммы"
    ROUND_TOTAL_SECTION = "section:has-text('Округление итоговой суммы')"
    ROUND_TOTAL_TOGGLE_BUTTON = "#priceRounding"

    # Блок "Лимиты на закупку"
    LIMITS_SECTION = "section:has-text('Лимиты на закупку')"
    PRICE_LIMIT_INPUT = "#maxGoodPrice"
    LIMIT_CHANGED_TOAST = "text=Лимит цены за ед. товара изменен в настройках аккаунта."

    def __init__(self, page: Page):
        self.page = page

    def open(self, base_url):
        with allure.step(f"Открываю {base_url + self.PATH}"):
            return self.page.goto(base_url + self.PATH)

    @allure.step("Состояние тумблера округления (по aria-checked)")
    def is_total_rounding_enabled(self) -> bool:
        """
        Возвращает True, если переключатель #priceRounding включен (aria-checked='true').
        """
        el = self.page.locator(self.ROUND_TOTAL_TOGGLE_BUTTON)
        expect(el).to_be_visible()
        aria = el.get_attribute("aria-checked") or ""
        return aria.lower() == "true"

    @allure.step("Включаю тумблер 'Округление итоговой суммы'")
    def enable_total_rounding(self):
        if not self.is_total_rounding_enabled():
            self.page.locator(self.ROUND_TOTAL_TOGGLE_BUTTON).click()

    @allure.step("Отключаю тумблер 'Округление итоговой суммы', если он включен")
    def disable_total_rounding(self):
        if self.is_total_rounding_enabled():
            self.page.locator(self.ROUND_TOTAL_TOGGLE_BUTTON).click()

    @allure.step("Кликаю рядом с инпутом лимита и жду уведомление об изменении (до 5 секунд)")
    def click_beside_limit_input_and_expect_toast(self):
        # 1) Клик рядом с инпутом (по контейнеру секции)
        self.page.locator(self.PRICE_LIMIT_INPUT).click(position={"x": 20, "y": 20})
        # 2) Ожидаем появление текста-уведомления до 5 секунд
        expect(self.page.locator(self.LIMIT_CHANGED_TOAST)).not_to_be_hidden(timeout=5000)

    @allure.step("Устанавливаю лимит цены за единицу товара")
    def set_item_price_limit(self, value: str):
        self.page.fill(self.PRICE_LIMIT_INPUT, "")
        self.page.fill(self.PRICE_LIMIT_INPUT, value)