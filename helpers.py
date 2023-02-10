#importações
import os
from quizcreator import app, db
from models import tb_user, tb_usertype, tb_tipostatus
from flask_wtf import FlaskForm
from wtforms import Form, StringField, validators, SubmitField,IntegerField, SelectField,PasswordField,DateField,EmailField,BooleanField,RadioField, TextAreaField, TimeField, TelField, DateTimeLocalField

##################################################################################################################################
#PESQUISA
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: pesquisa (geral)
#TIPO: edição
#TABELA: nenhuma
#---------------------------------------------------------------------------------------------------------------------------------
class FormularPesquisa(FlaskForm):
    pesquisa = StringField('Pesquisa:', [validators.Length(min=1, max=50)],render_kw={"placeholder": "digite sua pesquisa"} )
    pesquisa_responsiva = StringField('Pesquisa:', [validators.Length(min=1, max=50)],render_kw={"placeholder": "digite sua pesquisa"} )
    salvar = SubmitField('Pesquisar')

##################################################################################################################################
#USUÁRIO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: usuários
#TIPO: edição
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioUsuario(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o nome do usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")])
    login = StringField('Login:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o login do usuário"})    
    tipousuario = SelectField('Situação:', coerce=int,  choices=[(g.cod_usertype, g.desc_usertype) for g in tb_usertype.query.order_by('desc_usertype')])
    email = EmailField('Email:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o email do usuário"})
    salvar = SubmitField('Salvar')


#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: usuários
#TIPO: visualização
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioUsuarioVisualizar(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")], render_kw={'readonly': True})
    login = StringField('Login:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    tipousuario = SelectField('Tipo:', coerce=int, choices=[(g.cod_usertype, g.desc_usertype) for g in tb_usertype.query.order_by('desc_usertype')], render_kw={'readonly': True})
    email = EmailField('Email:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    salvar = SubmitField('Editar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: trocar senha do usuário
#TIPO: edição
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioUsuarioTrocarSenha(FlaskForm):
    senhaatual = PasswordField('Senha Atual:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a senha atual"})
    novasenha1 = PasswordField('Nova Senha:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a nova senha"})
    novasenha2 = PasswordField('Confirme Nova Senha:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite novamente a senha"})
    salvar = SubmitField('Editar')  

##################################################################################################################################
#TIPO DE USUÁRIO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: edição
#TABELA: tb_usertype
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioTipoUsuarioEdicao(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição do tipo de usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: visualização
#TABELA: tb_usertype
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioTipoUsuarioVisualizar(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')    

##################################################################################################################################
#TIPO DE STATUS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de status
#TIPO: edição
#TABELA: tb_usertype
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioTipoStatusEdicao(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição do tipo de status"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de status
#TIPO: visualização
#TABELA: tb_usertype
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioTipoStatusVisualizar(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')    

##################################################################################################################################
#PESQUISA
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: pesquisa
#TIPO: edição
#TABELA: tb_pesquisa
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioPesquisaEdicao(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição do tipo de status"})
    codext = StringField('Código externo:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição do tipo de status"})
    desc = TextAreaField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={"placeholder": "digite a descrição do tipo de status"})
    status = SelectField('Situação:', coerce=int,  choices=[(g.cod_tipostatus, g.desc_tipostatus) for g in tb_tipostatus.query.order_by('desc_tipostatus')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: pesquisa
#TIPO: visualização
#TABELA: tb_ustb_pesquisaertype
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioPesquisaVisualizar(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    codext = StringField('Código externo:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    desc = TextAreaField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int,  choices=[(g.cod_tipostatus, g.desc_tipostatus) for g in tb_tipostatus.query.order_by('desc_tipostatus')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')

##################################################################################################################################
#PERGUNTA
##################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: pergunta
#TIPO: edição
#TABELA: tb_pergunta
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioPerguntaEdicao(FlaskForm):
    desc = TextAreaField('Pergunta:', [validators.DataRequired(), validators.Length(min=1, max=500)], render_kw={"placeholder": "digite a descrição da pergunta"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    ordem = IntegerField('Ordem:', [validators.DataRequired()])
    salvar = SubmitField('Salvar') 

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: pesquisa
#TIPO: visualização
#TABELA: tb_pergunta
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioPerguntaVisualizar(FlaskForm):
    desc = TextAreaField('Pergunta:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    ordem = IntegerField('Ordem:', [validators.DataRequired()], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')

##################################################################################################################################
#RESPOSTA
##################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: resposta
#TIPO: edição
#TABELA: tb_resposta
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioRespostaEdicao(FlaskForm):
    desc = StringField('Resposta:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição da resposta"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    certa = SelectField('Correta:', coerce=int, choices=[(0, 'Não'),(1, 'Sim')])
    salvar = SubmitField('Salvar') 

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: pesquisa
#TIPO: visualização
#TABELA: tb_pergunta
#---------------------------------------------------------------------------------------------------------------------------------
class FormularioRespostaVisualizar(FlaskForm):
    desc = StringField('Pergunta:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    certa = SelectField('Certa:', coerce=int, choices=[(0, 'Não'),(1, 'Sim')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')