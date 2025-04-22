ShadyPay (Банкинг)
===


![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)  ![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)


---


## Содержание

1. [Общее описание][glob]
2. [Установка][install]
3. [Запуск серверной части][run_server]<br>
   3.1 [Запуск через консоль][run_server_cmd] <br>
   3.2 [Запуск с помощью docker][run_server_docker] <br>
4. [Запуск клиентской части][run_client] <br>
5. [Список того, что было реализованно][about]
<br>

---

<br>

[glob]: +

## 1. Описание программы:
   

    ShadyPay - это курсовой проект, целью которого было создание клиент-серверного приложения, 
      где клиент с сервером взаимодействуют с помощью сокетов
   
    Тема проекта - банковское приложение которое позволяет пользователю переводить деньги между своими счетами, 
      а также переводить на счета других пользователей.

<br>

##### Основные функции:

* Создание счета
* Перевод денег на свои счета
* Перевод денег по номеру счета
* Перевод денег по номеру телефона
* Конвертация валюты (перевод между счетами с разными валютами)


<br>

---

<br>

[install]: +
## 2. Установка 
   
### Шаги:
1.  Откройте команлную строку
2. Перейдите в директорию в которой вы хотите расположить проект
3. Введите команду ``` git clone https://github.com/ShapMiki/Mobil_banking-Kursovaya-socket-.git```
4. Введите команду ``` cd Mobil_banking-Kursovaya-socket- ``` - переход в корневую директорию проекта

<br>

---

<br>

[run_server]: +
## 3. Запуск серверной части 


[run_server_cmd]: +
### 3.1 Запуск через консоль

1. Нуйжно перейти в директорию свервера(server)

    
    "ВАШ_ПУТЬ_ДО_ПРОЕКТА/Mobil_banking-Kursovaya-socket-/sever"

2. Создание PostgreSQL бд <br>
   2.1 Установите PostgreSQL с [оффициального сайта](https://www.postgresql.org/download/) <br>
   2.2 Запустите БД

2. Создание .env файла

```
DB_HOST = <ХОСТ КОТОРЫЙ ВЫ УКАЗАЛИ ПРИ РЕГИСТРАЦИИ БД>
DB_PORT = <ПОРТ КОТОРЫЙ ВЫ УКАЗАЛИ ПРИ РЕГИСТРАЦИИ БД>
DB_USER = <ИМЯ ПОЛЬЗОВАТЛЯ КОТОРЫЙ ВЫ УКАЗАЛИ ПРИ РЕГИСТРАЦИИ БД>
DB_PASSWORD = <ПАРОЛЬ КОТОРЫЙ ВЫ УКАЗАЛИ ПРИ РЕГИСТРАЦИИ БД>
DB_NAME = <ИМЯ БД КОТОРЫЙ ВЫ УКАЗАЛИ ПРИ РЕГИСТРАЦИИ БД>
secret_key_for_jwt = fc8281467e46ff9a657f820003f09fc2ea025d5be062e7bb60af8806d967feb4
algorithm_for_jwt = <АЛГОРИТМ ДЛЯ JWT (напр. SH256)>
host = 0.0.0.0 #<СЕРВЕР ПРОСЛУШИВАЕТ ВСЕ IP СВОИХ ИНТЕРФЕЙСОВ>
port = 3334 #<ПОРТ НА КОТОРОМ РАБОТАЕТ СОКЕТ>
secret_server_key = 3nBGTLyXjpz_X-CLFtkEVnm6TdwoX2Igm_3wll1JLek=  #<Секретный ключь для шифрования>
time_zone = 3
config_version = v1.0.0.28.03.2025 
currencyapicom_api_key = <API ключ сайта curencyapicom>
```
    secret_key_for_jwt и secret_server_key можно сгерерировать командой 
```python utils/generate_key.py```
     
    После чего надо скопировать ключи и вставить в .env в соответсвующие места
    все - <УКАЗАНИЯ> надо заменить на ваши данные
    все - #<ПОДСКАЗКИ> можно удалить

3. перейдите в cmd  и находясь в директории <br>
"ВАШ_ПУТЬ_ДО_ПРОЕКТА/Mobil_banking-Kursovaya-socket-/sever"<br>
   3.1 Создайте виртуальную среду командой:     (Не обязательно)<br>
   ``` python -m venv myvenv```<br>
   3.2 Запустите виртуальную среду командой:   (Не обязательно)<br>
   ``` myvenv/scripts/activate```<br>
   3.3 Установите зависимости командой: <br>
   ``` pip install -r requirements.txt```<br>
   3.4 Проведите миграции алембика командой:           <br>
   ```alembic upgrade head```<br><br>

4. Запустите сервер командой: <br>
   ```python main.py```
   
<br>

[run_server_docker]: +
### 3.2 Запуск с помощью docker

1. Убедитесь, что у вас установлен Docker. Если нет, установите его с [официального сайта](https://www.docker.com/get-started).
2. откройте cmd и перейдите в директорию server проекта:<br>
  "ВАШ_ПУТЬ_ДО_ПРОЕКТА/Mobil_banking-Kursovaya-socket-/sever"
3. Создайте файл .env: 
```
DB_HOST = db
DB_PORT = 5432
DB_USER = postgres
DB_PASSWORD = postgres
DB_NAME = mydb
secret_key_for_jwt = fc8281467e46ff9a657f820003f09fc2ea025d5be062e7bb60af8806d967feb4
algorithm_for_jwt = HS256
host = 0.0.0.0 
port = 3334
secret_server_key = 3nBGTLyXjpz_X-CLFtkEVnm6TdwoX2Igm_3wll1JLek=
time_zone = 3
config_version = v1.0.0.28.03.2025
currencyapicom_api_key = <API ключ сайта curencyapicom>
```
4. И для запуска введите в cmd введите команду ```docker compose up --build```


<br>

---

<br>

[run_client]: +
## 4. Запуск клиентской части

#### Шаги

1. Перейдите в директорию client из корневой папки проекта<br>
  "ВАШ_ПУТЬ_ДО_ПРОЕКТА/Mobil_banking-Kursovaya-socket-/client"
2. Создайте виртуальную среду командой:     (Не обязательно)<br>
   ``` python -m venv myvenv```<br>
3. Запустите виртуальную среду командой:   (Не обязательно)<br>
   ``` myvenv/scripts/activate```<br>
4. Установка зависимостей командой в cmd:<br>
```pip install -r requirements.txt```
5. Запуск командой в cmd:<br>
```python main.py```


<br>

---

<br>

[about]: +

## 5. Список того, что было реализованно

1. Авторизация с помощью JWT
2. Симметричное шифрование данных при отправке
3. Кеширование паролей в БД
4. Отправка данных через сокет форматом: 
```json
{
   "headers": {
      "method": "",
      "route": "",
      "JWT": "",
      "ip": "",
      "config_version": "v1.0.0.28.03.2025"
   },
   "data": {
   "ДАННЫЕ1": "1",
   "ДАННЫЕ2": "2"
  }
}      
```
5. Управление БД c помощью SQLAlchemy
6.  Управление версиями БД c помощью Alembic
7. Написана своя архитектура для запросов
8. Имеется Docker 


