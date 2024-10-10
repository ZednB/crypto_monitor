import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Настройка веб-драйвера
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Запуск в фоновом режиме
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def monitor_price(driver, url, search_key):
    driver.get(url)
    print("Открыта страница:", url)

    try:
        # Ожидание загрузки поля ввода поиска
        print("Ожидание поля ввода поиска...")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'searchInput'))
        )
        print("Поле ввода найдено, ввод ключевого слова...")
        search_box.send_keys(search_key)

        # Поиск кнопки отправки и клик по ней
        print("Поиск кнопки отправки...")
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'applySearchBtn'))
        )
        search_button.click()
        print("Поиск выполнен для ключевого слова:", search_key)

        # Ожидание загрузки карточки товара
        print("Ожидание загрузки карточки товара...")
        product = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'article.product-card'))
        )

        # Скролл к продукту для уверенности, что элемент виден
        driver.execute_script("arguments[0].scrollIntoView();", product)

        # Извлечение данных
        product_name = product.find_element(By.CSS_SELECTOR, '.product-card__link').get_attribute('aria-label').strip()
        try:
            product_price = product.find_element(By.CSS_SELECTOR, '.price__lower-price').text.strip()
        except:
            product_price = product.find_element(By.CSS_SELECTOR, '.product-card__price').text.strip()
        # print("HTML карточки продукта:", product.get_attribute('outerHTML'))
        return {'name': product_name, 'price': product_price}

    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None


# Сохранение данных в CSV
def save_to_csv(data, filename='market_data.csv'):
    if data:
        with open(filename, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'price'])
            if file.tell() == 0:  # Если файл новый, записать заголовки
                writer.writeheader()
            writer.writerow(data)


def main():
    url = 'https://www.wildberries.ru/'
    search_key = 'леска для спиннинга'

    # Настройка драйвера
    driver = setup_driver()

    try:
        # Мониторинг цены
        result = monitor_price(driver, url, search_key)

        if result:
            print(f"Товар найден: {result['name']}, Цена: {result['price']}")
        else:
            print("Товар не найден или произошла ошибка.")

        save_to_csv(result)

    finally:
        # Закрыть браузер
        driver.quit()


if __name__ == "__main__":
    main()

# if __name__ == "__main__":
#     # Инициализация драйвера
#     driver = setup_driver()
#
#     # Пример URL для теста
#     url_wildberries = 'https://www.wildberries.ru/'
#
#     # Пример мониторинга товара
#     result = monitor_price(driver, url_wildberries, 'копье')
#     print(result)
#
#     # Сохранение в CSV
#     save_to_csv(result)
#
#     # Закрытие драйвера
#     driver.quit()
