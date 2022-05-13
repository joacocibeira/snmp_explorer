import mysql.connector as mariadb


# ---------------------------------------------------------------------------
#queries predeterminadas
# ---------------------------------------------------------------------------
create = """ CREATE TABLE IF NOT EXISTS cm_models(
             vendor VARCHAR(255)  NOT NULL,
             model  VARCHAR(255)  NOT NULL,
             softversion VARCHAR(255) NOT NULL,
             PRIMARY KEY (vendor,model,softversion)
)
"""

insert = """INSERT INTO my_database.cm_models (vendor, model, softversion) VALUES ('{0}','{1}','{2}')"""


# ---------------------------------------------------------------------------
#conexion a la base de datos
# ---------------------------------------------------------------------------
def db_connect(host_name, user_name, user_password):
    try:
        connection = mariadb.connect(host = host_name,
                                     database='my_database',
                                     user=user_name,
                                     password=user_password
                                    )
    except Exception as e:
        print(f'Error al conectar a la base de datos: \n {e}')
        raise SystemExit

    return connection

# ---------------------------------------------------------------------------
#insert de una nueva entrada
# ---------------------------------------------------------------------------
def db_insert(cursor,data):
    try:
        cursor.execute(insert.format(data['VENDOR'],data['MODEL'],data['SW_REV']))
        return True
    except Exception as e:
        if e.errno == 1062:
            print('Este CM ya esta listado en el inventario de la base de datos, no se permiten entradas duplciadas')
        else:
            print(f'Error al insertar en la tabal: \n {e}')
        return False      
