# INF601 - Advanced Programming in Python
# Gage Giffin
# Mini Project 5

from flask import Blueprint, render_template

bp = Blueprint('main', __name__)


@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/about')
def about():
    return render_template('about.html')
