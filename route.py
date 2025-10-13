from main import app
from models import Usuario, db
from flask import render_template, request, redirect, url_for, session, jsonify
from functools import wraps

# Decorator para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Decorator para verificar tipo de usuário específico
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login', next=request.url))
            
            user_role = session.get('user_tipo')
            if user_role not in allowed_roles:
                return "Acesso negado! Você não tem permissão para acessar esta página.", 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Se já está logado, redireciona para a página apropriada
    if 'user_id' in session:
        user_tipo = session.get('user_tipo')
        return redirect_to_correct_route(user_tipo)
    
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Buscar usuário no banco de dados
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_senha(senha):
            # Configurar sessão
            session['user_id'] = usuario.id
            session['user_email'] = usuario.email
            session['user_tipo'] = usuario.tipo
            session['logged_in'] = True
            
            # Redirecionar para a página correta baseada no tipo de usuário
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect_to_correct_route(usuario.tipo)
        
        return render_template("login.html", resultado="Informação inválidas")

    return render_template("login.html")

def redirect_to_correct_route(user_tipo):
    """Redireciona para a rota correta baseada no tipo de usuário"""
    user_tipo_lower = user_tipo.lower()
    
    if user_tipo_lower in ['dono']:
        return redirect(url_for('sistema'))
    elif user_tipo_lower in ['sistema']:
        return redirect(url_for('sistema'))
    elif user_tipo_lower in ['funcionário', 'funcionario']:
        return redirect(url_for('funcionario'))
    else:
        return redirect(url_for('homepage'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('homepage'))

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        conf_senha = request.form.get("conf-senha") 
        perfil = request.form.get("perfil")

        if senha != conf_senha:
            return render_template("cadastro.html", erro="Senhas diferentes")
        
        # Verificar se email já existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            return render_template("cadastro.html", erro="Email já cadastrado.")
        
        # Criar novo usuário
        novo_usuario = Usuario(email=email, tipo=perfil)
        novo_usuario.set_senha(senha)
        
        try:
            db.session.add(novo_usuario)
            db.session.commit()
            return render_template("cadastro.html", resultado="Cadastro concluído!")
        except Exception as e:
            db.session.rollback()
            return render_template("cadastro.html", erro="Erro ao cadastrar usuário.")

    return render_template("cadastro.html")

@app.route("/esq_senha", methods=["GET", "POST"])
def esq_senha():
    if request.method == "POST":
        email = request.form.get("email_esq")
        senha_atual = request.form.get("pass_esq_atual")
        nova_senha = request.form.get("pass_esq_nova")
        confirmar_senha = request.form.get("pass_esq_conf")

        if not email or not senha_atual or not nova_senha or not confirmar_senha:
            return jsonify({"error": "Preencha todos os campos."}), 400
        if nova_senha != confirmar_senha:
            return jsonify({"error": "Senhas não conferem."}), 400
        if len(nova_senha) < 6:
            return jsonify({"error": "Senha deve ter ao menos 6 caracteres."}), 400
        
        # Buscar usuário no banco de dados
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario:
            return jsonify({"error": "Usuário não encontrado."}), 400
        
        if not usuario.check_senha(senha_atual):
            return jsonify({"error": "Senha atual incorreta."}), 400
        
        # Atualizar senha
        try:
            usuario.set_senha(nova_senha)
            db.session.commit()
            return jsonify({"message": "Senha alterada com sucesso."})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Erro ao atualizar senha: {str(e)}"}), 500

    return render_template("esqueceu.html")

# Rotas protegidas com controle de acesso
@app.route("/funcionario")
@login_required
@role_required(['Funcionário', 'Funcionario'])
def funcionario():
    return render_template("funcionario.html")

@app.route("/dono")
@login_required
@role_required(['Sistema', 'Dono'])
def dono():
    return render_template("dono.html")

@app.route("/clientes")
@login_required
@role_required(['Funcionário', 'Funcionario', 'Sistema', 'Dono'])
def clientes():
    return render_template("clientes.html")

@app.route("/gestao")
@login_required
@role_required(['Sistema', 'Dono'])
def gestao():
    return render_template("gestao.html")

@app.route("/sistema")
@login_required
@role_required(['Sistema', 'Dono'])
def sistema():
    return render_template("sistema.html")