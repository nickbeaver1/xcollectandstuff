import time
import threading
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
)


# ============================================================
# НАСТРОЙКИ XCOLLECT
# ============================================================

BASE_URL = "http://xcollect.fasp.local"

USERS_URL = (
    "http://xcollect.fasp.local/setup/usersSetup.zul"
)

XCOLLECT_LOGIN = "n.perepelitsa"
XCOLLECT_PASSWORD = "DredgenReckoner127."


# ============================================================
# SELENIUM
# ============================================================

class XCollectSearch:

    def __init__(self, log):

        self.driver = None
        self.log = log

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
    # ПОИСК ПОЛЯ ЛОГИНА ДЛЯ ПОИСКА ПОЛЬЗОВАТЕЛЯ
    # ========================================================

    def find_login_search_field(self):

        candidates = [

            # Основной вариант — по смысловому атрибуту name,
            # он стабильнее сгенерированного id.
            "//input[@name='employee_login']",

            # Запасной вариант — по фрагменту id, если name
            # вдруг не совпадёт (сгенерированные ZK id могут
            # меняться между перезагрузками страницы).
            "//input[contains(@id, 'tFxP') "
            "and contains(@class, 'z-textbox')]",

            "//input[contains(@id, 'tFxP')]",
        ]

        for xpath in candidates:

            try:

                elements = self.driver.find_elements(
                    By.XPATH,
                    xpath
                )

                for element in elements:

                    try:

                        if element.is_displayed():
                            return element

                    except Exception:
                        continue

            except Exception:
                continue

        raise Exception(
            "Не найдено поле поиска по логину "
            "(employee_login / tFxP...)."
        )

    # ========================================================
    # ПОИСК СТРОКИ РЕЗУЛЬТАТА ПО ЛОГИНУ
    # ========================================================

    def find_result_row(self, login):

        candidates = [

            # Точное совпадение текста — самый надёжный вариант.
            "//div[contains(@class, 'z-listcell-content') "
            f"and normalize-space(text())='{login}']",

            # На случай, если внутри есть лишние пробелы/обёртки.
            "//div[contains(@class, 'z-listcell-content') "
            f"and contains(normalize-space(text()), '{login}')]",

            # Запасной вариант через саму ячейку td.
            "//td[contains(@class, 'z-listcell')]"
            f"//*[contains(normalize-space(text()), '{login}')]",
        ]

        for xpath in candidates:

            try:

                elements = self.driver.find_elements(
                    By.XPATH,
                    xpath
                )

                for element in elements:

                    try:

                        if element.is_displayed():
                            return element

                    except Exception:
                        continue

            except Exception:
                continue

        raise Exception(
            f"Не найдена строка результата для логина '{login}'."
        )

    # ========================================================
    # ПОИСК ПОЛЯ ВНУТРИ МОДАЛКИ РЕДАКТИРОВАНИЯ
    # ========================================================

    def find_edit_modal_field(self, modal, id_hint, value_hint=None):

        xpath_id = (
            f".//input[contains(@id, '{id_hint}') "
            "and contains(@class, 'z-combobox-input')]"
        )

        try:

            for el in modal.find_elements(By.XPATH, xpath_id):

                if el.is_displayed():
                    return el

        except Exception:
            pass

        if value_hint:

            xpath_val = (
                ".//input[contains(@class, 'z-combobox-input') "
                f"and contains(@value, '{value_hint}')]"
            )

            try:

                for el in modal.find_elements(By.XPATH, xpath_val):

                    if el.is_displayed():
                        return el

            except Exception:
                pass

        raise Exception(
            f"Не найдено поле (id_hint='{id_hint}') в модалке."
        )

    # ========================================================
    # ВЫБОР ЗНАЧЕНИЯ В COMBOBOX
    # ========================================================

    def select_combobox_value(self, field, value):

        self.driver.execute_script(
            "arguments[0].focus();",
            field
        )

        try:

            field.clear()
            field.send_keys(value)
            time.sleep(0.5)
            field.send_keys("\n")

        except Exception:

            self.driver.execute_script(
                """
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
                """,
                field,
                value
            )

    # ========================================================
    # ПОИСК МОДАЛКИ
    # ========================================================

    def wait_for_modal(self, timeout=15):

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
    # RUN — открываем XCollect, логинимся, ищем поле,
    # вводим логин, жмём Enter. Дальше пока не идём.
    # ========================================================

    def run(self, login):

        try:

            self.log(
                "🌐 Запускаем Chrome..."
            )

            options = webdriver.ChromeOptions()

            options.add_argument(
                "--ignore-certificate-errors"
            )

            options.add_argument(
                "--disable-extensions"
            )

            options.add_argument(
                "--start-maximized"
            )

            self.driver = webdriver.Chrome(
                options=options
            )

            self.driver.maximize_window()

            # =================================================
            # ЛОГИН В XCOLLECT
            # =================================================

            self.log(
                "🔐 Открываем XCollect..."
            )

            self.driver.get(
                BASE_URL
            )

            time.sleep(2)

            login_input = WebDriverWait(
                self.driver,
                15
            ).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//input["
                        "@type='text' and "
                        "("
                        "contains(@name,'login') or "
                        "contains(@id,'login') or "
                        "@name='username' or "
                        "@id='username'"
                        ")"
                        "]"
                    )
                )
            )

            login_input.clear()

            login_input.send_keys(
                XCOLLECT_LOGIN
            )

            self.log(
                "✅ Логин введён"
            )

            password_input = WebDriverWait(
                self.driver,
                15
            ).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//input[@type='password']"
                    )
                )
            )

            password_input.clear()

            password_input.send_keys(
                XCOLLECT_PASSWORD
            )

            self.log(
                "✅ Пароль введён"
            )

            login_button = WebDriverWait(
                self.driver,
                15
            ).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains("
                        "normalize-space(.), "
                        "'Выполнить')]"
                    )
                )
            )

            self.safe_click(
                login_button
            )

            self.log(
                "✅ Кнопка 'Выполнить' нажата"
            )

            self.log(
                "⏳ Ждём загрузку следующей страницы 5 секунд..."
            )

            time.sleep(5)

            # =================================================
            # ПЕРЕХОД НА СТРАНИЦУ ПОЛЬЗОВАТЕЛЕЙ
            # =================================================

            self.log(
                "➡️ Переходим в управление пользователями..."
            )

            self.driver.get(
                USERS_URL
            )

            time.sleep(3)

            # =================================================
            # ПОИСК ПОЛЯ ЛОГИНА
            # =================================================

            self.log(
                "🔎 Ищем поле поиска по логину..."
            )

            search_field = WebDriverWait(
                self.driver,
                20
            ).until(
                lambda driver: self.find_login_search_field()
            )

            self.log(
                "✅ Поле поиска найдено"
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                search_field
            )

            time.sleep(0.3)

            self.driver.execute_script(
                "arguments[0].focus();",
                search_field
            )

            try:
                search_field.clear()
            except Exception:
                pass

            # =================================================
            # ВВОД ЛОГИНА
            # =================================================

            self.log(
                f"⌨️ Вводим логин: {login}"
            )

            try:

                search_field.send_keys(
                    login
                )

            except Exception:

                self.driver.execute_script(
                    """
                    arguments[0].value = arguments[1];

                    arguments[0].dispatchEvent(
                        new Event('input', { bubbles: true })
                    );

                    arguments[0].dispatchEvent(
                        new Event('change', { bubbles: true })
                    );
                    """,
                    search_field,
                    login
                )

            self.log(
                "✅ Логин введён в поле поиска"
            )

            time.sleep(0.5)

            # =================================================
            # НАЖАТИЕ ENTER (СИМУЛЯЦИЯ ПОИСКА)
            # =================================================

            self.log(
                "⏎ Нажимаем Enter..."
            )

            try:

                search_field.send_keys(
                    Keys.ENTER
                )

            except Exception:

                self.driver.execute_script(
                    """
                    arguments[0].dispatchEvent(
                        new KeyboardEvent('keydown', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            bubbles: true
                        })
                    );
                    """,
                    search_field
                )

            self.log(
                "✅ Enter нажат"
            )

            time.sleep(2)

            # =================================================
            # ПОИСК СТРОКИ РЕЗУЛЬТАТА
            # =================================================

            self.log(
                "🔎 Ищем строку результата поиска..."
            )

            result_row = WebDriverWait(
                self.driver,
                20
            ).until(
                lambda driver: self.find_result_row(login)
            )

            self.log(
                "✅ Строка результата найдена"
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                result_row
            )

            time.sleep(0.5)

            # =================================================
            # ДВОЙНОЙ КЛИК ПО СТРОКЕ РЕЗУЛЬТАТА
            # =================================================

            self.log(
                "🖱 Двойной клик по строке результата..."
            )

            try:

                ActionChains(
                    self.driver
                ).double_click(
                    result_row
                ).perform()

            except Exception:

                self.driver.execute_script(
                    """
                    const el = arguments[0];
                    const evt = new MouseEvent('dblclick', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    el.dispatchEvent(evt);
                    """,
                    result_row
                )

            self.log(
                "✅ Двойной клик выполнен"
            )

            # =================================================
            # ОЖИДАНИЕ МОДАЛКИ
            # =================================================

            self.log(
                "⏳ Ждём открытия модального окна..."
            )

            modal = self.wait_for_modal(
                timeout=15
            )

            self.log(
                "✅ Модальное окно открыто"
            )

            # =================================================
            # ДОМЕН (AD)
            # =================================================

            self.log(
                "🔎 Ищем поле домена..."
            )

            domain_field = self.find_edit_modal_field(
                modal, "k5-real", value_hint="AD"
            )

            self.log(
                "⏳ Выбираем домен: [FASP_LOCAL] Fasp.local AD"
            )

            self.select_combobox_value(
                domain_field,
                "[FASP_LOCAL] Fasp.local AD"
            )

            self.log(
                "✅ Домен выбран"
            )

            # =================================================
            # ДОСТУП
            # =================================================

            self.log(
                "🔎 Ищем поле доступа..."
            )

            access_field = self.find_edit_modal_field(
                modal, "m5-real", value_hint="не указано"
            )

            self.log(
                "⏳ Выбираем доступ: Стандартный"
            )

            self.select_combobox_value(
                access_field,
                "Стандартный"
            )

            self.log(
                "✅ Доступ выбран"
            )

            # =================================================
            # ПРОВЕРКА ПОЛЯ ПОЛА
            # =================================================

            self.log(
                "🔎 Проверяем поле пола..."
            )

            gender_field = self.find_edit_modal_field(
                modal, "65-real"
            )

            gender_value = (
                gender_field.get_attribute("value") or ""
            ).strip()

            if gender_value not in ("Муж", "Жен"):

                raise Exception(
                    f"Поле пола не заполнено корректно: '{gender_value}'"
                )

            self.log(
                f"✅ Пол заполнен корректно: {gender_value}"
            )

            # =================================================
            # КОНЕЦ ЭТАПА (ТЕСТОВЫЙ ЗАПУСК)
            # =================================================

            self.log("")
            self.log("=" * 60)
            self.log(
                "🛑 ЭТАП ЗАВЕРШЁН: домен выбран, доступ выбран, "
                "пол проверен."
            )
            self.log(
                "🛑 Дальнейшие действия пока не выполняются."
            )
            self.log("=" * 60)

            return True

        except Exception as e:

            self.log("")
            self.log("=" * 60)
            self.log(
                "❌ ОШИБКА SELENIUM"
            )
            self.log("=" * 60)

            self.log(
                repr(e)
            )

            try:

                self.driver.save_screenshot(
                    "xcollect_search_error.png"
                )

                self.log(
                    "📸 Скриншот: xcollect_search_error.png"
                )

            except Exception:
                pass

            return False


