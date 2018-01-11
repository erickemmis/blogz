from flask import Flask, request, redirect, render_template, session, flash
import datetime, html

from model import Blog,User
from hashutils import compare_hash
from app import app,db

@app.before_request
def require_login():
    #allowed access routes without signing in
    allowed_routes = ['login', 'signup', 'blog', 'index']
    #redirect if not 
    # #!!!-- had to include the static folder --!! 
    # https://stackoverflow.com/questions/14759186/python-flask-before-request-exclude-static-directory
    if request.endpoint not in allowed_routes and 'username' not in session and '/static/' not in request.path:
        return redirect('/login')

@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", users=users)

@app.route('/login', methods=["POST", "GET"])
def login():

    #declare variables for render_template
    error = None
    username = ''

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        #get user from username
        user = User.query.filter_by(username=username).first()

        #error check username and password
        if not user:
            error = "username does not exist"
            username=''
        if user and not compare_hash(password, user.password):
            error = "password is incorrect"
            password=''
        #if no errors proceed to newpost route
        if not error:
            session['username'] = username
            return redirect('/newpost')

        

    return render_template("login.html", error=error, username=username)

@app.route('/signup', methods=["POST", "GET"])
def signup():
    error = None
    username = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if not all((username,password,verify)):
            error = "one or more fields are blank"
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = "username already exists"

        if all((username, password,verify)) and not password == verify:
            error = "Password does not match verification"

        if len(username) < 3 or len(password) < 3:
            error = "both username and password must be atlest 3 characters"

        if not error:
            #create new user
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            #login user
            session['username'] = username

            return redirect('/newpost')



    return render_template("signup.html", error=error, username=username)


@app.route('/logout')
def logout():
    del session['username']
    return redirect("/blog")

@app.route('/blog')
def blog():
    POSTS_PER_PAGE = 5
    page = 1


    if len(request.args) >= 1:
        if 'page' in request.args:
            page = int(request.args['page'])

        if 'post_id' in request.args:
            post_id = request.args.get('post_id')
            post = Blog.query.filter_by(id=post_id).first()
            return render_template('post.html', post=post)

        if 'user_id' in request.args:
            owner = User.query.filter_by(id=request.args['user_id']).first()
            user_blog = Blog.query.filter_by(owner=owner).order_by(Blog.post_date.desc()).paginate(page,POSTS_PER_PAGE,False)
            return render_template('user_blog.html', blog=user_blog, owner=owner)


    blog = Blog.query.order_by(Blog.post_date.desc()).paginate(page,POSTS_PER_PAGE,False)
    return render_template('blog.html', blog=blog)

@app.route('/newpost', methods=["POST","GET"])
def newpost():

    if request.method == 'POST':
        valid = True
        title_error = ''
        body_error = ''

        title = request.form['title']
        body = request.form['body']
        current_user = User.query.filter_by(username=session['username']).first()

        #check if both title and body are there
        if not title:
            title_error = "Pleae fill in a title"
            valid = False
        if not body:
            body_error = "Pleae fill in a body"
            valid = False


        if valid:
            #add and commit title and body in a new post if valid 
            new_post = Blog(title, body, current_user)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?post_id={0}'.format(new_post.id))
        else: 
            return render_template('newpost.html', 
                                           title_error=title_error,
                                           body_error=body_error)


    return render_template('newpost.html')
    

if __name__ == '__main__':
    app.run()