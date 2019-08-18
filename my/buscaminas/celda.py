# coding=utf-8

class Celda():

    def __init__(self, fila, columna):
        self.__abierta = False
        self.__marcada = False
        self.__hay_mina = False
        self.__fila = fila
        self.__columna = columna

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
        self.__hay_mina = True

    def get_fila(self):
        return self.__fila

    def get_columna(self):
        return self.__columna
