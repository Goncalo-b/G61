from flask import render_template, session
from analysis import get_analysis_data
from datafile import filename

def apps_analysis():
    ulogin = session.get("user")
    if ulogin is not None:
        data = get_analysis_data(filename + 'novadatabase6.db')
        return render_template("analysis.html", kpis=data['kpis'], charts=data['charts'], ulogin=ulogin)
    return render_template("index.html", ulogin=ulogin)
