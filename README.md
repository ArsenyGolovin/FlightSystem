__Цель__: Создание рабочего веб-приложения для управления сетью аэропортов России.

__Задачи__:
+ Подключение Flask;
+	Создание ORM-модели базы данных;
+	Добавление различных проверок для исключения ошибок;
+	Реализация изменения статусов рейсов в зависимости от текущего времени.

__Описание__:

При запуске программы предлагается зарегистрироваться или войти как управляющий компанией или как клиент.

__Возможности управляющего__: 
+	Просмотр доступных аэропортов;
+	Просмотр, добавление, задержка, отмена рейсов;
+	Просмотр, добавление, удаление самолётов из списка если они не используются.

__Возможности клиента__:
+	Просмотр доступных аэропортов;
+	Просмотр рейсов;
+	Просмотр своих билетов, их покупка и возврат.

Стоимость билета и время прибытия самолёта рассчитывается исходя из данных самолёта и местоположения аэропортов.

__Технологии__:
+	Flask;
+	Flask-login;
+	Flask-wtf, wtforms;
+	sqlalchemy;
+	sqlite3;
+	requests.
