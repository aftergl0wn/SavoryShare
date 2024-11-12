# Проект Foodgram
Автор: Анастасия Давыдова  
«Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, 
добавлять чужие рецепты в избранное и подписываться на публикации других авторов.  
Ссылка на сайт: 
```
https://foodgram-anastasia.zapto.org/recipes
```

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/aftergl0wn/foodgram.git
```

```
cd foodgram
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

