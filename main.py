import requests
def get_rate():        # Юзаем API ЦБ для получения курса USD/RUB
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'

    response = requests.get(url) # вызов функц get из библиотек requests ↙
        # ↑ (Отправка HTTP-запрос методом GET на указанный url)
    response.raise_for_status()  # Метод, который провераяет, был ли запрос успешным

    data = response.json() # метод, который преобразует тело ответа из JSON формата в Python обьект
    usd_rate = data['Valute']['USD']['Value'] 
        #  обращ к соварю Valute(влож словарь с всеми валют), => выбираем подсловарь usd
        # из данных доллара берем знач value (курс или значение, как хош называй)
        #   
    return round(usd_rate, 2)        