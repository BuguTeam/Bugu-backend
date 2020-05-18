# app/auth/__init__.py

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
from .views import gen_openid
from .views import gen_3rd_session