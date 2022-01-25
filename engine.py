import requests
from config import x_rapidapi_key
from main import logger
import settings


class CityNotFound(Exception):
    def __str__(self):
        return 'Город не найден.'


class HotelsNotFound(Exception):
    def __str__(self):
        return 'Отели не найдены.'


class LowPriceSearch:
    """
    Класс для принятия обработанных запросов и получения ответа от сервера.
    LowPriceSearch - базовый класс поиска, специализирующийся на подборе дешеёвых отелей.
    """

    def __init__(self, context):
        self.rapidapi_key = x_rapidapi_key
        self.headers = {
            'x-rapidapi-key': self.rapidapi_key,
            'x-rapidapi-host': 'hotels4.p.rapidapi.com'
        }
        self.lang = settings.API_LANG_KEYS[context['lang']]
        self.curr = context['curr']
        self.city_id = context['city_id']
        self.context = context

    def get_cities(self):
        """
        Метод по выдаче списка гео объектов
        """
        req = requests.request(
            'GET',
            'https://hotels4.p.rapidapi.com/locations/search',
            params={
                'query': self.context['city'],
                'locale': self.lang
            },
            headers=self.headers)
        json = req.json()
        if not json['suggestions'][0]['entities']:
            raise CityNotFound
        objects = []
        i = 0
        for object in json['suggestions'][0]['entities']:
            i += 1
            if i > 5:
                break
            obj_id = object['destinationId']
            name = object['name']
            objects.append((obj_id, name))
        return objects

    def get_hotels(self):
        """
        Метод создания запроса и получения ответа с сервера
        """
        querystring = {"destinationId": f"{self.city_id}", "pageNumber": "1", "pageSize": "25", "checkIn": "2021-08-10",
                       "checkOut": "2021-09-01", "adults1": "1", "sortOrder": "PRICE", "locale": self.lang,
                       "currency": self.curr}

        req = requests.request('GET', 'https://hotels4.p.rapidapi.com/properties/list', params=querystring,
                               headers=self.headers)

        self.data = req.json()

    def sort(self):
        """
        Метод сортировки данных из полученного ответа
        """
        self.total = []
        i = 0
        if not self.data['data']['body']['searchResults']['results']:
            raise HotelsNotFound
        for hotel in self.data['data']['body']['searchResults']['results']:
            i += 1
            try:
                price = hotel['ratePlan']['price']['exactCurrent']
                address = hotel['address']['streetAddress']
            except KeyError:
                i -= 1
                continue
            image = hotel['optimizedThumbUrls']['srpDesktop']
            hotel_param = (i, hotel['name'], price, address, image)
            self.total.append(hotel_param)
            if i >= self.context['number']:
                break
        if not self.total:
            raise HotelsNotFound

    def return_result(self):
        """
        Метод форматирования данных в текст для отправки пользователю
        """
        result_list = []
        actual_num = len(self.total)
        if actual_num < self.context['number']:
            warn_text = f'К сожалению не нашлось заданного кол-ва отелей. Всего нашлось {actual_num}'
            result_list.append(warn_text)
        first_text = f'Список самых дешёвых отелей:\n'
        result_list.append((first_text, None))
        for hotel in self.total:
            text = f'{hotel[0]}. <b>{hotel[1]}</b>\n' \
                   f'ЦЕНА: <b>{hotel[2]}</b>{settings.API_CURR_KEYS[self.curr]}\n' \
                   f'АДРЕС: <i>{hotel[3]}</i>'
            image = hotel[4]
            item = (text, image)
            result_list.append(item)
        return result_list

    def get_result(self):
        """
        Метод для получения конечного результата используя предыдущие методы
        """
        try:
            self.get_hotels()
            self.sort()
            return self.return_result()
        except HotelsNotFound:
            return 'Отели не найдены, повторите попытку.'
        except Exception as exc:
            logger.error(exc)
            return 'Что-то пошло не так!'


