# Shitty code I wrote a day before deadline
# Don't Judge ;)

from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)
app.debug=True
app.secret_key = 'xyz'

# users = {'username': 'password', 'sanjay':'123', 'sahil':'123'}
session = {'username':'student'}

db = sqlite3.connect('main.db')
cursor = db.cursor()
cursor.execute('SELECT username, password FROM login')
data = cursor.fetchall()
users = dict(data)
cursor.execute('SELECT username, id FROM login')
data = cursor.fetchall()
userids = dict(data)
db.close()

@app.route('/posts')
def root():
    db = sqlite3.connect('main.db')  
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts ORDER BY id DESC')
    posts = cursor.fetchall()
    cursor.execute('SELECT DISTINCT topic FROM posts;')
    topics = cursor.fetchall()
    upvotes = {}
    for post in posts:
        cursor.execute('SELECT COUNT(userid) FROM upvotes WHERE postid = %s;' % post[0])
        num = cursor.fetchall()
        upvotes[post[0]] = num[0][0]
    db.close()
    topics = [item[0] for item in topics if item[0] is not None]
    return render_template('posts.html', upvotes=upvotes, posts=posts, topics=topics, username=session["username"])

@app.route('/upvote/<_id>')
def upvote(_id):
    if session["username"] != 'student':
        db = sqlite3.connect('main.db')  
        cursor = db.cursor()
        cursor.execute('SELECT 1 FROM upvotes WHERE userid = ? AND postid = ? LIMIT 1', (userids[session["username"]], _id))
        existing_row = cursor.fetchone()
        if not existing_row:
            cursor.execute('INSERT INTO upvotes (userid, postid) VALUES (?, ?)', (userids[session["username"]], _id))
            db.commit()
        db.close()
        return redirect('/posts')
    return redirect('/posts')

@app.route('/downvote/<_id>')
def downvote(_id):
    if session["username"] != 'student':
        db = sqlite3.connect('main.db')  
        cursor = db.cursor()
        cursor.execute('SELECT * FROM upvotes WHERE userid="%s" AND postid="%s";' % (userids[session["username"]], _id))
        existing_row = cursor.fetchone()
        if existing_row:
            cursor.execute('DELETE FROM upvotes WHERE userid="%s" AND postid="%s";' % (userids[session["username"]], _id))
            db.commit()
        db.close()
        return redirect('/posts')
    return redirect('/posts')

@app.route('/topic/<topic>')
def topic(topic):
    db = sqlite3.connect('main.db')  
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts ORDER BY id DESC')
    posts = cursor.fetchall()
    cursor.execute('SELECT DISTINCT topic FROM posts;')
    topics = cursor.fetchall()
    posts2 = []
    upvotes = {}
    for post in posts:
        if post[4] == topic:
            posts2.append(post)
    for post in posts2:
        cursor.execute('SELECT COUNT(userid) FROM upvotes WHERE postid = %s;' % post[0])
        num = cursor.fetchall()
        upvotes[post[0]] = num[0][0]
    cursor.execute('SELECT DISTINCT topic FROM posts;')
    topics = cursor.fetchall()
    db.close()
    topics = [item[0] for item in topics if item[0] is not None]
    return render_template('posts.html', upvotes=upvotes, posts=posts2, topics=topics, username=session["username"])

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
    topic = request.args.get('topic')

    return render_template('edit.html', title=title, post=post, _id=_id, topic=topic)


@app.route('/insert')
def insert():
    db = sqlite3.connect('main.db')  
    cursor = db.cursor()
    title = request.args.get('title')
    post = request.args.get('post')
    user = session['username']
    topic = request.args.get('topic')
    cursor.execute('INSERT INTO posts(title, post, user, topic) VALUES("%s", "%s", "%s", "%s")' % (title, post.replace('"', "'"), user, topic))
    db.commit()
    db.close()
    return redirect('/posts')

@app.route('/update/<_id>')
def update(_id):
    db = sqlite3.connect('main.db')  
    cursor = db.cursor()
    title = request.args.get('title')
    post = request.args.get('post')
    topic = request.args.get('topic')
    cursor.execute('UPDATE posts SET title="%s", post="%s", topic="%s" WHERE id=%s' % (title, post.replace('"', "'"), topic, _id))
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
