#!/usr/bin/env python3  
#----------------------------------------------------------------------------
# Author      : Joaquin Cibeira
# Created Date: 05/11/2022
# version ='1.0'
# ---------------------------------------------------------------------------
""" Este script permite obtener los datos de fabricacion de un cablemodem con su direccion IP 
    a travez del protocolo SNMP """  
# ---------------------------------------------------------------------------
import re
import os
import sys
from pysnmp import hlapi
from queries import create, insert, db_connect, db_insert
from XmlHandler import XmlHandler as XH
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
#Funciones  SNMP
# ---------------------------------------------------------------------------
def get(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types(oids)
    )
    return fetch(handler, 1)[0]

def construct_object_types(list_of_oids):
        object_types = []
        for oid in list_of_oids:
            object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
        return object_types

def fetch(handler, count):
        result = []
        for i in range(count):
            try:
                error_indication, error_status, error_index, var_binds = next(handler)
                if not error_indication and not error_status:
                    items = {}
                    for var_bind in var_binds:
                        items[str(var_bind[0])] = cast(var_bind[1])
                    result.append(items)
                else:
                    print('Error de respuesta, puede que no exista un CM en esta IP')
                    sys.exit()
            except StopIteration:
                break
        return result

def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value

# ---------------------------------------------------------------------------
#Funciones de procesamiento de strings
# ---------------------------------------------------------------------------
def extract_data(s):
    lista = [x.split(':') for x in s.split(';')[1:]]
    d = {x[0].strip():re.findall(r'[a-zA-Z0-9_.-]+',x[1])[0] for x in lista}
    return d


ipv4_rule = r'\b(?:\d{1,3}\.){3}\d{1,3}\b' # formato IPv4 255.255.255.255
oid = '1.3.6.1.2.1.1.1.0'
def main():

    #En caso de no existir las variables de ambiente para las credenciales, son creadas
    if 'DB_USER' not in os.environ.keys():
        os.environ['DB_USER'] = input('por favor ingrese el usuario de la base de datos: ')
    if 'DB_PASSWORD' not in os.environ.keys():
        os.environ['DB_PASSWORD'] = input('por favor ingrese la password de la base de datos: ')

    #Conexion con la base de datos
    db = db_connect('localhost', os.environ['DB_USER'], os.environ['DB_PASSWORD'])
    cursor = db.cursor()
    cursor.execute(create)

    try:
        ip, mode = sys.argv[1:]
    except:
        print('Por favor ingrese IP y modo separados por un espacio \n ej: "255.255.255.255 1.3.6.1.2.1.1.1.0 db"')    
        sys.exit()

    if not re.search(ipv4_rule,ip):
        print('la IP debe ser una direccion IPv4 \n ej: "255.255.255.255"')    
    
    mib = get(ip, [oid], hlapi.CommunityData('private'))
    data = extract_data(mib[f'{oid}'])
    data = {key:value for (key,value) in data.items() if key in ['VENDOR','MODEL','SW_REV']}

    if mode == 'db':                    #modo de operacion por base de datos                
        if db_insert(cursor,data):
            db.commit()
            print('CM listado exitosamente en la base de datos')
        else:
            db.rollback()
    elif mode == 'file':                #modo de operacion por archivo           
        x = XH('cm_models.xml')
        if not x.search_file(data):
            x.file_append(data)
    elif mode == 'both':                #modo de operacion por base de datos y archivo
        if db_insert(cursor,data):
            x = XH('cm_models.xml')
            if not x.search_file(data):
                x.file_append(data)
                db.commit()
                print('CM listado exitosamente en la base de datos')
            else:
                db.rollback()
    else:
        print('Modo incorrecto, los modos correctos son [db|file|both]')
    
    cursor.close()
    db.close()

if __name__ == '__main__':
    main()
    

