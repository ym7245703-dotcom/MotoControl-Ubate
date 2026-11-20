"""Crea la base de datos 'motocontrol' en XAMPP y las tablas."""
import os
import mysql.connector

con = mysql.connector.connect(host=os.getenv("DB_HOST", "localhost"),
                              port=int(os.getenv("DB_PORT", "3306")),
                              user=os.getenv("DB_USER", "root"),
                              password=os.getenv("DB_PASS", ""))
cur = con.cursor()
with open("schema.sql", encoding="utf-8") as f:
    for sentencia in f.read().split(";"):
        if sentencia.strip():
            cur.execute(sentencia)
con.commit()
con.close()
print("Base de datos 'motocontrol' lista.")
