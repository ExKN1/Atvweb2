import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import pymysql

load_dotenv()

app = Flask(__name__)
app.secret_key = 'chave_secreta_macacos_evoluidos'

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
def home():
    return redirect(url_for('cadastro'))

@app.route('/contato')
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form.get('email')
        assunto = request.form.get('assunto')
        descricao = request.form.get('descricao')

        if not email or not assunto or not descricao:
            flash('Preencha todos os campos!', 'danger')
            return redirect(url_for('cadastro'))

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO mensagens (email, assunto, descricao) VALUES (%s, %s, %s)"
                cursor.execute(sql, (email, assunto, descricao))
            conn.commit()
            flash('Mensagem enviada com sucesso!', 'success')
            return redirect(url_for('listar'))
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao enviar: {e}', 'danger')
        finally:
            conn.close()

    return render_template('contato.html')

@app.route('/listar')
def listar():
    conn = get_db_connection()
    mensagens = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM mensagens ORDER BY id DESC")
            mensagens = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('listar.html', mensagens=mensagens)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
