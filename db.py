import os
import mysql.connector


class BaseDatos:
    """Acceso a MySQL/MariaDB de XAMPP (config por variables de entorno)."""

    def __init__(self):
        # Parámetros de conexión; se pueden cambiar con variables de entorno
        # (DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME).
        self.cfg = dict(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "motocontrol"),
        )

    def _correr(self, sql, params, consulta):
        # Abre una conexión, ejecuta la sentencia y la cierra siempre.
        # Si es consulta devuelve las filas; si no, confirma (commit) y devuelve el id nuevo.
        con = mysql.connector.connect(**self.cfg)
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(sql, params)
            if consulta:
                return cur.fetchall()
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def consultar(self, sql, params=()):
        # SELECT que devuelve una lista de diccionarios.
        return self._correr(sql, params, True)

    def uno(self, sql, params=()):
        # SELECT que devuelve solo la primera fila (o None).
        filas = self.consultar(sql, params)
        return filas[0] if filas else None

    def ejecutar(self, sql, params=()):
        # INSERT / UPDATE / DELETE.
        return self._correr(sql, params, False)

    def insertar(self, entidad):
        # Inserta cualquier Entidad usando su TABLA y sus CAMPOS (consulta parametrizada).
        cols = ", ".join(entidad.CAMPOS)
        marcas = ", ".join(["%s"] * len(entidad.CAMPOS))
        return self.ejecutar(
            f"INSERT INTO {entidad.TABLA} ({cols}) VALUES ({marcas})",
            entidad.valores())
