import time
import peewee
import telebot
from telebot import types

import engine
import handlers
import settings
from config import TOKEN

from loguru import logger

from mtranslate import translate

from models import UserState, UserInfo

bot = telebot.TeleBot(TOKEN)

logger.add('bot.log', format='{level} - {message} - {time}')


def user_is_registered(user_id):
    """
    Проверка пользователя на учёт в базе данных (для персонализации настроек)
    :param user_id: Идентификатор пользователя
    :return: bool
    """
    try:
        UserInfo.get(UserInfo.user_id == user_id)
        return True
    except IndexError and peewee.DoesNotExist:
        return False


def state_is_active(user_id):
    """
    Проверка пользователя на активность сценария
    :param user_id: Идентификатор пользователя
    :return: bool
    """
    try:
        UserState.get(UserState.user_id == user_id)
        return True
    except IndexError and peewee.DoesNotExist:
        return False


def send_message(user_id, text, lang, reply_markup=types.ReplyKeyboardRemove(selective=False), parse=None, image=None):
    """
    Доработанный метод отправки сообщений с поддержкой мультиязычности
    :param user_id: Идентификатор пользователя
    :param text: Текст для отправки
    :param lang: Язык интерфейса в настройках пользователя
    :param reply_markup:
    :return: None
    """
    text_to_send = translate(text, from_language='ru', to_language=lang) if lang != 'ru' else text
    if image:
        try:
            bot.send_photo(user_id, image, caption=text_to_send, parse_mode=parse)
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(user_id, text_to_send, reply_markup=reply_markup, parse_mode=parse)
    else:
        time.sleep(0.1)
        bot.send_message(user_id, text_to_send, reply_markup=reply_markup, parse_mode=parse)


@bot.message_handler(func=lambda m: True)
def on_event(message):
    """
    Обрабочтик сообщений
    :param message: Объект входящего сообщения
    :return: None
    """
    try:
        user_id: int = message.chat.id
        text: str = message.text
        if not user_is_registered(user_id=user_id):
            new_user = UserInfo(
                user_id=user_id,
                user_nickname=message.chat.first_name,
                username=message.chat.username,
                lang='ru',
                currency='RUB'
            )
            new_user.save()
        user_settings = UserInfo.get(UserInfo.user_id == user_id)
        if state_is_active(user_id):
            user = UserState.get(UserState.user_id == user_id)
            if any(item == text.lower() for item in settings.START_COMMANDS):
                logger.info(f'User {user_id} brakes scenario - {user.scenario_name} and gets {text}')
                user.delete_instance()
                send_message(user_id, settings.GREETING_ANSWER, user_settings.lang)
            else:
                steps = settings.SCENARIOS[user.scenario_name]['steps']
                step = steps[user.step_name]
                handler = getattr(handlers, step['handler'])
                next_step = steps[step['next_step']]
                if text.lower() == 'назад' or text.lower() == 'return':
                    prev_step = step['prev_step']
                    if prev_step:
                        logger.info(f'User {user_id} returns from {user.step_name} to {prev_step}')
                        step = steps[prev_step]
                        user.step_name = prev_step
                        user.save()
                        send_message(user_id, step['text'].format(**user.context), user_settings.lang)
                    else:
                        logger.info(f'User {user_id} canceled scenario - {user.scenario_name}')
                        user.delete_instance()
                        send_message(user_id, 'Команда отменена', lang=user_settings.lang)
                    return
                if handler(text=text, context=user.context):
                    user_settings = UserInfo.get(UserInfo.user_id == user_id)
                    next_message = next_step['text'].format(**user.context)
                    if next_step['options']:
                        if next_step['options'] == True:
                            send_message(user_id, next_message, user_settings.lang, reply_markup=None)
                        else:
                            options = next_step['options']
                            markup = types.ReplyKeyboardMarkup(row_width=4)
                            for item in options:
                                itembtn = types.KeyboardButton(item)
                                markup.add(itembtn)
                            send_message(user_id, next_message, user_settings.lang, reply_markup=markup)
                    else:
                        send_message(user_id, next_message, user_settings.lang)
                    if next_step['next_step']:
                        user.step_name = step['next_step']
                        user.save()
                        logger.info(f'User {user_id} gets scenario - {user.scenario_name} - {user.step_name}')
                    else:
                        logger.info(f'User {user_id} finished scenario - {user.scenario_name}')
                        user.delete_instance()
                    if next_step['result']:
                        finder_class = getattr(engine, next_step['result'])
                        finder = finder_class(user.context)
                        result = finder.get_result()
                        if isinstance(result, str):
                            send_message(user_id, result, user_settings.lang)
                            return
                        else:
                            for item in result:
                                if item[1]:
                                    text = item[0]
                                    image = item[1]
                                    send_message(user_id, text, user_settings.lang, parse='HTML', image=image)
                                else:
                                    text = item[0]
                                    send_message(user_id, text, user_settings.lang, parse='HTML')
                else:
                    send_message(user_id, step['failure_text'], user_settings.lang)
        else:
            if any(item == text.lower() for item in settings.START_COMMANDS):
                send_message(user_id, settings.GREETING_ANSWER, user_settings.lang)
                logger.info(f'User {user_id} gets {text}')
            elif any(item == text.lower() for item in settings.SETTINGS_COMMANDS):
                markup = types.ReplyKeyboardMarkup(row_width=4)
                options = settings.SETTINGS_OPTIONS
                for item in options:
                    item_translation = translate(item, from_language='ru', to_language=user_settings.lang)
                    markup.add(item_translation)
                send_message(user_id, 'Выберите параметр:', user_settings.lang, reply_markup=markup)
                logger.info(f'User {user_id} gets {text}')
            else:
                for intent in settings.INTENTS:
                    if any(command in text.lower() for command in intent['command']):
                        scenario = intent['scenario']
                        logger.info(f'User {user_id} started scenario - {scenario}')
                        step_name = settings.SCENARIOS[scenario]['first_step']
                        new_state = UserState(
                            user_id=user_id,
                            scenario_name=scenario,
                            step_name=step_name,
                            curr=settings.API_CURR_KEYS[user_settings.currency],
                            context={'id': user_id, 'lang': user_settings.lang, 'curr': user_settings.currency,
                                     'curr_key': settings.API_CURR_KEYS[user_settings.currency]}
                        )
                        new_state.save()
                        step = settings.SCENARIOS[scenario]['steps'][step_name]
                        text = settings.SCENARIOS[scenario]['steps'][step_name]['text']
                        if step['options']:
                            options = step['options']
                            markup = types.ReplyKeyboardMarkup(row_width=4)
                            for item in options:
                                itembtn = types.KeyboardButton(item)
                                markup.add(itembtn)
                            send_message(user_id, text, user_settings.lang, reply_markup=markup)
                        else:
                            send_message(user_id, text, user_settings.lang)
                        break
                else:
                    send_message(user_id, settings.DEFAULT_ANSWER, user_settings.lang)
    except Exception as exc:
        logger.error(exc)


if __name__ == '__main__':
    bot.polling()
