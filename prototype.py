from __future__ import with_statement
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/tmp/microblog.db'
DEBUG = True
SECRET_KEY = 'ubersecretKey'
USERNAME = 'admin'
PASSWORD = 'default'


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text, id from entries order by id desc')
    entries = [dict(title=row[0], text=row[1], postid=str(row[2])) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
     if request.method=='POST':
        if not session.get('logged_in'):
            abort(401)  
        g.db.execute('insert into entries (title, text) values (?, ?)',
                     [request.form['title'], request.form['text']])
        g.db.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('show_entries'))
     return render_template('add_entry.html')

@app.route('/delete/<int:post_id>', methods=['GET'])
def delete_entry(post_id):
    if session.get('logged_in'):
        g.db.execute('delete from entries where id = ?', [post_id])
        g.db.commit()
        flash("Deleting post #%d"%post_id)
        return redirect(url_for('show_entries'))
    else:
        flash("Please login before deleting anything!")
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/posts/<int:post_id>')
def show_entry(post_id):
    db_query=g.db.execute('select title, text from entries where id like(?)',[post_id])
    blog_entry = [dict(title=row[0], text=row[1]) for row in db_query.fetchall()]
    current_entry=blog_entry[0]
    return render_template('entry.html', current_entry=current_entry, post_id=post_id)

@app.route('/update_post', methods=['POST'])
def update_entry():
    if session.get('logged_in'):
        update_dict = request.form
        g.db.execute('update entries set title= ?,text= ? where id= ?', [update_dict['title'],update_dict['text'], update_dict['post_id']])
        g.db.commit()
        flash('Entry has been updated')
        return redirect(url_for('show_entries'))
    else:
        flash('Please login!')
        return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
