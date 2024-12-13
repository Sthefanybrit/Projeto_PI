from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'projeto'  # Chave secreta para sessões e mensagens flash

# Configuração do banco de dados
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'db_gerenciador'
}

# Função para conectar ao banco de dados
def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password != confirm_password:
            flash('As senhas não coincidem. Tente novamente.')
            return redirect(url_for('cadastro'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO tb_usuarios (usu_nome, usu_email, usu_senha) VALUES (%s, %s, %s)",
                (nome, email, hashed_password)
            )
            conn.commit()
            flash('Cadastro realizado com sucesso! Faça login para acessar.')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Email já cadastrado. Use um email diferente.')
            return redirect(url_for('cadastro'))
        finally:
            cursor.close()
            conn.close()

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tb_usuarios WHERE usu_email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            if check_password_hash(user['usu_senha'], password):
                session['user_id'] = user['usu_id']
                return redirect(url_for('usuario'))  # Redireciona para a nova página inicial
            else:
                flash('Senha incorreta. Tente novamente.')
        else:
            flash('Usuário não encontrado. Cadastre-se primeiro.')

    return render_template('login.html')

@app.route('/usuario')
def usuario():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.')
        return redirect(url_for('login'))
    return render_template('usuario.html')  # Renderiza a nova página do usuário


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logout realizado com sucesso.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
