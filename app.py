from flask import Flask,request,render_template,redirect,make_response
import sqlite3
import json

db= sqlite3.connect("contact.db")
cur = db.cursor()
cur.execute("CREATE table if not exists user(id INTEGER PRIMARY KEY AUTOINCREMENT,name text,email text,password text)")
cur.execute("CREATE table if not exists profile(to_id INTEGER,names text ,links text)")
db.commit()
db.close() 

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/profile",methods=["POST","GET"])
def profile():
    if request.method=="POST":
        email = request.form.get("email")
        password=request.form.get("password")
        db= sqlite3.connect("contact.db")
        cur = db.cursor()
        cur.execute("SELECT * from user WHERE email=? and password=?",(email,password))
        fetch = cur.fetchall()
        db.close()
        cid = request.cookies.get("id")
        current = str(request.host_url) + str(cid)
        if fetch:
            cookiename = request.cookies.get("name")
            return render_template("profile.html",email=email,name=cookiename,current=current)
        else:
            return "404"
    else:
        cname = request.cookies.get("name")
        cemail = request.cookies.get("email")
        cpassword = request.cookies.get("password")
        cid = request.cookies.get("id")
        if cname and cemail and cpassword:
            db= sqlite3.connect("contact.db")
            cur = db.cursor()
            cur.execute("SELECT * from user WHERE email=? and password=?",(cemail,cpassword))
            fetch = cur.fetchall()
            db.close()
            current = str(request.host_url) + str(cid)
            if fetch:
                return render_template("profile.html",email=cemail,name=cname,current=current)

@app.errorhandler(404)
def error():
    return "Not found",404

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method=="POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        db= sqlite3.connect("contact.db")
        cur = db.cursor()
        cur.execute("INSERT into user(name,email,password) VALUES(?,?,?)",(name,email,password))
        db.commit()
        cur.execute("SELECT id from user WHERE email=? and password=?",(email,password))
        fetid = str(cur.fetchall()[0][0])
        db.close()
        resp= make_response(render_template("login.html"))
        resp.set_cookie("email",email)
        resp.set_cookie("password",password)
        resp.set_cookie("name",name)
        resp.set_cookie("id",fetid)
        return resp
    else:
        return render_template("login.html")
@app.route("/signup",methods=["POST","GET"])
def signup():
    return render_template("signup.html")

@app.route("/admin")
def admin():
    return render_template("loginadmin.html")

@app.route('/adminpanel',methods=["POST","GET"])
def adminpanel():
    if request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email=="admin" and password=="0109471":
            db= sqlite3.connect("contact.db")
            cur = db.cursor()
            cur.execute("SELECT * from user")
            fetch = cur.fetchall()
            db.close()
            return fetch
            
@app.route("/added",methods=["POST"])
def added():
    if request.method=="POST":
        names = request.form.getlist("name[]")
        links = request.form.getlist("link[]")
        id = request.cookies.get("id")
        json_names = json.dumps(names)
        json_links = json.dumps(links)
        db= sqlite3.connect("contact.db")
        cur = db.cursor()
        cur.execute("INSERT into profile(to_id,names,links)VALUES(?,?,?)",(id,json_names,json_links))
        db.commit()
        db.close()
        return redirect(f"/{id}")

@app.route("/<id>",methods=["POST","GET"])
def profilelink(id):
    db= sqlite3.connect("contact.db")
    cur = db.cursor()
    cur.execute("SELECT name,email from user WHERE id=?",(id,))
    fetch = cur.fetchall()
    if fetch:
        name = fetch[0][0]
        email = fetch[0][1]
        cur.execute("SELECT names,links from profile where to_id=?",(id,))
        fetg = cur.fetchall()
        fetnames = fetg[0][0]
        fetlinks = fetg[0][1]
        lnames=json.loads(fetnames)
        links=json.loads(fetlinks)
        print(lnames,links)
        my_dict = dict(zip(lnames, links))
        print(my_dict)
        db.close()
        return render_template("idprofile.html",name=name,email=email,d=my_dict)
    else:
        return "page not found"


app.run(debug=True)