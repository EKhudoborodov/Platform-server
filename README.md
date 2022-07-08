# ТЗ
Предметная область:
  Платформа для написания и публикации статей.
Задача:
  Реализовать сервер backend для платформы, отвечающий следующим требованиям:
  1) Сервер должен обеспечивать регистрацию и авторизацию пользователей
  2) Сервер должен поддерживать разграничение пользователей по ролям:
    * Администратор -- полный доступ ко всем функциям, может назначать роли. Включает в себя все роли.
    * Модератор -- проверяет новые статьи и может их либо одобрить, либо отклонить. Проверяет комментарии.
    * Писатель -- может создавать новые статьи.
    * Обычный пользователь (читатель) -- может читать статьи и оставлять комментарии.
     Не зарегистрированный пользователь не должен иметь доступа к системе.
  3) Статья может находиться в следющих состояниях:
    * Черновик (Статья, добавленная Писателем, но ещё не опубликованная. Только Писатель может поменять состояние на Опубликована)
    * Опубликована (Опубликованная статья, только Модератор видит опубликованные статьи)
    * Одобрена (Статья, одобренная Модератором, видна всем читателям)
    * Отклонена (Отклонённая Модератором статья, к ней должен быть прикреплён комментарий с причиной отклонения)
  4) У одной статьи может быть несколько авторов и редакторов.
  5) У одного пользователя может быть несколько ролей.
  6) Сервер должен поддерживать процесс редактирования статьи в состоянии Черновик.
  7) Должна быть возможность блокировки пользователей
  8) Статья, находящаяся в состоянии Одобрена, не должна редактироваться, однако её автор может убрать её в черновик.
  Дополнительные требования:
  10) Сервер должен использовать защищённые версии протоколов (https, wss и другие)
  11) Должны поддерживаться множественные сессии пользователей, с возможностью отключить все и все, кроме текущей.
  12) Сервер должен поддерживать связывание аккаунтов (авторизация через сторонние сервисы (пример: Яндекс ID, ВКонтакте, Mail.ru))
  13) Сервер должен поддерживать оценки статей
  14) Сервер должен предоставлять информацию о новых одобренных статьях 
  15) Сервер должен поддерживать поиск статей по следующим показателям:
    * По оценкам читателей
    * По количеству читателей
    * По названию
    * По содержимому
    * По ключевым словам
    * По авторам 
    * По дате публикации
  16) Статьи должны группироваться по секциям

# Platform-server
Framework: Flask;
Imports: requests, os, psycopg2, functional, json, datetime, flask;
Data base: server_db;
Url for data (method['GET']): 
  ![image](https://user-images.githubusercontent.com/90326938/177958673-47b538b3-2ea6-4148-b6c1-66c4ff9a10fd.png)
Tables:
  1) article: {id, name, title, description, isdeleted}
  2) article_status: {article_id, status_id}
  3) article_topic: {article_id, topic_id}
  4) article_writer: {article_id, user_id, isauthor}
  5) rating: {id, user_id, article_id, date, rate, isdeleted}
  6) role_user: {user_id, role_id}
  7) status: {id, name, description}
  8) topic: {id, name}
  9) users: {id, login, password, fullname, isbanned}

# Код и реализация
  1) Регистрация и авторизация пользователей
     ![image](https://user-images.githubusercontent.com/90326938/177948873-16ff00e7-bc34-4cca-bdb8-41537bc13d57.png)
     ![image](https://user-images.githubusercontent.com/90326938/177949760-cc1f28ff-1b08-4fae-b61a-55e9a11fba52.png) ![image](https://user-images.githubusercontent.com/90326938/177949852-fbfd8d2e-b47b-4018-bae1-a7f209d1df62.png)
  2) Разграничение по ролям (При переходе на любую страничку идёт проверка ролей пользователя, если у пользователя нет роли, необходимой 
     для просмотра страницы, его вернёт на начальную страницу; (5) у одного пользователя может быть несколько ролей)
     ![image](https://user-images.githubusercontent.com/90326938/177949216-e318f98c-fdb4-4aa7-a456-2c348a64d731.png)
     ![image](https://user-images.githubusercontent.com/90326938/177955919-8b8b9f40-a674-43ad-b018-4143c7df54b3.png)
  3) Статья, может находиться в состоянии "Черновик" (6) с возможностью редактирования на сайте
     ![image](https://user-images.githubusercontent.com/90326938/177950937-b0d5f397-900b-402e-be14-55662253ae9d.png)
     ![image](https://user-images.githubusercontent.com/90326938/177952557-9ea4197a-c9b1-49b6-9864-8149b61a14f8.png)
     В состоянии "Опубликована" - модератор или администратор могут одобрить статьтю или отклонить
     ![image](https://user-images.githubusercontent.com/90326938/177951372-21ddfba6-25cd-4797-bd24-361a867e13e8.png)
     ![image](https://user-images.githubusercontent.com/90326938/177953548-8e13dde1-1b6a-42dd-b8f6-0029e08e366b.png)
     В состоянии "Одобрена" - одобренные статьи отображаются на главной странице
     ![image](https://user-images.githubusercontent.com/90326938/177953823-e9cad57b-d7c2-4955-8f9d-8bb1b0eb6a2c.png)
     ![image](https://user-images.githubusercontent.com/90326938/177953945-75d67462-f361-472f-be0a-3e24b84762de.png)
     В состоянии "Отклонена" - читатели не могут видеть статью
     ![image](https://user-images.githubusercontent.com/90326938/177954603-6e57bd01-fee0-4eeb-b76f-0f2a90ffdc25.png)
     ![image](https://user-images.githubusercontent.com/90326938/177954856-f14dc36b-fcbb-4760-8230-c09ce4f6fca6.png)
  4) Автор статьи может добавлять соавторов и редакторов к своей статье
     ![image](https://user-images.githubusercontent.com/90326938/177955210-58addee9-7b81-441d-81bb-1cafd2c1e0be.png)
     ![image](https://user-images.githubusercontent.com/90326938/177955747-8f58d883-31b7-4a9e-8c5c-01db8340e172.png)
  7) Администратор может блокировать пользоватея
     ![image](https://user-images.githubusercontent.com/90326938/177956666-e7e00d32-c5e7-4106-a8bc-c24e98dccf56.png)
     ![image](https://user-images.githubusercontent.com/90326938/177957007-c337b33f-cb46-47a0-933b-f788eab82e61.png)
     Заблокированный потзователь не имеет доступа к сейту
     ![image](https://user-images.githubusercontent.com/90326938/177957248-4200885a-ee2a-4452-adad-fdc81a1cfd90.png)
  8) Авторы и редакторы не могут редактировать опубликованную статью
     ![image](https://user-images.githubusercontent.com/90326938/177957692-c86dbd85-d2f8-4afe-9823-3ebab2d5769e.png)
  13) Сервер поддерживает возможность оценки статей
     ![image](https://user-images.githubusercontent.com/90326938/177958197-a03250d1-4c33-4e74-a898-e9c4ecad4f48.png)
     ![image](https://user-images.githubusercontent.com/90326938/177958363-4d9563f0-d0f1-4fb9-8498-07f7436d3444.png)





     
