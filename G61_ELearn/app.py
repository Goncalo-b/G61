# -*- coding: utf-8 -*-
"""
@author: Grupo 61 - FEUP PC II 2025/2026
"""
from flask import Flask, render_template, request, session
from datafile import filename
from classes.platform_class import Platform
from classes.certificate import Certificate
from classes.course import Course
from classes.person import Person
from classes.transaction import Trans
from subs.apps_gform import apps_gform
from subs.apps_analysis import apps_analysis
from subs.apps_stats import apps_stats

app = Flask(__name__)
app.secret_key = 'g61_feup_pc2_2026'

db = filename + 'novadatabase6.db'
Platform.read(db)
Certificate.read(db)
Course.read(db)
Person.read(db)
Trans.read(db)

def get_stats():
    return {'platforms': len(Platform.obj), 'certificates': len(Certificate.obj),
            'courses': len(Course.obj), 'persons': len(Person.obj),
            'transactions': len(Trans.obj)}

@app.route("/")
def index():
    return render_template("index.html", ulogin=session.get("user"), stats=get_stats())

@app.route("/login")
def login():
    return render_template("login.html", ulogin=None, resul="")

@app.route("/logoff")
def logoff():
    session.pop("user", None)
    return render_template("index.html", ulogin=None, stats=get_stats())

@app.route("/chklogin", methods=["post","get"])
def chklogin():
    user = request.form["user"]
    pwd  = request.form["password"]
    if (user == "root" and pwd == "1234") or (user == "g61" and pwd == "feup2026"):
        session["user"] = user
        return render_template("index.html", ulogin=user, stats=get_stats())
    return render_template("login.html", ulogin=None, resul="Utilizador ou password incorretos.")

@app.route("/gform/<cname>", methods=["post","get"])
def gform(cname):
    return apps_gform(cname)

@app.route("/analysis")
def analysis():
    return apps_analysis()

@app.route("/stats")
def stats():
    return apps_stats()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
