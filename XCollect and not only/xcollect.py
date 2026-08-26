import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)

from transliterate import translit


# ============================================================
# НАСТРОЙКИ
# ============================================================

BASE_URL = "http://xcollect.fasp.local"
USERS_URL = f"{BASE_URL}/setup/usersSetup.zul"

LOGIN = "n.perepelitsa"
PASSWORD = "123456Qw"

BRANCH = "Воронеж"


# ============================================================
# БИБЛИОТЕКА ИМЁН
# ============================================================

FEMALE_NAMES = {
    "Александра", "Алина", "Алла", "Анастасия", "Ангелина", "Анна",
    "Антонина", "Валентина", "Валерия", "Варвара", "Василиса", "Вера",
    "Вероника", "Виктория", "Галина", "Дарья", "Диана", "Евгения",
    "Екатерина", "Елена", "Елизавета", "Жанна", "Зинаида", "Зоя",
    "Инесса", "Инна", "Ирина", "Камилла", "Карина", "Кира", "Клавдия",
    "Кристина", "Ксения", "Лада", "Лариса", "Лидия", "Лилия", "Любовь",
    "Людмила", "Майя", "Маргарита", "Марина", "Мария", "Надежда",
    "Наталья", "Нелли", "Нина", "Оксана", "Олеся", "Ольга", "Полина",
    "Раиса", "Регина", "Римма", "Светлана", "София", "Таисия",
    "Тамара", "Татьяна", "Ульяна", "Юлия", "Яна",

    "Гульнара", "Дилноза", "Зебо", "Мадина", "Мухлиса", "Нигора",
    "Ойдин", "Раъно", "Севара", "Феруза", "Хилола", "Шахноза",
    "Юлдуз", "Дилфуза", "Гульчехра", "Нодира", "Озода", "Хадича",
    "Фатима", "Малика", "Ширин", "Гульбахор", "Заррина", "Диёра",
    "Камола", "Лайло", "Мавзуна", "Махлиё", "Нозима", "Ойгуль",
    "Равшана", "Саодат", "Сорбон", "Угилжон", "Фарзона", "Хуснида",
    "Шоира", "Эъзоза", "Ясмин", "Барно", "Гульсара", "Дурдона",
    "Зухра", "Карима", "Мунира", "Наргиза", "Ойша", "Сайёра",
    "Толибжон", "Мухлижон", "Мухлижа",

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
    "Икром", "Кудрат", "Мурод", "Нуриддин", "Обод", "Парвиз",
    "Рустам", "Самир", "Тойир", "Умид", "Файзиддин", "Хаким",
    "Чоршанбе", "Шавкат", "Эшон", "Юнус", "Абдулла", "Ботир",
    "Ғафур", "Дилшод", "Жонибек", "Зубайр", "Илхом", "Қосим",

    "Азамат", "Айбек", "Аман", "Арстан", "Байэль", "Бекболот",
    "Бекзат", "Болот", "Борон", "Данияр", "Досбол", "Дуйшон",
    "Жаныбек", "Жениш", "Замир", "Зарлык", "Искендер", "Калыс",
    "Керим", "Кубат", "Кудайберген", "Мадияр", "Максат", "Медер",
    "Мырза", "Назар", "Нурбек", "Нурлан", "Омурбек", "Орозбек",
    "Сабыр", "Сагын", "Самат", "Сейит", "Сыдык", "Талант", "Тамырлан",
    "Темирлан", "Тугельбай", "Улан", "Улугбек", "Эдил", "Эмиль",
    "Эрмек", "Эсен", "Юсуп",
}


# ============================================================
# ТРАНСЛИТЕРАЦИЯ
# ============================================================

def transliterate_to_latin(text):
    """
    Кириллица -> латиница.
    Используем именно translit(), чтобы не было ошибки
    name 'transliterate' is not defined.
    """
    if not text:
        return ""

    return translit(text, "ru", reversed=True).lower()


def generate_login(first_name, surname):
    """
    Логин:
    первая буква имени + "." + фамилия

    Сикорский Никита
    -> n.sikorskiy
    """

    first_letter = transliterate_to_latin(first_name[0])
    surname_latin = transliterate_to_latin(surname)

    return f"{first_letter}.{surname_latin}"


