# main.py

from flask import Flask, request, jsonify, redirect, render_template
import hashlib
from math import floor
import string
from urlparse import urlparse
import sqlite3
from sqlite3 import OperationalError
from flask_cors import CORS

host = 'http://localhost:9999/'
app = Flask(__name__)
cors = CORS(app)

#Create url_shortner.db in the root folder of the application


def table_check():
    print "===== creating the table ====="
    create_table = """
        CREATE TABLE WEB_URL(
        ID text PRIMARY KEY,
        URL text NOT NULL
        );
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
            print "===== created table successfully ====="
        except Exception as e:
            print "===== unable to create table =====", e
            pass


# Home page where user should enter

@app.route('/', methods=['GET'])
def home0():
    print "===== Home ====="
    return render_template('home.html')


@app.route('/', methods=['POST'])
def home1():
    if request.method == 'POST':
        original_url = request.form.get('url')
        encoded_string = hashlib.sha1(
            str(original_url).encode('utf-8')).hexdigest()[0:12]
        print "===== the original url is: ", original_url
        print "===== the encoded string is: ", encoded_string
        if urlparse(original_url).scheme == '':
            original_url = 'http://' + original_url
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            result_cursor = cursor.execute(
                "INSERT INTO WEB_URL (ID, URL) VALUES (?, ?)", (encoded_string, original_url))
            print result_cursor
    return jsonify({'url': 'http://localhost:5000/' + encoded_string})


@app.route('/short/<short_url>')
def home2(short_url):
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        select_row = """
            SELECT URL FROM WEB_URL
            WHERE ID='%s'
            """ % (short_url)
    result_cursor = cursor.execute(select_row)
    try:
        redirect_url = result_cursor.fetchone()[0]
        print "===== redirecting to ======", redirect_url
    except Exception as e:
        print e
    return redirect(redirect_url)


@app.route('/recent/<pageNumber>')
def home3(pageNumber):
    skip = int(pageNumber)
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        select_row = """
            SELECT * FROM WEB_URL LIMIT 10 OFFSET (SELECT COUNT(*) FROM WEB_URL)-'%d'
            """ % (skip)
    result_cursor = cursor.execute(select_row)

    return jsonify({'results':
                    [dict(zip([column[0] for column in cursor.description], row))
                     for row in result_cursor.fetchall()]})


@app.route('/totalRecords')
def home4():
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        select_row = """
            SELECT COUNT(*) FROM WEB_URL
            """
    result_cursor = cursor.execute(select_row)
    return str(result_cursor.fetchone()[0])


if __name__ == '__main__':
    # Create Database
    table_check()
app.run(threaded=True)
