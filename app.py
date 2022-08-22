from email.policy import default
from mailbox import NoSuchMailboxError
from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import InputRequired, Length
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/db.db'
app.config['SECRET_KEY'] = 'mysupersecretultrasecretkey1234'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db  = SQLAlchemy(app)

####################### BASE DE DATOS #################
class User(UserMixin, db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(200))
    user_ci = db.Column(db.String(200))
    user_password = db.Column(db.String(200))

class Productos (db.Model):
    id = db.Column(db.Integer,primary_key=True)
    nombre =db.Column(db.String(200))
    cantidad =db.Column(db.Integer)
    emprendimiento_correpsondiente = db.Column(db.Integer, db.ForeignKey('emprendimiento.id'))

class Ingreso(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    emprendimiento_id = db.Column(db.Integer, db.ForeignKey('emprendimiento.id'))
    ingreso = db.Column(db.Integer)
    
class Egreso(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    emprendimiento_id = db.Column(db.Integer, db.ForeignKey('emprendimiento.id'))
    egreso = db.Column(db.Integer)

class Tareas(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    tarea_desc = db.Column(db.String(200))
    fecha = db.Column(db.DateTime(timezone=True))
    completado = db.Column(db.Boolean, default=False)
    emprendimiento_id = db.Column(db.Integer, db.ForeignKey('emprendimiento.id'))

class Emprendimiento(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    ##user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    emp_name = db.Column(db.String(200))
    emp_ruc = db.Column(db.String(200))
    emp_city = db.Column(db.String(200))
    emp_desc = db.Column(db.String(200))
    emp_ingreso = db.relationship('Ingreso', backref='emprendimiento', lazy='select')
    emp_egreso = db.relationship('Egreso', backref='emprendimiento', lazy='select')
    emp_tareas = db.relationship('Tareas', backref='emprendimiento', lazy='select')

####################### URL- ENDPOINTS ########
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    ci = StringField('ci', validators=[InputRequired(), Length(min=4,max=25)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/register', methods = ['GET', 'POST'])
def create_user():
    if request.method =='POST':
        print("entre en post")
        print(request.form['name'])
        print(request.form['ci'])
        print(request.form)
        user = User(
            user_name = request.form['name'],
            user_ci = request.form['ci'],
            user_password = request.form['pass']
        )
        print(user)
        db.session.add(user)
        db.session.commit()
        # return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(user_ci=form.ci.data).first()
        if user:
            print()
            login_user(user)
            return redirect(url_for('/'))

    return render_template("login.html", form=form)

@app.route('/register_finanza', methods = ['GET', 'POST'])
def finanzas():
    if request.method =='POST':
        print('entre en post la concha de la lora')
        total = Finanzas(
            ingresos = request.form['ingresos'],
            egresos = request.form['egresos']
    )
        db.session.add(total)
        db.session.commit()
        return redirect(url_for('piechart'))
    else:
        return render_template('finanzas.html')


@app.route('/calendar')
def calendar():
    return render_template('calendar.html')




@app.route('/piechart')
def piechart():
    total = Finanzas.query.all()
    return render_template('piechart.html', total=total)