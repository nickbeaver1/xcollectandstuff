import re
import time
import threading
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from selenium import webdriver
from selenium.webdriver.common.by import By
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
USERS_URL = "http://xcollect.fasp.local/setup/usersSetup.zul"

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
    return translit(text, "ru", reversed=True).lower()


def generate_login(first_name, surname):
    first = transliterate_to_latin(first_name[0])
    last = transliterate_to_latin(surname)

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
        raise ValueError("Заявка пустая.")

    text = re.sub(r"\s+", " ", text)

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    dates = re.findall(
        r"\b\d{2}\.\d{2}\.\d{4}\b",
        text
    )

    if len(dates) < 2:
        raise ValueError(
            f"Найдено дат: {len(dates)}. "
            "Нужно минимум две даты."
        )

    # Первая дата = дата вхождения
    # Вторая дата = дата рождения
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

    gender = detect_gender(first_name)

    login = generate_login(
        first_name,
        surname
    )

    email = f"{login}@fasp.ru"

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
                EC.element_to_be_clickable(element)
            )

            element.click()

        except ElementClickInterceptedException:

            self.driver.execute_script(
                "arguments[0].click();",
                element
            )

    # ========================================================
    # ПОИСК ПОЛЯ ПЕРВОЙ МОДАЛКИ
    # ========================================================

    def find_modal_field(self, modal, name):

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
            f"Не найдено поле '{name}' внутри модального окна."
        )

    # ========================================================
    # ЗАПОЛНЕНИЕ ОБЫЧНОГО ПОЛЯ
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

            field.send_keys(value)

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
            field.send_keys(value)

            time.sleep(0.5)

            field.send_keys("\n")

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
    # ПОИСК ВТОРОЙ МОДАЛКИ
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
    # ПОИСК ПОЛЯ ВТОРОЙ МОДАЛКИ
    # ========================================================

    def find_second_modal_field(
        self,
        modal,
        suffix
    ):

        xpaths = [
            f".//input[contains(@id, '{suffix}')]",
            f".//input[contains(@id, '{suffix.lower()}')]",
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

        # Диагностический fallback:
        # иногда ZK может менять часть ID.
        inputs = modal.find_elements(
            By.XPATH,
            ".//input"
        )

        for field in inputs:

            try:

                field_id = field.get_attribute("id") or ""

                if suffix.lower() in field_id.lower():

                    if field.is_displayed():
                        return field

            except Exception:
                pass

        raise Exception(
            f"Во второй модалке не найдено поле "
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
            f"⏳ Вторая модалка: {suffix} → {value}"
        )

        field = self.find_second_modal_field(
            modal,
            suffix
        )

        # Сначала кликаем именно по реальному input
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            field
        )

        time.sleep(0.3)

        try:

            self.safe_click(field)

        except Exception:

            self.driver.execute_script(
                "arguments[0].click();",
                field
            )

        time.sleep(0.4)

        # Вводим значение.
        # Для ZK combobox это обычно приводит
        # к появлению списка вариантов.
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

    def find_created_user(self, login):

        self.log("")
        self.log(
            "🔎 Ищем созданного пользователя..."
        )

        def search(driver):

            # ------------------------------------------------
            # Вариант 1:
            # конкретный i1-cave.z
            # ------------------------------------------------

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
        ).until(search)

        self.log(
            "✅ Пользователь найден"
        )

        return element

    # ========================================================
    # ВТОРОЙ ЭТАП
    # ========================================================

    def configure_created_user(self, login):

        self.log("")
        self.log("=" * 60)
        self.log(
            "🔧 НАСТРОЙКА СОЗДАННОГО ПОЛЬЗОВАТЕЛЯ"
        )
        self.log("=" * 60)

        # ----------------------------------------------------
        # Ждём исчезновения первой модалки
        # ----------------------------------------------------

        self.log(
            "⏳ Ждём закрытия окна создания..."
        )

        try:

            WebDriverWait(
                self.driver,
                15
            ).until(
                EC.invisibility_of_element_located(
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

        except TimeoutException:

            self.log(
                "⚠️ Модалка не исчезла за 15 секунд, "
                "продолжаем поиск пользователя..."
            )

        time.sleep(1)

        # ----------------------------------------------------
        # Ищем логин
        # ----------------------------------------------------

        user_element = self.find_created_user(
            login
        )

        # ----------------------------------------------------
        # Кликаем по логину
        # ----------------------------------------------------

        self.log(
            f"🖱 Открываем пользователя: {login}"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            user_element
        )

        time.sleep(0.5)

        try:

            self.safe_click(
                user_element
            )

        except Exception:

            self.driver.execute_script(
                "arguments[0].click();",
                user_element
            )

        self.log(
            "✅ Пользователь открыт"
        )

        # ----------------------------------------------------
        # Ждём новую модалку
        # ----------------------------------------------------

        self.log(
            "⏳ Ждём второе модальное окно..."
        )

        second_modal = self.wait_for_modal(
            timeout=15
        )

        self.log(
            "✅ Второе модальное окно найдено"
        )

        # ----------------------------------------------------
        # N4 — fasp.local
        # ----------------------------------------------------

        self.select_second_modal_combobox(
            second_modal,
            "n4-real",
            DOMAIN_VALUE
        )

        # ----------------------------------------------------
        # P4 — Доступ стандартный
        # ----------------------------------------------------

        self.select_second_modal_combobox(
            second_modal,
            "p4-real",
            ACCESS_VALUE
        )

        # ----------------------------------------------------
        # СОХРАНИТЬ
        # ----------------------------------------------------

        self.log(
            "💾 Ищем кнопку 'Сохранить'..."
        )

        save_button = WebDriverWait(
            self.driver,
            10
        ).until(
            lambda driver: second_modal.find_element(
                By.XPATH,
                ".//button[contains("
                "normalize-space(.), "
                "'Сохранить'"
                ")]"
            )
        )

        self.log(
            "✅ Кнопка 'Сохранить' найдена"
        )

        self.safe_click(
            save_button
        )

        self.log(
            "✅ Настройки пользователя сохранены"
        )

        time.sleep(2)

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

        original_window = self.driver.current_window_handle

        old_handles = set(
            self.driver.window_handles
        )

        self.log(
            "🌐 Открываем отчёт в новой вкладке..."
        )

        # ----------------------------------------------------
        # Открываем новую вкладку
        # ----------------------------------------------------

        self.driver.execute_script(
            "window.open(arguments[0], '_blank');",
            REPORT_URL
        )

        WebDriverWait(
            self.driver,
            10
        ).until(
            lambda driver:
            len(driver.window_handles) > len(old_handles)
        )

        new_handles = set(
            self.driver.window_handles
        )

        new_window = (
            new_handles - old_handles
        ).pop()

        self.driver.switch_to.window(
            new_window
        )

        self.log(
            "✅ Перешли в новую вкладку отчёта"
        )

        # ----------------------------------------------------
        # Ждём поле отчёта
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Ввод логина
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # ENTER
        # ----------------------------------------------------

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

    def run(self, data):

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
            # ЛОГИН
            # =================================================

            self.log(
                "🔐 Открываем XCollect..."
            )

            self.driver.get(
                BASE_URL
            )

            time.sleep(2)

            # Поле логина
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

            # Пароль
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

            # Кнопка входа
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
            # НОВЫЙ ЭТАП
            # =================================================

            self.configure_created_user(
                data["login"]
            )

            # =================================================
            # ОТЧЁТ
            # =================================================

            self.open_report_and_enter_login(
                data["login"]
            )

            # =================================================
            # ГОТОВО
            # =================================================

            self.log("")
            self.log("=" * 60)
            self.log(
                "🎉 ВСЯ ЦЕПОЧКА ЗАВЕРШЕНА!"
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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class XCollectApp(ctk.CTk):

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

        for row, (key, title) in enumerate(field_names):

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

    def set_status(
        self,
        text,
        color="#55d66b"
    ):

        self.after(
            0,
            lambda: self.status_label.configure(
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

            self.data[key] = entry.get().strip()

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
                "● ЦЕПОЧКА ЗАВЕРШЕНА",
                "#55d66b"
            )

            self.after(
                0,
                lambda: messagebox.showinfo(
                    "Готово",
                    (
                        "Пользователь создан и "
                        "дополнительные этапы выполнены.\n\n"
                        f"Логин: {self.data['login']}\n"
                        f"E-mail: {self.data['email']}"
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
                lambda: messagebox.showerror(
                    "Ошибка",
                    (
                        "Selenium завершился с ошибкой.\n"
                        "Подробности смотри в журнале."
                    )
                )
            )

        self.after(
            0,
            lambda: self.create_button.configure(
                state="normal"
            )
        )

        self.after(
            0,
            lambda: self.parse_button.configure(
                state="normal"
            )
        )


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":

    app = XCollectApp()

    app.mainloop()