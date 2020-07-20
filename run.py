from flask import Flask , render_template, g, request, url_for,redirect, session
import sqlite3
import requests
import json
import smtplib, ssl, glob
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database import get_db
import hashlib
import requests
import os
from random import randint


app = Flask(__name__)

app.config['DEBUG']=True
app.config['SECRET_KEY']= os.urandom(24)

# FUNCTIONS
def authenticator(email, token):
    user_result = None
    db = get_db()
    cur = db.execute('select "name","email" from users where "email" = ?;',[email])
    user_result = cur.fetchone()
    name = user_result['name']
    subject = "Verify Email Address"
    sender_email = "isboomboomboom@gmail.com"
    receiver_email = user_result['email']
    temp_email = hashlib.md5(receiver_email.encode())
    password = "Test_1234#"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email
    bodytext = "Click on the link to verify account :"
    link = "http://127.0.0.1:5000/verify?a="+token+"&b="+str(temp_email.hexdigest())
    body = bodytext+link
    message.attach(MIMEText(body, "plain"))
    text = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)






# ROUTES
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def home():
    return  render_template('index.html')

@app.route('/login')
def login():
    return  render_template('login.html')

@app.route('/verify', methods=['GET','POST'])
def verify():
    token=request.args.get('a')
    emailgot = request.args.get('b')
    if request.method == 'POST':
        username = request.form['login-username']
        password = hashlib.md5(request.form['login-password'].encode())
        token = request.form['token']
        db = get_db()
        cur = db.execute('select "id","name","username","email","password","token" from users where "username" = ?;',[username])
        result=cur.fetchone()
        if result:
            if result['password']==password.hexdigest() and token==result['token'] :
                session['username'] = username
                f=get_db()
                f.execute('update users set "activation_status" = 1 where username=? ', [username])
                f.commit()
                return  redirect(url_for('dashboard'))
            else :
                return "fail1"#render_template('login.html',flag=0)
        else:
            return "fail2"#render_template('login.html',flag=0)
    return render_template('authenticate.html',flag = 1,token=token,emailgot=emailgot)



@app.route('/signup', methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['signup-name']
        role = request.form['signup-role']
        email = request.form['signup-email']
        password = hashlib.md5(request.form['signup-password'].encode())
        token = hashlib.md5(str(randint(1,1000000)).encode())
        db = get_db()
        cur = db.execute('select * from users where "email" = ?;',[email])
        result=cur.fetchone()
        if result:
            return render_template('signup.html',flag = 0)
        db.execute('insert into users ("name","email","password","token","role") values (?,?,?,?,?)',[name,email,password.hexdigest(),token.hexdigest(),role])
        db.commit()
        authenticator(email,token.hexdigest())
        return redirect(url_for('login'))
    return render_template('signup.html', flag = 1)

@app.route('/logout')
def logout():
    user = get_current_user()
    if user:
        session.pop('email', None)
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


if(__name__) == "__main__":
    app.run()