# ============================================================
# ОПРЕДЕЛЕНИЕ ПОЛА
# ============================================================

def detect_gender(first_name):

    name = first_name.strip().capitalize()

    if name in FEMALE_NAMES:
        return "Ж"

    if name in MALE_NAMES:
        return "М"

    # Запасной вариант
    if name.endswith(("а", "я")):
        return "Ж"

    return "М"


# ============================================================
# ПРЕДВАРИТЕЛЬНОЕ ПРИЧЁСЫВАНИЕ ЗАЯВКИ
# ============================================================

def normalize_application(text):

    text = text.strip()

    # Убираем лишние пробелы
    text = re.sub(r"\s+", " ", text)

    # Приводим разные тире к обычному
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    return text


# ============================================================
# ПАРСЕР
# ============================================================

def parse_input(text):

    text = normalize_application(text)

    print("\n" + "=" * 70)
    print("ПРЕДВАРИТЕЛЬНО ОБРАБОТАННАЯ ЗАЯВКА")
    print("=" * 70)
    print(text)
    print("=" * 70)

    # --------------------------------------------------------
    # Ищем ВСЕ даты
    # --------------------------------------------------------

    dates = re.findall(
        r"\b\d{2}\.\d{2}\.\d{4}\b",
        text
    )

    if len(dates) < 2:
        raise ValueError(
            f"Найдено дат: {len(dates)}. "
            f"Нужно минимум 2 даты."
        )

    # В твоём новом формате:
    #
    # 24.08.2026 Сикорский Никита Юрьевич ...
    # 16.09.1994 г.р.
    #
    # Поэтому:
    #
    # первая дата = дата выхода/заявки
    # вторая дата = дата рождения
    #
    application_date = dates[0]
    birth_date = dates[1]

    # --------------------------------------------------------
    # Удаляем даты из текста
    # --------------------------------------------------------

    text_without_dates = re.sub(
        r"\b\d{2}\.\d{2}\.\d{4}\b",
        " ",
        text
    )

    # --------------------------------------------------------
    # Удаляем служебные куски
    # --------------------------------------------------------

    cleaned = text_without_dates

    cleaned = re.sub(
        r"\bг\.р\.",
        " ",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"\bдата\s+при[её]ма\b",
        " ",
        cleaned,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Ищем ФИО
    #
    # Берём первое нормальное сочетание:
    # Фамилия Имя Отчество
    # --------------------------------------------------------

    fio_match = re.search(
        r"\b([А-ЯЁ][а-яё]+)\s+"
        r"([А-ЯЁ][а-яё]+)\s+"
        r"([А-ЯЁ][а-яё]+)\b",
        cleaned
    )

    if not fio_match:

        # Запасной вариант без отчества
        fio_match = re.search(
            r"\b([А-ЯЁ][а-яё]+)\s+"
            r"([А-ЯЁ][а-яё]+)\b",
            cleaned
        )

        if not fio_match:
            raise ValueError("Не удалось определить ФИО.")

        surname = fio_match.group(1)
        first_name = fio_match.group(2)
        middle_name = ""

    else:

        surname = fio_match.group(1)
        first_name = fio_match.group(2)
        middle_name = fio_match.group(3)

    gender = detect_gender(first_name)

    return {
        "application_date": application_date,
        "surname": surname,
        "first_name": first_name,
        "middle_name": middle_name,
        "birth_date": birth_date,
        "entry_date": application_date,
        "gender": gender,
        "branch": BRANCH,
    }


# ============================================================
# ВСПОМОГАТЕЛЬНОЕ: НАЙТИ ЭЛЕМЕНТ
# ============================================================

def wait_element(xpath, timeout=15):

    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(
            (By.XPATH, xpath)
        )
    )


# ============================================================
# ВСПОМОГАТЕЛЬНОЕ: КЛИК
# ============================================================

def safe_click(element):

    try:

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(element)
        )

        element.click()

    except ElementClickInterceptedException:

        driver.execute_script(
            "arguments[0].click();",
            element
        )


