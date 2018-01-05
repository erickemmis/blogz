from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 
import datetime, html


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://blogz:AARGPRDtmetOhvD0@localhost:8889/blogz"
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.String(280))
    post_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.post_date = datetime.datetime.now()
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/blog')
def blog():

    if len(request.args) == 1:
        post_id = request.args.get('id')
        post = Blog.query.filter_by(id=post_id).first()
        return render_template('post.html', post=post)

    blog = Blog.query.order_by(Blog.post_date.desc()).all()
    return render_template('blog.html', blog=blog)

@app.route('/newpost', methods=["POST","GET"])
def newpost():

    if request.method == 'POST':
        valid = True
        title_error = ''
        body_error = ''

        title = request.form['title']
        body = request.form['body']
        #TODO get current owner id

        #check if both title and body are there
        if not title:
            title_error = "Pleae fill in a title"
            valid = False
        if not body:
            body_error = "Pleae fill in a body"
            valid = False


        if valid:
            #add and commit title and body in a new post if valid
            #TODO include owner id for th new_post
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_post.id))
        else: 
            return render_template('newpost.html', 
                                           title_error=title_error,
                                           body_error=body_error)


    return render_template('newpost.html')
    

if __name__ == '__main__':
    app.run()