# ============================================================
# GUI
# ============================================================

ctk.set_appearance_mode(
    "dark"
)

ctk.set_default_color_theme(
    "blue"
)


class XCollectSearchApp(
    ctk.CTk
):

    def __init__(self):

        super().__init__()

        self.title(
            "XCollect — поиск пользователя"
        )

        self.geometry(
            "800x600"
        )

        self.minsize(
            700,
            520
        )

        self.build_ui()

    # ========================================================
    # GUI
    # ========================================================

    def build_ui(self):

        header = ctk.CTkFrame(
            self,
            corner_radius=0
        )

        header.pack(
            fill="x"
        )

        title = ctk.CTkLabel(
            header,
            text="XCollect User Search",
            font=ctk.CTkFont(
                size=27,
                weight="bold"
            )
        )

        title.pack(
            side="left",
            padx=25,
            pady=20
        )

        self.status_label = ctk.CTkLabel(
            header,
            text="● Готов",
            text_color="#55d66b",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )

        self.status_label.pack(
            side="right",
            padx=25
        )

        main = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        main.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        # ----------------------------------------------------
        # Запрос логина
        # ----------------------------------------------------

        ctk.CTkLabel(
            main,
            text="🔑 Запрос логина",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=5,
            pady=(0, 8)
        )

        self.login_entry = ctk.CTkEntry(
            main,
            height=42,
            font=ctk.CTkFont(
                size=15
            ),
            placeholder_text="Например: i.ivanov"
        )

        self.login_entry.pack(
            fill="x",
            padx=5
        )

        # ----------------------------------------------------
        # Найти
        # ----------------------------------------------------

        self.search_button = ctk.CTkButton(
            main,
            text="🔎  НАЙТИ ПОЛЬЗОВАТЕЛЯ",
            height=50,
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            command=self.search_clicked
        )

        self.search_button.pack(
            fill="x",
            padx=5,
            pady=(15, 20)
        )

        # ----------------------------------------------------
        # Лог
        # ----------------------------------------------------

        ctk.CTkLabel(
            main,
            text="📟 Журнал выполнения",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=5,
            pady=(0, 8)
        )

        self.log_box = ctk.CTkTextbox(
            main,
            font=ctk.CTkFont(
                family="Consolas",
                size=12
            )
        )

        self.log_box.pack(
            fill="both",
            expand=True,
            padx=5
        )

        self.log_box.configure(
            state="disabled"
        )

    # ========================================================
    # LOG
    # ========================================================

    def log(self, text):

        def update():

            self.log_box.configure(
                state="normal"
            )

            self.log_box.insert(
                "end",
                text + "\n"
            )

            self.log_box.see(
                "end"
            )

            self.log_box.configure(
                state="disabled"
            )

        self.after(
            0,
            update
        )

    # ========================================================
    # STATUS
    # ========================================================

    def set_status(self, text, color="#55d66b"):

        self.after(
            0,
            lambda:
            self.status_label.configure(
                text=text,
                text_color=color
            )
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def search_clicked(self):

        login = self.login_entry.get().strip()

        if not login:

            messagebox.showwarning(
                "Пустой логин",
                "Введите логин для поиска."
            )

            return

        self.search_button.configure(
            state="disabled"
        )

        self.set_status(
            "● Выполняется...",
            "#ffaa00"
        )

        self.log("")
        self.log("=" * 60)
        self.log(
            f"🚀 ЗАПУСК ПОИСКА: {login}"
        )
        self.log("=" * 60)

        thread = threading.Thread(
            target=self.selenium_thread,
            args=(login,),
            daemon=True
        )

        thread.start()

    # ========================================================
    # SELENIUM THREAD
    # ========================================================

    def selenium_thread(self, login):

        bot = XCollectSearch(
            self.log
        )

        success = bot.run(
            login
        )

        if success:

            self.set_status(
                "● ЭТАП ВЫПОЛНЕН",
                "#55d66b"
            )

        else:

            self.set_status(
                "● Ошибка",
                "#ff5555"
            )

            self.after(
                0,
                lambda:
                messagebox.showerror(
                    "Ошибка",
                    (
                        "Selenium завершился с ошибкой.\n"
                        "Подробности смотри в журнале."
                    )
                )
            )

        self.after(
            0,
            lambda:
            self.search_button.configure(
                state="normal"
            )
        )


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":

    app = XCollectSearchApp()

    app.mainloop()