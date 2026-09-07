import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
    WebDriverException,
)


# ============================================================
# НАСТРОЙКИ
# ============================================================

BASE_URL = "http://xcollect.fasp.local"

USERS_URL = (
    "http://xcollect.fasp.local/setup/usersSetup.zul"
)

CHROME_DEBUG_ADDRESS = "127.0.0.1:9222"


# ============================================================
# ВТОРАЯ ЧАСТЬ XCOLLECT
# ============================================================

class XCollectSecond:

    def __init__(self, login):
        self.login = login
        self.driver = None

    # ========================================================
    # ЛОГ
    # ========================================================

    def log(self, text):
        print(
            text,
            flush=True
        )

    # ========================================================
    # SAFE CLICK
    # ========================================================

    def safe_click(self, element):

        try:

            WebDriverWait(
                self.driver,
                10
            ).until(
                EC.element_to_be_clickable(
                    element
                )
            )

            element.click()

        except ElementClickInterceptedException:

            self.driver.execute_script(
                "arguments[0].click();",
                element
            )

    # ========================================================
    # ПОДКЛЮЧЕНИЕ К УЖЕ ЗАПУЩЕННОМУ CHROME
    # ========================================================

    def connect_to_chrome(self):

        self.log("")
        self.log("=" * 60)
        self.log(
            "🔗 ПОДКЛЮЧЕНИЕ К УЖЕ ЗАПУЩЕННОМУ CHROME"
        )
        self.log("=" * 60)

        self.log(
            f"🔌 Chrome debugging: "
            f"{CHROME_DEBUG_ADDRESS}"
        )

        options = webdriver.ChromeOptions()

        options.add_experimental_option(
            "debuggerAddress",
            CHROME_DEBUG_ADDRESS
        )

        try:

            self.driver = webdriver.Chrome(
                options=options
            )

        except WebDriverException as e:

            self.log("")
            self.log(
                "❌ Не удалось подключиться к Chrome."
            )

            self.log(
                "❌ Проверь, что первый файл запустил Chrome "
                "с remote debugging на порту 9222."
            )

            self.log(
                f"❌ Ошибка: {repr(e)}"
            )

            raise

        self.log(
            "✅ Подключение к существующему Chrome выполнено"
        )

        try:

            self.log(
                f"🌐 Текущий URL: "
                f"{self.driver.current_url}"
            )

        except Exception:
            pass

        self.log(
            f"👤 Полученный логин: {self.login}"
        )

    # ========================================================
    # ОЖИДАНИЕ МОДАЛЬНОГО ОКНА
    # ========================================================

    def wait_for_modal(
        self,
        timeout=15
    ):

        return WebDriverWait(
            self.driver,
            timeout
        ).until(

            EC.visibility_of_element_located(

                (
                    By.XPATH,
                    "//div[contains("
                    "concat(' ', "
                    "normalize-space(@class), ' '), "
                    "' z-window-modal '"
                    ")]"
                )

            )
        )

    # ========================================================
    # ОТКРЫВАЕМ USERS
    # ========================================================

    def open_users(self):

        self.log("")
        self.log("=" * 60)
        self.log(
            "👥 ЭТАП 1 — ОТКРЫВАЕМ ПОЛЬЗОВАТЕЛЕЙ"
        )
        self.log("=" * 60)

        self.log(
            "🌐 Открываем управление пользователями..."
        )

        self.driver.get(
            USERS_URL
        )

        self.log(
            f"🌐 URL: {USERS_URL}"
        )

        self.log(
            "⏳ Ждём загрузку страницы..."
        )

        time.sleep(3)

        self.log(
            "✅ Страница пользователей открыта"
        )

    # ========================================================
    # НАХОДИМ ПОЛЕ Qx.z-textbox
    # ========================================================

    def find_search_input(self):

        self.log("")
        self.log(
            "🔎 Ищем поле поиска Qx.z-textbox..."
        )

        search_input = WebDriverWait(
            self.driver,
            20
        ).until(

            EC.visibility_of_element_located(

                (
                    By.XPATH,

                    "//input[contains(@class, 'Qx') "
                    "and contains(@class, 'z-textbox')]"
                )

            )
        )

        self.log(
            "✅ Поле Qx.z-textbox найдено"
        )

        return search_input

    # ========================================================
    # ВВОДИМ ЛОГИН
    # ========================================================

    def enter_login(self):

        self.log("")
        self.log("=" * 60)
        self.log(
            "🔎 ЭТАП 2 — ПОИСК ПОЛЬЗОВАТЕЛЯ"
        )
        self.log("=" * 60)

        search_input = self.find_search_input()

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            search_input
        )

        time.sleep(0.3)

        try:

            search_input.click()

        except Exception:

            self.driver.execute_script(
                "arguments[0].click();",
                search_input
            )

        try:

            search_input.clear()

        except Exception:
            pass

        search_input.send_keys(
            self.login
        )

        self.log(
            f"✅ В поле поиска введён логин: "
            f"{self.login}"
        )

    # ========================================================
    # НАХОДИМ Qb1.z-button
    # ========================================================

    def find_search_button(self):

        self.log(
            "🔎 Ищем кнопку Qb1.z-button..."
        )

        search_button = WebDriverWait(
            self.driver,
            15
        ).until(

            EC.element_to_be_clickable(

                (
                    By.XPATH,

                    "//*[contains(@class, 'Qb1') "
                    "and contains(@class, 'z-button')]"
                )

            )
        )

        self.log(
            "✅ Кнопка Qb1.z-button найдена"
        )

        return search_button

    # ========================================================
    # НАЖИМАЕМ ПОИСК
    # ========================================================

    def click_search(self):

        search_button = self.find_search_button()

        self.safe_click(
            search_button
        )

        self.log(
            "✅ Кнопка поиска нажата"
        )

        self.log(
            "⏳ Ждём результат поиска..."
        )

        time.sleep(2)

    # ========================================================
    # НАХОДИМ Qh2.z-listcell
    # ========================================================

    def find_user_result(self):

        self.log("")
        self.log(
            "🔎 ЭТАП 3 — ИЩЕМ РЕЗУЛЬТАТ ПОЛЬЗОВАТЕЛЯ"
        )

        self.log(
            "🔎 Ищем Qh2.z-listcell..."
        )

        list_cell = WebDriverWait(
            self.driver,
            20
        ).until(

            EC.visibility_of_element_located(

                (
                    By.XPATH,

                    "//*[contains(@class, 'Qh2') "
                    "and contains(@class, 'z-listcell')]"
                )

            )
        )

        self.log(
            "✅ Qh2.z-listcell найден"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            list_cell
        )

        time.sleep(0.5)

        return list_cell

    # ========================================================
    # ПКМ ПО ПОЛЬЗОВАТЕЛЮ
    # ========================================================

    def open_context_menu(
        self,
        list_cell
    ):

        self.log("")
        self.log(
            "🖱 ЭТАП 4 — ОТКРЫВАЕМ КОНТЕКСТНОЕ МЕНЮ"
        )

        self.log(
            "🖱 Нажимаем ПКМ по Qh2.z-listcell..."
        )

        ActionChains(
            self.driver
        ).context_click(
            list_cell
        ).perform()

        self.log(
            "✅ Контекстное меню вызвано"
        )

        time.sleep(1)

    # ========================================================
    # НАХОДИМ Qv1-a.z-menuitem-content
    # ========================================================

    def find_menu_item(self):

        self.log(
            "🔎 Ищем Qv1-a.z-menuitem-content..."
        )

        menu_item = WebDriverWait(
            self.driver,
            15
        ).until(

            EC.visibility_of_element_located(

                (
                    By.XPATH,

                    "//*[contains(@class, 'Qv1-a') "
                    "and contains("
                    "@class, "
                    "'z-menuitem-content'"
                    ")]"
                )

            )
        )

        self.log(
            "✅ Qv1-a.z-menuitem-content найден"
        )

        return menu_item

    # ========================================================
    # НАЖИМАЕМ ПУНКТ КОНТЕКСТНОГО МЕНЮ
    # ========================================================

    def click_menu_item(self):

        menu_item = self.find_menu_item()

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            menu_item
        )

        time.sleep(0.3)

        self.safe_click(
            menu_item
        )

        self.log(
            "✅ Пункт контекстного меню нажат"
        )

    # ========================================================
    # ЖДЁМ ВТОРУЮ МОДАЛКУ
    # ========================================================

    def wait_for_second_modal(self):

        self.log("")
        self.log(
            "⏳ ЭТАП 5 — ЖДЁМ ВТОРОЕ МОДАЛЬНОЕ ОКНО..."
        )

        modal = self.wait_for_modal(
            timeout=15
        )

        self.log("")
        self.log("=" * 60)
        self.log(
            "🟢 ВТОРОЕ МОДАЛЬНОЕ ОКНО ОТКРЫТО"
        )
        self.log("=" * 60)

        self.log(
            "🛑 На этом этапе останавливаемся."
        )

        return modal

    # ========================================================
    # ОСНОВНОЙ RUN
    # ========================================================

    def run(self):

        try:

            # ------------------------------------------------
            # 1. Подключаемся к существующему Chrome
            # ------------------------------------------------

            self.connect_to_chrome()

            # ------------------------------------------------
            # 2. Открываем USERS
            # ------------------------------------------------

            self.open_users()

            # ------------------------------------------------
            # 3. Вводим логин
            # ------------------------------------------------

            self.enter_login()

            # ------------------------------------------------
            # 4. Нажимаем поиск
            # ------------------------------------------------

            self.click_search()

            # ------------------------------------------------
            # 5. Находим пользователя
            # ------------------------------------------------

            list_cell = self.find_user_result()

            # ------------------------------------------------
            # 6. ПКМ
            # ------------------------------------------------

            self.open_context_menu(
                list_cell
            )

            # ------------------------------------------------
            # 7. Нажимаем пункт меню
            # ------------------------------------------------

            self.click_menu_item()

            # ------------------------------------------------
            # 8. Ждём вторую модалку
            # ------------------------------------------------

            self.wait_for_second_modal()

            return True

        except Exception as e:

            self.log("")
            self.log("=" * 60)
            self.log(
                "❌ ОШИБКА ВТОРОГО СКРИПТА"
            )
            self.log("=" * 60)

            self.log(
                repr(e)
            )

            # ------------------------------------------------
            # Скриншот
            # ------------------------------------------------

            try:

                self.driver.save_screenshot(
                    "xcollect_second_error.png"
                )

                self.log(
                    "📸 Скриншот сохранён: "
                    "xcollect_second_error.png"
                )

            except Exception:
                pass

            return False


