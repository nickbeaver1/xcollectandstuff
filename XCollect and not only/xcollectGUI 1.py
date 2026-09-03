import re
import time
import threading
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
)

from transliterate import translit


# ============================================================
# НАСТРОЙКИ XCOLLECT
# ============================================================

BASE_URL = "http://xcollect.fasp.local"

USERS_URL = (
    "http://xcollect.fasp.local/setup/usersSetup.zul"
)

REPORT_URL = (
    "http://xcollect.fasp.local:81/"
    "ReportServer/Pages/ReportViewer.aspx?"
    "%2f%d0%a3%d0%bf%d1%80%d0%b0%d0%b2%d0%bb%d0%b5%d0%bd%d0%b8%d0%b5"
    "%2f01.+%d0%92%d0%bd%d0%b5%d1%81%d1%82%d0%b8+KKID+"
    "%d1%83+%d0%bd%d0%be%d0%b2%d0%be%d0%b3%d0%be+"
    "%d1%81%d0%be%d1%82%d1%80%d1%83%d0%b4%d0%bd%d0%b8%d0%ba%d0%b0"
    "&rs:Command=Render"
)

XCOLLECT_LOGIN = "n.perepelitsa"
XCOLLECT_PASSWORD = "123456Qw"

DEFAULT_BRANCH = "Воронеж"

DOMAIN_VALUE = "fasp.local"
ACCESS_VALUE = "Доступ стандартный"

SECOND_SCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "xcollect_second.py"
)

CHROME_DEBUG_PORT = 9222


# ============================================================
# ИМЕНА ДЛЯ ОПРЕДЕЛЕНИЯ ПОЛА
# ============================================================

FEMALE_NAMES = {
    "Александра", "Алина", "Алла", "Анастасия", "Ангелина", "Анна",
    "Антонина", "Валентина", "Валерия", "Варвара", "Василиса", "Вера",
    "Вероника", "Виктория", "Галина", "Дарья", "Диана", "Евгения",
    "Екатерина", "Елена", "Елизавета", "Жанна", "Зинаида", "Зоя",
    "Инесса", "Инна", "Ирина", "Камилла", "Карина", "Кира", "Клавдия",
    "Кристина", "Ксения", "Лада", "Лариса", "Лидия", "Лилия",
    "Любовь", "Людмила", "Майя", "Маргарита", "Марина", "Мария",
    "Надежда", "Наталья", "Нелли", "Нина", "Оксана", "Олеся", "Ольга",
    "Полина", "Раиса", "Регина", "Римма", "Светлана", "София",
    "Таисия", "Тамара", "Татьяна", "Ульяна", "Юлия", "Яна",

    "Гульнара", "Дилноза", "Зебо", "Мадина", "Мухлиса", "Нигора",
    "Ойдин", "Раъно", "Севара", "Феруза", "Хилола", "Шахноза",
    "Юлдуз", "Дилфуза", "Гульчехра", "Нодира", "Озода", "Хадича",
    "Фатима", "Малика", "Ширин", "Гульбахор", "Заррина", "Диёра",
    "Камола", "Лайло", "Мавзуна", "Махлиё", "Нозима", "Ойгуль",
    "Равшана", "Саодат", "Сорбон", "Угилжон", "Фарзона", "Хуснида",
    "Шоира", "Эъзоза", "Ясмин", "Барно", "Гульсара", "Дурдона",
    "Зухра", "Карима", "Мунира", "Наргиза", "Ойша", "Сайёра",
    "Мухлижон", "Мухлижа",

    "Айгуль", "Айдай", "Айсулуу", "Акжаркын", "Алтынай", "Арууке",
    "Бактыгуль", "Береке", "Гульзат", "Гульмира", "Дамира", "Динара",
    "Жамиля", "Жибек", "Жылдыз", "Зульфия", "Индира", "Каныкей",
    "Кундуз", "Мира", "Назгуль", "Нургуль", "Нурия", "Перизат",
    "Рахат", "Саадат", "Сабина", "Саида", "Салтанат", "Самара",
    "Сауле", "Сезим", "Томирис", "Уулкан", "Фарида", "Халида",
    "Чинара", "Шахло", "Эльвира", "Эмилия",
}


