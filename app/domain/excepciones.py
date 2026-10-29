
class DominioError(Exception):
    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)

class RecursoNoEncontradoError(DominioError):
    #recurso no encontrado 
    pass

class ReglaNegocioError(DominioError):
    #violacion de reglas de negocio
    pass

class ConflictoError(DominioError):
    #violacion de regla duplicidad
    pass
