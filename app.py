from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy

# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user



app = Flask(__name__)

import config

db = SQLAlchemy(app)

import models

import routes


