import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import pymysql

load_dotenv()

app = Flask(__name__)
app.secret_key = 'chave_secreta_atividade4'

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    return redirect(url_for('listar'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        categoria = request.form.get('categoria')
        preco = request.form.get('preco')

        if not nome or not categoria or not preco:
            flash('Preencha todos os campos!', 'danger')
            return redirect(url_for('cadastro'))

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO produtos (nome, categoria, preco) VALUES (%s, %s, %s)"
                cursor.execute(sql, (nome, categoria, preco))
            conn.commit()
            flash('Registro salvo com sucesso!', 'success')
            return redirect(url_for('listar'))
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao inserir: {e}', 'danger')
        finally:
            conn.close()

    return render_template('cadastro.html')

@app.route('/listar')
def listar():
    conn = get_db_connection()
    produtos = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM produtos ORDER BY id DESC")
            produtos = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('listar.html', produtos=produtos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
