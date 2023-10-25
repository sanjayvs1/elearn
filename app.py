from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)
app.debug=True
app.secret_key = 'xyz'

users = {'username': 'password', 'sanjay':'123'}
session = {'username':'student'}

@app.route('/posts')
def root():
    db = sqlite3.connect('main.db')  
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts ORDER BY id DESC')
    posts = cursor.fetchall()
    db.close()
    
    return render_template('posts.html', posts=posts, username=session["username"])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/post/<_id>')
def post(_id):
    db = sqlite3.connect('main.db')  
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts WHERE id=%s' % _id)
    post = cursor.fetchone()
    db.close()
    return render_template('post.html', post=post)

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/edit')
def edit():
    title = request.args.get('title')
    post = request.args.get('post')
    _id = request.args.get('_id')

    return render_template('edit.html', title=title, post=post, _id=_id)


@app.route('/insert')
def insert():
    db = sqlite3.connect('main.db')  
    cursor = db.cursor()
    title = request.args.get('title')
    post = request.args.get('post')
    cursor.execute('INSERT INTO posts(title, post) VALUES("%s", "%s")' % (title, post.replace('"', "'")))
    db.commit()
    db.close()
    return redirect('/posts')

@app.route('/update/<_id>')
def update(_id):
    db = sqlite3.connect('main.db')  
    cursor = db.cursor()
    title = request.args.get('title')
    post = request.args.get('post')
    cursor.execute('UPDATE posts SET title="%s", post="%s" WHERE id=%s' % (title, post.replace('"', "'"), _id))
    db.commit()
    db.close()
    return redirect('/posts')

@app.route('/delete/<_id>')
def delete(_id):
    db = sqlite3.connect('main.db')  
    cursor = db.cursor()
    cursor.execute('DELETE FROM posts WHERE id=%s' % _id)
    db.commit()
    db.close()
    return redirect('/posts')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect('/posts')

        return 'Invalid credentials. <a href="/login">Login</a>'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session['username'] = 'student'
    return redirect('/posts')
  
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080,threaded=True)
