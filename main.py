from flask import Flask,url_for,jsonify,request,render_template,session,redirect,render_template_string
from flask_sqlalchemy import SQLAlchemy
import json, os
import JsonLoader as jl
import pickle_loader as pl
import gemini
from flask_cors import CORS
import PasswordEncoder as pe
from datetime import datetime

app = Flask(__name__)
app.secret_key = '1ekfr40t040rto'

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///database.db"
CORS(app)
file = "data.dat"
if not os.path.exists(file):
  pl.save_pickle({}, file)
data = pl.load_pickle(file)

db = SQLAlchemy(app)

class QuotesDataBase(db.Model):
  __tablename__ = 'quotes'
  id=db.Column(db.Integer,primary_key=True)
  quote_description = db.Column(db.Text,nullable=False, unique=False)
  quote_owner = db.Column(db.String(20), nullable=False)
  unique_id = db.Column(db.ForeignKey("user.id"))
  
class User(db.Model):
  __tablename__ = 'user'
  id=db.Column(db.Integer,primary_key=True)
  username = db.Column(db.String(64), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)
  quotes = db.relationship('MyQuotes', backref='owner', lazy=True)
  
class MyQuotes(db.Model):
  __tablename__ = 'myquotes'
  id=db.Column(db.Integer,primary_key=True)
  quote_description = db.Column(db.Text,nullable=False, unique=False)
  quote_owner = db.Column(db.String(20), nullable=False)
  unique_id = db.Column(db.ForeignKey("user.id"))
  
class Admin(db.Model):
  id = db.Column(db.Integer,primary_key=True)
  username=db.Column(db.String(64))
  password = db.Column(db.String(120))

@app.route("/user_home", methods=["POST", "GET"])
def user_home():
  username = session.get("username")
  user = User.query.filter_by(username=username).first()
  print(user.username)
  quotes = user.quotes
  print([x.quote_description for x in quotes])
  return render_template("home.html",quotes=quotes, username=username)
  
@app.route("/")
def login():
  return render_template("login.html")
  
@app.route("/login",methods=["POST","GET"])
def check_login():
  admin_list = Admin.query.all()
  username = request.form.get("username")
  print(username)
  password = request.form["password"]
  if not username and password:
    return f"No values entered for username and password",404
  if username in [x.username for x in admin_list]:
    return redirect(url_for('admin_login', username=username, password=password))
  print(username,password)
  user = User.query.filter_by(username=username).first()
  if user:
    if user.password != pe.encode_str(password):
      return jsonify({"status":"Error happened. Invalid Password."})
    print("Login successful, for ",username)
    session["username"]=username
    return redirect(url_for("home_quotes"))
  new_user = User(username=username,password=pe.encode_str(password))
  db.session.add(new_user)
  db.session.commit()
  session["username"] = username
  return redirect(url_for('home_quotes'))
  
@app.route("/home/quotes")
def home_quotes():
  username = session.get("username")
  _quotes_ = QuotesDataBase.query.all()
  quotes = [quote for quote in _quotes_]
  return render_template("home.html",quotes=quotes, username=username)
  
@app.route("/create/quote", methods=["POST", "GET"])
def create_quote(): 
  quote_description = request.form.get("quote")
  print(quote_description)
  if not quote_description:
    return render_template("create_quote.html", error="Please enter a valid quote")
  owner = session.get("username")
  new_public_post = QuotesDataBase(quote_description=quote_description, quote_owner=owner)
  db.session.add(new_public_post)
  db.session.commit()
  return render_template("create_quote.html",status="Your quote has been added successfully")
  
@app.route("/myquotes")
def my_quotes():
  username = session.get("username")
  user = User.query.filter_by(username=username).first()
  qoutes = user.quotes
  return render_template("white_list.html", quotes=quotes)

@app.route("/contact/form",methods=["POST","GET"] )
def contact_form():
  global data,file
  username = session.get("username")
  name =request.form.get("name")
  phone = request.form.get("phone")
  email = request.form.get("email")
  issue = request.form.get("issue")
  if not name or phone=="" or issue=="" or email=="":
    return render_template("contact.Html",error="One or more fields need to be filled")
  data[username]={
    "name":name,
    "email":email,
    "phone":phone,
    "issue":issue, 
    "data":time.asctime(time.gmtime())
    }
  try:
    jl.save_json(data , file)
    return render_template("contact.html",status="You Issue have been submitted for viewing. Thank you for your feedback", username=username)
  except Exception as e:
    return render_template("home.html", error="Your message wws not sent successfully, Please try again.", username=us)
    
