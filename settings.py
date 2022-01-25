START_COMMANDS = ['/start', '/hello-world']

SETTINGS_COMMANDS = ['/settings']
SETTINGS_OPTIONS = ['Язык', 'Валюта']

INTENTS = [
    {
        'name': 'Поиск по сниженной цене',
        'command': ['/lowprice'],
        'scenario': 'lowprice',
    },
    {
        'name': 'Поиск по завышенной цене',
        'command': ['/highprice'],
        'scenario': 'highprice',
    },
    {
        'name': 'Настраивемый поиск',
        'command': ['/bestdeal'],
        'scenario': 'bestdeal',
    },
    {
        'name': 'Смена языка',
        'command': ['язык', 'language'],
        'scenario': 'lang',
    },
    {
        'name': 'Смена валюты',
        'command': ['валюта', 'currency'],
        'scenario': 'curr',
    },
]

API_LANG_KEYS = {'ru': 'ru_RU', 'en': 'en_US'}

API_CURR_KEYS = {'USD': '$', 'RUB': '₽', 'EUR': '€'}

GREETING_ANSWER = 'Здравствуйте, я бот по подбору отелей.\n' \
                  'Имеются 4 команды:\n' \
                  '/lowprice - Подбор самых дешёвых отелей\n' \
                  '/highprice - Подбор самых дорогих отелей\n' \
                  '/bestdeal - Подбор по собственным параметрам\n' \
                  '/settings - Настройки'

DEFAULT_ANSWER = 'Не знаю как ответить.\n' \
                 'Для информации введите команду /start'

SCENARIOS = {
    'lowprice': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Введите город в котором будет проводиться поиск',
                'failure_text': 'Город не найден в базе данных, повторите попытку',
                'handler': 'handler_city',
                'next_step': 'stepX',
                'prev_step': None,
                'options': None,
                'result': None
            },
            'stepX': {
                'text': 'Теперь выберите объект поиска',
                'failure_text': 'Некорректное значение, повторите попытку',
                'handler': 'handler_city_option',
                'next_step': 'step2',
                'prev_step': 'step1',
                'options': True,
                'result': None
            },
            'step2': {
                'text': 'Отлично, объект для поиска - {city}.\n'
                        'Теперь введите кол-во отелей для поиска (не более 20)',
                'failure_text': 'Недопустимое число. Допускается только от 1 до 20 вариантов',
                'handler': 'handler_number',
                'next_step': 'step3',
                'prev_step': 'step1',
                'options': None,
                'result': None
            },
            'step3': {
                'text': 'Подождите, ведётся подбор...',
                'failure_text': None,
                'handler': None,
                'next_step': None,
                'prev_step': 'step2',
                'options': None,
                'result': 'LowPriceSearch'
            },
        }
    },
    'highprice': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Введите город в котором будет проводиться поиск',
                'failure_text': 'Город не найден найден данных, повторите попытку',
                'handler': 'handler_city',
                'next_step': 'stepX',
                'prev_step': None,
                'options': None,
                'result': None
            },
            'stepX': {
                'text': 'Теперь выберите объект поиска',
                'failure_text': 'Некорректное значение, повторите попытку',
                'handler': 'handler_city_option',
                'next_step': 'step2',
                'prev_step': 'step1',
                'options': True,
                'result': None
            },
            'step2': {
                'text': 'Отлично, город - {city}.\n'
                        'Теперь введите кол-во отелей для поиска (не более 20)',
                'failure_text': 'Недопустимое число. Допускается только от 1 до 20 вариантов',
                'handler': 'handler_number',
                'next_step': 'step3',
                'prev_step': 'step1',
                'options': None,
                'result': None
            },
            'step3': {
                'text': 'Подождите, ведётся подбор...',
                'failure_text': None,
                'handler': None,
                'next_step': None,
                'prev_step': 'step2',
                'options': None,
                'result': 'HighPriceSearch'
            },
        }
    },
    'bestdeal': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Введите город в котором будет проводиться поиск',
                'failure_text': 'Город не найден найден данных, повторите попытку',
                'handler': 'handler_city',
                'next_step': 'stepX',
                'prev_step': None,
                'options': None,
                'result': None
            },
            'stepX': {
                'text': 'Теперь выберите объект поиска',
                'failure_text': 'Некорректное значение, повторите попытку',
                'handler': 'handler_city_option',
                'next_step': 'step2',
                'prev_step': 'step1',
                'options': True,
                'result': None
            },
            'step2': {
                'text': 'Теперь введите минимальную цену. ({curr_key})',
                'failure_text': 'Что-то пошло не так, повторите попытку',
                'handler': 'handler_min_price',
                'next_step': 'step3',
                'prev_step': 'step1',
                'options': None,
                'result': None
            },
            'step3': {
                'text': 'Минимальная цена - {min_price}{curr_key}.\n'
                        'Теперь введите максимальную цену ({curr_key})',
                'failure_text': 'Что-то пошло не так, повторите попытку',
                'handler': 'handler_max_price',
                'next_step': 'step4',
                'prev_step': 'step2',
                'options': None,
                'result': None
            },
            'step4': {
                'text': 'Диапозон цен {min_price}{curr_key} - {max_price}{curr_key}.\n'
                        'Теперь введите минимальное расстояние от центра города. (км)',
                'failure_text': 'Что-то пошло не так, повторите попытку',
                'handler': 'handler_min_dist',
                'next_step': 'step5',
                'prev_step': 'step3',
                'options': None,
                'result': None
            },
            'step5': {
                'text': 'Минимальное расстояние от центра - {min_dist}км\n'
                        'Введите максимальное значение',
                'failure_text': 'Что-то пошло не так, повторите попытку',
                'handler': 'handler_max_dist',
                'next_step': 'step6',
                'prev_step': 'step4',
                'options': None,
                'result': None
            },
            'step6': {
                'text': 'Теперь введите кол-во отелей для поиска (не более 20)',
                'failure_text': 'Недопустимое число. Допускается только от 1 до 20 вариантов',
                'handler': 'handler_number',
                'next_step': 'step7',
                'prev_step': 'step5',
                'options': None,
                'result': None
            },
            'step7': {
                'text': 'Подождите, ведётся подбор...',
                'failure_text': None,
                'handler': None,
                'next_step': None,
                'prev_step': 'step6',
                'options': None,
                'result': 'CustomSearch'
            },
        }
    },
    'lang': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Выберите язык:',
                'failure_text': 'Язык не поддерживается, выберите из предложенных',
                'handler': 'handler_lang',
                'next_step': 'step2',
                'prev_step': None,
                'options': ['Русский', 'English'],
                'result': None
            },
            'step2': {
                'text': 'Язык был успешно сменён',
                'failure_text': None,
                'handler': None,
                'next_step': None,
                'prev_step': 'step1',
                'options': None,
                'result': None
            },
        }
    },
    'curr': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Выберите валюту:',
                'failure_text': 'Валюта не поддерживается, выберите из предложенных',
                'handler': 'handler_curr',
                'next_step': 'step2',
                'prev_step': None,
                'options': ['$', '₽', '€'],
                'result': None
            },
            'step2': {
                'text': 'Валюта был успешно заменена',
                'failure_text': None,
                'handler': None,
                'next_step': None,
                'prev_step': 'step1',
                'options': None,
                'result': None
            },
        }
    },
}
