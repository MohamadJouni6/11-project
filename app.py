from flask import Flask, flash, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = "c1o!l2t@a3r#j4o$"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:J#kL9!pQ2vR@localhost/tree"
db = SQLAlchemy(app)

class users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), nullable=False, unique=True)
  email = db.Column(db.String(50), nullable=False, unique=True)
  hash = db.Column(db.String(200), nullable=False)

  def __repr__(self):
    return f"User('{self.username}', '{self.email}')"

class registeration(FlaskForm):
  username = StringField("Username", validators=[DataRequired()])
  email = EmailField("Email", validators=[DataRequired(), Email()])
  password = PasswordField("Password", validators=[DataRequired()])
  confirmation = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
  submit = SubmitField("Register")

class logging(FlaskForm):
  username = StringField("Username", validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired()])
  submit = SubmitField("Login")

@app.cli.command("create_db")
def create_db():
  with app.app_context():
    db.create_all()

def login_required(f):
  """
  Decorate routes to require login.

  http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
  """
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if session.get("user_id") is None:
      return redirect("/login")
    return f(*args, **kwargs)
  return decorated_function

@app.route("/")
@login_required
def index():
  return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
  form = registeration()
  if form.validate_on_submit():
    user = users.query.filter_by(email=form.email.data).first()
    if user:
      flash("Sorry! This email is for an existing account.")
      return redirect("/register")
    
    user = users.query.filter_by(username=form.username.data).first()
    if user:
      flash("Sorry! This username is already taken.")
      return redirect("/register")

    new_user = users(username=form.username.data, email=form.email.data, hash=generate_password_hash(form.password.data))
    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id
    flash("You have registered successfully! Welcome!")
    return redirect("/")

  return render_template("register.html", form=form)

@app.route("/login", methods = ["POST", "GET"])
def login():
  form = logging()
  return render_template("login.html", form=form)
  
@app.errorhandler(404)
def page_not_found(e):
  return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
  return render_template("404.html"), 500

if __name__ == '__main__':
  # Use Flask CLI to create tables
  @app.cli.command("create_db")
  def create_db():
    with app.app_context():
      db.create_all()
  app.run(debug=True, port=5000)