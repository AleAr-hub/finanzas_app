from app import app
from app.db import Base, engine


if __name__ == '__main__':
    Base.metadata.drop_all(bind=engine)  # Esta linea borra el contenido de la base de datos
    Base.metadata.create_all(bind=engine)  # Creacion de la base de datos
    app.run(
        debug=True)  # El debug=True hace que cada vez que reiniciemos el servidor o modifiquemos codigo, el servidor de Flask se reinicie solo
