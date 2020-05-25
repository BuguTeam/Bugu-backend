# app/user/__init__.py
# coding=utf-8

from flask import Blueprint

user = Blueprint('user', __name__) # 设置模板目录，为默认

from . import views