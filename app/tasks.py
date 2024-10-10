import csv
from datetime import datetime
from email.message import EmailMessage

import aiosmtplib
from tortoise.exceptions import DoesNotExist

from app.models import CurrencyPair, Price, PriceChangeLog
from app.utils import fetch_price_from_binance


async def send_email(subject, body):
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'Ru.Zubayr@gmail.com'  # Замени на свой email
    smtp_password = 'izib cjtk kdjt owbo'  # Замени на свой пароль

    msg = EmailMessage()
    msg['From'] = smtp_user
    msg['To'] = smtp_user
    msg['Subject'] = subject

    msg.set_content(body)

    try:
        # Создание экземпляра SMTP и подключение
        smtp = aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port, start_tls=True)
        await smtp.connect()  # Подключение
        await smtp.login(smtp_user, smtp_password)  # Вход
        await smtp.send_message(msg)  # Отправка сообщения
        print("Email sent successfully!")
        await smtp.quit()  # Завершение работы
    except Exception as e:
        print(f"Error sending email: {e}")


async def get_price(pair_name):
    print(f"Получение цены для пары {pair_name}...")
    data = await fetch_price_from_binance(pair_name)

    if data and 'price' in data:
        print(f"Цена для {pair_name}: {data['price']}")
        return float(data['price'])
    else:
        print(f"Ошибка получения цены для {pair_name}: {data}")
        return None


async def check_price(pair_name, old_price):
    print(f"Проверка цены для пары {pair_name}")
    new_price = await get_price(pair_name)

    if new_price is not None:
        print(f"Цена для {pair_name}: {new_price}")
        difference = (new_price - old_price) / old_price

        if difference >= 0.0003:
            write_to_csv(pair_name, new_price, difference)

            # Разделим pair_name на базовую и котируемую валюту
            if 'USDT' in pair_name:
                base_currency = pair_name[:-4]  # Убираем 'USDT'
                quote_currency = 'USDT'
            elif 'BTC' in pair_name:
                base_currency = pair_name[:-3]  # Убираем 'BTC'
                quote_currency = 'BTC'
            else:
                base_currency = pair_name[:-3]  # Для всех остальных пар
                quote_currency = pair_name[-3:]

            # Форматируем валютную пару правильно
            formatted_pair_name = f"{base_currency}/{quote_currency}"

            await record_price_change(formatted_pair_name, new_price, difference)
        else:
            print(f"Изменение цены для {pair_name} меньше порога, пропускаем запись.")
    else:
        print(f"Не удалось получить цену для {pair_name}.")


def write_to_csv(pair_name, new_price, difference):
    print(f"Запись в CSV для {pair_name}: {new_price}, разница: {difference}")
    with open('prices.csv', mode='a') as file:
        writer = csv.writer(file)
        writer.writerow([f"Название: {pair_name}, Цена: {new_price}, Время: {datetime.now().isoformat()}, Разница: {difference}"])


async def record_price_change(pair_name, new_price, difference):
    try:
        # Найдем валютную пару в базе данных
        currency_pair = await CurrencyPair.get_or_none(base_currency=pair_name.split('/')[0],
                                                       quote_currency=pair_name.split('/')[1])

        if currency_pair:
            # Запись изменений
            currency_pair.price = new_price
            currency_pair.difference = difference
            currency_pair.total_amount = 3  # Запишите общее количество BTC, если необходимо
            await currency_pair.save()
            await send_email(f"Уведомление о росте цены {pair_name}",
                             f"Стоимость ваших накоплений в {pair_name}, разница в цене {difference}")
            print(f"Записано изменение цены для {pair_name}: {new_price}, разница: {difference}")
        else:
            print(f"Валютная пара {pair_name} не найдена в базе данных.")
    except Exception as e:
        print(f"Ошибка при записи в базу данных: {e}")