# ============================================================
# ПОИСК МОДАЛЬНОГО ОКНА
# ============================================================

def get_modal():

    print("\n⏳ Ждём появления модального окна...")

    modal = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//div[contains(concat(' ', normalize-space(@class), ' '), ' z-window-modal ')]"
            )
        )
    )

    print("✅ Найдено div.z-window-modal")
    print("✅ Модальное окно действительно появилось")

    return modal


# ============================================================
# ПОИСК ПОЛЯ ВНУТРИ МОДАЛКИ
# ============================================================

def find_modal_field(modal, name):

    selectors = {

        # Фамилия
        "surname": [
            ".//input[contains(@id, 'y3') and contains(@class, 'z-textbox')]",
            ".//input[contains(@id, 'y3')]",
        ],

        # Имя
        "first_name": [
            ".//input[contains(@id, '_4') and contains(@class, 'z-textbox')]",
            ".//input[contains(@id, '_4')]",
        ],

        # Отчество
        "middle_name": [
            ".//input[contains(@id, '14') and contains(@class, 'z-textbox')]",
            ".//input[contains(@id, '14')]",
        ],

        # Сокращенное имя
        "short_name": [
            ".//input[contains(@id, '34') and contains(@class, 'z-textbox')]",
            ".//input[contains(@id, '34')]",
        ],

        # E-mail
        "email": [
            ".//input[contains(@id, '54') and contains(@class, 'z-textbox')]",
            ".//input[contains(@id, '54')]",
        ],

        # Дата рождения
        "birth_date": [
            ".//input[contains(@id, '74-real')]",
        ],

        # Пол
        "gender": [
            ".//input[contains(@id, '94-real')]",
        ],

        # Филиал
        "branch": [
            ".//input[contains(@id, 'b4-real')]",
        ],

        # Дата вхождения
        "entry_date": [
            ".//input[contains(@id, '3-real')]",
        ],

        # Логин
        "login": [
            ".//input[@name='employee_login']",
            ".//input[contains(@id, 'x2')]",
        ],
    }

    if name not in selectors:
        raise ValueError(
            f"Неизвестное поле: {name}"
        )

    for xpath in selectors[name]:

        try:

            element = modal.find_element(
                By.XPATH,
                xpath
            )

            if element.is_displayed():

                print(
                    f"✅ Поле '{name}' найдено: "
                    f"{element.get_attribute('id')}"
                )

                return element

        except NoSuchElementException:
            continue

    raise Exception(
        f"Не найдено поле '{name}' внутри модального окна."
    )


# ============================================================
# ЗАПОЛНЕНИЕ ПОЛЯ
# ============================================================

