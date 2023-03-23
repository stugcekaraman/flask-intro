from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flaskext.mysql import MySQL
import mysql.connector
from wtforms import Form, StringField, TextAreaField, PasswordField, EmailField,validators
from passlib.hash import sha256_crypt
import datetime

 #Kullanıcı Kayıt Formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim", validators=[
                       validators.Length(min=4, max=25)])
    email = EmailField(
        "E-mail Adresi", validators=[validators.Email(message="Geçerli bir e-mail giriniz.")])
    username = StringField("Kullanıcı Adı", validators=[
                           validators.Length(min=5, max=35)])
    password = PasswordField("Parola:", validators=[validators.DataRequired(
        message="Lütfen bir parola belirleyin."), validators.EqualTo(fieldname="confirm", message="Parolanız Uyuşmuyor")])
    confirm = PasswordField("Parola Doğrula")

#Kullanıcı Giriş Formu
class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")


app = Flask(__name__)
mysqll= MySQL()
mydb = mysql.connector.connect(host = "localhost", user="root",password="",database="ybblog",port=3306)
mysqll.init_app(app)
app.secret_key="ybblog"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="ybblog"
app.config["MYSQL_CURSORCLASS"]="DictCursor"




# def runSql(query, *args):
#     cursor = mydb.cursor()
#     data = args[0]
#     sorgu = query
#     cursor.execute(sorgu, data)
#     mydb.commit()
#     cursor.close()

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
    current_time = datetime.datetime.now()
    if request.method =="POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email= form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        
        cursor = mydb.cursor()
        sorgu = "Insert into users(name, email, username, password, created_at) VALUES(%s, %s, %s, %s, %s)"
        cursor.execute(sorgu,(name,email,username,password, current_time))
        mydb.commit()
        cursor.close()

    
        # # THIS DATA WILL BE USED FOR DB QUERY
        # data = (
        #     form.name.data,
        #     form.email.data,
        #     form.username.data,
        #     sha256_crypt.hash(form.password.data)
        # )

        # SQL FUNCTION
        
        

        # Success Message
        flash("Başarıyla Kayıt Oldunuz...","success")

        # Success Redirection
        return redirect("/login")
    else:
        # Unsuccess Redirection
        return render_template("register.html",form=form)
    
#LOGIN
@app.route("/login", methods = ["GET","POST"])
def Login():
    form = LoginForm(request.form)

    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data
        cursor = mydb.cursor(buffered=True)
        sorgu = "Select * FROM users WHERE username = %s"
        cursor.execute(sorgu, (username,))
        result = cursor.fetchone()
        if result:
            real_password = str(result[4])
            if sha256_crypt.verify(password_entered, real_password):
                flash("Başarıyla Giriş Yaptınız","success")
                return redirect(url_for("index"))
            else:
                flash("Parolanız Yanlış.","danger")
        else:
            flash("Böyle bir kullanıcı bulunmuyor.","danger")


    return render_template("login.html", form = form)



@app.route("/article/<string:id>")
def detail(id):
    return "Article Id:" + id


if __name__ == "__main__":
    app.run(debug=True)
