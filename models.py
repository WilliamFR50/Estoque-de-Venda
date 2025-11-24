from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_id = db.Column(db.String(10), unique=True, nullable=False)  # CL001, CL002, etc.
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)  # 123.456.789-00
    status = db.Column(db.String(10), nullable=False, default='active')  # active/inactive
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'cpf': self.cpf,
            'status': self.status,
            'data_cadastro': self.data_cadastro.strftime('%Y-%m-%d')
        }

class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    produto_id = db.Column(db.String(10), unique=True, nullable=False)  # PR001, PR002, etc.
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    quantidade_estoque = db.Column(db.Integer, nullable=False, default=0)
    disponivel = db.Column(db.Boolean, nullable=False, default=True)
    imagem_url = db.Column(db.String(200))
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'produto_id': self.produto_id,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': self.preco,
            'categoria': self.categoria,
            'quantidade_estoque': self.quantidade_estoque,
            'disponivel': self.disponivel,
            'imagem_url': self.imagem_url,
            'data_cadastro': self.data_cadastro.strftime('%Y-%m-%d')
        }
    
class Venda(db.Model):
    __tablename__ = 'vendas'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venda_id = db.Column(db.String(10), unique=True, nullable=False)  # VD001, VD002, etc.
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    valor_total = db.Column(db.Float, nullable=False)
    forma_pagamento = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='concluido')
    observacoes = db.Column(db.Text)
    data_venda = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    cliente = db.relationship('Cliente', backref='vendas')
    produto = db.relationship('Produto', backref='vendas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'venda_id': self.venda_id,
            'cliente_id': self.cliente_id,
            'produto_id': self.produto_id,
            'cliente_nome': self.cliente.nome,
            'produto_nome': self.produto.nome,
            'quantidade': self.quantidade,
            'valor_total': self.valor_total,
            'forma_pagamento': self.forma_pagamento,
            'status': self.status,
            'observacoes': self.observacoes,
            'data_venda': self.data_venda.strftime('%d/%m/%Y')
        }

class Despesa(db.Model):
    __tablename__ = 'despesas'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_despesa = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    observacoes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'categoria': self.categoria,
            'valor': self.valor,
            'data_despesa': self.data_despesa.strftime('%d/%m/%Y'),
            'observacoes': self.observacoes
        }