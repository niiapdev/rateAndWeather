import requests

# Используем API ЦБ РФ для получения курса USD/RUB
url = 'https://www.cbr-xml-daily.ru/daily_json.js'

response = requests.get(url) # вызов функц get из библиотек requests ↙
# ↑ (Отправка HTTP-запрос методом GET на указанный url)
response.raise_for_status()  # Метод, который провераяет, был ли запрос успешным

data = response.json() # метод, который преобразует тело ответа из JSON формата в Python обьект
usd_rate = data['Valute']['USD']['Value'] 
#  обращ к соварю Valute(влож словарь с всеми валют), => выбираем подсловарь usd
# из данных доллара берем знач value (курс)

print(f"Курс доллара к рублю: {usd_rate:.2f} RUB")
# : — начало формата. 
# .2f —  показ число float и двумя знаками после запятой
print(type(usd_rate))  # <class 'float'>