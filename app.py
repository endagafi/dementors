
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
    emprendimiento_correpsondiente = db.Column(db.Integer, db.ForeignKey('emprendimiento.emp_id'))

class Ingreso(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    emprendimiento_id = db.Column(db.Integer, db.ForeignKey('emprendimiento.emp_id'))
    ingreso = db.Column(db.Integer)
    
class Egreso(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    emprendimiento_id = db.Column(db.Integer, db.ForeignKey('emprendimiento.emp_id'))
    egreso = db.Column(db.Integer)

class Tareas(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    tarea_desc = db.Column(db.String(200))
    fecha = db.Column(db.DateTime(timezone=True))
    completado = db.Column(db.Boolean, default=False)
    emprendimiento_id = db.Column(db.Integer, db.ForeignKey('emprendimiento.emp_id'))

class Emprendimiento(db.Model):
    emp_id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
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
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods = ['GET', 'POST'])
def create_user():
    if request.method =='POST':
        print("entre en post")
        print(request.form['name'])
        print(request.form['ci'])
        print(request.form['pass'])
        user = User(
            user_name = request.form['name'],
            user_ci = request.form['ci'],
            user_password = request.form['pass']
        )
        print(user)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    try:
        form1 = LoginForm()
        print(request.form)
        ci = request.form['ci']
        if ci != "":
            print("voy a conusltar")
            user = User.query.filter_by(user_ci=ci).first()
            print("================================hbfkja")
            if user:
                print("=====================fdhbjbdshhdbsbgfbskhdgf")
                login_user(user)
                return redirect(url_for('profile'))
    except:
        return render_template("login.html", form1 = form1)

    

@app.route('/emprendimientos')
@login_required
def emprendimientos():
    return render_template('emprendimientos.html')

@app.route('/ver_emprendimientos/<int:emp_id>', methods=['POST','GET'])
@login_required
def ver_emprendimientos(emp_id):
    user = User.query.filter_by(id=current_user.id).first()
    emprendimiento = Emprendimiento.query.filter_by(emp_id=emp_id).first()
    if not emprendimiento:
        return 'no existe el emprendimiento'
    return render_template('dashboard.html', user=user, emprendimiento=emprendimiento)


@app.route('/registrar_emprendimiento', methods = ['GET', 'POST'])
def register_emp():
    if request.method =='POST':
        print("entre en post")
        emprendimiento = Emprendimiento(
            user_id = current_user.id,
            emp_name = request.form['emp_name'],
            emp_ruc = request.form['emp_ruc'],
            emp_city = request.form['emp_city'],
            emp_desc = request.form['emp_desc']
        )
        print(emprendimiento)
        db.session.add(emprendimiento)
        db.session.commit()
        return redirect(url_for("profile"))
    
    return render_template('registrar_emprendimiento.html')

@app.route('/main_page')
@login_required
def main_page():
    return render_template('profile.html')

@app.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
    emprendimientos = Emprendimiento.query.filter_by(user_id=current_user.id)
    return render_template('profile.html', emprendimientos=emprendimientos)

# @app.route('/add_income', methods = ['GET', 'POST'])
# def add_income(emp_id):
#     if request.method == 'POST':
#         emprendimiento_id = Emprendimiento.query.filter_by(emp_id=emp_id).first
#         print(emprendimiento_id)
#         ingreso = Ingreso(
#             emprendimiento_id = emp_id,
#             ingreso = request.form['ingreso']
#         )
#         print(ingreso)
#         db.session.add(ingreso)
#         db.session.commit()
#         return redirect(url_for('dashboard.html'))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))