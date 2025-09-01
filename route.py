from main import app
from flask import render_template, request, redirect, url_for, session, jsonify


@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        try:
            with open("usuarios.txt", "r") as file:
                for linha in file:
                    partes = linha.strip().split("-")
                    dados = {}
                    for parte in partes:
                        if ": " in parte:
                            chave, valor = parte.split(": ", 1)
                            dados[chave] = valor

                    if dados.get("email") == email and dados.get("senha") == senha:
                        perfil = dados.get("perfil")
                        return redirect(url_for(perfil.lower(), user=perfil))
        except FileNotFoundError:
            pass

        return render_template("login.html", resultado="Informação inválidas")

    return render_template("login.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        conf_senha = request.form.get("conf-senha") 
        perfil = request.form.get("perfil")

        if senha != conf_senha:
            return render_template("cadastro.html", erro="Senhas diferentes")
        
        try:
            with open("usuarios.txt", "r") as file:
                for linha in file:
                    partes = linha.strip().split("-")
                    dados = {}
                    for parte in partes:
                        if ": " in parte:
                            chave, valor = parte.split(": ", 1)
                            dados[chave] = valor

                    if dados.get("email") == email:
                        return render_template("cadastro.html", erro="Email já cadastrado.")
        except FileNotFoundError:
            pass

        with open("usuarios.txt", "a") as file:
            if perfil.lower() == "Funcionario":
                file.write(f"email: {email}-senha: {senha}-perfil: Funcionario\n")
            else:
                file.write(f"email: {email}-senha: {senha}-perfil: Dono\n")

        return render_template("cadastro.html", resultado="Cadastro concluído!")
 

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
        
        try:
            linhas = []
            atualizado = False
            with open("usuarios.txt", "r") as file:
                for linha in file:
                    if f"email: {email}" in linha:
                        partes = linha.strip().split("-")
                        dados = {}
                        for parte in partes:
                            if ": " in parte:
                                chave, valor = parte.split(": ", 1)
                                dados[chave] = valor
                        if dados.get("senha") != senha_atual:
                            return jsonify({"error": "Senha atual incorreta."}), 400
                        dados["senha"] = nova_senha
                        nova_linha = "-".join([f"{k}: {v}" for k, v in dados.items()])
                        linhas.append(nova_linha + "\n")
                        atualizado = True
                    else:
                        linhas.append(linha)
            if atualizado:
                with open("usuarios.txt", "w") as file:
                    file.writelines(linhas)
                return jsonify({"message": "Senha alterada com sucesso."})
            else:
                return jsonify({"error": "Usuário não encontrado."}), 400
        except Exception as e:
            return jsonify({"error": f"Erro ao atualizar senha: {str(e)}"}), 500

    return render_template("esqueceu.html")


@app.route("/funcionario")
def funcionario():
    return render_template("funcionario.html")

@app.route("/dono")
def dono():
    return render_template("dono.html")

@app.route("/clientes")
def clientes():
    return render_template("clientes.html")