MALE_NAMES = {
    "Александр", "Алексей", "Анатолий", "Андрей", "Антон", "Аркадий",
    "Арсений", "Артём", "Борис", "Вадим", "Валентин", "Валерий",
    "Василий", "Виктор", "Виталий", "Владимир", "Владислав",
    "Вячеслав", "Геннадий", "Георгий", "Глеб", "Григорий", "Даниил",
    "Денис", "Дмитрий", "Евгений", "Егор", "Иван", "Игорь", "Илья",
    "Кирилл", "Константин", "Лев", "Леонид", "Максим", "Марат",
    "Марк", "Матвей", "Михаил", "Никита", "Николай", "Олег", "Павел",
    "Пётр", "Роман", "Руслан", "Сергей", "Станислав", "Степан",
    "Тимофей", "Фёдор", "Юрий", "Ярослав",

    "Абдурашид", "Алишер", "Бахром", "Дониёр", "Зоир", "Ислом",
    "Карим", "Лутфи", "Мухаммад", "Нодир", "Одил", "Равшан", "Сардор",
    "Темур", "Улугбек", "Фарход", "Хусниддин", "Шухрат", "Эркин",
    "Ясин", "Азиз", "Бекзод", "Гулом", "Даврон", "Жамшид", "Зокир",
    "Икром", "Кудрат", "Мурод", "Нуриддин", "Обод", "Парвиз", "Рустам",
    "Самир", "Тойир", "Умид", "Файзиддин", "Хаким", "Чоршанбе",
    "Шавкат", "Эшон", "Юнус", "Абдулла", "Ботир", "Ғафур", "Дилшод",
    "Жонибек", "Зубайр", "Илхом", "Қосим",

    "Азамат", "Айбек", "Аман", "Арстан", "Байэль", "Бекболот", "Бекзат",
    "Болот", "Борон", "Данияр", "Досбол", "Дуйшон", "Жаныбек", "Жениш",
    "Замир", "Зарлык", "Искендер", "Калыс", "Керим", "Кубат",
    "Кудайберген", "Мадияр", "Максат", "Медер", "Мырза", "Назар",
    "Нурбек", "Нурлан", "Омурбек", "Орозбек", "Сабыр", "Сагын",
    "Самат", "Сейит", "Сыдык", "Талант", "Тамырлан", "Темирлан",
    "Тугельбай", "Улан", "Улугбек", "Эдил", "Эмиль", "Эрмек", "Эсен",
    "Юсуп",
}


# ============================================================
# ПАРСЕР
# ============================================================

def transliterate_to_latin(text):
    return translit(
        text,
        "ru",
        reversed=True
    ).lower()


def generate_login(first_name, surname):
    first = transliterate_to_latin(
        first_name[0]
    )

    last = transliterate_to_latin(
        surname
    )

    return f"{first}.{last}"


def detect_gender(first_name):

    name = first_name.strip().capitalize()

    if name in FEMALE_NAMES:
        return "Ж"

    if name in MALE_NAMES:
        return "М"

    if name.endswith(("а", "я")):
        return "Ж"

    return "М"


def parse_application(text):

    text = text.strip()

    if not text:
        raise ValueError(
            "Заявка пустая."
        )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = text.replace(
        "–",
        "-"
    )

    text = text.replace(
        "—",
        "-"
    )

    dates = re.findall(
        r"\b\d{2}\.\d{2}\.\d{4}\b",
        text
    )

    if len(dates) < 2:
        raise ValueError(
            f"Найдено дат: {len(dates)}. "
            "Нужно минимум две даты."
        )

    entry_date = dates[0]
    birth_date = dates[1]

    cleaned = re.sub(
        r"\b\d{2}\.\d{2}\.\d{4}\b",
        " ",
        text
    )

    fio_match = re.search(
        r"\b"
        r"([А-ЯЁ][а-яё]+)"
        r"\s+"
        r"([А-ЯЁ][а-яё]+)"
        r"\s+"
        r"([А-ЯЁ][а-яё]+)"
        r"\b",
        cleaned
    )

    if fio_match:

        surname = fio_match.group(1)
        first_name = fio_match.group(2)
        middle_name = fio_match.group(3)

    else:

        fio_match = re.search(
            r"\b"
            r"([А-ЯЁ][а-яё]+)"
            r"\s+"
            r"([А-ЯЁ][а-яё]+)"
            r"\b",
            cleaned
        )

        if not fio_match:
            raise ValueError(
                "Не удалось определить ФИО."
            )

        surname = fio_match.group(1)
        first_name = fio_match.group(2)
        middle_name = ""

    gender = detect_gender(
        first_name
    )

    login = generate_login(
        first_name,
        surname
    )

    email = (
        f"{login}@fasp.ru"
    )

    if middle_name:

        short_name = (
            f"{surname} "
            f"{first_name[0]}."
            f"{middle_name[0]}."
        )

    else:

        short_name = (
            f"{surname} "
            f"{first_name[0]}."
        )

    return {
        "surname": surname,
        "first_name": first_name,
        "middle_name": middle_name,
        "birth_date": birth_date,
        "entry_date": entry_date,
        "gender": gender,
        "branch": DEFAULT_BRANCH,
        "login": login,
        "email": email,
        "short_name": short_name,
    }


