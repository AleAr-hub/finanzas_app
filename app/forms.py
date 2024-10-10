from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.db import session
from app.models import Usuario


class RegistroForm(FlaskForm):
    nombre_registro = StringField('Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    email_registro = StringField('Email',
                                 validators=[DataRequired(), Email(message='Por favor ingresa un email valido')])
    password_registro = PasswordField('Contraseña', validators=[DataRequired()])
    confirmar_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password_registro',
                                                                                                   message='Las contraseñas no coinciden')])
    submit_registro = SubmitField('Registrarse')

    def validate_email(self, email):
        usuario = session.query(Usuario).filter_by(email_usuario=email.data).first()
        if usuario:
            raise ValidationError('El email ya está en uso. Prueba uno diferente')


class InicioForm(FlaskForm):
    email_inicio = StringField('Email', validators=[DataRequired(), Email()])
    password_inicio = PasswordField('Contraseña', validators=[DataRequired()])
    recordar = BooleanField('Recordarme')
    submit_inicio = SubmitField('Iniciar Sesion')


class EditarNombreForm(FlaskForm):
    nombre_usuario = StringField('Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    submit_nombre = SubmitField('Actualizar Nombre')


class EditarEmailForm(FlaskForm):
    email_usuario = StringField('Email',
                                validators=[DataRequired(), Email(message='Por favor ingresa un email valido')])
    submit_email = SubmitField('Actualizar Correo')

    def validate_email(self, email_usuario):
        if email_usuario.data != current_user.email_usuario:
            usuario = session.query(Usuario).filter_by(email_usuario=email_usuario.data).first()
            if usuario:
                raise ValidationError('El email ya está en uso. Prueba uno diferente')


class EditarImagenUsuario(FlaskForm):
    imagen_usuario = FileField('Imagen', validators=[FileAllowed(['jpg', 'png'])])
    submit_imagen = SubmitField('Actualizar imagen')


class SolicitarResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar Restablecimiento de Contraseña')


class ResetPasswordForm(FlaskForm):
    password_nuevo = PasswordField('Nueva Contraseña', validators=[DataRequired()])
    confirmar_password_nuevo = PasswordField('Confirmar nueva Contraseña',
                                             validators=[DataRequired(), EqualTo('password_nuevo',
                                                                                 message='Las contraseñas no coinciden')])
    submit = SubmitField('Restablecer Contraseña')
