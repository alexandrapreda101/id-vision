from flask import Flask
import website.views as views
import website.auth as auth
from os import path
from website.models import db, DB_NAME, User
from flask_login import LoginManager

# db
def create_db(app):
    if not path.exists("app/" + DB_NAME):
        db.create_all(app=app)
        print("Created Database!")


app = Flask(__name__)
app.config["SECRET_KEY"] = "austin_powers"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
db.init_app(app)
create_db(app)

login_manager = LoginManager()
login_manager.login_view = "auth.autentificare"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# url
app.add_url_rule("/", "index", views.index)
app.add_url_rule(
    "/recunoastere", "recunoastere", views.recunoastere, methods=["GET", "POST"]
)
app.add_url_rule(
    "/autentificare", "autentificare", auth.autentificare, methods=["GET", "POST"]
)
app.add_url_rule(
    "/inregistrare", "inregistrare", auth.inregistrare, methods=["GET", "POST"]
)
app.add_url_rule("/despre", "despre", views.despre)
app.add_url_rule(
    "/pagina_mea", "pagina_mea", views.pagina_mea, methods=["GET", "POST", "DELETE"]
)
app.add_url_rule("/logout", "logout", auth.logout)
app.add_url_rule("/credentiale", "credentiale", auth.credentiale)
app.add_url_rule("/usercnp", "usercnp", auth.usercnp, methods=["GET", "POST"])
app.add_url_rule("/modificare", "modificare", views.modificare, methods=["GET", "POST"])


# run
if __name__ == "__main__":
    app.run(debug=True)
