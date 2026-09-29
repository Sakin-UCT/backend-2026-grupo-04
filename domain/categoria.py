class CategoriaEstacion:
    def __init__(self, id: int, nombre: str, tarifa_hora: float, descripcion: str = None):
        self.id = id
        self.nombre = nombre
        self.tarifa_hora = tarifa_hora
        self.descripcion = descripcion