from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flaskext.mysql import MySQL
import mysql.connector
from wtforms import Form, StringField, TextAreaField, PasswordField, EmailField,validators
from passlib.hash import sha256_crypt
from functools import wraps



#Kullanıcı Giriş Decorator'ı
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın.","danger")
            return redirect("/login")
    return decorated_function


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
app.secret_key="ybblog" #flash mesajları için
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="ybblog"
app.config["MYSQL_CURSORCLASS"]="DictCursor"



@app.route('/')
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mydb.cursor()
    sorgu = "Select * From articles where author = %s"
    cursor.execute(sorgu, (session["username"],))
    articles = cursor.fetchall()
    if articles:
        return render_template("dashboard.html", articles=articles)
        
    else:
        return render_template("dashboard.html")


# Kayıt Olma
@app.route("/register", methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    
    if request.method =="POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email= form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        
        cursor = mydb.cursor()
        sorgu = "Insert into users(name, email, username, password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mydb.commit()
        cursor.close()

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
        cursor = mydb.cursor()
        sorgu = "Select * From users where username = %s"
        cursor.execute(sorgu,(username,))

        result = cursor.fetchone()
        if result:
            real_password = str(result[4])
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla Giriş Yaptınız","success")

                session["logged_in"] = True
                session["username"] = username

                return redirect(url_for("index"))
            else:
                flash("Parolanız Yanlış.","danger")
                

        else:
            flash("Böyle bir kullanıcı bulunmuyor.","danger")
            
    return render_template("login.html", form = form)
#Detay Sayfası
@app.route("/article/<string:id>")
def article(id):
    cursor = mydb.cursor()
    sorgu = "Select * From articles where id = %s"
    cursor.execute(sorgu,(id,))
    article = cursor.fetchone()
    if article:
        return render_template("article.html", article=article)
    else:
        return render_template("article.html")


#LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))



#Makale Ekleme
@app.route("/addarticle", methods=["GET","POST"])
def addarticle():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data


        cursor = mydb.cursor()
        sorgu = "Insert into articles(title,author,content) VALUES(%s,%s,%s)"
        cursor.execute(sorgu,(title,session["username"],content))
        mydb.commit()
        cursor.close()

        flash("Makale Başarıyla Eklendi","success")
        return redirect(url_for("dashboard"))
    return render_template("addarticle.html",form=form)


# Makale Silme
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mydb.cursor()
    sorgu = "Select * from articles where author = %s and  id = %s"
    cursor.execute(sorgu,(session["username"],id))
    result = cursor.fetchall()
    if result:
        sorgu2 = "Delete from articles where id = %s"
        cursor.execute(sorgu2,(id,))
        mydb.commit()
        flash("Makale silindi.","success")
        return redirect(url_for("dashboard"))

    else:
        flash("Böyle bir makale yok veya bu işleme yetkiniz yok.", "danger")
        return redirect(url_for("index"))

#Makale Güncelleme
@app.route("/edit/<string:id>", methods = ["GET","POST"])
@login_required
def update(id):
    if request.method == "GET":
        cursor = mydb.cursor()
        sorgu = "Select * from articles where id = %s and author = %s"
        cursor.execute(sorgu,(id,session["username"]))
        article = cursor.fetchall()
        
        if article:
            form = ArticleForm()
            form.title.data = article[0][1]
            form.content.data = article[0][3]
            return render_template("update.html",form = form)
            
        else:
            flash("Böyle bir makale yok veya bu işleme yetkiniz yok.","danger")
            return redirect(url_for("index"))
    else:
        #POST REQUEST
        form = ArticleForm(request.form)
        newTitle = form.title.data
        newContent = form.content.data
        sorgu2 = "Update articles Set title = %s, content = %s where id =%s"
        cursor = mydb.cursor()
        cursor.execute(sorgu2, (newTitle,newContent,id))
        mydb.commit()
        flash("Makale başarıyla güncellendi.","success")
        return redirect(url_for("dashboard"))
    


#Makale Form
class ArticleForm(Form):
    
    title = StringField("Makale Başlığı",validators=[validators.length(min=5,max=100)])
    content = TextAreaField("Makale İçeriği",validators=[validators.length(min=10)])

#SEARCH
@app.route("/search",methods=["GET","POST"])
def search():
    if request.method=="GET":
        return redirect(url_for("index"))
    else:
        keyword = request.form.get("keyword")
        cursor = mydb.cursor()
        sorgu = "Select * from articles where title like '%{}%' or content like'%{}%'".format(keyword,keyword) 
        cursor.execute(sorgu)
        articles = cursor.fetchall()
        if articles:
            return render_template("articles.html", articles = articles)
        
        else:
            flash("Aranan kelimeye uygun makale bulunamadı","danger")
            return redirect(url_for("articles"))

#Makale Sayfası
@app.route("/articles")
def articles():
    cursor = mydb.cursor()
    sorgu = "Select * From articles"
    cursor.execute(sorgu)
    articles=cursor.fetchall()
    if articles:
        
        return render_template("articles.html", articles = articles)
    else:
        
        return render_template("articles.html")
    
if __name__ == "__main__":
    app.run(debug=True)
