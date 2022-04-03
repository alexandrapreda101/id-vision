from flask import render_template, request, flash, redirect, url_for
import os
from website.models import User, db
from website.utils import face_rec, ocr, getwidth
from flask_login import login_required, current_user
from pathlib import Path

UPLOAD_FOLDER = "static/uploads"


def base():
    return render_template("base.html")


def index():
    return render_template("index.html", user=current_user)


def despre():
    return render_template("despre.html", user=current_user)


@login_required
def pagina_mea():
    if request.method == "POST":
        if request.form["delete"] == "Stergere cont":
            db.session.delete(current_user)
            db.session.commit()
            flash("Contul a fost sters!", category="success")
            return redirect(url_for("index"))
    return render_template("pagina_mea.html", user=current_user)


def modificare():
    if request.method == "POST":
        current_user.nume = request.form.get("nume")
        current_user.prenume = request.form.get("prenume")
        current_user.cnp = request.form.get("cnp")
        current_user.serie = request.form.get("serie")
        current_user.loc_nastere = request.form.get("loc_nastere")
        current_user.domiciliu = request.form.get("domiciliu")
        current_user.emis_expirare = request.form.get("centru")
        db.session.commit()
        flash("Modificările au fost salvate!", category="success")
        return redirect(url_for("pagina_mea"))

    return render_template("modificare.html", user=current_user)


def recunoastere():
    if request.method == "POST":
        f = request.files["image"]
        filename = f.filename
        path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(path)
        width = getwidth(path)

        if face_rec(path):
            ocr(path)
            return render_template(
                "recunoastere.html",
                fileupload=True,
                img_name=filename,
                width=width,
                user=current_user,
            )
        else:
            flash("Persoana nu a fost recunoscută! Mai încercați!", category="error")
    return render_template(
        "recunoastere.html",
        fileupload=False,
        img_name="upload.png",
        width="300",
        user=current_user,
    )
