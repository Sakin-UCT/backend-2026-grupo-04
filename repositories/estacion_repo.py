from domain.estacion import Estacion, EstadoEstacion

class EstacionRepository:
    def __init__(self):
        self._estaciones = []
        self._siguiente_id = 1

    def obtener_todos(self):
        #devuelve una copia de la lista de estaciones
        return list(self._estaciones)

    def obtener_por_id(self, estacion_id):
        for estacion in self._estaciones:
            if estacion.id == estacion_id:
                return estacion
        return

    def guardar(self, codigo, ubicacion, categoria_id):
        #crea una estadion nueva y la devuelve
        nueva_estacion = Estacion(
            id=self._siguiente_id,
            codigo=codigo,
            ubicacion=ubicacion,
            categoria_id=categoria_id,
            estado=EstadoEstacion.DISPONIBLE,
        )
        self._siguiente_id += 1
        self._estaciones.append(nueva_estacion)
        return nueva_estacion

    def actualizar_estado(self, estacion_id, nuevo_estado):
        #actualiza el estado y la devuelve actualizada
        estacion = self.obtener_por_id(estacion_id)
        if estacion is None:
            return
        estacion.estado = nuevo_estado
        return estacion

estacion_repositorio = EstacionRepository()
#llamen a esto