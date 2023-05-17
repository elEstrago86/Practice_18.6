import requests
import json
import telebot
from telebot import types
from config import TOKEN


# Ключ API для получения курсов валют
API_KEY = "b5770b36b6ad640ec6a90e944e7e1e53c72f3e469f50cf6db5614ca6063494ca"


# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)


class APIException(Exception):
    def __init__(self, message):
        self.message = message


class CurrencyConverter:
    @staticmethod
    def get_price(base, quote, amount):
        url = f"https://min-api.cryptocompare.com/data/price?fsym={base}&tsyms={quote}"
        response = requests.get(url)
        data = json.loads(response.text)

        if "Response" in data:
            raise APIException(data["Message"])

        if quote not in data:
            raise APIException("Неправильно указана целевая валюта.")

        rate = data[quote]
        total = rate * amount
        return total


@bot.message_handler(commands=['start', 'help'])
def send_instructions(message):
    instructions = (
        "Привет! Я бот для конвертации валют.\n\n"
        "Чтобы узнать цену на определенную валюту, отправь мне сообщение в формате:\n"
        "<имя валюты, цену которой ты хочешь узнать> <имя валюты, в которой надо узнать цену первой валюты> <количество первой валюты>\n\n"
        "Например, для получения цены на 50 долларов в рублях, отправь мне сообщение: USD RUB 50\n\n"
        "Чтобы увидеть список доступных валют, введи команду /values."
    )
    bot.reply_to(message, instructions)


@bot.message_handler(commands=['values'])
def send_currency_values(message):
    currency_values = (
        "Доступные валюты:\n"
        "USD - Доллар США\n"
        "EUR - Евро\n"
        "RUB - Российский рубль"
    )
    bot.reply_to(message, currency_values)


@bot.message_handler(func=lambda message: True)
def convert_currency(message):
    try:
        text = message.text.upper()
        values = text.split()
        if len(values) != 3:
            raise APIException("Неправильный формат запроса.")

        base = values[0]
        quote = values[1]
        amount = float(values[2])

        total = CurrencyConverter.get_price(base, quote, amount)
        result = f"{amount} {base} = {total} {quote}"
        bot.reply_to(message, result)

    except APIException as e:
        error_message = f"Ошибка: {e}"
        bot.reply_to(message, error_message)


# Запуск бота
bot.polling(none_stop=True)