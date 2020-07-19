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

@app.route('/signup', methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['signup-name']
        username = request.form['signup-username']
        email = request.form['signup-email']
        password = hashlib.md5(request.form['signup-password'].encode())
        token = hashlib.md5(str(randint(1,1000000)).encode())
        db = get_db()
        cur = db.execute('select "id","name","username","email","password" from users where "username" = ?;',[username])
        result=cur.fetchone()
        if result:
            return render_template('signup.html',flag = 0)
        db.execute('insert into users ("name","username","email","password","token") values (?,?,?,?,?)',[name,username,email,password.hexdigest(),token.hexdigest()])
        db.commit()
        authenticator(username,token.hexdigest())
        return redirect(url_for('login'))
    return render_template('signup.html', flag = 1)

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
