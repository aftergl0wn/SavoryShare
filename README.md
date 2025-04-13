# Проект SavoryShare
Автор: Анастасия Давыдова  
«SavoryShare» — сайт, на котором пользователи могут публиковать свои рецепты, 
добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/aftergl0wn/SavoryShare.git
```

```
cd SavoryShare
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Запустить проект через Docker:

```
docker compose up
```
Применить миграции

```
docker compose exec backend python manage.py migrate
```

Собрать статику Django 

```
docker compose exec backend python manage.py collectstatic
```

Скопировать статику в /backend_static/static/

```
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/ 
```
