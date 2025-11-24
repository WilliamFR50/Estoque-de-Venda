from main import app
from models import Usuario, Cliente, Produto, Despesa, Venda, db
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from sqlalchemy import func, extract

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
@role_required(['Sistema', 'Dono'])
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

@app.route("/novo_pedido")
@login_required
@role_required(['Sistema', 'Dono'])
def novo_pedido():
    return render_template("novo_pedido.html")

@app.route("/vendas")
@login_required
@role_required(['Sistema', 'Dono'])
def vendas():
    return render_template("vendas.html")

# API para obter clientes
@app.route("/api/clientes", methods=["GET"])
@login_required
def api_get_clientes():
    try:
        # Obter parâmetros de filtro
        status_filter = request.args.get('status', 'all')
        search_term = request.args.get('search', '').lower()
        
        # Query base
        query = Cliente.query
        
        # Aplicar filtros
        if status_filter != 'all':
            query = query.filter(Cliente.status == status_filter)
        
        if search_term:
            query = query.filter(
                db.or_(
                    Cliente.nome.ilike(f'%{search_term}%'),
                    Cliente.email.ilike(f'%{search_term}%'),
                    Cliente.telefone.ilike(f'%{search_term}%'),
                    Cliente.cpf.ilike(f'%{search_term}%')
                )
            )
        
        # Ordenar por nome
        clientes = query.order_by(Cliente.nome).all()
        
        # Converter para dicionário
        clientes_data = [cliente.to_dict() for cliente in clientes]
        
        # Calcular estatísticas
        total_clientes = Cliente.query.count()
        clientes_ativos = Cliente.query.filter_by(status='active').count()
        clientes_inativos = total_clientes - clientes_ativos
        
        return jsonify({
            'clientes': clientes_data,
            'estatisticas': {
                'total': total_clientes,
                'ativos': clientes_ativos,
                'inativos': clientes_inativos
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API para adicionar cliente
@app.route("/api/clientes", methods=["POST"])
@login_required
def api_add_cliente():
    try:
        data = request.get_json()
        
        # Validar dados
        if not all(key in data for key in ['nome', 'email', 'telefone', 'cpf']):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Verificar se CPF já existe
        cliente_existente = Cliente.query.filter_by(cpf=data['cpf']).first()
        if cliente_existente:
            return jsonify({'error': 'CPF já cadastrado'}), 400
        
        # Gerar ID do cliente
        ultimo_cliente = Cliente.query.order_by(Cliente.id.desc()).first()
        if ultimo_cliente:
            ultimo_numero = int(ultimo_cliente.cliente_id[2:])
            novo_id = f"CL{ultimo_numero + 1:03d}"
        else:
            novo_id = "CL001"
        
        # Criar novo cliente
        novo_cliente = Cliente(
            cliente_id=novo_id,
            nome=data['nome'],
            email=data['email'],
            telefone=data['telefone'],
            cpf=data['cpf'],
            status=data.get('status', 'active')
        )
        
        db.session.add(novo_cliente)
        db.session.commit()
        
        return jsonify({'message': 'Cliente adicionado com sucesso', 'cliente': novo_cliente.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API para atualizar cliente
@app.route("/api/clientes/<int:cliente_id>", methods=["PUT"])
@login_required
def api_update_cliente(cliente_id):
    try:
        data = request.get_json()
        cliente = Cliente.query.get_or_404(cliente_id)
        
        # Atualizar campos
        if 'nome' in data:
            cliente.nome = data['nome']
        if 'email' in data:
            cliente.email = data['email']
        if 'telefone' in data:
            cliente.telefone = data['telefone']
        if 'cpf' in data:
            # Verificar se o novo CPF já existe em outro cliente
            cliente_existente = Cliente.query.filter(Cliente.cpf == data['cpf'], Cliente.id != cliente_id).first()
            if cliente_existente:
                return jsonify({'error': 'CPF já cadastrado'}), 400
            cliente.cpf = data['cpf']
        if 'status' in data:
            cliente.status = data['status']
        
        db.session.commit()
        
        return jsonify({'message': 'Cliente atualizado com sucesso', 'cliente': cliente.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API para excluir cliente
@app.route("/api/clientes/<int:cliente_id>", methods=["DELETE"])
@login_required
def api_delete_cliente(cliente_id):
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        
        db.session.delete(cliente)
        db.session.commit()
        
        return jsonify({'message': 'Cliente excluído com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API para obter produtos
# Atualize a rota /api/produtos para aceitar o parâmetro limit
@app.route("/api/produtos", methods=["GET"])
@login_required
def api_get_produtos():
    try:
        # Obter parâmetros de filtro
        categoria_filter = request.args.get('categoria', 'all')
        disponibilidade_filter = request.args.get('disponibilidade', 'all')
        search_term = request.args.get('search', '').lower()
        sort_by = request.args.get('sort', 'name')
        limit = request.args.get('limit', type=int)
        
        # Query base
        query = Produto.query
        
        # Aplicar filtros
        if categoria_filter != 'all':
            query = query.filter(Produto.categoria == categoria_filter)
        
        if disponibilidade_filter != 'all':
            disponivel = disponibilidade_filter == 'available'
            query = query.filter(Produto.disponivel == disponivel)
        
        if search_term:
            query = query.filter(
                db.or_(
                    Produto.nome.ilike(f'%{search_term}%'),
                    Produto.categoria.ilike(f'%{search_term}%'),
                    Produto.descricao.ilike(f'%{search_term}%')
                )
            )
        
        # Aplicar ordenação
        if sort_by == 'name':
            query = query.order_by(Produto.nome)
        elif sort_by == 'category':
            query = query.order_by(Produto.categoria)
        elif sort_by == 'price-asc':
            query = query.order_by(Produto.preco)
        elif sort_by == 'price-desc':
            query = query.order_by(Produto.preco.desc())
        elif sort_by == 'recent':
            query = query.order_by(Produto.data_cadastro.desc())
        
        # Aplicar limite se especificado
        if limit:
            query = query.limit(limit)
        
        produtos = query.all()
        
        # Converter para dicionário
        produtos_data = [produto.to_dict() for produto in produtos]
        
        # Obter categorias únicas
        categorias = db.session.query(Produto.categoria).distinct().all()
        categorias_lista = [cat[0] for cat in categorias]
        
        # Calcular estatísticas (apenas se não houver limite)
        if not limit:
            total_produtos = Produto.query.count()
            produtos_disponiveis = Produto.query.filter_by(disponivel=True).count()
            produtos_indisponiveis = total_produtos - produtos_disponiveis
            total_categorias = len(categorias_lista)
            
            estatisticas = {
                'total': total_produtos,
                'disponiveis': produtos_disponiveis,
                'indisponiveis': produtos_indisponiveis,
                'categorias': total_categorias
            }
        else:
            estatisticas = {}
        
        return jsonify({
            'produtos': produtos_data,
            'categorias': categorias_lista,
            'estatisticas': estatisticas
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# API para adicionar produto
@app.route("/api/produtos", methods=["POST"])
@login_required
def api_add_produto():
    try:
        data = request.get_json()
        
        # Validar dados
        required_fields = ['nome', 'preco', 'categoria', 'quantidade_estoque']
        if not all(key in data for key in required_fields):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Gerar ID do produto
        ultimo_produto = Produto.query.order_by(Produto.id.desc()).first()
        if ultimo_produto:
            ultimo_numero = int(ultimo_produto.produto_id[2:])
            novo_id = f"PR{ultimo_numero + 1:03d}"
        else:
            novo_id = "PR001"
        
        # Criar novo produto
        novo_produto = Produto(
            produto_id=novo_id,
            nome=data['nome'],
            descricao=data.get('descricao', ''),
            preco=float(data['preco']),
            categoria=data['categoria'],
            quantidade_estoque=int(data['quantidade_estoque']),
            disponivel=data.get('disponivel', True),
            imagem_url=data.get('imagem_url', '')
        )
        
        db.session.add(novo_produto)
        db.session.commit()
        
        return jsonify({'message': 'Produto adicionado com sucesso', 'produto': novo_produto.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API para atualizar produto
@app.route("/api/produtos/<int:produto_id>", methods=["PUT"])
@login_required
def api_update_produto(produto_id):
    try:
        data = request.get_json()
        produto = Produto.query.get_or_404(produto_id)
        
        # Atualizar campos
        if 'nome' in data:
            produto.nome = data['nome']
        if 'descricao' in data:
            produto.descricao = data['descricao']
        if 'preco' in data:
            produto.preco = float(data['preco'])
        if 'categoria' in data:
            produto.categoria = data['categoria']
        if 'quantidade_estoque' in data:
            produto.quantidade_estoque = int(data['quantidade_estoque'])
        if 'disponivel' in data:
            produto.disponivel = bool(data['disponivel'])
        if 'imagem_url' in data:
            produto.imagem_url = data['imagem_url']
        
        db.session.commit()
        
        return jsonify({'message': 'Produto atualizado com sucesso', 'produto': produto.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API para excluir produto
@app.route("/api/produtos/<int:produto_id>", methods=["DELETE"])
@login_required
def api_delete_produto(produto_id):
    try:
        produto = Produto.query.get_or_404(produto_id)
        
        db.session.delete(produto)
        db.session.commit()
        
        return jsonify({'message': 'Produto excluído com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500  
    
# API para obter métricas da gestão
@app.route("/api/gestao/metricas")
@login_required
def api_get_metricas():
    try:
        # Calcular período dos últimos 30 dias
        data_limite = datetime.utcnow() - timedelta(days=30)
        data_mes_anterior = datetime.utcnow() - timedelta(days=60)
        
        # Receita Total (últimos 30 dias)
        receita_total = db.session.query(func.sum(Venda.valor_total)).filter(
            Venda.data_venda >= data_limite
        ).scalar() or 0
        
        # Receita do mês anterior (para comparação)
        receita_mes_anterior = db.session.query(func.sum(Venda.valor_total)).filter(
            Venda.data_venda >= data_mes_anterior,
            Venda.data_venda < data_limite
        ).scalar() or 0
        
        # Calcular variação percentual
        if receita_mes_anterior > 0:
            variacao_receita = ((receita_total - receita_mes_anterior) / receita_mes_anterior) * 100
        else:
            variacao_receita = 100 if receita_total > 0 else 0
        
        # Total de Vendas (últimos 30 dias)
        total_vendas = Venda.query.filter(
            Venda.data_venda >= data_limite
        ).count()
        
        # Total de Vendas do mês anterior
        vendas_mes_anterior = Venda.query.filter(
            Venda.data_venda >= data_mes_anterior,
            Venda.data_venda < data_limite
        ).count()
        
        # Variação de vendas
        if vendas_mes_anterior > 0:
            variacao_vendas = ((total_vendas - vendas_mes_anterior) / vendas_mes_anterior) * 100
        else:
            variacao_vendas = 100 if total_vendas > 0 else 0
        
        # Despesas Totais (últimos 30 dias)
        despesas_total = db.session.query(func.sum(Despesa.valor)).filter(
            Despesa.data_despesa >= data_limite
        ).scalar() or 0
        
        # Despesas do mês anterior
        despesas_mes_anterior = db.session.query(func.sum(Despesa.valor)).filter(
            Despesa.data_despesa >= data_mes_anterior,
            Despesa.data_despesa < data_limite
        ).scalar() or 0
        
        # Variação de despesas
        if despesas_mes_anterior > 0:
            variacao_despesas = ((despesas_total - despesas_mes_anterior) / despesas_mes_anterior) * 100
        else:
            variacao_despesas = 100 if despesas_total > 0 else 0
        
        # Lucro Líquido
        lucro_liquido = receita_total - despesas_total
        lucro_mes_anterior = (receita_mes_anterior or 0) - (despesas_mes_anterior or 0)
        
        if lucro_mes_anterior > 0:
            variacao_lucro = ((lucro_liquido - lucro_mes_anterior) / lucro_mes_anterior) * 100
        else:
            variacao_lucro = 100 if lucro_liquido > 0 else 0
        
        return jsonify({
            'receita_total': round(receita_total, 2),
            'variacao_receita': round(variacao_receita, 1),
            'lucro_liquido': round(lucro_liquido, 2),
            'variacao_lucro': round(variacao_lucro, 1),
            'total_vendas': total_vendas,
            'variacao_vendas': round(variacao_vendas, 1),
            'despesas_total': round(despesas_total, 2),
            'variacao_despesas': round(variacao_despesas, 1)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API para obter dados dos gráficos
@app.route("/api/gestao/graficos")
@login_required
def api_get_graficos():
    try:
        # Dados para gráfico de Receita vs Despesas (últimos 6 meses)
        meses = []
        receitas = []
        despesas = []
        
        for i in range(5, -1, -1):
            data_inicio = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
            data_fim = data_inicio + timedelta(days=30)
            
            # Receita do mês
            receita = db.session.query(func.sum(Venda.valor_total)).filter(
                Venda.data_venda >= data_inicio,
                Venda.data_venda < data_fim
            ).scalar() or 0
            
            # Despesas do mês
            despesa = db.session.query(func.sum(Despesa.valor)).filter(
                Despesa.data_despesa >= data_inicio,
                Despesa.data_despesa < data_fim
            ).scalar() or 0
            
            meses.append(data_inicio.strftime('%B'))
            receitas.append(float(receita))
            despesas.append(float(despesa))
        
        # Dados para gráfico de Vendas por Categoria
        vendas_por_categoria = db.session.query(
            Produto.categoria,
            func.sum(Venda.quantidade).label('total_vendas')
        ).join(Venda, Produto.id == Venda.produto_id).group_by(Produto.categoria).all()
        
        categorias = [v[0] for v in vendas_por_categoria]
        vendas_categoria = [int(v[1]) for v in vendas_por_categoria]
        
        return jsonify({
            'receita_despesas': {
                'meses': meses,
                'receitas': receitas,
                'despesas': despesas
            },
            'vendas_categoria': {
                'categorias': categorias,
                'vendas': vendas_categoria
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API para obter últimas vendas
@app.route("/api/gestao/ultimas-vendas")
@login_required
def api_get_ultimas_vendas():
    try:
        vendas = Venda.query.join(Cliente).join(Produto).order_by(
            Venda.data_venda.desc()
        ).limit(10).all()
        
        vendas_data = [venda.to_dict() for venda in vendas]
        
        return jsonify({'vendas': vendas_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API para obter despesas recentes
@app.route("/api/gestao/despesas-recentes")
@login_required
def api_get_despesas_recentes():
    try:
        despesas = Despesa.query.order_by(
            Despesa.data_despesa.desc()
        ).limit(10).all()
        
        despesas_data = [despesa.to_dict() for despesa in despesas]
        
        return jsonify({'despesas': despesas_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API para adicionar nova venda
@app.route("/api/vendas", methods=["POST"])
@login_required
def api_add_venda():
    try:
        data = request.get_json()
        
        # Validar dados
        required_fields = ['cliente_id', 'produto_id', 'quantidade', 'forma_pagamento']
        if not all(key in data for key in required_fields):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Buscar produto para obter preço
        produto = Produto.query.get(data['produto_id'])
        if not produto:
            return jsonify({'error': 'Produto não encontrado'}), 404
        
        # Verificar estoque
        if produto.quantidade_estoque < data['quantidade']:
            return jsonify({'error': 'Estoque insuficiente'}), 400
        
        # Gerar ID da venda
        ultima_venda = Venda.query.order_by(Venda.id.desc()).first()
        if ultima_venda:
            ultimo_numero = int(ultima_venda.venda_id[2:])
            novo_id = f"VD{ultimo_numero + 1:03d}"
        else:
            novo_id = "VD001"
        
        # Calcular valor total
        valor_total = produto.preco * data['quantidade']
        
        # Criar nova venda
        nova_venda = Venda(
            venda_id=novo_id,
            cliente_id=data['cliente_id'],
            produto_id=data['produto_id'],
            quantidade=data['quantidade'],
            valor_total=valor_total,
            forma_pagamento=data['forma_pagamento'],
            status=data.get('status', 'concluido'),
            observacoes=data.get('observacoes', '')
        )
        
        # Atualizar estoque do produto
        produto.quantidade_estoque -= data['quantidade']
        if produto.quantidade_estoque == 0:
            produto.disponivel = False
        
        db.session.add(nova_venda)
        db.session.commit()
        
        return jsonify({'message': 'Venda registrada com sucesso', 'venda': nova_venda.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API para adicionar nova despesa
@app.route("/api/despesas", methods=["POST"])
@login_required
def api_add_despesa():
    try:
        data = request.get_json()
        
        # Validar dados
        required_fields = ['descricao', 'categoria', 'valor']
        if not all(key in data for key in required_fields):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Criar nova despesa
        nova_despesa = Despesa(
            descricao=data['descricao'],
            categoria=data['categoria'],
            valor=float(data['valor']),
            observacoes=data.get('observacoes', '')
        )
        
        db.session.add(nova_despesa)
        db.session.commit()
        
        return jsonify({'message': 'Despesa registrada com sucesso', 'despesa': nova_despesa.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500