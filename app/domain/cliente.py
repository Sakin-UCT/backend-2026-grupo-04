from datetime import datetime

class Cliente:
    def __init__(self, id: int, nombre: str, correo: str, fecha_registro: datetime):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.fecha_registro = fecha_registro