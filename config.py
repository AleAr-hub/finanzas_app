import os


class Config:
    '''
    Esta clase contiene una variable de entorno para asignar una SECRET KEY
    que se utiliza para gestionar sesiones, firmar cookies y otros mecanismos de seguridad.

    Para ejecutar el servidor SMTP en consola hay que ejecutar el siguiente comando:
    python3 -m smtpd -c DebuggingServer -n localhost:1025

    '''
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or '944e9176671338f4b6c909a1a2276e87'  # Este codigo hexadecimal ha sido generado con la libreria de python secrets
    MAIL_SERVER = 'localhost' # Servidor local
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'noreply@demo.com' # Remitente generico