# importação de dependencias
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
import time
from datetime import date, timedelta
from quizcreator import app, db
from models import tb_user,\
    tb_usertype,\
    tb_tipostatus,\
    tb_pesquisa,\
    tb_pergunta,\
    tb_resposta
from helpers import \
    FormularPesquisa, \
    FormularioUsuarioTrocarSenha,\
    FormularioUsuario, \
    FormularioUsuarioVisualizar, \
    FormularioTipoUsuarioEdicao,\
    FormularioTipoUsuarioVisualizar,\
    FormularioTipoStatusEdicao,\
    FormularioTipoStatusVisualizar,\
    FormularioPesquisaEdicao,\
    FormularioPesquisaVisualizar,\
    FormularioPerguntaEdicao,\
    FormularioPerguntaVisualizar,\
    FormularioRespostaEdicao,\
    FormularioRespostaVisualizar

# ITENS POR PÁGINA
from config import ROWS_PER_PAGE, CHAVE
from flask_bcrypt import generate_password_hash, Bcrypt, check_password_hash

import string
import random
import numbers

##################################################################################################################################
#GERAL
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: index
#FUNÇÃO: redirecionar para página principal
#PODE ACESSAR: todos os usuários
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))        
    return render_template('index.html', titulo='Bem vindos')

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: logout
#FUNÇÃO: remover dados de sessão e deslogar ususários
#PODE ACESSAR: todos os usuários
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session['usuario_logado'] = None
    flash('Logout efetuado com sucesso','success')
    return redirect(url_for('login'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: login
#FUNÇÃO: direcionar para formulário de login
#PODE ACESSAR: todos os usuários
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/login')
def login():
    return render_template('login.html')

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: autenticar
#FUNÇÃO: autenticar usuário
#PODE ACESSAR: todos os usuários
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/autenticar', methods = ['GET', 'POST'])
def autenticar():
    usuario = tb_user.query.filter_by(login_user=request.form['usuario']).first()
    senha = check_password_hash(usuario.password_user,request.form['senha'])
    if usuario:
        if senha:
            session['usuario_logado'] = usuario.login_user
            session['nomeusuario_logado'] = usuario.name_user
            session['tipousuario_logado'] = usuario.cod_usertype
            session['coduser_logado'] = usuario.cod_user
            flash(usuario.name_user + ' Usuário logado com sucesso','success')
            #return redirect('/')
            return redirect('/')
        else:
            flash('Verifique usuário e senha', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Usuário não logado com sucesso','success')
        return redirect(url_for('login'))

##################################################################################################################################
#USUARIOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: usuario
#FUNÇÃO: tela do sistema para mostrar os usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/usuario', methods=['POST','GET'])
def usuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('usuario')))        
    form = FormularPesquisa()
    page = request.args.get('page', 1, type=int)
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data

    if pesquisa == "" or pesquisa == None:    
        usuarios = tb_user.query\
        .join(tb_usertype, tb_usertype.cod_usertype==tb_user.cod_usertype)\
        .add_columns(tb_user.login_user, tb_user.cod_user, tb_user.name_user, tb_user.status_user, tb_usertype.desc_usertype)\
        .order_by(tb_user.name_user)\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)
    else:
        usuarios = tb_user.query\
        .filter(tb_user.name_user.ilike(f'%{pesquisa}%'))\
        .join(tb_usertype, tb_usertype.cod_usertype==tb_user.cod_usertype)\
        .add_columns(tb_user.login_user, tb_user.cod_user, tb_user.name_user, tb_user.status_user, tb_usertype.desc_usertype)\
        .order_by(tb_user.name_user)\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)


    return render_template('usuarios.html', titulo='Usuários', usuarios=usuarios, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoUsuario
#FUNÇÃO: mostrar o formulário de cadastro de usuário
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/novoUsuario')
def novoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoUsuario')))     
    form = FormularioUsuario()
    return render_template('novoUsuario.html', titulo='Novo Usuário', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarUsuario
#FUNÇÃO: inserir informações do usuário no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarUsuario', methods=['POST',])
def criarUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login',proxima=url_for('criarUsuario')))      
    form = FormularioUsuario(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('novoUsuario'))
    nome  = form.nome.data
    status = form.status.data
    login = form.login.data
    tipousuario = form.tipousuario.data
    email = form.email.data
    #criptografar senha
    senha = generate_password_hash("teste@12345").decode('utf-8')
    usuario = tb_user.query.filter_by(name_user=nome).first()
    if usuario:
        flash ('Usuário já existe','danger')
        return redirect(url_for('index')) 
    novoUsuario = tb_user(name_user=nome, status_user=status, login_user=login, cod_usertype=tipousuario, password_user=senha, email_user=email)
    db.session.add(novoUsuario)
    db.session.commit()
    flash('Usuário criado com sucesso','success')
    return redirect(url_for('usuario'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarUsuarioexterno - NÃO DISPONIVEL NESTA VERSAL
#FUNÇÃO: inserir informações do usuário no banco de dados realizam cadastro pela área externa
#PODE ACESSAR: novos usuários
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/criarUsuarioexterno', methods=['POST',])
def criarUsuarioexterno():    
    nome  = request.form['nome']
    status = 0
    email = request.form['email']
    localarroba = email.find("@")
    login = email[0:localarroba]
    tipousuario = 2
    #criptografar senha
    senha = generate_password_hash(request.form['senha']).decode('utf-8')
    usuario = tb_user.query.filter_by(name_user=nome).first()
    if usuario:
        flash ('Usuário já existe','danger')
        return redirect(url_for('login')) 
    novoUsuario = tb_user(name_user=nome, status_user=status, login_user=login, cod_usertype=tipousuario, password_user=senha, email_user=email)
    db.session.add(novoUsuario)
    db.session.commit()
    flash('Usuário criado com sucesso, favor logar com ele','success')
    return redirect(url_for('login'))  

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarUsuario
#FUNÇÃO: mostrar formulário de visualização dos usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarUsuario/<int:id>')
def visualizarUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarUsuario')))    
    usuario = tb_user.query.filter_by(cod_user=id).first()
    form = FormularioUsuarioVisualizar()
    form.nome.data = usuario.name_user
    form.status.data = usuario.status_user
    form.login.data = usuario.login_user
    form.tipousuario.data = usuario.cod_usertype
    form.email.data = usuario.email_user
    return render_template('visualizarUsuario.html', titulo='Visualizar Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarUsuario
#FUNÇÃO: mostrar formulário de edição dos usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/editarUsuario/<int:id>')
def editarUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarUsuario/<int:id>')))  
    usuario = tb_user.query.filter_by(cod_user=id).first()
    form = FormularioUsuario()
    form.nome.data = usuario.name_user
    form.status.data = usuario.status_user
    form.login.data = usuario.login_user
    form.tipousuario.data = usuario.cod_usertype
    form.email.data = usuario.email_user
    return render_template('editarUsuario.html', titulo='Editar Usuário', id=id, form=form)    
       
#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarUsuario
#FUNÇÃO: alterar as informações dos usuários no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarUsuario', methods=['POST',])
def atualizarUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarUsuario')))          
    form = FormularioUsuario(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('atualizarUsuario'))
    id = request.form['id']
    usuario = tb_user.query.filter_by(cod_user=request.form['id']).first()
    usuario.name_user = form.nome.data
    usuario.status_user = form.status.data
    usuario.login_user = form.login.data
    usuario.cod_uertype = form.tipousuario.data
    db.session.add(usuario)
    db.session.commit()
    flash('Usuário alterado com sucesso','success')
    return redirect(url_for('visualizarUsuario', id=request.form['id']))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarSenhaUsuario
#FUNÇÃO: formulário para edição da tela do usuário
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarSenhaUsuario/')
def editarSenhaUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarUsuario')))    
    form = FormularioUsuarioTrocarSenha()
    return render_template('trocarsenha.html', titulo='Trocar Senha', id=id, form=form)  

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: trocarSenhaUsuario
#FUNÇÃO: alteração da senha do usuário no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/trocarSenhaUsuario', methods=['POST',])
def trocarSenhaUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarUsuario')))          
    form = FormularioUsuarioTrocarSenha(request.form)
    if form.validate_on_submit():
        id = session['coduser_logado']
        usuario = tb_user.query.filter_by(cod_user=id).first()
        if form.senhaatual.data != usuario.password_user:
            flash('senha atual incorreta','danger')
            return redirect(url_for('editarSenhaUsuario'))

        if form.senhaatual.data != usuario.password_user:
            flash('senha atual incorreta','danger')
            return redirect(url_for('editarSenhaUsuario')) 

        if form.novasenha1.data != form.novasenha2.data:
            flash('novas senhas não coincidem','danger')
            return redirect(url_for('editarSenhaUsuario')) 
        usuario.password_user = generate_password_hash(form.novasenha1.data).decode('utf-8')
        db.session.add(usuario)
        db.session.commit()
        flash('senha alterada com sucesso!','success')
    else:
        flash('senha não alterada!','danger')
    return redirect(url_for('editarSenhaUsuario')) 

##################################################################################################################################
#TIPO DE USUARIOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: tipousuario
#FUNÇÃO: tela do sistema para mostrar os tipos de usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/tipousuario', methods=['POST','GET'])
def tipousuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('tipousuario')))         
    page = request.args.get('page', 1, type=int)
    form = FormularPesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    
    if pesquisa == "" or pesquisa == None:     
        tiposusuario = tb_usertype.query.order_by(tb_usertype.desc_usertype)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        tiposusuario = tb_usertype.query.order_by(tb_usertype.desc_usertype)\
        .filter(tb_usertype.desc_usertype.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('tipousuarios.html', titulo='Tipo Usuário', tiposusuario=tiposusuario, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoTipoUsuario
#FUNÇÃO: mostrar o formulário de cadastro de tipo de usuário
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoTipoUsuario')
def novoTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoTipoUsuario'))) 
    form = FormularioTipoUsuarioEdicao()
    return render_template('novoTipoUsuario.html', titulo='Novo Tipo Usuário', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarTipoUsuario
#FUNÇÃO: inserir informações do tipo de usuário no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarTipoUsuario', methods=['POST',])
def criarTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarTipoUsuario')))     
    form = FormularioTipoUsuarioEdicao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarTipoUsuario'))
    desc  = form.descricao.data
    status = form.status.data
    tipousuario = tb_usertype.query.filter_by(desc_usertype=desc).first()
    if tipousuario:
        flash ('Tipo Usuário já existe','danger')
        return redirect(url_for('tipousuario')) 
    novoTipoUsuario = tb_usertype(desc_usertype=desc, status_usertype=status)
    flash('Tipo de usuário criado com sucesso!','success')
    db.session.add(novoTipoUsuario)
    db.session.commit()
    return redirect(url_for('tipousuario'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarTipoUsuario
#FUNÇÃO: mostrar formulário de visualização dos tipos de usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarTipoUsuario/<int:id>')
def visualizarTipoUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarTipoUsuario')))  
    tipousuario = tb_usertype.query.filter_by(cod_usertype=id).first()
    form = FormularioTipoUsuarioVisualizar()
    form.descricao.data = tipousuario.desc_usertype
    form.status.data = tipousuario.status_usertype
    return render_template('visualizarTipoUsuario.html', titulo='Visualizar Tipo Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarTipoUsuario
##FUNÇÃO: mostrar formulário de edição dos tipos de usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarTipoUsuario/<int:id>')
def editarTipoUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarTipoUsuario')))  
    tipousuario = tb_usertype.query.filter_by(cod_usertype=id).first()
    form = FormularioTipoUsuarioEdicao()
    form.descricao.data = tipousuario.desc_usertype
    form.status.data = tipousuario.status_usertype
    return render_template('editarTipoUsuario.html', titulo='Editar Tipo Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarTipoUsuario
#FUNÇÃO: alterar as informações dos tipos de usuários no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarTipoUsuario', methods=['POST',])
def atualizarTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarTipoUsuario')))      
    form = FormularioTipoUsuarioEdicao(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        tipousuario = tb_usertype.query.filter_by(cod_usertype=request.form['id']).first()
        tipousuario.desc_usertype = form.descricao.data
        tipousuario.status_usertype = form.status.data
        db.session.add(tipousuario)
        db.session.commit()
        flash('Tipo de usuário atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarTipoUsuario', id=request.form['id']))    

##################################################################################################################################
#TIPO DE STATUS PESQUISA
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: status
#FUNÇÃO: tela do sistema para mostrar os tipos de status de pesquisa cadastrados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/tipostatus', methods=['POST','GET'])
def tipostatus():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('tipostatus')))         
    page = request.args.get('page', 1, type=int)
    form = FormularPesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    if pesquisa == "" or pesquisa == None:     
        tiposstatus = tb_tipostatus.query.order_by(tb_tipostatus.desc_tipostatus)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        tiposstatus = tb_usertype.query.order_by(tb_tipostatus.desc_tipostatus)\
        .filter(tb_usertype.desc_tipostatus.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('tipostatus.html', titulo='Tipo Status', tiposstatus=tiposstatus, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoTipoStatus
#FUNÇÃO: mostrar o formulário de cadastro de tipo de status
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoTipoStatus')
def novoTipoStatus():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoTipoStatus'))) 
    form = FormularioTipoStatusEdicao()
    return render_template('novoTipoStatus.html', titulo='Novo Tipo Status', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarTipoStatus
#FUNÇÃO: inserir informações do tipo de statys no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarTipoStatus', methods=['POST',])
def criarTipoStatus():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarTipoStatus')))     
    form = FormularioTipoStatusEdicao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarTipoStatus'))
    desc  = form.descricao.data
    status = form.status.data
    tipoustatus = tb_tipostatus.query.filter_by(desc_tipostatus=desc).first()
    if tipoustatus:
        flash ('Tipo status já existe','danger')
        return redirect(url_for('tipousuario')) 
    novoTipoStatus = tb_tipostatus(desc_tipostatus=desc, status_tipostatus=status)
    flash('Tipo de status criado com sucesso!','success')
    db.session.add(novoTipoStatus)
    db.session.commit()
    return redirect(url_for('tipostatus'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarTipoStatus
#FUNÇÃO: mostrar formulário de visualização dos tipos de status cadastrados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarTipoStatus/<int:id>')
def visualizarTipoStatus(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarTipoStatus')))  
    tipostatus = tb_tipostatus.query.filter_by(cod_tipostatus=id).first()
    form = FormularioTipoStatusVisualizar()
    form.descricao.data = tipostatus.desc_tipostatus
    form.status.data = tipostatus.status_tipostatus
    return render_template('visualizarTipoStatus.html', titulo='Visualizar Tipo Status', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarTipoUsuario
##FUNÇÃO: mostrar formulário de edição dos tipos de usuários cadastrados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarTipoStatus/<int:id>')
def editarTipoStatus(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarTipoStatus')))  
    tipostatus = tb_tipostatus.query.filter_by(cod_tipostatus=id).first()
    form = FormularioTipoStatusEdicao()
    form.descricao.data = tipostatus.desc_tipostatus
    form.status.data = tipostatus.status_tipostatus
    return render_template('editarTipoStatus.html', titulo='Editar Tipo Status', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarTipoUsuario
#FUNÇÃO: alterar as informações dos tipos de usuários no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarTipoStatus', methods=['POST',])
def atualizarTipoStatus():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarTipoStatus')))      
    form = FormularioTipoStatusEdicao(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        tipostatus = tb_tipostatus.query.filter_by(cod_tipostatus=request.form['id']).first()
        tipostatus.desc_tipostatus = form.descricao.data
        tipostatus.status_tipostatus = form.status.data
        db.session.add(tipostatus)
        db.session.commit()
        flash('Tipo de status atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarTipoStatus', id=request.form['id']))    

##################################################################################################################################
#PESQUISA
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: pesquisa
#FUNÇÃO: tela do sistema para mostrar as pesquisa cadastradas
#PODE ACESSAR: usuários do tipo administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/pesquisa', methods=['POST','GET'])
def pesquisa():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('pesquisa')))         
    page = request.args.get('page', 1, type=int)
    form = FormularPesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    if pesquisa == "" or pesquisa == None:     
        pesquisas = tb_pesquisa.query.order_by(tb_pesquisa.desc_pesquisa)\
        .join(tb_tipostatus, tb_tipostatus.cod_tipostatus==tb_pesquisa.cod_tipostatus)\
        .add_columns(tb_pesquisa.nome_pesquisa, tb_pesquisa.cod_pesquisa, tb_tipostatus.desc_tipostatus, tb_pesquisa.cod_tipostatus)\
        .filter(tb_pesquisa.cod_user == session['coduser_logado'])\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        pesquisas = tb_pesquisa.query.order_by(tb_pesquisa.desc_pesquisa)\
        .join(tb_tipostatus, tb_tipostatus.cod_tipostatus==tb_pesquisa.cod_tipostatus)\
        .add_columns(tb_pesquisa.nome_pesquisa, tb_pesquisa.cod_pesquisa, tb_tipostatus.desc_tipostatus)\
        .filter(tb_pesquisa.cod_user == session['coduser_logado'])\
        .filter(tb_pesquisa.nome_pesquisa.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('pesquisas.html', titulo='Pesquisas', pesquisas=pesquisas, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoPesquisa
#FUNÇÃO: mostrar o formulário de cadastro de pesquisa
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoPesquisa')
def novoPesquisa():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoPesquisa'))) 
    form = FormularioPesquisaEdicao()
    return render_template('novoPesquisa.html', titulo='Nova Pesquisa', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarPesquisa
#FUNÇÃO: inserir informações de pesquisa no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarPesquisa', methods=['POST',])
def criarPesquisa():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarPesquisa')))     
    form = FormularioPesquisaEdicao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarPesquisa'))
    desc  = form.desc.data
    nome  = form.nome.data
    status = form.status.data
    codext = form.codext.data
    coduser = session['coduser_logado']
    pesquisa = tb_pesquisa.query.filter_by(nome_pesquisa=desc).first()
    if pesquisa:
        flash ('Pesquisa já existe','danger')
        return redirect(url_for('pesquisa')) 
    novoPesquisa = tb_pesquisa(desc_pesquisa=desc, cod_tipostatus=status, nome_pesquisa=nome, codext_pesquisa=codext, cod_user=coduser)
    flash('Pesquisa criada com sucesso!','success')
    db.session.add(novoPesquisa)
    db.session.commit()
    return redirect(url_for('pesquisa'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarPesquisa
#FUNÇÃO: mostrar formulário de visualização das pesquisas cadastradas
#PODE ACESSAR: todos
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarPesquisa/<int:id>')
def visualizarPesquisa(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarPesquisa')))  
    pesquisa = tb_pesquisa.query.filter_by(cod_pesquisa=id).first()
    form = FormularioPesquisaVisualizar()
    form.desc.data = pesquisa.desc_pesquisa
    form.status.data = pesquisa.cod_tipostatus
    form.nome.data = pesquisa.nome_pesquisa
    form.codext.data = pesquisa.codext_pesquisa
    page = request.args.get('page', 1, type=int)
    perguntas = tb_pergunta.query.order_by(tb_pergunta.ordem_pergunta)\
        .filter(tb_pergunta.cod_pesquisa == id)\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)   


    return render_template('visualizarPesquisa.html', titulo='Visualizar Pesquisa', id=id, form=form, perguntas=perguntas)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarPesquisa
##FUNÇÃO: mostrar formulário de edição das pesquisas cadastradas
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarPesquisa/<int:id>')
def editarPesquisa(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarPesquisa')))  
    pesquisa = tb_pesquisa.query.filter_by(cod_pesquisa=id).first()
    form = FormularioPesquisaEdicao()
    form.desc.data = pesquisa.desc_pesquisa
    form.status.data = pesquisa.cod_tipostatus
    form.nome.data = pesquisa.nome_pesquisa
    form.codext.data = pesquisa.codext_pesquisa
    return render_template('editarPesquisa.html', titulo='Editar Pesquisa', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarPesquisa
#FUNÇÃO: alterar as informações de pesquisa no banco de dados
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarPesquisa', methods=['POST',])
def atualizarPesquisa():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarPesquisa')))      
    form = FormularioPesquisaEdicao(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        pesquisa = tb_pesquisa.query.filter_by(cod_pesquisa=request.form['id']).first()
        pesquisa.desc_pesquisa = form.desc.data
        pesquisa.cod_tipostatus = form.status.data
        pesquisa.nome_pesquisa = form.nome.data
        pesquisa.codext_pesquisa = form.codext.data
        db.session.add(pesquisa)
        db.session.commit()
        flash('Pesquisa atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarPesquisa', id=request.form['id'])) 

##################################################################################################################################
#PERGUNTA
##################################################################################################################################   
#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoPergunta
#FUNÇÃO: mostrar o formulário de cadastro de pergunta
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoPergunta/<int:id>')
def novoPergunta(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoPergunta'))) 
    form = FormularioPerguntaEdicao()
    return render_template('novoPergunta.html', titulo='Nova Pergunta', form=form, id=id)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarPergunta
#FUNÇÃO: inserir informações de pergunta no banco de dados
#PODE ACESSAR: usuários do tipo administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarPergunta', methods=['POST',])
def criarPergunta():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarPergunta')))     
    form = FormularioPerguntaEdicao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarPergunta'))
    id = request.form['id']
    desc  = form.desc.data
    status = form.status.data
    ordem = form.ordem.data
    cod_pesquisa = id
    pergunta = tb_pergunta.query.filter_by(desc_pergunta=desc).first()\
            .filter(tb_pergunta.cod_pesquisa == id)
    if pergunta:
        flash ('Pergunta já existe','danger')
        return redirect(url_for('pesquisa')) 
    novoPergunta = tb_pergunta(desc_pergunta=desc, status_pergunta=status, cod_pesquisa=cod_pesquisa, ordem_pergunta=ordem)
    flash('Pergunta criada com sucesso!','success')
    db.session.add(novoPergunta)
    db.session.commit()
    return redirect(url_for('visualizarPesquisa', id=id))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarPergunta
#FUNÇÃO: visualizar informações de pergunta no banco de dados
#PODE ACESSAR: todos
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarPergunta/<int:id><int:idpergunta>')
def visualizarPergunta(id,idpergunta):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarPergunta')))  
    pergunta = tb_pergunta.query.filter_by(cod_pergunta=idpergunta).first()
    page = request.args.get('page', 1, type=int)
    form = FormularioPerguntaVisualizar()
    form.desc.data = pergunta.desc_pergunta
    form.status.data = pergunta.status_pergunta
    form.ordem.data = pergunta.ordem_pergunta

    respostas = tb_resposta.query.order_by(tb_resposta.desc_resposta)\
        .filter(tb_resposta.cod_pergunta == idpergunta)\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)       
    
    return render_template('visualizarPergunta.html', titulo='Visualizar Pergunta', id=id, form=form, idpergunta=idpergunta,respostas=respostas)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarPergunta
#FUNÇÃO: editar informações de pergunta no banco de dados
#PODE ACESSAR: todos
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/editarPergunta/<int:id><int:idpergunta>')
def editarPergunta(id,idpergunta):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarPergunta')))  
    pergunta = tb_pergunta.query.filter_by(cod_pergunta=idpergunta).first()
    form = FormularioPerguntaEdicao()
    form.desc.data = pergunta.desc_pergunta
    form.status.data = pergunta.status_pergunta
    form.ordem.data = pergunta.ordem_pergunta
    return render_template('editarPergunta.html', titulo='Editar Pergunta', id=id, form=form, idpergunta=idpergunta)   
 
#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarPergunda
#FUNÇÃO: alterar as informações de pergunta no banco de dados
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarPergunta/<int:id><int:idpergunta>', methods=['POST',])
def atualizarPergunta(id,idpergunta):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarPergunta')))      
    form = FormularioPerguntaEdicao(request.form)
    if form.validate_on_submit():
        idpergunta = request.form['id']
        pergunta = tb_pergunta.query.filter_by(cod_pergunta=idpergunta).first()
        pergunta.desc_pergunta = form.desc.data
        pergunta.cod_tipostatus = form.status.data
        pergunta.ordem_pergunta = form.ordem.data
        db.session.add(pergunta)
        db.session.commit()
        flash('Pergunta atualizada com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarPergunta', id=id, idpergunta=idpergunta)) 

##################################################################################################################################
#RESPOSTAS
################################################################################################################################## 
#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoResposta
#FUNÇÃO: mostrar o formulário de cadastro de resposta
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoResposta/<int:id><int:idpergunta>')
def novoResposta(id,idpergunta):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoPergunta'))) 
    form = FormularioRespostaEdicao()
    return render_template('novoResposta.html', titulo='Nova Resposta', form=form, id=id, idpergunta=idpergunta)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarResposta
#FUNÇÃO: inserir informações de resposta no banco de dados
#PODE ACESSAR: todos
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarResposta/<int:id><int:idpergunta>', methods=['POST',])
def criarResposta(id,idpergunta):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarResposta')))     
    form = FormularioRespostaEdicao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarResposta'))
    idpergunta = request.form['id']
    desc  = form.desc.data
    status = form.status.data
    certa = form.certa.data
    cod_pesquisa = id
    resposta = tb_resposta.query.filter_by(desc_resposta=desc).first()\
            .filter(tb_resposta.cod_pergunta == idpergunta)
    if resposta:
        flash ('Resposta já existe','danger')
        return redirect(url_for('visualizarPergunta',id=id,idpergunta=idpergunta)) 
    novoResposta = tb_resposta(desc_resposta=desc, status_resposta=status, cod_pergunta=idpergunta, certa_resposta=certa)
    flash('Resposta criada com sucesso!','success')
    db.session.add(novoResposta)
    db.session.commit()
    return redirect(url_for('visualizarPergunta', id=id, idpergunta=idpergunta))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarResposta
#FUNÇÃO: visualizar informações de resposta no banco de dados
#PODE ACESSAR: todos
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarResposta/<int:id><int:idpergunta><int:idresposta>')
def visualizarResposta(id,idpergunta,idresposta):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarPergunta')))  
    resposta = tb_resposta.query.filter_by(cod_resposta=idresposta).first()
    page = request.args.get('page', 1, type=int)
    form = FormularioRespostaVisualizar()
    form.desc.data = resposta.desc_resposta
    form.status.data = resposta.status_resposta
    form.certa.data = resposta.certa_resposta   
    
    return render_template('visualizarResposta.html', titulo='Visualizar Resposta', id=id, form=form, idpergunta=idpergunta,idresposta=idresposta) 

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarResposta
#FUNÇÃO: editar informações de resposta no banco de dados
#PODE ACESSAR: todos
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/editarResposta/<int:id><int:idpergunta><int:idresposta>')
def editarResposta(id,idpergunta,idresposta):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarPergunta')))  
    resposta = tb_resposta.query.filter_by(cod_resposta=idresposta).first()
    form = FormularioRespostaEdicao()
    form.desc.data = resposta.desc_resposta
    form.status.data = resposta.status_resposta
    form.certa.data = resposta.certa_resposta
    return render_template('editarResposta.html', titulo='Editar Resposta', id=id, form=form, idpergunta=idpergunta,idresposta=idresposta)  

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarResposta
#FUNÇÃO: alterar as informações de resposta no banco de dados
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarResposta/<int:id><int:idpergunta><int:idresposta>', methods=['POST',])
def atualizarResposta(id,idpergunta,idresposta):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarResposta')))      
    form = FormularioRespostaEdicao(request.form)
    if form.validate_on_submit():
        idresposta = request.form['id']
        resposta = tb_resposta.query.filter_by(cod_resposta=idresposta).first()
        resposta.desc_resposta = form.desc.data
        resposta.status_resposta = form.status.data
        resposta.certa_resposta = form.certa.data
        db.session.add(resposta)
        db.session.commit()
        flash('Resposta atualizada com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarResposta', id=id, idpergunta=idpergunta, idresposta=idresposta)) 