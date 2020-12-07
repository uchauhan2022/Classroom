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

def get_current_user():
    user_result = None
    if 'username' in session:
        username = session['username']
        db = get_db()
        cur = db.execute('select "id","name","email","password" from users where "name" = ?;',[username])
        user_result = cur.fetchone()
    
    return user_result

@app.route('/')
def home():
    return  render_template('index.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    user = get_current_user()
    if user:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['login-username']
        password = hashlib.md5(request.form['login-password'].encode())
        db = get_db()
        cur = db.execute('select "activation_status","name","email","password","role" from users where "name" = ?;',[username])
        result=cur.fetchone()
        if result:
            if result['password']==password.hexdigest() :
                if result['activation_status']==1:
                    session['username'] = username
                    if result["role"]=="Teacher":
                        return redirect(url_for('dashboardt'))
                    return  redirect(url_for('dashboard'))
                else:
                    return "please verify account"
            else :
                return render_template('login.html',flag=0)
        else:
            return render_template('login.html',flag=0) # render_template('login.html',flag=0)
    return render_template('login.html',flag = 1)



@app.route('/verify', methods=['GET','POST'])
def verify():
    token=request.args.get('a')
    emailgot = request.args.get('b')
    if request.method == 'POST':
        email = request.form['authenticate-email']
        password = hashlib.md5(request.form['authenticate-password'].encode())
        token = request.form['token']
        db = get_db()
        cur = db.execute('select "id","name","email","password","token" from users where "email" = ?;',[email])
        result=cur.fetchone()
        if result:
            if result['password']==password and token==result['token'] :
                session['email'] = email
                f=get_db()
                f.execute('update users set "activation_status" = 1 where email=? ', [email])
                f.commit()
                return  redirect(url_for('adminApproval'))
            else :
                return str(password)#render_template('login.html',flag=0)
        else:
            return "fail2"#render_template('login.html',flag=0)
    return render_template('authenticate.html',flag = 1,token=token,emailgot=emailgot)


@app.route('/adminApproval')
def adminApproval():
    return '<h1> Wait for administration Approval'

@app.route('/profile')
def profile():
    return render_template('user_profile.html')

@app.route('/profilet')
def profilet():
    return render_template('user_profile.html')


@app.route('/UCS503')
def UCS503():
    user=get_current_user()
    if user:
        topics = get_topics('ucs503')
        assignments=get_assignments('ucs503')
        quiz=get_quiz('ucs503')
        return render_template('UCS503.html', user=user,topics=topics,assignments=assignments,quiz=quiz)
    else:
        return redirect(url_for("login"))

@app.route('/coe4')
def coe4():
    user=get_current_user()
    if user:
        topics = get_topics('ucs503')
        assignments=get_assignments('ucs503')
        quiz=get_quiz('ucs503')
        return render_template('UCS503.html', user=user,topics=topics,assignments=assignments,quiz=quiz)
    else:
        return redirect(url_for("login"))

def get_quiz(x):
    db=get_db()
    cur = db.execute('select * from quiz where code = ?;',[x])
    result=cur.fetchall()
    return result

def get_topics(x):
    db=get_db()
    cur = db.execute('select * from topics where code = ?;',[x])
    result=cur.fetchall()
    return result

def get_assignments(x):
    db=get_db()
    cur = db.execute('select * from assignments where code = ?;',[x])
    result=cur.fetchall()
    return result

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

@app.route('/dashboard' ,methods = ['GET','POST'] )
def dashboard():
    user = get_current_user()
    if user:
        tasks=get_tasks(user['name'])
        if request.method=='POST':
            heading = request.form['task-heading']
            description = request.form['task-description']
            db = get_db()
            db.execute('insert into tasks ("user", "heading","description") values(?,?,?)',[user["name"],heading,description])
            db.commit()
            tasks=get_tasks(user['name'])
            return render_template('dashboard.html', user=user,tasks=tasks)
        return render_template('dashboard.html', user=user,tasks=tasks)
    else :
        return redirect(url_for('login'))

@app.route('/dashboardt' ,methods = ['GET','POST'] )
def dashboardt():
    user = get_current_user()
    
    if user:
        tasks = get_tasks(user['name'])
        lectures=get_lectures(user['name'])
        if request.method=='POST':
            name = request.form['lecture-name']
            description = request.form['lecture-description']
            date = request.form['lecture-date']
            time = request.form['lecture-time']
            batch = request.form['lecture-batch']
            db = get_db()
            db.execute('insert into lectures ("user", "name","description","date","time","batch") values(?,?,?,?,?,?)',[user["name"],name,description,date,time,batch])
            db.commit()
            lectures=get_lectures(user['name'])
            return render_template('dashboardt.html', user=user,lectures=lectures, tasks = tasks)
        return render_template('dashboardt.html', user=user,lectures=lectures,tasks=tasks)
    else :
        return redirect(url_for('login'))

def get_tasks(x):
    db=get_db()
    cur = db.execute('select * from tasks where user = ?;',[x])
    result=cur.fetchall()
    return result

def get_lectures(x):
    db=get_db()
    cur = db.execute('select * from lectures where user = ?;',[x])
    result=cur.fetchall()
    return result

@app.route('/logout')
def logout():
    user = get_current_user()
    if user:
        session.pop('username', None)
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


if(__name__) == "__main__":
    app.run()
