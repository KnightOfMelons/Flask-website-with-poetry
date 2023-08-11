import sqlite3
import os

from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g

from DataBase import DataBase

DATABASE = '/tmp/flsk.db'
DEBUG = True
SECRET_KEY = '00609b93a1aeab8bdbabff9583293bea48b91b1f'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsk.db')))

def connect_db():
    con = sqlite3.connect(app.config['DATABASE'])
    con.row_factory = sqlite3.Row
    return con

def create_db():
    db = connect_db()
    with open('sq_db.sql', 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

menu = [
    {'name': 'Biography', 'url': '/'},
    {'name': 'Artworks', 'url': '/artworks'},
    {'name': 'Feedback', 'url': '/contacts'}
]

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.route('/index')
@app.route('/')
def index():
    db = get_db()
    dbase = DataBase(db)
    return render_template('index.html', title='Main', menu=dbase.get_menu(), posts=dbase.get_posts_announces())

@app.route('/add_post', methods=['POST','GET'])
def add_post():
    db = get_db()
    dbase = DataBase(db)

    if request.method == 'POST':
        if len(request.form['title']) > 4 and len(request.form['text']) > 10:
            res = dbase.add_post(request.form['title'], request.form['text'], request.form['url'])
            if res:
                flash('Verse added successfully!', category='success')
            else:
                flash('Error adding verse', category='error')
        else:
            flash('Error adding verse', category='error')
    return render_template('add_post.html', title='Adding verse', menu=dbase.get_menu())

@app.route('/post/<post_id>')
def show_post(post_id):
    db = get_db()
    dbase = DataBase(db)

    title, post = dbase.get_post(post_id)
    if not title:
        abort(404)

    return render_template('post.html', title=title, post=post, menu=dbase.get_menu())

@app.route('/artworks')
def artworks():
    return render_template('artworks.html', title='Artworks', menu=menu)

@app.route('/contacts', methods=['POST','GET'])
def contacts():
    if request.method == 'POST':
        if len(request.form['username']) > 1:
            flash('Message sent successfully!', category='success')
        else:
            flash('Error!', category='error')

    return render_template('contacts.html', title='Feedback',menu=menu)

@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Пользователь {username}'

@app.route('/login', methods=['POST','GET'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == 'william' and request.form['password'] == '1616':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', title='Authorization', menu=menu)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu), 404

if __name__ == '__main__':
    app.run(debug=True)
