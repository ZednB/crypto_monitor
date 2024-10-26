import csv
import time

from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc


# Настройка веб-драйвера
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.add_argument('--headless')  # Запуск в фоновом режиме
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# def refresh_page_if_needed(driver):
#     try:
#         # Поиск кнопки "Обновить"
#         refresh_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Обновить')]"))
#         )
#         # Клик по кнопке "Обновить"
#         refresh_button.click()
#         print("Страница обновлена.")
#     except:
#         # Кнопка "Обновить" не найдена, продолжаем без обновления
#         print("Кнопка 'Обновить' не найдена.")


def monitor_wildberries(driver, search_key):
    driver.get('https://www.wildberries.ru/')
    print("Открыта страница:", 'https://www.wildberries.ru/')

    try:
        # Ожидание загрузки поля ввода поиска
        print("Ожидание поля ввода поиска...")
        search_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'searchInput'))
        )
        print("Поле ввода найдено, ввод ключевого слова...")
        search_box.send_keys(search_key)

        # Поиск кнопки отправки и клик по ней
        print("Поиск кнопки отправки...")
        search_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'applySearchBtn'))
        )
        search_button.click()
        print("Поиск выполнен для ключевого слова:", search_key)

        # Ожидание загрузки карточки товара
        print("Ожидание загрузки карточки товара...")
        # product_list = WebDriverWait(driver, 10).until(
        #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.product-card'))
        # )
        retries = 3  # Количество повторных попыток в случае ошибки
        found = False  # Флаг для отслеживания, был ли найден релевантный товар
        while retries > 0 and not found:  # Добавляем проверку, чтобы цикл завершался после нахождения товара
            try:
                product_list = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.product-card'))
                )

                # Перебираем товары до тех пор, пока не найдем релевантный
                for product in product_list:
                    # Скролл к продукту для уверенности, что элемент виден
                    driver.execute_script("arguments[0].scrollIntoView();", product)

                    # Извлечение названия товара из атрибута aria-label
                    product_name = product.find_element(By.CSS_SELECTOR, '.product-card__link').get_attribute(
                        'aria-label').strip()

                    # Проверка релевантности товара
                    if search_key.lower() in product_name.lower():
                        if not found:  # Если товар еще не был найден
                            # Извлечение цены товара
                            try:
                                product_price = product.find_element(By.CSS_SELECTOR,
                                                                     '.price__lower-price').text.strip()
                            except:
                                product_price = product.find_element(By.CSS_SELECTOR,
                                                                     '.product-card__price').text.strip()

                            print(f"Товар найден: {product_name}, Цена: {product_price}")
                            found = True  # Устанавливаем флаг, что товар найден
                            break  # Прерываем цикл после нахождения первого релевантного товара

                    else:
                        print(f"Найден нерелевантный товар: {product_name}")

                if not found:
                    print("Релевантных товаров не найдено")
                    return {'name': None, 'price': None}

            except StaleElementReferenceException:
                print("Элемент устарел, повторная попытка...")
                retries -= 1
                if retries == 0:
                    raise Exception("Не удалось получить актуальные элементы страницы после нескольких попыток.")
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None


# def monitor_ozon(driver, search_key):
#     retries = 3  # Количество повторных попыток
#     for attempt in range(retries):
#         try:
#             driver.get('https://www.ozon.ru/')
#             print("Открыта страница:", 'https://www.ozon.ru/')
#
#             # Ожидание загрузки поля поиска
#             search_box = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Искать на Ozon"]'))
#             )
#             print("Поле ввода найдено, ввод ключевого слова...")
#             search_box.clear()  # Очистка поля ввода на случай, если там уже есть текст
#             search_box.send_keys(search_key + Keys.RETURN)
#
#             # Ожидание загрузки результатов поиска
#             print("Ожидание загрузки карточек товара...")
#             product_list = WebDriverWait(driver, 20).until(
#                 EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.tile-root'))  # Селектор карточек
#             )
#
#             if not product_list:
#                 print("Список товаров пуст.")
#                 return {'name': None, 'price': None}
#
#             # Перебор товаров и поиск первого релевантного
#             for product in product_list:
#                 product_name = product.find_element(By.CSS_SELECTOR, 'span.tsBody500Medium').text.strip()
#                 product_price = product.find_element(By.CSS_SELECTOR,
#                                                      'span.c3017-a1.tsHeadline500Medium').text.strip() if product.find_elements(
#                     By.CSS_SELECTOR, 'span.c3017-a1.tsHeadline500Medium') else "Цена не указана"
#
#                 # print(f"Найден товар: {product_name}, Цена: {product_price}")  # Вывод всех найденных товаров
#
#                 if search_key.lower() in product_name.lower():
#                     print(f"Товар найден: {product_name}, Цена: {product_price}")
#                     return {'name': product_name, 'price': product_price}
#
#             print("Релевантных товаров не найдено на Ozon")
#             return {'name': None, 'price': None}
#
#         except Exception as e:
#             print(f"Ошибка на Ozon: {e}")
#             if attempt < retries - 1:
#                 print("Повторная попытка...")
#                 refresh_page_if_needed(driver)
#             else:
#                 print("Не удалось выполнить поиск на Ozon после нескольких попыток.")
#                 return {'name': None, 'price': None}


# def monitor_yandex(driver, search_key):
#     # driver.get('https://market.yandex.ru/')
#     driver = uc.Chrome(version_main=129)
#     try:
#         driver.get('https://market.yandex.ru/')
#         time.sleep(10)
#         print("Открыта страница:", "https://market.yandex.ru/")
#         search_box = WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.ID, 'header-search'))
#         )
#         search_box.clear()
#         search_box.send_keys(search_key)
#         search_box.submit()
#         time.sleep(10)
#
#         product_list = WebDriverWait(driver, 20).until(
#             EC.presence_of_all_elements_located((By.XPATH, '//article[contains(@data-auto, "searchIncut") or contains(@class, "_3B3ah") or contains(@class, "_3BHKe")]'))
#         )
#         for product in product_list:
#             try:
#                 product_name = product.find_element(By.XPATH, './/h3 | .//a[contains(@class, "_3Ex26")]').text
#                 product_price = product.find_element(By.XPATH, './/span[contains(@class, "_1Nw1U") or contains(@class, "_3NaXx") or contains(@class, "_3C8lx")]').text
#                 print(f"Товар найден на Yandex.Market: {product_name}, Цена: {product_price}")
#                 return {"name": product_name, "цена": product_price}
#             except Exception as e:
#                 print(f"Ошибка при обработке товара: {e}")
#     except Exception as e:
#         print(f"Ошибка на Yandex.Market: {e}")
#         return None
#     finally:
#         driver.quit()


# Сохранение данных в CSV
def save_to_csv(data, filename='market_data.csv'):
    if data:
        with open(filename, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'price'])
            if file.tell() == 0:  # Если файл новый, записать заголовки
                writer.writeheader()
            writer.writerow(data)


def main():
    items = ['копье', 'дуршлаг', 'красные носки', 'леска для спиннинга']

    # Настройка драйвера
    driver = setup_driver()

    try:
        for item in items:
            print(f"Поиск по ключевому слову: {item}")
            wildberries_result = monitor_wildberries(driver, item)
            # ozon_result = monitor_ozon(driver, item)
            # yandex_result = monitor_yandex(driver, item)
            for result in wildberries_result:
                if result:
                    save_to_csv(result)

    finally:
        # Закрыть браузер
        driver.quit()


if __name__ == "__main__":
    main()
