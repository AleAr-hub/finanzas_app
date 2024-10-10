import os

from werkzeug.utils import secure_filename

from flask_login import login_user, current_user, logout_user, login_required

from app import app, bcrypt, mail, s
from flask import render_template, request, redirect, url_for, flash, current_app

from app.models import Categoria, Transaccion, Usuario
from app.forms import RegistroForm, InicioForm, EditarEmailForm, EditarNombreForm, EditarImagenUsuario, \
    SolicitarResetPasswordForm, ResetPasswordForm

from app.db import session
from flask_mail import Message


@app.route('/')
@login_required
def home():
    usuario_actual = current_user

    if not usuario_actual.is_authenticated:
        flash('Por favor, inicia sesion.', 'warning')
        return redirect(url_for('inicio'))

    # Filtrado de categorias y transacciones del usuario
    categorias = session.query(Categoria).filter_by(usuario_id=usuario_actual.id).all()
    transacciones = session.query(Transaccion).filter_by(usuario_id=usuario_actual.id).all()

    imagen_usuario = url_for('static', filename=f'images/{usuario_actual.imagen_usuario}')

    total = sum(transaccion.ingreso for transaccion in transacciones) - sum(
        transaccion.gasto for transaccion in transacciones)

    return render_template('home.html', lista_de_categorias=categorias, lista_de_transacciones=transacciones,
                           total=total, nombre_usuario=usuario_actual.nombre_usuario, imagen_usuario=imagen_usuario,
                           title='Home')


@app.route('/crear-categoria', methods=['POST'])
@login_required
def categoria():
    usuario_actual = current_user
    nombre = str(request.form['categoria']).upper()

    categoria = Categoria(nombre_categoria=nombre, usuario_id=usuario_actual.id)
    session.add(categoria)
    session.commit()
    return redirect(url_for('home'))


@app.route('/crear-transaccion', methods=['POST'])
@login_required
def transaccion():
    usuario_actual = current_user
    # Utilizo .get() para obtener el valor del campo o None si no esta presente
    ingreso = request.form.get('ingreso')
    gasto = request.form.get('gasto')
    categoria_id = request.form.get('categoria_id')

    # Si no se ingresa un valor por defecto se establecera en 0.0
    ingreso = float(ingreso) if ingreso else 0.0
    gasto = float(gasto) if gasto else 0.0

    transaccion = Transaccion(ingreso=ingreso, gasto=gasto, categoria_id=int(categoria_id),
                              usuario_id=usuario_actual.id)
    session.add(transaccion)
    session.commit()
    return redirect(url_for('home'))


