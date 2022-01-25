from telebot import types
import engine
import main
from models import UserInfo


def handler_city(text, context):
    """
    Обработчик городов для подбора
    :param text: Сообщение для обработки
    :param context: Информация внутри запроса
    :return: bool
    """
    text = text.capitalize()
    user_settings = UserInfo.get(UserInfo.user_id == context['id'])
    if not any(str(num) in text for num in range(1, 10)):
        finder = engine.LowPriceSearch({'city': text, 'city_id': None, 'lang': context['lang'], 'curr': context['curr']})
        try:
            result = finder.get_cities()
        except engine.CityNotFound:
            return False
        context['options'] = result
        markup = types.ReplyKeyboardMarkup(row_width=4)
        for item in result:
            name = item[1]
            itembtn = types.KeyboardButton(name)
            markup.add(itembtn)
        main.send_message(context['id'], 'Составлен список объектов', lang=user_settings.lang, reply_markup=markup)
        return True
    else:
        return False


def handler_city_option(text, context):
    options = context['options']
    for item in options:
        city_id = item[0]
        name = item[1]
        if name == text:
            context['city_id'] = city_id
            context['city'] = name
            return True
    else:
        return False


def handler_number(text, context):
    """
    Обработчик кол-ва допустимых отелей для подбора
    :param text: Сообщение для обработки
    :param context: Информация внутри запроса
    :return: bool
    """
    if text.isnumeric():
        number = int(text)
        if 0 < number <= 20:
            context['number'] = number
            return True
        else:
            return False
    else:
        return False


def handler_min_price(text, context):
    """
    Обработчик минимального значения цены
    :param text: Сообщение для обработки
    :param context: Информация внутри запроса
    :return: bool
    """
    if text.isnumeric():
        number = int(text)
        if number > 0:
            context['min_price'] = number
            return True
        else:
            return False
    else:
        return False


def handler_max_price(text, context):
    """
    Обработчик максимального значения цены
    :param text: Сообщение для обработки
    :param context: Информация внутри запроса
    :return: bool
    """
    if text.isnumeric():
        number = int(text)
        if number <= 0:
            return False
        min_price = context['min_price']
        if number < min_price:
            return False
        context['max_price'] = number
        return True
    else:
        return False


def handler_min_dist(text, context):
    """
    Обработчик минимального значения расстояния
    :param text: Сообщение для обработки
    :param context: Информация внутри запроса
    :return: bool
    """
    if text.isnumeric():
        number = int(text)
        if number > 0:
            context['min_dist'] = number
            return True
        else:
            return False
    else:
        return False


def handler_max_dist(text, context):
    """
    Обработчик максимального значения расстояния
    :param text: Сообщение для обработки
    :param context: Информация внутри запроса
    :return: bool
    """
    if text.isnumeric():
        number = int(text)
        if number <= 0:
            return False
        min_price = context['min_dist']
        if number < min_price:
            return False
        context['max_dist'] = number
        return True
    else:
        return False


def handler_lang(text, context):
    """
    Обработчик смены доступных языков
    :param text: Сообщение для обработки
    :param context: Информация внутри запроса
    :return: bool
    """
    text = text.lower()
    user_id = context['id']
    user_settings = UserInfo.get(UserInfo.user_id == user_id)
    if text == 'русский':
        lang = 'ru'
        user_settings.lang = lang
        user_settings.save()
        return True
    elif text == 'english':
        lang = 'en'
        user_settings.lang = lang
        user_settings.save()
        return True
    else:
        return False


def handler_curr(text, context):
    """
    Обработчик смены валюты из доступных вариантов
    :param text: Сообщение для обработки
    :param context: Информация внутри запроса
    :return: bool
    """
    text = text.lower()
    user_id = context['id']
    user_settings = UserInfo.get(UserInfo.user_id == user_id)
    if text == '$':
        curr = 'USD'
        user_settings.currency = curr
        user_settings.save()
        return True
    elif text == '₽':
        curr = 'RUB'
        user_settings.currency = curr
        user_settings.save()
        return True
    elif text == '€':
        curr = 'EUR'
        user_settings.currency = curr
        user_settings.save()
        return True
    else:
        return False