@app.route("/getai/quote", methods=["POST","GET"])
def generate_ai_quote():
  try:
    quote_ai = gemini.chat_ai("give me a random quote, just a random quote, dont ask me if i want more or any extra texts, just the random quote text directly. dont even say, heres the random quote , just give the random quote directly.")
    return render_template("create_quote.html",generated_ai_quote=quote_ai)
  except Exception as e:
    return render_template("create_quote.html", error="Error occured, could not create a quote.")
    
@app.route("/create_post")
def create_post():
  return render_template("create_quote.html")
@app.route("/issues")
def contact_template():
  username=session.get("username")
  return render_template("contact.html", username=username)
@app.route("/logout")
def logout():
  session.pop("username")
  return render_template_string("""
  <h2>Logged you out successfully. Don't go back, you might encounter unforseen errors."</h2><br>
  <a href="/">Click here to go back to login page.</a>
  """)
  
  
 ######### ADMIN MANAGEMENT HERE #######
 
 
 
@app.route("/super_user_login/<username>/<password>", methods=["POST","GET"])
def admin_login(username, password):
  admin_user = Admin.query.filter_by(username=username).first()
  if not admin_user:
    return render_template("login.html")
  if admin_user.password!=password:
    return render_template("login.html")
  session["admin"]=username
  return redirect(url_for('admin_home'))
    
@app.route("/admin/home")
def admin_home():
  users = User.query.all()
  username = session.get("admin")
  quotes = QuotesDataBase.query.all()
  admin_users = Admin.query.filter_by(username=username).first()
  return render_template("/admin/admin_dashboard.html", users=users, admin_user=admin_users, quotes=quotes)
  
@app.route("/make_admin/<username>", methods=["POST", "GET"])
def make_admin(username):
  users = User.query.all()
  user = User.query.filter_by(username=username).first()
  if not user or user.username=="":
    return render_template("/admin/users.html", error="Invalid name and password.", users = users)
  try:
    new_admin = Admin(username=user.username, password =user.password)
    db.session.add(new_admin)
    db.session.commit()
    return render_template("/admin/users.html", status=f"You have successfully made {username} an Admin.", users=users)
  except Exception as e:
    return render_template("/admin/users.html", error="An error occured, seems you have made that user an Admin already.", users=users)

@app.route("/delete_qoute/<quote_id>",  methods=["POST","GET"])
def delete_quote(quote_id):
  quotes = QuotesDataBase.query.all()
  for x in quotes:
    if quote_id.strip().lower()==x.quote_description.strip().lower():
      db.session.delete(x)
      db.session.commit()
      return render_template("/admin/quotes.html", status="Quote has been deleted successfully!", quotes=quotes)
    return render_template("/admin/quotes.html", error="Could not delete quote ", quotes=quotes)
  return render_template("/admin/quotes.html", error="Could not find a matching ID.", quotes=quotes)
  
@app.route("/all_quotes")
def all_quotes():
  quotes = QuotesDataBase.query.all()
  return render_template("/admin/quotes.html", quotes=quotes)
  
@app.route("/all_users")
def all_users():
  users = User.query.all()
  return render_template("/admin/users.html", users=users)

@app.route("/delete_user/<username>", methods=["POST","GET"])
def delete_user(username):
  users = User.query.all()
  user = User.query.filter_by(username=username).first()
  if not user:
    return render_template("/admin/users.html", error=f"The user {username} was not found !" ,users=users)
  db.session.delete(user)
  db.session.commit()
  return render_template("/admin/users.html",status=f"User {username} has be deleted..." , users=users)
  
@app.route("/admin_logout")
def  admin_logout():
  session.pop("admin")
  return render_template_string("""
  <h2>Logged you out successfully as Admin. Don't go back, you might encounter unforseen errors."</h2><br>
  <a href="/">Click here to go back to login page.</a>
  """)
  
@app.route("/search_user", methods=["GET", "POST"])
def search_user():
  username = request.args.get("usernames")
  return username
  
@app.route("/feedbacks")
def feedback():
  global data
  print(data)
  data_ = data
  return render_template("/admin/feedback.html", data=data_)
  
with app.app_context():
  db.create_all()
if __name__ == '__main__':
  app.run(debug=True)