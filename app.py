from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
import sqlite3
import os
import secrets
import hmac
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-local-apenas-para-testes-nao-usar-em-producao")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
ESTADOS_ENCOMENDA = ["Recebida", "Em preparação", "Enviada", "Entregue", "Cancelada"]
DB = Path(__file__).with_name("loja.db")

PRODUTOS_INICIAIS = [
    ("Sapatilha Urban", "Unissexo", 2500, "https://images.unsplash.com/photo-154 shoe-1"),
    ("Sapato Clássico", "Masculino", 3800, "https://images.unsplash.com/photo-1614252369475-531eba835eb1"),
    ("Sandália Elegance", "Feminino", 1800, "https://images.unsplash.com/photo-1562273138-f46be4ebdf33"),
    ("Ténis Sport", "Desportivo", 4200, "https://images.unsplash.com/photo-1542291026-7eec264c27ff"),
    ("Bota Casual", "Unissexo", 5000, "https://images.unsplash.com/photo- boots"),
    ("Sapato Infantil", "Infantil", 1600, "https://images.unsplash.com/photo-1514989940723-e8e51635b782"),
]

def conectar():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def iniciar_bd():
    with conectar() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL, categoria TEXT NOT NULL,
                preco INTEGER NOT NULL, imagem TEXT NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS encomendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL, telefone TEXT NOT NULL,
                endereco TEXT NOT NULL, total INTEGER NOT NULL,
                itens TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Recebida',
                criada_em TEXT NOT NULL DEFAULT ''
            )
        """)
        # Atualiza também bases de dados antigas, sem apagar encomendas existentes.
        colunas = {linha[1] for linha in con.execute("PRAGMA table_info(encomendas)").fetchall()}
        if "estado" not in colunas:
            con.execute("ALTER TABLE encomendas ADD COLUMN estado TEXT NOT NULL DEFAULT 'Recebida'")
        if "criada_em" not in colunas:
            con.execute("ALTER TABLE encomendas ADD COLUMN criada_em TEXT NOT NULL DEFAULT ''")
        if con.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
            # Imagens ilustrativas; pode trocar os links pelas fotografias dos seus produtos.
            imagens = [
                "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=700",
                "https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=700",
                "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=700",
                "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=700",
                "https://images.unsplash.com/photo- boots?w=700",
                "https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=700",
            ]
            produtos = [
                ("Ténis Urban", "Unissexo", 2500, imagens[0]),
                ("Sapato Clássico", "Masculino", 3800, imagens[1]),
                ("Sandália Elegance", "Feminino", 1800, imagens[2]),
                ("Ténis Sport", "Desportivo", 4200, imagens[3]),
                ("Bota Casual", "Unissexo", 5000, imagens[4]),
                ("Sapato Infantil", "Infantil", 1600, imagens[5]),
            ]
            con.executemany(
                "INSERT INTO produtos (nome,categoria,preco,imagem) VALUES (?,?,?,?)",
                produtos
            )

def obter_carrinho():
    carrinho = session.get("carrinho", {})
    itens = []
    total = 0
    with conectar() as con:
        for produto_id, quantidade in carrinho.items():
            produto = con.execute(
                "SELECT * FROM produtos WHERE id = ?", (produto_id,)
            ).fetchone()
            if produto:
                subtotal = produto["preco"] * quantidade
                itens.append({"produto": produto, "quantidade": quantidade, "subtotal": subtotal})
                total += subtotal
    return itens, total

@app.route("/")
def inicio():
    categoria = request.args.get("categoria", "")
    with conectar() as con:
        if categoria:
            produtos = con.execute(
                "SELECT * FROM produtos WHERE categoria = ? ORDER BY id DESC", (categoria,)
            ).fetchall()
        else:
            produtos = con.execute("SELECT * FROM produtos ORDER BY id DESC").fetchall()
    return render_template("inicio.html", produtos=produtos, categoria=categoria)

@app.post("/adicionar/<int:produto_id>")
def adicionar(produto_id):
    carrinho = session.get("carrinho", {})
    chave = str(produto_id)
    carrinho[chave] = carrinho.get(chave, 0) + 1
    session["carrinho"] = carrinho
    flash("Produto adicionado ao carrinho!")
    return redirect(request.referrer or url_for("inicio"))

@app.route("/carrinho")
def ver_carrinho():
    itens, total = obter_carrinho()
    return render_template("carrinho.html", itens=itens, total=total)

@app.post("/remover/<int:produto_id>")
def remover(produto_id):
    carrinho = session.get("carrinho", {})
    carrinho.pop(str(produto_id), None)
    session["carrinho"] = carrinho
    return redirect(url_for("ver_carrinho"))

@app.route("/finalizar", methods=["GET", "POST"])
def finalizar():
    itens, total = obter_carrinho()
    if not itens:
        flash("O carrinho está vazio.")
        return redirect(url_for("inicio"))

    if request.method == "POST":
        cliente = request.form.get("cliente", "").strip()
        telefone = request.form.get("telefone", "").strip()
        endereco = request.form.get("endereco", "").strip()
        if not cliente or not telefone or not endereco:
            flash("Preencha todos os campos.")
            return render_template("finalizar.html", itens=itens, total=total)

        resumo = "; ".join(
            f'{i["produto"]["nome"]} x{i["quantidade"]}' for i in itens
        )
        with conectar() as con:
            con.execute(
                "INSERT INTO encomendas (cliente,telefone,endereco,total,itens,estado,criada_em) VALUES (?,?,?,?,?,?,?)",
                (cliente, telefone, endereco, total, resumo, "Recebida", datetime.now().strftime("%d/%m/%Y %H:%M"))
            )
        session["carrinho"] = {}
        return render_template("sucesso.html", cliente=cliente, total=total)

    return render_template("finalizar.html", itens=itens, total=total)



def administrador_autenticado():
    return session.get("administrador") is True


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


@app.context_processor
def disponibilizar_csrf():
    return {"csrf_token": csrf_token}


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not ADMIN_PASSWORD:
        return ("A área de administração ainda não foi configurada. No Render, adicione a variável ADMIN_PASSWORD e faça novo deploy.", 503)
    if administrador_autenticado():
        return redirect(url_for("admin_encomendas"))
    if request.method == "POST":
        token = request.form.get("csrf_token", "")
        if not hmac.compare_digest(token, session.get("csrf_token", "")):
            abort(400)
        password = request.form.get("password", "")
        if hmac.compare_digest(password, ADMIN_PASSWORD):
            session.clear()
            session["administrador"] = True
            flash("Sessão iniciada com sucesso.")
            return redirect(url_for("admin_encomendas"))
        flash("Palavra-passe incorreta.")
    return render_template("admin_login.html")


@app.route("/admin/encomendas")
def admin_encomendas():
    if not administrador_autenticado():
        return redirect(url_for("admin"))
    with conectar() as con:
        encomendas = con.execute("SELECT * FROM encomendas ORDER BY id DESC").fetchall()
    return render_template("admin_encomendas.html", encomendas=encomendas, estados=ESTADOS_ENCOMENDA)


@app.post("/admin/encomenda/<int:encomenda_id>/estado")
def admin_atualizar_estado(encomenda_id):
    if not administrador_autenticado():
        return redirect(url_for("admin"))
    token = request.form.get("csrf_token", "")
    if not hmac.compare_digest(token, session.get("csrf_token", "")):
        abort(400)
    estado = request.form.get("estado", "")
    if estado not in ESTADOS_ENCOMENDA:
        abort(400)
    with conectar() as con:
        con.execute("UPDATE encomendas SET estado = ? WHERE id = ?", (estado, encomenda_id))
    flash(f"Estado da encomenda #{encomenda_id} atualizado.")
    return redirect(url_for("admin_encomendas"))


@app.post("/admin/sair")
def admin_sair():
    if not administrador_autenticado():
        return redirect(url_for("admin"))
    token = request.form.get("csrf_token", "")
    if not hmac.compare_digest(token, session.get("csrf_token", "")):
        abort(400)
    session.clear()
    flash("Terminaste a sessão de administração.")
    return redirect(url_for("admin"))

# Inicializa a base de dados tanto no uso local como no servidor web.
iniciar_bd()

if __name__ == "__main__":
    app.run(debug=True)