# ============================================================
# MAIN
# ============================================================

def main():

    print("")
    print("=" * 60)
    print(
        "🚀 XCOLLECT SECOND SCRIPT"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Проверяем аргументы
    # --------------------------------------------------------

    if len(sys.argv) < 2:

        print(
            "❌ Не передан логин."
        )

        print(
            "Использование:"
        )

        print(
            "python xcollect_second.py login"
        )

        sys.exit(1)

    login = sys.argv[1].strip()

    if not login:

        print(
            "❌ Передан пустой логин."
        )

        sys.exit(1)

    print(
        f"👤 Логин: {login}"
    )

    # --------------------------------------------------------
    # Создаём второй Selenium
    # --------------------------------------------------------

    app = XCollectSecond(
        login
    )

    # --------------------------------------------------------
    # Запускаем
    # --------------------------------------------------------

    success = app.run()

    # --------------------------------------------------------
    # Результат
    # --------------------------------------------------------

    if success:

        print("")
        print("=" * 60)
        print(
            "✅ ВТОРАЯ ЧАСТЬ ЗАВЕРШЕНА"
        )
        print(
            "✅ ВТОРАЯ МОДАЛКА ОТКРЫТА"
        )
        print(
            "🛑 ДАЛЬШЕ ПОКА НЕ ИДЁМ"
        )
        print("=" * 60)

        # Не закрываем Chrome.
        # Не вызываем driver.quit().
        #
        # Первый Chrome должен остаться открытым.

        while True:
            time.sleep(1)

    else:

        print("")
        print(
            "❌ Вторая часть завершилась с ошибкой."
        )

        sys.exit(1)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()