# ============================================================
# SELENIUM
# ============================================================

class XCollectSelenium:

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
    # ПЕРВАЯ МОДАЛКА
    # ========================================================

    def find_modal_field(
        self,
        modal,
        name
    ):

        selectors = {

            "surname": [
                ".//input[contains(@id, 'y3') and contains(@class, 'z-textbox')]",
                ".//input[contains(@id, 'y3')]",
            ],

            "first_name": [
                ".//input[contains(@id, '_4') and contains(@class, 'z-textbox')]",
                ".//input[contains(@id, '_4')]",
            ],

            "middle_name": [
                ".//input[contains(@id, '14') and contains(@class, 'z-textbox')]",
                ".//input[contains(@id, '14')]",
            ],

            "short_name": [
                ".//input[contains(@id, '34') and contains(@class, 'z-textbox')]",
                ".//input[contains(@id, '34')]",
            ],

            "email": [
                ".//input[contains(@id, '54') and contains(@class, 'z-textbox')]",
                ".//input[contains(@id, '54')]",
            ],

            "birth_date": [
                ".//input[contains(@id, '74-real')]",
            ],

            "gender": [
                ".//input[contains(@id, '94-real')]",
            ],

            "branch": [
                ".//input[contains(@id, 'b4-real')]",
            ],

            "entry_date": [
                ".//input[contains(@id, '3-real')]",
            ],

            "login": [
                ".//input[@name='employee_login']",
                ".//input[contains(@id, 'x2')]",
            ],
        }

        for xpath in selectors[name]:

            try:

                element = modal.find_element(
                    By.XPATH,
                    xpath
                )

                if element.is_displayed():
                    return element

            except NoSuchElementException:
                continue

        raise Exception(
            f"Не найдено поле '{name}' "
            "внутри модального окна."
        )

    # ========================================================
    # ЗАПОЛНЕНИЕ ПОЛЯ
    # ========================================================

    def fill_modal_field(
        self,
        modal,
        name,
        value
    ):

        self.log(
            f"⏳ Заполняем: {name}"
        )

        field = self.find_modal_field(
            modal,
            name
        )

        self.driver.execute_script(
            "arguments[0].focus();",
            field
        )

        try:
            field.clear()
        except Exception:
            pass

        try:

            field.send_keys(
                value
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
                field,
                value
            )

        self.log(
            f"✅ {name}: {value}"
        )

    # ========================================================
    # COMBOBOX ПЕРВОЙ МОДАЛКИ
    # ========================================================

    def fill_combobox(
        self,
        modal,
        name,
        value
    ):

        self.log(
            f"⏳ Выбираем: {name} → {value}"
        )

        field = self.find_modal_field(
            modal,
            name
        )

        self.driver.execute_script(
            "arguments[0].focus();",
            field
        )

        try:

            field.clear()

            field.send_keys(
                value
            )

            time.sleep(0.5)

            field.send_keys(
                "\n"
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
                field,
                value
            )

        self.log(
            f"✅ {name}: {value}"
        )

    # ========================================================
    # ПОИСК МОДАЛКИ
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
    # ВТОРАЯ МОДАЛКА
    # ========================================================

    def find_second_modal_field(
        self,
        modal,
        suffix
    ):

        xpaths = [

            f".//input[contains(@id, '{suffix}')]",

            f".//input[contains("
            f"@id, '{suffix.lower()}'"
            f")]",

        ]

        for xpath in xpaths:

            try:

                field = modal.find_element(
                    By.XPATH,
                    xpath
                )

                if field.is_displayed():
                    return field

            except NoSuchElementException:
                pass

        inputs = modal.find_elements(
            By.XPATH,
            ".//input"
        )

        for field in inputs:

            try:

                field_id = (
                    field.get_attribute("id")
                    or ""
                )

                if suffix.lower() in field_id.lower():

                    if field.is_displayed():
                        return field

            except Exception:
                pass

        raise Exception(
            "Во второй модалке не найдено поле "
            f"с окончанием ID '{suffix}'."
        )

    # ========================================================
    # ВЫБОР ВО ВТОРОЙ МОДАЛКЕ
    # ========================================================

    def select_second_modal_combobox(
        self,
        modal,
        suffix,
        value
    ):

        self.log(
            f"⏳ Вторая модалка: "
            f"{suffix} → {value}"
        )

        field = self.find_second_modal_field(
            modal,
            suffix
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            field
        )

        time.sleep(0.3)

        try:

            self.safe_click(
                field
            )

        except Exception:

            self.driver.execute_script(
                "arguments[0].click();",
                field
            )

        time.sleep(0.4)

        try:

            field.send_keys(
                value
            )

            time.sleep(0.5)

            field.send_keys(
                "\n"
            )

        except Exception:

            self.driver.execute_script(
                """
                arguments[0].value = arguments[1];

                arguments[0].dispatchEvent(
                    new Event('input', {bubbles:true})
                );

                arguments[0].dispatchEvent(
                    new Event('change', {bubbles:true})
                );

                arguments[0].dispatchEvent(
                    new Event('blur', {bubbles:true})
                );
                """,
                field,
                value
            )

        time.sleep(0.5)

        self.log(
            f"✅ Выбрано: {value}"
        )

    # ========================================================
    # ПОИСК СОЗДАННОГО ПОЛЬЗОВАТЕЛЯ
    # ========================================================

    def find_created_user(
        self,
        login
    ):

        self.log("")
        self.log(
            "🔎 Ищем созданного пользователя..."
        )

        def search(driver):

            xpaths = [

                (
                    "//input[contains(@id, 'i1-cave') "
                    "and @value="
                    f"'{login}']"
                ),

                (
                    "//input[contains(@id, 'i1-cave') "
                    "and contains(@value, "
                    f"'{login}')]"
                ),

                (
                    "//input[@value="
                    f"'{login}']"
                ),

                (
                    "//*[normalize-space(text())="
                    f"'{login}']"
                ),

                (
                    "//*[contains(normalize-space(text()), "
                    f"'{login}')]"
                ),
            ]

            for xpath in xpaths:

                try:

                    elements = driver.find_elements(
                        By.XPATH,
                        xpath
                    )

                    for element in elements:

                        try:

                            if element.is_displayed():
                                return element

                        except Exception:
                            pass

                except Exception:
                    pass

            return False

        element = WebDriverWait(
            self.driver,
            20
        ).until(
            search
        )

        self.log(
            "✅ Пользователь найден"
        )

        return element

    # ========================================================
    # НОВЫЙ ЭТАП:
    # Qx.z-textbox → Qb1.z-button
    # → Qh2.z-listcell → ПКМ
    # → Qv1-a.z-menuitem-content
    # ========================================================

    def configure_created_user(
        self,
        login
    ):

        self.log("")
        self.log("=" * 60)
        self.log(
            "🔧 НАСТРОЙКА СОЗДАННОГО ПОЛЬЗОВАТЕЛЯ"
        )
        self.log("=" * 60)

        # ----------------------------------------------------
        # Снова открываем управление пользователями
        # ----------------------------------------------------

        self.log(
            "🌐 Снова открываем управление пользователями..."
        )

        self.driver.get(
            USERS_URL
        )

        time.sleep(3)

        # ----------------------------------------------------
        # Qx.z-textbox
        # ----------------------------------------------------

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

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            search_input
        )

        time.sleep(0.3)

        search_input.click()

        search_input.clear()

        search_input.send_keys(
            login
        )

        self.log(
            f"✅ В поиск введён логин: {login}"
        )

        # ----------------------------------------------------
        # Qb1.z-button
        # ----------------------------------------------------

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

        self.safe_click(
            search_button
        )

        self.log(
            "✅ Кнопка поиска нажата"
        )

        # ----------------------------------------------------
        # Ждём появления результата
        # ----------------------------------------------------

        self.log(
            "⏳ Ждём результат поиска..."
        )

        time.sleep(2)

        # ----------------------------------------------------
        # Qh2.z-listcell
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # ПКМ по Qh2.z-listcell
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Qv1-a.z-menuitem-content
        # ----------------------------------------------------

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
                    "and contains(@class, 'z-menuitem-content')]"
                )
            )
        )

        self.log(
            "✅ Qv1-a.z-menuitem-content найден"
        )

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

        # ----------------------------------------------------
        # Ждём модальное окно
        # ----------------------------------------------------

        self.log(
            "⏳ Ждём новое модальное окно..."
        )

        modal = self.wait_for_modal(
            timeout=15
        )

        self.log(
            "✅ МОДАЛЬНОЕ ОКНО ОТКРЫТО"
        )

        self.log(
            "🛑 Останавливаемся на этом этапе."
        )

        # Пока модалку НЕ трогаем.
        return modal

    # ========================================================
    # ЗАПУСК ВТОРОГО СКРИПТА
    # ========================================================

    def launch_second_script(self, login):

        self.log("")
        self.log("=" * 60)
        self.log(
            "➡️ ПЕРЕДАЁМ УПРАВЛЕНИЕ ВТОРОМУ ФАЙЛУ"
        )
        self.log("=" * 60)

        if not os.path.exists(SECOND_SCRIPT):
            raise FileNotFoundError(
                f"Второй файл не найден:\n{SECOND_SCRIPT}"
            )

        self.log(
            f"📂 Второй файл: {SECOND_SCRIPT}"
        )

        self.log(
            f"👤 Передаём логин: {login}"
        )

        subprocess.Popen(
            [
                sys.executable,
                SECOND_SCRIPT,
                login
            ],
            cwd=os.path.dirname(SECOND_SCRIPT)
        )

        self.log(
            "✅ Второй файл запущен"
        )


    # ========================================================
    # ОТЧЁТ
    # ========================================================

    def open_report_and_enter_login(
        self,
        login
    ):

        self.log("")
        self.log("=" * 60)
        self.log(
            "📊 ОТЧЁТ KKID"
        )
        self.log("=" * 60)

        old_handles = set(
            self.driver.window_handles
        )

        self.log(
            "🌐 Открываем отчёт в новой вкладке..."
        )

        self.driver.execute_script(
            "window.open(arguments[0], '_blank');",
            REPORT_URL
        )

        WebDriverWait(
            self.driver,
            10
        ).until(
            lambda driver:
            len(driver.window_handles)
            > len(old_handles)
        )

        new_handles = (
            set(self.driver.window_handles)
            - old_handles
        )

        new_window = new_handles.pop()

        self.driver.switch_to.window(
            new_window
        )

        self.log(
            "✅ Перешли в новую вкладку отчёта"
        )

        self.log(
            "⏳ Ждём поле логина отчёта..."
        )

        report_input = WebDriverWait(
            self.driver,
            30
        ).until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "ReportViewerControl_ctl04_ctl03_txtValue"
                )
            )
        )

        WebDriverWait(
            self.driver,
            10
        ).until(
            EC.visibility_of(
                report_input
            )
        )

        self.log(
            "✅ Поле отчёта найдено"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            report_input
        )

        self.driver.execute_script(
            "arguments[0].focus();",
            report_input
        )

        report_input.clear()

        report_input.send_keys(
            login
        )

        self.log(
            f"✅ В отчёт введён логин: {login}"
        )

        report_input.send_keys(
            "\n"
        )

        self.log(
            "⏎ Нажат Enter"
        )

        time.sleep(3)

        self.log(
            "✅ Этап отчёта завершён"
        )

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
        data
    ):

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

            # =================================================
            # REMOTE DEBUGGING
            # =================================================

            options.add_argument(
                f"--remote-debugging-port={CHROME_DEBUG_PORT}"
            )

            self.driver = webdriver.Chrome(
                options=options
            )

            self.driver.maximize_window()

            # =================================================
            # ЛОГИН
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
            # USERS
            # =================================================

            self.log(
                "➡️ Переходим в управление пользователями..."
            )

            self.driver.get(
                USERS_URL
            )

            time.sleep(3)

            # =================================================
            # НОВЫЙ ПОЛЬЗОВАТЕЛЬ
            # =================================================

            self.log(
                "🔎 Ищем 'Добавить нового пользователя'..."
            )

            add_button = WebDriverWait(
                self.driver,
                15
            ).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//span[contains("
                        "normalize-space(.), "
                        "'Добавить нового пользователя'"
                        ")]"
                    )
                )
            )

            self.log(
                "✅ Кнопка найдена"
            )

            self.safe_click(
                add_button
            )

            self.log(
                "✅ Кнопка нажата"
            )

            # =================================================
            # ПЕРВАЯ МОДАЛКА
            # =================================================

            self.log(
                "⏳ Ждём появления модального окна..."
            )

            modal = self.wait_for_modal(
                timeout=15
            )

            self.log(
                "✅ Модальное окно найдено"
            )

            # =================================================
            # ЗАПОЛНЕНИЕ ПЕРВОЙ МОДАЛКИ
            # =================================================

            self.fill_modal_field(
                modal,
                "login",
                data["login"]
            )

            self.fill_modal_field(
                modal,
                "surname",
                data["surname"]
            )

            self.fill_modal_field(
                modal,
                "first_name",
                data["first_name"]
            )

            self.fill_modal_field(
                modal,
                "middle_name",
                data["middle_name"]
            )

            self.fill_modal_field(
                modal,
                "short_name",
                data["short_name"]
            )

            self.fill_modal_field(
                modal,
                "email",
                data["email"]
            )

            self.fill_modal_field(
                modal,
                "birth_date",
                data["birth_date"]
            )

            self.fill_combobox(
                modal,
                "gender",
                data["gender"]
            )

            self.fill_combobox(
                modal,
                "branch",
                data["branch"]
            )

            self.fill_modal_field(
                modal,
                "entry_date",
                data["entry_date"]
            )

            # =================================================
            # СОЗДАТЬ
            # =================================================

            self.log(
                "💾 Ищем кнопку 'Завести'..."
            )

            save_button = modal.find_element(
                By.XPATH,
                ".//button[contains("
                "normalize-space(.), "
                "'Завести'"
                ")]"
            )

            self.log(
                "✅ Кнопка 'Завести' найдена"
            )

            self.safe_click(
                save_button
            )

            self.log(
                "🚀 Кнопка 'Завести' нажата"
            )

            time.sleep(3)

            # =================================================
            # НАСТРОЙКА СОЗДАННОГО ПОЛЬЗОВАТЕЛЯ
            # =================================================

            self.configure_created_user(
                data["login"]
            )

            # =================================================
            # ПЕРЕДАЧА ВТОРОМУ ФАЙЛУ
            # =================================================

            self.log("")
            self.log("=" * 60)
            self.log(
                "🟢 ПЕРВАЯ ЧАСТЬ ЗАВЕРШЕНА"
            )
            self.log(
                "🟢 МОДАЛЬНОЕ ОКНО ОТКРЫТО"
            )
            self.log("=" * 60)

            self.launch_second_script(
                data["login"]
            )

            self.log(
                "➡️ Первый файл завершил свою работу."
            )

            self.log(
                "➡️ Продолжение выполняет xcollect_second.py"
            )

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
                    "xcollect_error.png"
                )

                self.log(
                    "📸 Скриншот: xcollect_error.png"
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


class XCollectApp(
    ctk.CTk
):

    def __init__(self):

        super().__init__()

        self.title(
            "XCollect — создание пользователя"
        )

        self.geometry(
            "1050x820"
        )

        self.minsize(
            900,
            700
        )

        self.data = None

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
            text="XCollect User Creator",
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

        main = ctk.CTkScrollableFrame(
            self
        )

        main.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        # ----------------------------------------------------
        # Заявка
        # ----------------------------------------------------

        ctk.CTkLabel(
            main,
            text="📋 Заявка",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=5,
            pady=(0, 8)
        )

        self.application_text = ctk.CTkTextbox(
            main,
            height=130,
            font=ctk.CTkFont(
                size=14
            )
        )

        self.application_text.pack(
            fill="x",
            padx=5
        )

        # ----------------------------------------------------
        # Распознать
        # ----------------------------------------------------

        self.parse_button = ctk.CTkButton(
            main,
            text="🔎  РАСПОЗНАТЬ ЗАЯВКУ",
            height=45,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            ),
            command=self.parse_clicked
        )

        self.parse_button.pack(
            fill="x",
            padx=5,
            pady=15
        )

        # ----------------------------------------------------
        # Данные
        # ----------------------------------------------------

        ctk.CTkLabel(
            main,
            text="👤 Данные пользователя",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=5,
            pady=(10, 10)
        )

        fields_frame = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )

        fields_frame.pack(
            fill="x",
            padx=5
        )

        self.fields = {}

        field_names = [
            ("surname", "Фамилия"),
            ("first_name", "Имя"),
            ("middle_name", "Отчество"),
            ("birth_date", "Дата рождения"),
            ("entry_date", "Дата вхождения"),
            ("gender", "Пол"),
            ("branch", "Филиал"),
        ]

        for row, (
            key,
            title
        ) in enumerate(field_names):

            label = ctk.CTkLabel(
                fields_frame,
                text=title,
                width=150,
                anchor="w",
                font=ctk.CTkFont(
                    size=14,
                    weight="bold"
                )
            )

            label.grid(
                row=row,
                column=0,
                padx=8,
                pady=5,
                sticky="w"
            )

            entry = ctk.CTkEntry(
                fields_frame,
                height=36,
                font=ctk.CTkFont(
                    size=14
                )
            )

            entry.grid(
                row=row,
                column=1,
                padx=8,
                pady=5,
                sticky="ew"
            )

            self.fields[key] = entry

        fields_frame.grid_columnconfigure(
            1,
            weight=1
        )

        # ----------------------------------------------------
        # Учётная запись
        # ----------------------------------------------------

        ctk.CTkLabel(
            main,
            text="🔐 Учетная запись",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=5,
            pady=(20, 10)
        )

        account_frame = ctk.CTkFrame(
            main
        )

        account_frame.pack(
            fill="x",
            padx=5
        )

        self.login_entry = self.make_account_field(
            account_frame,
            "Логин",
            0
        )

        self.email_entry = self.make_account_field(
            account_frame,
            "E-mail",
            1
        )

        self.short_entry = self.make_account_field(
            account_frame,
            "Сокращенное имя",
            2
        )

        # ----------------------------------------------------
        # Создать
        # ----------------------------------------------------

        self.create_button = ctk.CTkButton(
            main,
            text="🚀  СОЗДАТЬ ПОЛЬЗОВАТЕЛЯ",
            height=52,
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            command=self.create_clicked,
            state="disabled"
        )

        self.create_button.pack(
            fill="x",
            padx=5,
            pady=(25, 15)
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
            pady=(10, 8)
        )

        self.log_box = ctk.CTkTextbox(
            main,
            height=180,
            font=ctk.CTkFont(
                family="Consolas",
                size=12
            )
        )

        self.log_box.pack(
            fill="x",
            padx=5,
            pady=(0, 15)
        )

        self.log_box.configure(
            state="disabled"
        )

    # ========================================================
    # ACCOUNT FIELD
    # ========================================================

    def make_account_field(
        self,
        parent,
        title,
        row
    ):

        label = ctk.CTkLabel(
            parent,
            text=title,
            width=150,
            anchor="w",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )

        label.grid(
            row=row,
            column=0,
            padx=12,
            pady=8,
            sticky="w"
        )

        entry = ctk.CTkEntry(
            parent,
            height=36,
            font=ctk.CTkFont(
                size=14
            )
        )

        entry.grid(
            row=row,
            column=1,
            padx=12,
            pady=8,
            sticky="ew"
        )

        parent.grid_columnconfigure(
            1,
            weight=1
        )

        return entry

    # ========================================================
    # LOG
    # ========================================================

    def log(
        self,
        text
    ):

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

    def set_status(
        self,
        text,
        color="#55d66b"
    ):

        self.after(
            0,
            lambda:
            self.status_label.configure(
                text=text,
                text_color=color
            )
        )

    # ========================================================
    # PARSE
    # ========================================================

    def parse_clicked(self):

        text = self.application_text.get(
            "1.0",
            "end"
        ).strip()

        if not text:

            messagebox.showwarning(
                "Пустая заявка",
                "Вставь текст заявки."
            )

            return

        try:

            data = parse_application(
                text
            )

        except Exception as e:

            messagebox.showerror(
                "Ошибка распознавания",
                str(e)
            )

            self.set_status(
                "● Ошибка",
                "#ff5555"
            )

            return

        self.data = data

        for key, entry in self.fields.items():

            entry.delete(
                0,
                "end"
            )

            entry.insert(
                0,
                data[key]
            )

        self.login_entry.delete(
            0,
            "end"
        )

        self.login_entry.insert(
            0,
            data["login"]
        )

        self.email_entry.delete(
            0,
            "end"
        )

        self.email_entry.insert(
            0,
            data["email"]
        )

        self.short_entry.delete(
            0,
            "end"
        )

        self.short_entry.insert(
            0,
            data["short_name"]
        )

        self.create_button.configure(
            state="normal"
        )

        self.set_status(
            "● Заявка распознана",
            "#55d66b"
        )

        self.log(
            "✅ Заявка успешно распознана."
        )

        self.log(
            f"   {data['surname']} "
            f"{data['first_name']} "
            f"{data['middle_name']}"
        )

        self.log(
            f"   Логин: {data['login']}"
        )

    # ========================================================
    # СОЗДАНИЕ
    # ========================================================

    def create_clicked(self):

        if not self.data:

            messagebox.showwarning(
                "Нет данных",
                "Сначала распознай заявку."
            )

            return

        for key, entry in self.fields.items():

            self.data[key] = (
                entry.get().strip()
            )

        self.data["login"] = (
            self.login_entry.get().strip()
        )

        self.data["email"] = (
            self.email_entry.get().strip()
        )

        self.data["short_name"] = (
            self.short_entry.get().strip()
        )

        required = [
            "surname",
            "first_name",
            "birth_date",
            "entry_date",
            "login",
            "email",
        ]

        for key in required:

            if not self.data.get(key):

                messagebox.showerror(
                    "Не хватает данных",
                    f"Поле '{key}' пустое."
                )

                return

        answer = messagebox.askyesno(
            "Создание пользователя",
            (
                "Создать пользователя?\n\n"
                f"ФИО: {self.data['surname']} "
                f"{self.data['first_name']} "
                f"{self.data['middle_name']}\n"
                f"Логин: {self.data['login']}\n"
                f"E-mail: {self.data['email']}"
            )
        )

        if not answer:
            return

        self.create_button.configure(
            state="disabled"
        )

        self.parse_button.configure(
            state="disabled"
        )

        self.set_status(
            "● Выполняется...",
            "#ffaa00"
        )

        self.log("")
        self.log("=" * 60)
        self.log(
            "🚀 ЗАПУСК SELENIUM"
        )
        self.log("=" * 60)

        thread = threading.Thread(
            target=self.selenium_thread,
            daemon=True
        )

        thread.start()

    # ========================================================
    # SELENIUM THREAD
    # ========================================================

    def selenium_thread(self):

        bot = XCollectSelenium(
            self.log
        )

        success = bot.run(
            self.data
        )

        if success:

            self.set_status(
                "● ЭТАП ВЫПОЛНЕН",
                "#55d66b"
            )

            self.after(
                0,
                lambda:
                messagebox.showinfo(
                    "Готово",
                    (
                        "Цепочка дошла до "
                        "нового модального окна.\n\n"
                        f"Логин: {self.data['login']}\n\n"
                        "Дальнейшие действия пока "
                        "не выполнялись."
                    )
                )
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
            self.create_button.configure(
                state="normal"
            )
        )

        self.after(
            0,
            lambda:
            self.parse_button.configure(
                state="normal"
            )
        )


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":

    app = XCollectApp()

    app.mainloop()