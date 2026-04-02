from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersegredo")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ---------------- BANCO ---------------- #

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(200), nullable=False)
    pontos = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()

# ---------------- ROTAS ---------------- #

@app.route("/")
def home():
    if "usuario_id" not in session:
        return redirect("/login")
    usuario = Usuario.query.get(session["usuario_id"])
    return render_template("index.html", usuario=usuario.nome)

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]

        if Usuario.query.filter_by(nome=nome).first():
            return "Usuário já existe!"

        senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")
        novo = Usuario(nome=nome, senha=senha_hash)
        db.session.add(novo)
        db.session.commit()

        return redirect("/login")

    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(nome=nome).first()

        if usuario and bcrypt.check_password_hash(usuario.senha, senha):
            session["usuario_id"] = usuario.id
            return redirect("/")
        else:
            return "Login inválido!"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "usuario_id" not in session:
        return redirect("/login")

    pergunta = "Qual império africano ficou conhecido pelo ouro?"
    alternativas = [
        "Reino do Mali",
        "Reino Zulu",
        "Império Romano",
        "Reino do Congo"
    ]
    correta = "Reino do Mali"

    if request.method == "POST":
        resposta = request.form["resposta"]
        usuario = Usuario.query.get(session["usuario_id"])

        if resposta == correta:
            usuario.pontos += 10
        else:
            usuario.pontos -= 5

        db.session.commit()
        return redirect("/resultado")

    return render_template("quiz.html", pergunta=pergunta, alternativas=alternativas)

@app.route("/resultado")
def resultado():
    if "usuario_id" not in session:
        return redirect("/login")

    usuario = Usuario.query.get(session["usuario_id"])
    return render_template("resultado.html", pontos=usuario.pontos)

@app.route("/ranking")
def ranking():
    usuarios = Usuario.query.order_by(Usuario.pontos.desc()).all()
    return render_template("ranking.html", usuarios=usuarios)

if __name__ == "__main__":
    if __name__ == "__main__":
    app.run()
