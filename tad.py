"""TAD Cola (FIFO) implementado con nodos enlazados."""


# Nodo de la lista enlazada: guarda un dato y apunta al siguiente nodo.
class _Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ColaFIFO:
    """Primero en entrar, primero en ser atendido."""

    def __init__(self):
        self._frente = None
        self._final = None
        self._tamano = 0

    def encolar(self, dato):
        # Agrega un elemento al FINAL de la cola.
        nodo = _Nodo(dato)
        if self._final:
            self._final.siguiente = nodo
        else:
            self._frente = nodo
        self._final = nodo
        self._tamano += 1

    def desencolar(self):
        # Quita y devuelve el elemento del FRENTE (None si la cola está vacía).
        if self.esta_vacia():
            return None
        dato = self._frente.dato
        self._frente = self._frente.siguiente
        if self._frente is None:
            self._final = None
        self._tamano -= 1
        return dato

    def frente(self):
        # Consulta el primer elemento sin sacarlo.
        return None if self.esta_vacia() else self._frente.dato

    def esta_vacia(self):
        # True si no hay elementos.
        return self._tamano == 0

    def tamano(self):
        # Cantidad de elementos en la cola.
        return self._tamano

    def elementos(self):
        # Recorre los nodos de frente a final y devuelve los datos en una lista.
        salida, nodo = [], self._frente
        while nodo:
            salida.append(nodo.dato)
            nodo = nodo.siguiente
        return salida
