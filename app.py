from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель для хранения результатов теста
class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    group = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Создаем таблицы при первом запуске
with app.app_context():
    db.create_all()

# Главная страница - ввод данных
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Сохраняем данные в сессию
        session['first_name'] = request.form['first_name']
        session['last_name'] = request.form['last_name']
        session['group'] = request.form['group']
        return redirect(url_for('learning'))
    return render_template('index.html')

# Страница с обучающим материалом
@app.route('/learning')
def learning():
    if 'first_name' not in session:
        return redirect(url_for('index'))
    return render_template('learning.html')

# Страница с тестом
@app.route('/test', methods=['GET', 'POST'])
def test():
    if 'first_name' not in session:
        return redirect(url_for('index'))
    
    # Вопросы и ответы
    questions = [
        {
            'id': 1,
            'text': 'Что такое фишинг?',
            'answers': [
                {'id': '1a', 'text': 'Вид спортивной рыбалки', 'correct': False},
                {'id': '1b', 'text': 'Метод интернет-мошенничества', 'correct': True},
                {'id': '1c', 'text': 'Тип компьютерного вируса', 'correct': False}
            ]
        },
        {
            'id': 2,
            'text': 'Какой пароль считается наиболее надежным?',
            'answers': [
                {'id': '2a', 'text': '12345678', 'correct': False},
                {'id': '2b', 'text': 'qwerty123', 'correct': False},
                {'id': '2c', 'text': 'Jk7#mP2!9zR$', 'correct': True}
            ]
        },
        {
            'id': 3,
            'text': 'Что не следует публиковать в социальных сетях?',
            'answers': [
                {'id': '3a', 'text': 'Фото домашних животных', 'correct': False},
                {'id': '3b', 'text': 'Номер банковской карты', 'correct': True},
                {'id': '3c', 'text': 'Мемы про котиков', 'correct': False}
            ]
        },
        {
            'id': 4,
            'text': 'Как защитить свои личные данные?',
            'answers': [
                {'id': '4a', 'text': 'Использовать двухфакторную аутентификацию', 'correct': True},
                {'id': '4b', 'text': 'Делиться паролями с друзьями', 'correct': False},
                {'id': '4c', 'text': 'Использовать один пароль для всех сервисов', 'correct': False}
            ]
        }
    ]
    
    if request.method == 'POST':
        score = 0
        # Проверяем ответы
        for question in questions:
            answer_id = request.form.get(f'q{question["id"]}')
            if answer_id:
                for answer in question['answers']:
                    if answer['id'] == answer_id and answer['correct']:
                        score += 1
        
        # Сохраняем результат в базу данных
        result = TestResult(
            first_name=session['first_name'],
            last_name=session['last_name'],
            group=session['group'],
            score=score,
            max_score=len(questions)
        )
        db.session.add(result)
        db.session.commit()
        
        # Сохраняем результат в сессии
        session['test_score'] = score
        session['test_max_score'] = len(questions)
        return redirect(url_for('results'))
    
    return render_template('test.html', questions=questions)

@app.route('/clear-db')
def clear_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
    return "База данных очищена"

# Страница с результатами
@app.route('/results')
def results():
    if 'test_score' not in session:
        return redirect(url_for('index'))
    
    # Получаем последние результаты для отображения
    recent_results = TestResult.query.order_by(TestResult.timestamp.desc()).limit(10).all()
    
    return render_template('results.html', 
                           score=session['test_score'], 
                           max_score=session['test_max_score'],
                           recent_results=recent_results)

# Сброс сессии
@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)