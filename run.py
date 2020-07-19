from flask import Flask , render_template, g, request, url_for,redirect, session
# import sqlite3
# import requests
# import json
# import smtplib, ssl, glob
# from email import encoders
# from email.mime.base import MIMEBase
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from database import get_db
# import hashlib
# import requests
# import os
# from random import randint


app = Flask(__name__)


@app.route('/')
def home():
    return  render_template('index.html')

@app.route('/login')
def login():

    return  render_template('login.html')

@app.route('/signup', methods = ['GET','POST'])
def signup():
    return render_template('signup.html')


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
