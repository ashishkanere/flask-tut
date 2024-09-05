from flask import Flask, render_template, request, session 
from flask_mail import Mail

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json


# with open('config.json', 'r') as c:
#     #print(json.load(c))
#     params = json.load(c)["params"]

# local_server =params['local_server']



try:
    with open('config.json', 'r') as c:
        params = json.load(c)["params"]
        print(params)  # Print to verify the content
except Exception as e:
    print(f"Error loading config.json: {e}")


local_server = params.get('local_server', True)

app = Flask(__name__)

app.secret_key ='war-machine-rox'

app.config.update(
    MAIL_SERVER= 'smtp.gmail.com',
    MAIL_PORT= '456',
    MAIL_USE_SSL= True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['passwd']
)
mail = Mail(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/codingthunder'
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] =params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
    

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),  nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120),  nullable=False)
    date = db.Column(db.String(12),  nullable=True)
    email = db.Column(db.String(20),  nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80),  nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120),  nullable=False)
    tagline = db.Column(db.String(120),  nullable=False)
    date = db.Column(db.String(12),  nullable=True)
    img_file = db.Column(db.String(12),  nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:params["no_of_posts"]]
    return render_template('index.html', params=params, posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():

    if ('user' in session and session['user']==params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts= posts)

    if request.method=='POST':
       username = request.form.get('uname')
       userpass = request.form.get('upass')
       if(username == params['admin_user'] and userpass == params['admin_password']):
           session['user'] = username
           posts = Posts.query.all()
           return render_template('dashboard.html', params=params, posts= posts)
       

    else:
        return render_template('login.html', params=params) 

# @app.route("/contact")
# def contact():
#     return render_template('contact.html')


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post =Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',  params=params, post=post)


@app.route("/contact", methods ={'GET', 'POST'})
def contact():
    if(request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')

        entry = Contacts(name=name, phone_num=phone, date=datetime.now(), msg=message, email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name, 
                          sender=email,
                          recipients = [params['gmail-user']], 
                          body = message + "\n" + phone
                          )
    





    return render_template('contact.html', params=params)


app.run(debug=True)


