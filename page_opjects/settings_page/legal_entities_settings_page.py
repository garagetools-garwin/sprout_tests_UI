import allure
from playwright.sync_api import Page, expect


class LegalEntitiesPage:
    def __init__(self, page: Page):
        self.page = page

    PATH = "/settings/account/legal-entity-list"

    ADD_NEW_BUTTON = 'button:has-text("Добавить новое")'
    LEGAL_ENTITY_CARD = '.account-legal-entity-list-settings__table-item-name'
    ACTION_MENU_BUTTON = 'td.ant-table-cell button'
    EDIT_OPTION = 'text=Редактировать'
    DELETE_OPTION = 'text=Удалить'
    # CARD_NAME = '.settings-legal-entity-list__item-title'
    # CARD_INN = '.settings-legal-entity-list__item-inn'

    @allure.step("Открываю страницу Юридические лица")
    def open(self, base_url: str):
        return self.page.goto(base_url + self.PATH)

    def click_add_new(self):
        with allure.step("Кликаю 'Добавить новое'"):
            self.page.locator(self.ADD_NEW_BUTTON).click()

    def get_entity_cards(self):
        return self.page.locator(self.LEGAL_ENTITY_CARD)

    @allure.step("Открываю меню действий для первого юрлица")
    def open_action_menu(self):
        self.page.locator(self.ACTION_MENU_BUTTON).first.hover()

    @allure.step("Кликаю 'Редактировать'")
    def click_edit(self):
        self.page.locator(self.EDIT_OPTION).click()

    @allure.step("Кликаю 'Удалить'")
    def click_delete(self):
        self.page.locator(self.DELETE_OPTION).click()

    @allure.step("Удаляю последнее созданною юр лицо")
    def delete_last_created_legal_entity(self, base_url):
        modal = LegalEntityModal(page=self.page)
        self.open(base_url)

        with allure.step("Считаю количество карточек"):
            initial_count = self.get_entity_cards().count()
            print(initial_count)

        self.open_action_menu()
        self.click_delete()
        with allure.step("В появившейся модалке подтверждаю удаление"):
            modal.click_delete()
        with allure.step("Проверяю, что число карточек уменьшилось"):
            assert self.get_entity_cards().count() == initial_count - 1
            initial_count = self.get_entity_cards().count()
            print(initial_count)

    @allure.step("Удаляю карточку юридического лица с 'Автотест'")
    def delete_autotest_legal_entity(self, base_url):
        modal = LegalEntityModal(page=self.page)
        self.open(base_url)

        with allure.step("Считаю количество карточек"):
            initial_count = self.get_entity_cards().count()
            print(f"Изначальное число карточек: {initial_count}")

        # Найти все строки таблицы (rows)
        rows = self.page.locator('.ant-table-row.ant-table-row-level-0')
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
            delete_button = self.page.locator("text=Удалить")  # уточните путь, если в меню кнопка не видна глобально
            delete_button.click()

        with allure.step("В появившейся модалке подтверждаю удаление"):
            modal.click_delete()

        with allure.step("Проверяю, что число карточек уменьшилось"):
            new_count = self.get_entity_cards().count()
            print(f"Новое число карточек: {new_count}")
            assert new_count == initial_count - 1


class LegalEntityModal:

    def __init__(self, page: Page):
        self.page = page

    MODAL = 'div.ant-drawer-content-wrapper'
    DELETE_MODAL = 'div.ant-drawer-content-wrapper div:has-text("Вы уверены, что хотите удалить юр. лицо?")'
    NAME_INPUT = 'input#name'
    INN_INPUT = 'input#inn'
    KPP_INPUT = 'input#kpp'
    SAVE_BUTTON = 'button:has-text("Сохранить изменения")'
    ADD_BUTTON = 'button:has-text("Добавить юр. лицо")'
    # CLOSE_BUTTON = '.modal .close'
    DELETE_BUTTON = 'button:has-text("Удалить")'
    CANCEL_DELETE_BUTTON = 'button:has-text("Отмена")'
    COPY_BUTTON = 'button .icon-copy-dark-grey'


    with allure.step("Заполняю поля заданными значениями"):
        def fill(self, name, inn, kpp):
            self.page.locator(self.NAME_INPUT).fill(name)
            self.page.locator(self.INN_INPUT).fill(inn)
            self.page.locator(self.KPP_INPUT).fill(kpp)

    allure.step("Добавляю юр. лицо")
    def add(self):
        self.page.locator(self.ADD_BUTTON).click()

    allure.step("Сохраняю изменения")
    def save(self):
        self.page.locator(self.SAVE_BUTTON).click()

    @allure.step("Кликаю 'Удалить'")
    def click_delete(self):
        self.page.locator(self.DELETE_BUTTON).click()

    @allure.step("Кликаю 'Отмена'")
    def cancel_delete(self):
        self.page.locator(self.CANCEL_DELETE_BUTTON).click()

    @allure.step("Закрываю модальное окно")
    def close(self):
        self.page.locator(self.CLOSE_BUTTON).click()

    @allure.step("Нажимаю на Скопировать ИНН")
    def click_copy_inn(self):
        self.page.locator(self.COPY_BUTTON).nth(0).click()

    @allure.step("Нажимаю на Скопировать КПП")
    def click_copy_kpp(self):
        self.page.locator(self.COPY_BUTTON).nth(1).click()