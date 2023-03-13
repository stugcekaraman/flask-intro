from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

# Kullanıcı Kayıt Formu


class RegisterForm(Form):
    name = StringField("İsim Soyisim", validators=[
                       validators.length(min=4, max=25)])
    username = StringField("Kullanıcı Adı", validators=[
                           validators.length(min=5, max=35)])
    email = StringField(
        "E-mail Adresi", validators=[validators.Email(message="Geçerli E-Mail Giriniz.")])
    password = PasswordField("Parola:", validators=[validators.DataRequired(
        message="Lütfen bir parola belirleyin."), validators.EqualTo(fieldname="confirm", message="Parolanız Uyuşmuyor")])
    confirm = PasswordField("Parola Doğrula")


app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route('/')
def index():
    # articles = [
    #     {"id": 1, "title": "Deneme1", "content": "Deneme1 İçerik"},
    #     {"id": 2, "title": "Deneme2", "content": "Deneme2 İçerik"},
    #     {"id": 3, "title": "Deneme3", "content": "Deneme3 İçerik"}
    # ]
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")

# Kayıt Olma


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/article/<string:id>")
def detail(id):
    return "Article Id:" + id


if __name__ == "__main__":
    app.run(debug=True)
