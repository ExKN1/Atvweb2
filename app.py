import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import pymysql

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_secreta_atividade4")


def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )


# Página inicial original do site
@app.route("/")
def home():
    return render_template("index.html")


# Página institucional original
@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


# Mantém as duas URLs para compatibilidade:
# /contato é a página do site e /cadastro atende ao endereço exigido na atividade.
@app.route("/contato", methods=["GET", "POST"], endpoint="contato")
@app.route("/cadastro", methods=["GET", "POST"], endpoint="cadastro")
def cadastro():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        assunto = request.form.get("assunto", "").strip()
        descricao = request.form.get("descricao", "").strip()

        if not email or not assunto or not descricao:
            flash("Preencha todos os campos!", "danger")
            return redirect(url_for("contato"))

        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO mensagens (email, assunto, descricao)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (email, assunto, descricao))
            conn.commit()
            flash("Mensagem enviada com sucesso!", "success")
            return redirect(url_for("listar"))
        except Exception:
            if conn:
                conn.rollback()
            app.logger.exception("Erro ao salvar mensagem no banco de dados")
            flash("Não foi possível enviar a mensagem. Tente novamente.", "danger")
        finally:
            if conn:
                conn.close()

    return render_template("contato.html")


# Painel de mensagens armazenadas no MySQL
@app.route("/listar")
def listar():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM mensagens ORDER BY id DESC")
            mensagens = cursor.fetchall()
        return render_template("listar.html", mensagens=mensagens)
    except Exception:
        app.logger.exception("Erro ao consultar mensagens no banco de dados")
        flash("Não foi possível carregar as mensagens.", "danger")
        return redirect(url_for("contato"))
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