@app.route('/eliminar-transaccion/<id>')
@login_required
def eliminar_transaccion(id):
    usuario_actual = current_user
    transaccion = session.query(Transaccion).filter_by(id=id, usuario_id=usuario_actual.id).first()

    if transaccion:
        session.delete(transaccion)
        session.commit()
        flash('Transaccion eliminado correctamente.', 'success')
    else:
        flash('No tienes permiso para eliminar esta transaccion.', 'danger')

    return redirect(url_for('home'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form_registro = RegistroForm()
    if form_registro.validate_on_submit():
        usuario_existente = session.query(Usuario).filter_by(email_usuario=form_registro.email_registro.data).first()
        if usuario_existente:
            flash('Este correo ya esta en uso. Prueba uno diferente.', 'danger')
            return redirect(url_for('registro'))

        # Utilizo bcrypt para hashear la contraseña del usuriao y la decodifico en 'utf-8' para añadirla como un string a la columna password_usuario de la tabla Usuario
        hashed_password = bcrypt.generate_password_hash(form_registro.password_registro.data).decode('utf-8')
        usuario = Usuario(nombre_usuario=form_registro.nombre_registro.data,
                          email_usuario=form_registro.email_registro.data, password_usuario=hashed_password)

        session.add(usuario)
        session.commit()
        flash(f'Usuario {form_registro.nombre_registro.data} creado correctamente', 'info')
        return redirect(url_for('inicio'))

    return render_template('registro.html', title='Registro', form=form_registro)


@app.route('/inicio', methods=['GET', 'POST'])
def inicio():
    form_inicio = InicioForm()
    if form_inicio.validate_on_submit():
        usuario = session.query(Usuario).filter_by(email_usuario=form_inicio.email_inicio.data).first()
        if usuario and bcrypt.check_password_hash(usuario.password_usuario, form_inicio.password_inicio.data):
            login_user(usuario, remember=form_inicio.recordar.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('No se ha iniciado la sesion correctamente, revisa tu correo o contraseña', 'danger')
    return render_template('inicio.html', title='Inicio', form=form_inicio)


@app.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form_nombre = EditarNombreForm()
    form_email = EditarEmailForm()
    form_imagen = EditarImagenUsuario()

    # Obtener el usuario actual
    usuario_actual = current_user

    # Manejar cambios de nombre de usuario
    if form_nombre.submit_nombre.data and form_nombre.validate_on_submit():
        if form_nombre.nombre_usuario.data and form_nombre.nombre_usuario.data != usuario_actual.nombre_usuario:
            usuario_actual.nombre_usuario = form_nombre.nombre_usuario.data
            session.commit()
            flash('Tu nombre de usuario ha sido actualizado.', 'success')

    # Manejar cambios de email de usuario
    if form_email.submit_email.data and form_email.validate_on_submit():
        if form_email.email_usuario.data != usuario_actual.email_usuario:
            usuario_existente = session.query(Usuario).filter_by(email_usuario=form_email.email_usuario.data).first()
            if usuario_existente:
                flash('El email ya está en uso. Prueba uno diferente.', 'danger')
            else:
                usuario_actual.email_usuario = form_email.email_usuario.data
                session.commit()
                flash('Tu email de usuario ha sido actualizado.', 'success')

    # Manejar cambios de imagen de usuario
    if form_imagen.submit_imagen.data and form_imagen.validate_on_submit():
        if form_imagen.imagen_usuario.data:
            # Guardar la nueva imagen de perfil
            nombre_archivo = guardar_imagen(form_imagen.imagen_usuario.data)
            usuario_actual.imagen_usuario = nombre_archivo
            session.commit()
            flash('Tu imagen de perfil ha sido actualizada.', 'success')

    # Cargar las categorías del usuario actual
    categorias = session.query(Categoria).filter_by(usuario_id=usuario_actual.id).all()

    # Preparar la imagen del usuario
    imagen_usuario = url_for('static', filename=f'images/{usuario_actual.imagen_usuario}')

    return render_template('perfil.html', form_nombre=form_nombre,
                           form_email=form_email,
                           form_imagen=form_imagen,
                           imagen=imagen_usuario,
                           lista_de_categorias=categorias,
                           nombre_usuario=usuario_actual.nombre_usuario,
                           email_usuario=usuario_actual.email_usuario)


@app.route('/editar-categoria', methods=['POST'])
@login_required
def editar_categoria():
    usuario_actual = current_user
    categoria_id = request.form.get('categoria_id')
    nuevo_nombre = request.form.get('nuevo_nombre').upper()

    categoria = session.query(Categoria).filter_by(id=categoria_id, usuario_id=usuario_actual.id).first()
    if categoria:
        categoria.nombre_categoria = nuevo_nombre
        session.commit()
        flash('Categoría actualizada correctamente.', 'success')
    else:
        flash('No se pudo actualizar la categoría.', 'danger')

    return redirect(url_for('editar_perfil'))


@app.route('/reset_password', methods=['GET', 'POST'])
def solicitar_reset_password():
    form_solictar_reset = SolicitarResetPasswordForm()
    if form_solictar_reset.validate_on_submit():
        usuario = session.query(Usuario).filter_by(email_usuario=form_solictar_reset.email.data).first()
        if usuario:
            token = s.dumps(usuario.email_usuario, salt='password-reset-salt')
            enlace_reset = url_for('reset_password', token=token, _external=True)

            enviar_email_restablecimiento(usuario.email_usuario, enlace_reset)
            flash('Se ha enviado un enlace a tu email para restablecer la contraseña', 'info')
        else:
            flash('Este email no esta registrado', 'danger')

        return redirect(url_for('inicio'))
    return render_template('solicitar_reset_password.html', form=form_solictar_reset)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=1800)
    except:
        flash('El enlace ha expirado o ya no es valido', 'danger')
        return redirect(url_for('solicitar_reset_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        usuario = session.query(Usuario).filter_by(email_usuario=email).first()
        if usuario:
            hashed_password = bcrypt.generate_password_hash(form.password_nuevo.data).decode('utf-8')
            usuario.password_usuario = hashed_password
            session.commit()
            flash('Tu contraseña ha sido actualizada.', 'success')
            return redirect(url_for('inicio'))
    return render_template('reset_password.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('inicio'))


def guardar_imagen(imagen):
    nombre_archivo = secure_filename(imagen.filename)

    ruta_completa = os.path.join(current_app.root_path, './static/images', nombre_archivo)

    imagen.save(ruta_completa)

    return nombre_archivo


def enviar_email_restablecimiento(email, enlace_reset):
    msg = Message('Restablecimiento de contraseña',
                  sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
    msg.body = f'Con este enlace: {enlace_reset} podras restablecer tu contraseña.'
    mail.send(msg)
