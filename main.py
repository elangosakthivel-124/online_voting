from flask import Flask,render_template,request,redirect,session
from werkzeug.security import generate_password_hash,check_password_hash
import database

app = Flask(__name__)
app.secret_key = "secretkey"

database.init_db()

def db():
    return database.connect()

@app.route("/",methods=["GET","POST"])
def register():
    if request.method=="POST":
        u=request.form["username"]
        p=generate_password_hash(request.form["password"])
        try:
            con=db()
            con.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p))
            con.commit()
            return redirect("/login")
        except:
            pass
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"]
        p=request.form["password"]

        cur=db().cursor()
        cur.execute("SELECT * FROM users WHERE username=?",(u,))
        user=cur.fetchone()

        if user and check_password_hash(user[2],p):
            session["uid"]=user[0]
            session["role"]=user[4]
            return redirect("/admin" if user[4]=="admin" else "/vote")

    return render_template("login.html")

@app.route("/vote",methods=["GET","POST"])
def vote():
    if "uid" not in session:
        return redirect("/login")

    con=db()
    cur=con.cursor()

    cur.execute("SELECT voted FROM users WHERE id=?",(session["uid"],))
    if cur.fetchone()[0]:
        return redirect("/results")

    if request.method=="POST":
        cid=request.form["candidate"]
        cur.execute("UPDATE candidates SET votes=votes+1 WHERE id=?",(cid,))
        cur.execute("UPDATE users SET voted=1 WHERE id=?",(session["uid"],))
        con.commit()
        return redirect("/results")

    cur.execute("SELECT * FROM candidates")
    return render_template("vote.html",data=cur.fetchall())

@app.route("/admin",methods=["GET","POST"])
def admin():
    if session.get("role")!="admin":
        return redirect("/login")

    con=db()
    cur=con.cursor()

    if request.method=="POST":
        con.execute("INSERT INTO candidates(name) VALUES(?)",(request.form["name"],))
        con.commit()

    cur.execute("SELECT * FROM candidates")
    return render_template("admin.html",data=cur.fetchall())

@app.route("/results")
def results():
    cur=db().cursor()
    cur.execute("SELECT name,votes FROM candidates")
    return render_template("results.html",data=cur.fetchall())

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)
