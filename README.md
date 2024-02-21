### Данный репозиторий содержит исходный код api для автоматического заполнения сопроводительного письма с учётом CV и текста вакансии на базе YaGPT.

<br>

#### Перед использованием необходимо будет задать конфигурационные файлы с параметрами из примеров в папке config, а также создать ключ авторизации Yandex Cloud. Как это сделать — смотрите по следующим ссылкам:
- [Yandex Cloud IAM](https://cloud.yandex.ru/ru/docs/iam/operations/iam-token/create-for-sa#via-jwt)
- [Yandex Cloud Key](https://cloud.yandex.ru/ru/docs/iam/operations/authorized-key/create#console_1)
- [Yandex Cloud SA ID](https://cloud.yandex.ru/ru/docs/iam/operations/sa/get-id)

<br>

#### Как использовать локально:
- Установка зависимостей
```bash
git clone https://github.com/allseeteam/cover-letter-enchancer-backend
сd cover-letter-enchancer-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
- Запуск сервера
```bash
uvicorn api.api:app --host 0.0.0.0 --port 8000
```

<br>

#### Как использовать с docker:
```bash
git clone https://github.com/allseeteam/cover-letter-enchancer-backend
сd cover-letter-enchancer-backend
docker build -t cover-letter-enchancer-api .  
docker run -d -p 8000:8000 --name cover-letter-enchancer-api-container cover-letter-enchancer-api
```