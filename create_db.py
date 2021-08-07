# from project import create_app
# from project.models import db
# app = create_app('develop')
# with app.app_context():
#     db.drop_all()
#     db.create_all()
from project.script import redis_connect
conn=redis_connect.connect()
conn.set('key',123)
print(conn.get('key'))