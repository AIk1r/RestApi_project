ВАЖНО!
Все тесты проводил на https://www.postman.com
Поэтому рекомендую также работать с проектом при помощи postman


/create - POST-запрос для создания уведомления. Принимает объект Notification в теле запроса. Если пользователь не существует, создается новый пользователь. Затем создается уведомление, добавляется в список уведомлений пользователя и отправляется электронное письмо, если ключ уведомления соответствует условиям.

/list - GET-запрос для получения списка уведомлений. Принимает параметры user_id, skip и limit. Возвращает список уведомлений пользователя с указанным user_id, начиная с позиции skip и ограниченный limit количеством уведомлений.

/read - POST-запрос для пометки уведомления как прочитанного. Принимает параметры user_id и notification_id. Находит уведомление с указанным notification_id у пользователя с указанным user_id и помечает его как прочитанное.

Также в программе используются следующие модули и библиотеки:

fastapi - фреймворк для создания веб-приложений.

motor - асинхронный драйвер для работы с MongoDB.

pydantic - библиотека для валидации данных и сериализации/десериализации моделей.

email.mime.multipart и email.mime.text - модули для работы с электронными письмами.

dotenv - модуль для загрузки переменных окружения из файла .env.

os - модуль для работы с операционной системой.

smtplib - модуль для отправки электронных писем.

uuid - модуль для генерации уникальных идентификаторов.

datetime - модуль для работы с датой и временем.
