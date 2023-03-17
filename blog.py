from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flaskext.mysql import MySQL
import mysql.connector
from wtforms import Form, StringField, TextAreaField, PasswordField, EmailField,validators
from passlib.hash import sha256_crypt
# from mysqlx import connection

# Kullanıcı Kayıt Formu


class RegisterForm(Form):
    name = StringField("İsim Soyisim", validators=[
                       validators.Length(min=4, max=25)])
    username = StringField("Kullanıcı Adı", validators=[
                           validators.Length(min=5, max=35)])
    email = EmailField(
        "E-mail Adresi", validators=[validators.Email(message="Geçerli bir e-mail giriniz.")])
    password = PasswordField("Parola:", validators=[validators.DataRequired(
        message="Lütfen bir parola belirleyin."), validators.EqualTo(fieldname="confirm", message="Parolanız Uyuşmuyor")])
    confirm = PasswordField("Parola Doğrula")





app = Flask(__name__)
mydb = mysql.connector.connect(host = "localhost", user="root",password="",database="ybblog",port=3306)

app.secret_key="ybblog"
# app.config["MYSQL_HOST"] = "localhost"
# app.config["MYSQL_USER"] = "root"
# app.config["MYSQL_PASSWORD"] = ""
# app.config["MYSQL_DB"] = "ybblog"
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"
# mysqld = MySQL(app)
# mydb = mysql.connector.connect()


# mysql.init_app(app)



def runSql(query, *args):
    cursor = mydb.cursor()
    data = args[0]
    sorgu = query
    cursor.execute(sorgu, data)
    mydb.commit()
    cursor.close()


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")

# Kayıt Olma

@app.route("/register", methods = ["GET","POST"])
def register():

    form = RegisterForm(request.form)
    
    if request.method =="POST" and form.validate():

        # THIS DATA WILL BE USED FOR DB QUERY
        data = (
            form.name.data,
            form.username.data,
            form.email.data,
            sha256_crypt.hash(form.password.data)
        )

        # SQL FUNCTION
        runSql("Insert into user_table(name, email, username, password) VALUES(%s,%s,%s,%s)", data)

        # Success Message
        flash("Başarıyla Kayıt Oldunuz...","success")

        # Success Redirection
        return redirect(url_for("index"))
    else:
        
        # Unsuccess Redirection
        return render_template("register.html",form=form)


@app.route("/article/<string:id>")
def detail(id):
    return "Article Id:" + id


if __name__ == "__main__":
    app.run(debug=True)