class HighPriceSearch(LowPriceSearch):
    """
    Класс для принятия обработанных запросов и получения ответа от сервера.
    HighPriceSearch - класс наследованный от LowPriceSearch, имеющий все базовые методы,
    а также изменённые методы для подбора дорогих отелей.
    """

    def get_hotels(self):
        """
        Модфицированный метод создания запроса и получения ответа с сервера
        """
        querystring = {"destinationId": f"{self.city_id}", "pageNumber": "1", "pageSize": "25", "checkIn": "2021-08-10",
                       "checkOut": "2021-09-01", "adults1": "1", "sortOrder": "PRICE_HIGHEST_FIRST",
                       "locale": self.lang,
                       "currency": self.curr}

        req = requests.request('GET', 'https://hotels4.p.rapidapi.com/properties/list', params=querystring,
                               headers=self.headers)

        self.data = req.json()

    def return_result(self):
        """
        Метод форматирования данных в текст для отправки пользователю
        """
        result_list = []
        actual_num = len(self.total)
        if actual_num < self.context['number']:
            warn_text = f'К сожалению не нашлось заданного кол-ва отелей. Всего нашлось {actual_num}'
            result_list.append((warn_text, None))
        first_text = f'Список самых дорогих отелей:\n'
        result_list.append((first_text, None))
        for hotel in self.total:
            text = f'{hotel[0]}. <b>{hotel[1]}</b>\n' \
                   f'ЦЕНА: <b>{hotel[2]}</b>{settings.API_CURR_KEYS[self.curr]}\n' \
                   f'АДРЕС: <i>{hotel[3]}</i>'
            image = hotel[4]
            item = (text, image)
            result_list.append(item)
        return result_list


class CustomSearch(LowPriceSearch):
    """
    Класс для принятия обработанных запросов и получения ответа от сервера.
    CustomSearch - класс наследованный от LowPriceSearch, имеющий все базовые методы,
    а также изменённые методы для подбора отелей по специально заданным параметрам.
    """

    def get_hotels(self):
        """
        Модфицированный метод создания запроса и получения ответа с сервера
        """
        querystring = {"destinationId": f"{self.city_id}", "pageNumber": "1", "pageSize": "25", "checkIn": "2021-08-10",
                       "checkOut": "2021-09-01", "adults1": "1", "priceMin": f"{self.context['min_price']}",
                       "priceMax": f"{self.context['max_price']}",
                       "sortOrder": "PRICE",
                       "locale": self.lang,
                       "currency": self.curr}

        req = requests.request('GET', 'https://hotels4.p.rapidapi.com/properties/list', params=querystring,
                               headers=self.headers)

        self.data = req.json()

    def sort(self):
        """
        Модфицированный метод сортировки данных из полученного ответа
        """
        self.total = []
        i = 0
        for hotel in self.data['data']['body']['searchResults']['results']:
            i += 1
            try:
                price = hotel['ratePlan']['price']['exactCurrent']
                address = hotel['address']['streetAddress']
            except KeyError:
                i -= 1
                continue
            distance_str = hotel['landmarks'][0]['distance']
            distance_str = distance_str.replace(',', '.') if ',' in distance_str else distance_str
            dist = int(distance_str.split()[0]) if '.' not in distance_str else float(distance_str.split()[0])
            min_dist = self.context['min_dist']
            max_dist = self.context['max_dist']
            image = hotel['optimizedThumbUrls']['srpDesktop']
            if min_dist < dist < max_dist:
                hotel_param = (i, hotel['name'], price, address, image, dist)
                self.total.append(hotel_param)
            else:
                i -= 1
            if i >= self.context['number']:
                break
        if not self.total:
            raise HotelsNotFound

    def return_result(self):
        """
        Метод форматирования данных в текст для отправки пользователю
        """
        result_list = []
        actual_num = len(self.total)
        if actual_num < self.context['number']:
            warn_text = f'К сожалению не нашлось заданного кол-ва отелей. Всего нашлось {actual_num}'
            result_list.append(warn_text)
        first_text = f'Список отелей найденных по данному запросу:\n'
        result_list.append((first_text, None))
        for hotel in self.total:
            text = f'{hotel[0]}. <b>{hotel[1]}</b>\n' \
                   f'ЦЕНА: <b>{hotel[2]}</b>{settings.API_CURR_KEYS[self.curr]}\n' \
                   f'АДРЕС: <i>{hotel[3]}</i>\n' \
                   f'РАССТОЯНИЕ ОТ ЦЕНТРА: <b>{hotel[5]}</b>км\n'
            image = hotel[4]
            item = (text, image)
            result_list.append(item)
        return result_list
