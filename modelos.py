"""Clases del modelo (POO): herencia, encapsulación y polimorfismo en validar()."""


# Clase base: todas las entidades guardan sus datos y los validan.
# TABLA = tabla de MySQL; CAMPOS = columnas que se insertan.
class Entidad:
    TABLA = ""
    CAMPOS = ()

    def __init__(self, **datos):
        for campo in self.CAMPOS:
            setattr(self, campo, datos.get(campo))

    def validar(self):
        # Regla común: ningún campo puede estar vacío. Devuelve el mensaje de error o None.
        for campo in self.CAMPOS:
            valor = getattr(self, campo)
            if valor is None or str(valor).strip() == "":
                return f"El campo '{campo}' es obligatorio."
        return None

    def valores(self):
        # Valores en el mismo orden que CAMPOS (para el INSERT).
        return tuple(getattr(self, c) for c in self.CAMPOS)


# Propietario de una o varias motocicletas.
class Cliente(Entidad):
    TABLA = "clientes"
    CAMPOS = ("nombre", "telefono", "correo")


# Moto de un cliente. La placa se guarda en mayúsculas y es única.
class Motocicleta(Entidad):
    TABLA = "motocicletas"
    CAMPOS = ("id_cliente", "placa", "marca", "modelo", "kilometraje")

    def __init__(self, **datos):
        super().__init__(**datos)
        self.placa = (self.placa or "").strip().upper()

    def validar(self):
        error = super().validar()
        if error:
            return error
        if not str(self.kilometraje).isdigit():
            return "El kilometraje debe ser un número entero no negativo."
        return None


# Repuesto del inventario (cantidad y precio no pueden ser negativos).
class Repuesto(Entidad):
    TABLA = "repuestos"
    CAMPOS = ("nombre", "cantidad", "precio")

    def __init__(self, **datos):
        super().__init__(**datos)
        if self.precio:
            self.precio = str(self.precio).replace(",", ".")

    def validar(self):
        error = super().validar()
        if error:
            return error
        try:
            if int(self.cantidad) < 0 or float(self.precio) < 0:
                return "La cantidad y el precio deben ser positivos."
        except ValueError:
            return "Cantidad o precio inválidos."
        return None


# Orden de servicio asociada a una moto.
class OrdenServicio(Entidad):
    TABLA = "ordenes"
    CAMPOS = ("id_moto", "descripcion", "fecha", "mecanico")


# Recordatorio de mantenimiento por fecha y kilometraje.
class Recordatorio(Entidad):
    TABLA = "recordatorios"
    CAMPOS = ("id_moto", "descripcion", "fecha", "km_objetivo")