def fill_modal_field(modal, name, value):

    print(f"\n⏳ Заполняем: {name}")

    field = find_modal_field(
        modal,
        name
    )

    # Фокус через JS.
    # Это важно для ZK-модалки.
    driver.execute_script(
        "arguments[0].focus();",
        field
    )

    # Чистим
    driver.execute_script(
        """
        arguments[0].value = '';
        arguments[0].dispatchEvent(
            new Event('input', { bubbles: true })
        );
        """,
        field
    )

    # Основной вариант
    try:
        field.send_keys(value)

    except Exception:

        # Запасной JS
        driver.execute_script(
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

    print(
        f"✅ {name}: {value}"
    )


# ============================================================
# COMBOBOX
# ============================================================

def fill_combobox(modal, name, value):

    print(f"\n⏳ Выбираем: {name}")

    field = find_modal_field(
        modal,
        name
    )

    try:

        driver.execute_script(
            "arguments[0].focus();",
            field
        )

        field.send_keys(value)
        time.sleep(0.5)

        field.send_keys("\n")

    except Exception:

        driver.execute_script(
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

    print(
        f"✅ {name}: {value}"
    )


# ============================================================
# ДИАГНОСТИКА МОДАЛКИ
# ============================================================

def diagnostic_modal(modal):

    print("\n")
    print("=" * 70)
    print("ДИАГНОСТИКА МОДАЛЬНОГО ОКНА")
    print("=" * 70)

    print("\nMODAL:")
    print("tag:", modal.tag_name)
    print("id:", modal.get_attribute("id"))
    print("class:", modal.get_attribute("class"))

    print("\n---------- INPUT ----------")

    inputs = modal.find_elements(
        By.XPATH,
        ".//input"
    )

    for i, element in enumerate(inputs):

        print(
            f"[INPUT {i}] "
            f"id='{element.get_attribute('id')}' "
            f"name='{element.get_attribute('name')}' "
            f"class='{element.get_attribute('class')}' "
            f"type='{element.get_attribute('type')}' "
            f"value='{element.get_attribute('value')}'"
        )

    print("\n---------- BUTTONS ----------")

    buttons = modal.find_elements(
        By.XPATH,
        ".//button"
    )

    for i, button in enumerate(buttons):

        print(
            f"[BUTTON {i}] "
            f"id='{button.get_attribute('id')}' "
            f"class='{button.get_attribute('class')}' "
            f"text='{button.text}'"
        )

    # Сохраняем HTML
    html = modal.get_attribute("outerHTML")

    with open(
        "xcollect_modal.html",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)

    print(
        "\nHTML модального окна сохранён: "
        "xcollect_modal.html"
    )

    print("=" * 70)


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():

    global driver

    print(
        "=== Автоматическое создание пользователя в XCollect ==="
    )

    print(
        "\nВведите текст заявки:"
    )

    user_input = input(
        "\n> "
    ).strip()

    if not user_input:

        print(
            "❌ Текст не введён."
        )

        return

    # ========================================================
    # ПАРСИНГ
    # ========================================================

    try:

        data = parse_input(
            user_input
        )

    except Exception as e:

        print("\n")
        print("=" * 70)
        print("❌ ОШИБКА ПАРСИНГА")
        print("=" * 70)
        print(e)

        return

    # ========================================================
    # РАСПОЗНАННЫЕ ДАННЫЕ
    # ========================================================

    print("\n")
    print("=" * 70)
    print("РАСПОЗНАННЫЕ ДАННЫЕ")
    print("=" * 70)

    for key, value in data.items():

        print(
            f"{key:<18}: {value}"
        )

    # ========================================================
    # ГЕНЕРАЦИЯ
    # ========================================================

    login = generate_login(
        data["first_name"],
        data["surname"]
    )

    email = f"{login}@fasp.ru"

    if data["middle_name"]:

        short_name = (
            f"{data['surname']} "
            f"{data['first_name'][0]}."
            f"{data['middle_name'][0]}."
        )

    else:

        short_name = (
            f"{data['surname']} "
            f"{data['first_name'][0]}."
        )

    print("\n")
    print("=" * 70)
    print("СГЕНЕРИРОВАННЫЕ ДАННЫЕ")
    print("=" * 70)

    print(
        f"Логин:            {login}"
    )

    print(
        f"E-mail:           {email}"
    )

    print(
        f"Сокращённое имя:  {short_name}"
    )

    # ========================================================
    # CHROME
    # ========================================================

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

    driver = webdriver.Chrome(
        options=options
    )

    driver.maximize_window()

    try:

        # ====================================================
        # ЛОГИН
        # ====================================================

        print("\n")
        print("=" * 70)
        print("ЛОГИН")
        print("=" * 70)

        driver.get(
            BASE_URL
        )

        time.sleep(2)

        # ----------------------------------------------------
        # Логин
        # ----------------------------------------------------

        login_input = WebDriverWait(
            driver,
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
            LOGIN
        )

        print(
            "✅ Логин введён"
        )

        # ----------------------------------------------------
        # Пароль
        # ----------------------------------------------------

        password_input = WebDriverWait(
            driver,
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
            PASSWORD
        )

        print(
            "✅ Пароль введён"
        )

        # ----------------------------------------------------
        # ВОЙТИ
        # ----------------------------------------------------

        login_button = WebDriverWait(
            driver,
            15
        ).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(normalize-space(.), 'Выполнить')]"
                )
            )
        )

        safe_click(
            login_button
        )

        print(
            "✅ Кнопка 'Выполнить' нажата"
        )

        print(
            "⏳ Ждём загрузку XCollect 5 секунд..."
        )

        time.sleep(5)

        # ====================================================
        # СТРАНИЦА USERS
        # ====================================================

        print(
            "\n➡️ Переходим на usersSetup.zul..."
        )

        driver.get(
            USERS_URL
        )

        time.sleep(3)

        # ====================================================
        # ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ
        # ====================================================

        print("\n")
        print("=" * 70)
        print("ОТКРЫТИЕ НОВОГО ПОЛЬЗОВАТЕЛЯ")
        print("=" * 70)

        add_button = WebDriverWait(
            driver,
            15
        ).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//span[contains(normalize-space(.), "
                    "'Добавить нового пользователя')]"
                )
            )
        )

        print(
            "✅ Кнопка найдена"
        )

        safe_click(
            add_button
        )

        print(
            "✅ Кнопка нажата"
        )

        # ====================================================
        # ЖДЁМ МОДАЛКУ
        # ====================================================

        modal = get_modal()

        # ====================================================
        # ДИАГНОСТИКА
        # ====================================================

        diagnostic_modal(
            modal
        )

        # ====================================================
        # ЗАПОЛНЕНИЕ
        # ====================================================

        print("\n")
        print("=" * 70)
        print("ЗАПОЛНЕНИЕ ФОРМЫ")
        print("=" * 70)

        # ----------------------------------------------------
        # Логин
        # ----------------------------------------------------

        fill_modal_field(
            modal,
            "login",
            login
        )

        # ----------------------------------------------------
        # ФИО
        # ----------------------------------------------------

        fill_modal_field(
            modal,
            "surname",
            data["surname"]
        )

        fill_modal_field(
            modal,
            "first_name",
            data["first_name"]
        )

        fill_modal_field(
            modal,
            "middle_name",
            data["middle_name"]
        )

        fill_modal_field(
            modal,
            "short_name",
            short_name
        )

        # ----------------------------------------------------
        # Email
        # ----------------------------------------------------

        fill_modal_field(
            modal,
            "email",
            email
        )

        # ----------------------------------------------------
        # Дата рождения
        # ----------------------------------------------------

        fill_modal_field(
            modal,
            "birth_date",
            data["birth_date"]
        )

        # ----------------------------------------------------
        # Пол
        # ----------------------------------------------------

        fill_combobox(
            modal,
            "gender",
            data["gender"]
        )

        # ----------------------------------------------------
        # Филиал
        # ----------------------------------------------------

        fill_combobox(
            modal,
            "branch",
            data["branch"]
        )

        # ----------------------------------------------------
        # Дата входа
        # ----------------------------------------------------

        fill_modal_field(
            modal,
            "entry_date",
            data["entry_date"]
        )

        # ====================================================
        # СОХРАНЕНИЕ
        # ====================================================

        print("\n")
        print("=" * 70)
        print("СОХРАНЕНИЕ")
        print("=" * 70)

        save_button = modal.find_element(
            By.XPATH,
            ".//button[contains(normalize-space(.), 'Завести')]"
        )

        print(
            "✅ Кнопка 'Завести' найдена"
        )

        safe_click(
            save_button
        )

        print(
            "✅ Кнопка 'Завести' нажата"
        )

        time.sleep(3)

        print("\n")
        print("=" * 70)
        print("ГОТОВО")
        print("=" * 70)

        print(
            f"Пользователь: "
            f"{data['surname']} {data['first_name']} "
            f"{data['middle_name']}"
        )

        print(
            f"Логин: {login}"
        )

        print(
            f"E-mail: {email}"
        )

    except Exception as e:

        print("\n")
        print("=" * 70)
        print("❌ ОШИБКА SELENIUM")
        print("=" * 70)

        print(
            repr(e)
        )

        try:

            driver.save_screenshot(
                "xcollect_error.png"
            )

            print(
                "📸 Скриншот сохранён: "
                "xcollect_error.png"
            )

        except Exception:
            pass

    finally:

        input(
            "\nНажмите Enter для закрытия браузера..."
        )

        driver.quit()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()