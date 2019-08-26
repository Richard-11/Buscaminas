# coding=utf-8

class Celda():
    """
    Representa una celda del clásico juego Buscaminas.

    Autor: Richard Albán Fernández
    """

    __celdas_marcadas = 0

    def __init__(self):
        """
        Se inicializa el objeto celda con un estado que indica que está cerrado, sin marcar y sin mina. El número
        de minas por descubrir se inicializa a None y la lista de celdas vecinas está inicialmente vacía.
        :param fila:
        :param columna:
        """
        self.__abierta = False
        self.__marcada = False
        self.__hay_mina = False
        self.__minas_por_descubrir = None
        self.__celdas_vecinas = []

    def is_abierta(self):
        """
        Determina si la Celda está abierta o está cerrada.

        :return: True en caso de que la Celda esté abierta y False en caso de que esté cerrada
        """
        return self.__abierta

    def is_marcada(self):
        """
        Determina si una Celda está marcada o no.

        :return: True en caso de que la Celda esté maracada y False en caso contrario
        """
        return self.__marcada

    def hay_mina(self):
        """
        Determina si una Celda contiene una mina.

        :return: True en caso de que la Celda tenga una mina y False en caso contrario
        """
        return self.__hay_mina

    def poner_mina(self):
        """
        Establece que en la Celda hay una mina. Se lanza una excepción en caso de que se quiera poner una mina en una
        Celda que ya tenga mina.
        """
        if self.__hay_mina:
            raise ValueError("Esta celda ya tiene una mina.")

        self.__hay_mina = True

    def quitar_mina(self):
        """
        Establece que en la Celda no hay ninguna mina. Se lanza una excepción en caso de que se quiera quitar una mina
        en una Celda donde no hay ninguna mina.
        """
        if not self.__hay_mina:
            raise ValueError("Esta celda no tiene ninguna mina.")

        self.__hay_mina = False

    def marcar(self):
        """
        Establece que una Celda está marcada (True), si cuando se llama al método la celda no está marcada, y establece
        la Celda como no marcada (False) si cuando se llama al método la celda está marcada. Se lanza una excepción en
        caso de que se intente marca una celda que ya esté abierta.
        """
        if self.is_marcada():
            self.__marcada = False
            self.decrementa_celdas_marcadas()
        else:
            if self.is_abierta():
                raise ValueError("No se puede marcar una celda que ya está abierta.")

            self.__marcada = True
            self.incrementa_celdas_marcadas()

    def abrir(self):
        """
        Establece una Celda como abierta. Si se intenta abrir una celda que ya está abierta, se lanza una excepción.
        """
        if self.is_abierta():
            raise ValueError("No se puede abrir una celda que ya está abierta.")

        self.__abierta = True

    def get_minas_por_descubrir(self):
        """
        Devuelve el número de minas por descubrir.

        :return: número de minas por descubrir
        """
        return self.__minas_por_descubrir

    def set_minas_por_descubrir(self, minas_por_descubrir):
        """
        Establece el número de minas por descubrir de las Celda.

        :param minas_por_descubrir: número de minas a descubrir
        """
        self.__minas_por_descubrir = minas_por_descubrir

    def add_vecina(self, celda):
        """
        Añade una celda a la lista de celdas vecinas de una celda.

        :param celda: celda a añadir a la lista de celdas vecinas
        """
        self.__celdas_vecinas.append(celda)

    def get_celdas_vecinas(self):
        """
        Devuelve la cantidad de celdas vecinas que tiene una celda.

        :return: cantidad de celda vecinas de una celda
        """
        return self.__celdas_vecinas

    @classmethod
    def incrementa_celdas_marcadas(cls):
        """
        Incrementa en uno el número total de celdas marcadas.
        """
        cls.__celdas_marcadas += 1

    @classmethod
    def decrementa_celdas_marcadas(cls):
        """
        Decrementa en uno el número total de celdas marcadas.
        """
        cls.__celdas_marcadas -= 1

    @classmethod
    def get_celdas_marcadas(self):
        """
        Devuelve la cantidad de celdas que están marcadas.
        """
        return self.__celdas_marcadas

    @classmethod
    def reiniciar_celdas_marcadas(cls):
        """
        Reinicia a 0 la cantidas de celdas marcadas.
        """
        cls.__celdas_marcadas = 0