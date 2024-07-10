# Пользователь может добавить новое путешествие, заполнив форму с информацией 
# о месте назначения, датах поездки, бюджете и желаемых услугах.

from flask import Flask, request, render_template
import sqlite3  
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
#from flask_wtf.csrf import CsrfProtect
from flask_sqlalchemy import SQLAlchemy
from wtforms.fields import DateField
from werkzeug.datastructures import MultiDict

from datetime import datetime



# Определение формы с информацией о путешествии
class MyFormTrip(FlaskForm):
    # Поле для названия фильма
    name = StringField('Краткое название', validators=[DataRequired(), Length(min=2, max=100, message='Минимум %(min)d и максимум  %(max)d символа')]) 
    # Место назначения
    place = StringField('Место назначения', validators=[Optional(), Length(min=2, max=40, message='Минимум %(min)d и максимум  %(max)d символа')])
    # стоимость поездки
    cast = FloatField('Бюджет в руб. ',validators=[Optional(),NumberRange(min=0, message='положительное >0')])
    # Дата начала
    dat1 = DateField('Дата начала', format='%d.%m.%Y')
    # Дата приезда
    dat2 = DateField('Дата приезда', format='%d.%m.%Y')
    # Описание поездки полное
    comment = StringField('Описание поездки полное', validators=[Optional(), Length(min=0, max=3000, message='Минимум %(min)d и максимум  %(max)d символа')])
    # Кнопка
#    submit = SubmitField('Сохранить')


# Инициализация Flask приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
#csrf = CsrfProtect(app)

# Настройка соединения с базой данных (sqlite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trips.db'
db = SQLAlchemy(app)

# Класс данных о путешествии в SQLAlchemy
class Tour(db.Model):
    __tablename__ = 'tours'  # Указываем название таблицы

    # Определяем столбцы таблицы
    id = db.Column(db.Integer, primary_key=True)  # ID путешествия (первичный ключ)
    name = db.Column(db.String(100))  # Краткое название
    place = db.Column(db.String(40))  # Место назначение
    cast = db.Column(db.Float)  # Цена
    dat1 = db.Column(db.String(10))  # дата начала поездки
    dat2 = db.Column(db.String(10))  # дата конца поездки
    comment = db.Column(db.String(3000))  # полное описание

    # Конструктор для создания нового объекта Tour
    def __init__(self, name, place, cast, dat1, dat2, comment):
        self.name = name
        self.place = place
        self.cast = cast
        self.dat1 = dat1
        self.dat2 = dat2
        self.comment = comment


# Создание соединения с базой данных  
con = sqlite3.connect('./instance/trips.db', check_same_thread=False)
# Создание курсора для выполнения SQL запросов  
cur = con.cursor()

# Маршрут для корневой страницы
@app.route("/")
def hello_world():
    # Возврат главной страницы
    return render_template('index.html',my_action="")  # если были действия, выведем


# Маршрут для получения списка всех путешествий
@app.route("/tours" )
def tours():
    # Выполнение SQL запроса для получения всех путешествий
    res = cur.execute("select * from tours")
    # Получение результата запроса
    tours = res.fetchall()
    # Возвращение списка фильмов
    return render_template('tours.html', tours = tours)


#Маршрут для добавления нового фильма
@app.route("/tour_add")
def tour_add():
    # Получение данных о фильме из параметров запроса
    name = request.args.get('name')
    place = request.args.get('place')
    cast = request.args.get('cast')
    dat1 = request.args.get('dat2')
    dat2 = request.args.get('dat2')
    #dat1="01.02.2024"
    #dat2="01.02.2024"
    comment = request.args.get('comment')
#     # Формирование кортежа с данными о фильме
    tour_data = (name, place, cast, dat1, dat2, comment)
#     # Выполнение SQL запроса для добавления фильма в базу данных
    cur.execute('INSERT INTO tours (name, place, cast, dat1, dat2, comment) VALUES (?, ?, ?, ?, ?, ?)',  tour_data)
#     # Сохранение изменений в базе данных
    con.commit()
#     # Возвращение подтверждения о добавлении фильма
    my_action = "Добавлено путешествие  {} (с {} по {})".format(name, dat1, dat2)
    return render_template('index.html',my_action=my_action)  # если были действия, выведем



# Маршрут для отображения формы добавления путешествия SQLAlchemy
@app.route("/form_tour")
def form_tour():
#     # Создание формы
    form = MyFormTrip()    
#     # Возвращаем форму для отображения к заполнению
    return render_template('form_tour.html', form=form, my_action='/tour_add') # в этой же форме будем и редактировать


@app.route('/edit_id/<int:id>', methods=['GET', 'POST'])
def edit_id(id):
    # ищем, было ли путешествие
    # Выполнение SQL запроса для получения данных о фильме по ID
    res = cur.execute(f"select * from tours where id = ?", (id,))
    # Получение результата запроса
    tour = res.fetchone()    
    print(tour)
    # Проверка, найдено или нет путешествие
    if tour != None:
        # Создание формы
        #dat1=datetime.strptime(tour[4], '%Y-%m-%d')
        # datetime.strftime(dat1,'%Y-%m-%d')
        #dat1=dat..strftime("%Y-%m-%d")
        form = MyFormTrip(MultiDict([('name', tour[1]),('place', tour[2]),('cast', tour[3]),('dat1', tour[4]),('dat2', tour[5]),('comment', tour[6])])) 

        # Возвращение результата в форму для редактирования
        return render_template('form_tour.html', form=form, my_action='/tour_edit/'+str(id))
    else:
#         # Сообщение о том, что путешествия не существует   
        my_action = "Такого путешествия нет"
        return render_template('index.html',my_action=my_action)  # если были действия, выведем

@app.route('/tour_edit/<int:id>')
def tour_edit(id):
    # Получение данных о фильме из параметров запроса
    name = request.args.get('name')
    place = request.args.get('place')
    cast = request.args.get('cast')
    dat1 = request.args.get('dat2')
    dat2 = request.args.get('dat2')
    comment = request.args.get('comment')
#     # Формирование кортежа с данными о фильме
    tour_data = (name, place, cast, dat1, dat2, comment)
    try:
    #   Выполнение SQL запроса для добавления фильма в базу данных
        cur.execute("UPDATE tours SET name=?, place=?, cast=?, dat1=?, dat2=?, comment=? WHERE id = ?", (name, place, cast, dat1, dat2, comment, id))
    #   Сохранение изменений в базе данных
        con.commit()
        # Возвращение подтверждения о добавлении фильма
        my_action = "Отредактировано выбранное путешествие"    
    except:
        my_action = 'Error editing #{id}'.format(id=id)

    return render_template('index.html',my_action=my_action)  # если были действия, выведем


@app.route('/del_id/<int:id>', methods=['GET', 'POST'])
def del_id(id):
    try:
    #   Выполнение SQL запроса для добавления фильма в базу данных
        cur.execute('DELETE FROM tours WHERE id = ?', (id,))
    #   Сохранение изменений в базе данных
        con.commit()
        # Возвращение подтверждения о добавлении фильма
        my_action = "Удалено выбранное путешествие"    
    except:
        my_action = 'Error deleting #{id}'.format(id=id)

    return render_template('index.html',my_action=my_action)  # если были действия, выведем


# Запуск приложения, если оно выполняется как главный модуль
if __name__ == '__main__':
    # Отключение проверки CSRF для WTForms
    # app.config["WTF_CSRF_ENABLED"] = False  
    # Запуск приложения 
    app.run()