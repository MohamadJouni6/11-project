from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "c1o!l2t@a3r#j4o$"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tree.db"
db = SQLAlchemy(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), nullable=False)
  email = db.Column(db.String(50), nullable=False, unique=True)
  hash = db.Column(db.String(200), nullable=False)

def __repr__(self):
  return f"User('{self.username}', '{self.email}')"

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
  return render_template("templates/index.html")

@app.route("/register", methods = ["POST", "GET"])
def register():
  if request.method == "GET":
    return render_template("register.html")
  else:
    name = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirm")
    if not name or not password or not confirmation:
      flash("The name, password and confirmation must be provided")
      return redirect("/register")
    check = db.execute("SELECT username FROM users WHERE username = ?", name)
    if check:
      flash("Sorry, This name is already taken. Try another one.")
      return redirect("/register")
    
    if password != confirmation:
      flash("The password and the confirmation arent the same... Try Again.")
      return redirect("/register")
    
    hash = generate_password_hash(password)
    db.execute("INSERT INTO users (usernamem password_hash) VALUES (?, ?)", name, hash)
    id = db.execute("SELECT id FROM users WHERE username = ?", name)
    session["user_id"] = id[0]["id"]
    return redirect("/")

@app.route("/login", methods = ["POST", "GET"])
def login():
  if request.method == "GET":
    return render_template("login.html")
  else:
    name = request.form.get("username")
    password = request.form.get("password")
    if not name or not password:
      flash("The name and password must be provided")
      return redirect("/login")
    check = db.execute("SELECT * FROM users WHERE username = ?", name)
    if not check:
      flash("Sorry!! The username is wrong or doesnt exist... Try again.")
      return redirect("/login")
    if not check_password_hash(check[0]["password_hash"], password):
      flash("Sorry!! The password is incorrect... Try again.")
      return redirect("/login")
    session["user_id"] = check[0]["id"]
    return redirect("/")

@app.errorhandler(404)
def page_not_found(e):
  return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
  return render_template("404.html"), 500

if __name__ == '__main__':
    app.run(debug=True)