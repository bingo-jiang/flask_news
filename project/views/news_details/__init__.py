from flask import Blueprint

details=Blueprint("detail",__name__,url_prefix="/news")

from . import views