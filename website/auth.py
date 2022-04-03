from flask import flash, redirect, url_for, request, render_template
from website.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from website.utils import face_rec
from pathlib import Path

UPLOAD_FOLDER = "static/uploads"


def autentificare():
    if request.method == "POST":
        if request.form["submit_button"] == "Submit":
            nume_utilizator = request.form.get("numeutilizator").upper()
            parola = request.form.get("parola")
            user = User.query.filter_by(nume_utilizator=nume_utilizator).first()
            if user:
                if check_password_hash(user.parola, parola):
                    flash("Autentificare reușită!", category="success")
                    login_user(user, remember=True)
                    return redirect(url_for("pagina_mea"))
                else:
                    flash("Parola incorectă, mai încearcă", category="error")
            else:
                flash("Numele de utilizator nu există", category="error")
        if request.form["submit_button"] == "Ati uitat parola?":
            files = Path(UPLOAD_FOLDER).glob("*")
            for file in files:
                if face_rec(file):
                    return redirect(url_for("usercnp"))
                else:
                    flash(
                        "Persoana nu a fost recunoscută! Mai încercați!",
                        category="error",
                    )
    return render_template("autentificare.html", user=current_user)


def inregistrare():
    if request.method == "POST":
        nume = request.form.get("nume")
        prenume = request.form.get("prenume")
        cnp = request.form.get("cnp")

        user = User.query.filter_by(cnp=cnp).first()
        if user:
            flash("Contul există deja!", category="error")
        elif len(nume) < 3:
            flash("Numele nu este valid!", category="error")
        elif len(prenume) < 3:
            flash("Prenumele nu este valid!", category="error")
        elif len(cnp) != 13:
            flash("CNP-ul trebuie să aibă 13 caractere!", category="error")
        else:
            return redirect(url_for("recunoastere"))

    return render_template("inregistrare.html", user=current_user)


def usercnp():
    if request.method == "POST":
        cnp = request.form.get("cnp")
        user = User.query.filter_by(cnp=cnp).first()
        if user:
            login_user(user, remember=True)
            return redirect(url_for("credentiale"))
    return render_template("usercnp.html", user=current_user)


def credentiale():
    return render_template("credentiale.html", user=current_user)


@login_required
def logout():
    logout_user()
    return redirect(url_for("autentificare"))
