from leila_framework.main import Framework
from urls import fronts
from wsgiref.simple_server import make_server
from views import routes

application = Framework(routes, fronts)
port = 8000

with make_server('', port, application) as httpd:
    print("Запуск на порту 8000...")
    print("http://127.0.0.1:8000/")
    httpd.serve_forever()
