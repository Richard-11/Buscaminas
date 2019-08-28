# coding=utf-8

"""
Implementación del clásico juego Buscamnas con algunas modificaciones, las más importantes son:
    - Se jugará en una rejilla hexagonal, por lo que cada celda tendrá 6 vecinas en vez de las 8 del
      juego original.

    - Los números de las celdas abiertas indicarán las minas por descubrir en las celdas vecinas,
      en vez del número de minas existentes.

    - Se contará el tiempo transcurrido desde el inicio de cada partida.

    - Además de los tablero de tamaño estandar, generados al azar, será posible leer un tablero
      definido en un fichero de texto.

El objetivo de este juego es el de encontrar todas las minas escondidas en un área dividida en celdas
mediante el marcado y apertura de celdas (el marcado cuando se supone que existe mina y la apertura
cuando se supone que no existe). Como ayuda al jugador se le muestra información, en las celdas
abiertas, sobre el número de minas existentes en las celdas cerradas que la rodean (en nuestro caso el
número de minas por descubrir – descontando las ya marcadas – en las celdas vecinas).


ESTADO DE LAS CELDAS:

El estado de cada celda en un momento dado de la partida depende de 3 valores de tipo lógico: Si la
celda está abierta o cerrada, si ha sido marcada o no y si contiene o no una mina.

Al comienzo de la partida todas las celdas están cerradas y sin marcar, y contienen o no minas
dependiendo de la forma en que se ha inicializado el tablero (al azar o mediante lectura de fichero).

El carácter que se muestra en pantalla para cada celda viene dado por las siguientes reglas, donde se
define n = número de celdas vecinas con mina – número de celdas vecinas marcadas (es decir, el
número estimado de minas por descubrir en celdas vecinas):

En situación normal (ninguna celda abierta contiene mina, todas las celdas marcadas están cerradas):
    - '▓' si está cerrada y no marcada (celda sombreada)
    - 'X' si está cerrada y marcada
    - ' ' si está abierta y n = 0
    - '?' si está abierta y n < 0 (se han marcado un número excesivo de celdas vecinas)
    - El dígito que indica n si está abierta y n > 0

Al revelar el tablero (ya sea por explosión de mina o por finalización correcta) todas las celdas pasan
a estado abierto, y se pueden dar los siguientes estados adicionales:
    - '#' si está abierta, marcada, y no contiene mina (marcado erróneo)
    - '*' si está abierta, no marcada, y contiene mina (ausencia de marcado)


FORMATO DE LOS FICHEROS DE DEFINICIÓN DE TABLEROS:

Son ficheros de texto que constan de una primera línea donde se indica el número de filas y columnas
del tablero (2 enteros en el rango 1..30 separados por un espacio) a la que siguen una serie de líneas
(una por cada fila) de igual longitud (un carácter por columna) donde la presencia de una mina se
indica con el carácter asterisco (*).

Ejemplo:

2 4
*.*.
...*

El ejemplo indica el contenido de un fichero que define un tablero de 2 filas y 4
columnas con 3 minas situadas en las celdas (0,0), (0,2) y (1,3)


PETICIÓN DE LA(S) JUGADA(S):

Existen dos tipos de acciones que se pueden realizar: marcar una celda (cuando se cree que contiene
una mina) y abrir una celda (cuando se cree que no la contiene). La manera de indicar cada acción
es nombrar la celda seguida de un carácter de exclamación (!) si se desea marcar y de un carácter
asterisco (*) si se desea abrir. El usuario puede indicar más de una acción en la misma jugada, se
entiende que en ese caso se ejecutan en secuencia mientras sean acciones válidas (y no se produzca
una explosión, claro). Si se encuentra una acción no válida se muestra el mensaje de error adecuado
y el resto de acciones de la cadena se desecha.
No existe una acción específica para desmarcar una celda, simplemente si se pide marcar una celda
ya marcada se quita la marca existente (la celda sigue cerrada, por supuesto).
Si se pide abrir una celda ya abierta, se comprueba si su número de minas por descubrir 1 es menor
o igual a cero, y en ese caso se entiende que se desean abrir todas sus celdas vecinas cerradas y no
marcadas (si no es menor o igual a cero se muestra un error).

Se mostrará el estado del tablero, el número de celdas marcadas, el número de minas por descubrir y
el tiempo transcurrido y se pedirá al usuario que introduzca su jugada(s).


EVALUACIÓN DE UNA ACCIÓN VÁLIDA:

El pedir marcar una celda cambia su estado de no marcada o marcada o viceversa. Atención porque
esto cambiará el número mostrado en las celdas vecinas abiertas.

El pedir abrir una celda puede tener las siguientes consecuencias, aparte de cambiar su estado:
    - Si la celda contiene una mina, se termina la partida.

    - Si el número de minas a descubrir de la celda es menor o igual que cero entonces se
      abren recursivamente todas sus celdas vecinas no abiertas ni marcadas.


DETECCIÓN DE FIN DE PARTIDA:

Una partida termina cuando:
    - Se abre una celda que contiene una mina, ya sea por indicación directa de la acción del usuario
      o por la apertura recursiva mencionada en el apartado anterior. En ese caso se muestra un
      mensaje indicando al usuario que ha perdido la partida.

    - Cuando se cumple que hay tantas celdas marcadas como minas y que todas las celdas del
      tablero se han abierto o están marcadas. En ese caso se muestra un mensaje al usuario
      indicando que ha ganado la partida y mostrándoles el tiempo en segundos que ha tardado en
      completarla.

    En ambos caso se muestra el tablero con todas las celdas abiertas, el mensaje descrito, y se pasa al
    menú de inicio de partida.


ACTUALIZACIONES:

Versión: 1.1. Se corrige error que no permitía desmarcar celdas cuando se marcaba el número total de celdas.
Ahora, si la primera apertura se realiza sobre una mina entonces esa mina se mueve a la primera celda que no
contenga minas.


Autor: Richard Albán Fernández
"""

import random
import time
from celda import Celda

# Caracteres asociados a las acciones (! marcar, * abrir)
ACCIONES = "!*"

# Caracteres para el nombre de las filas y las columnas
NOMBRE_FILAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&"  # type: str
NOMBRE_COLUMNAS = "abcdefghijklmnopqrstuvwxyz=+-:/"  # type: str

# Asociación de caracteres y enteros
DIC_FILAS = dict(zip(NOMBRE_FILAS, range(len(NOMBRE_FILAS))))
DIC_COLUMNAS = dict(zip(NOMBRE_COLUMNAS, range(len(NOMBRE_COLUMNAS))))

# Caracteres para dibujar cuadros
COE = u'\u2500'  # ─
CNS = u'\u2502'  # │
CES = u'\u250C'  # ┌
CSO = u'\u2510'  # ┐
CNE = u'\u2514'  # └
CON = u'\u2518'  # ┘
COES = u'\u252C'  # ┬
CNES = u'\u251C'  # ├
CONS = u'\u2524'  # ┤
CONE = u'\u2534'  # ┴
CSOM = u'\u2593'  # ▒


def main():
    """
    Función principal.
    """
    while True:
        print "BUSCAMINAS"
        print "----------"
        print " 1. Principiante (9x9, 10 minas)"
        print " 2. Intermedio (16x16, 40 minas)"
        print " 3. Experto (16x30, 99 minas)"
        print " 4. Leer de fichero"
        print " 5. Salir"

        while True:
            try:
                modo = int(raw_input("\nEscoja opción: "))
                print
                break
            except ValueError:
                print "Por favor, introduzca una opción válida."

        if modo == 1:
            jugar(9, 9, 10)
        elif modo == 2:
            jugar(16, 16, 40)
        elif modo == 3:
            jugar(16, 30, 99)
        elif modo == 4:
            jugar(None, None, None, True)
        elif modo == 5:
            print "¡Hasta la próxima!"
            break
        else:
            print "Por favor, seleccione una opción válida.\n"

        print '\n'


def jugar(filas, columnas, minas, leer_fichero = False):
    """
    Realiza todas las operaciones que afectan a la partida.

    :param filas: filas que tendrá el tablero
    :param columnas: columnas que tendrá el tablero
    :param minas: minas que tendrá el tablero
    :param leer_fichero: determina si el tablero se creará aleatoriamente (False) o se leerá de fichero (True)
    """
    fin_de_partida = False
    partida_ganada = False
    tiempo_inicio = 0
    primera_apertura = True

    if leer_fichero:
        tablero, minas = leer_tablero()
    else:
        tablero = crear_tablero(filas, columnas, minas)

    calcular_minas_por_descubrir(tablero)

    if tablero:
        imprimir_tablero(tablero, minas, tiempo_inicio)
        tiempo_inicio = time.time()

        while not fin_de_partida:
            jugada = raw_input("Indique celda y acción (! marcar, * abrir): ")
            print

            # Se dividen las jugadas en una lista, en la que cada elemento es una jugada distinta
            jugada = dividir_en_subjugadas(jugada)

            for i in range(len(jugada)):
                jugada_valida = validar_jugada(jugada[i], tablero, minas)

                if not jugada_valida:
                    break

                hacer_jugada(jugada[i], tablero, primera_apertura)
                calcular_minas_por_descubrir(tablero)

                if ACCIONES[1] in jugada[i]:
                    primera_apertura = False

                fin_de_partida, partida_ganada = detectar_fin_de_partida(tablero, minas)

                if fin_de_partida:
                    abrir_celdas(tablero)
                    break

            tiempo_fin = time.time()
            tiempo = tiempo_fin - tiempo_inicio

            if fin_de_partida:
                if partida_ganada:
                    imprimir_tablero(tablero, minas, tiempo)
                    print "¡HAS GANADO LA PARTIDA! TIEMPO: "

                else:
                    imprimir_tablero(tablero, minas, tiempo)
                    print "GAME OVER"

                break

            imprimir_tablero(tablero, minas, tiempo)

    Celda.reiniciar_celdas_marcadas()


def crear_tablero(filas, columnas, minas):
    """
    Se crea un tablero a partir del número de filas, el número de columnas y el número de filas.

    :param filas: número de filas que tiene el tablero
    :param columnas: número de columnas que tiene el tablero
    :param minas: número de minas que tiene el tablero
    :return: el tablero con las dimensiones y minas adecuadas
    """
    tablero = []

    # Se rellena el tablero con objetos de la clase Celda
    for i in range(filas):
        componentes_fila = []
        for j in range(columnas):
            componentes_fila.append(Celda())

        tablero.append(componentes_fila)

    # Una vez el tablero está relleno de objeto Celda, lo rellenamos con las minas adecuadas según el modo de juego
    while minas != 0:
        i = random.randint(0, filas - 1)
        j = random.randint(0, columnas - 1)

        if not tablero[i][j].hay_mina():
            tablero[i][j].poner_mina()
            minas -= 1

    return tablero


def calcular_minas_por_descubrir(tablero):
    """
    Se calcula el número de minas por descubrir que tiene cada una de las celdas. Además, se añaden las celdas vecinas
    de cada Celda en una lista que tiene cada objeto de este tipo.

    :param tablero: tablero en el que se calcula el número de minas por descubrir de cada celda
    """
    celdas_vecinas_con_mina = 0
    celdas_vecinas_marcadas = 0

    for i in range(len(tablero)):
        for j in range(len(tablero[0])):

            # Parte superior
            if i == 0:
                if j == 0:
                    if tablero[i][j + 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i][j + 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i + 1][j].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i + 1][j].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i + 1][j + 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i + 1][j + 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if not tablero[i][j].get_celdas_vecinas():
                        tablero[i][j].add_vecina(tablero[i][j + 1])
                        tablero[i][j].add_vecina(tablero[i + 1][j])
                        tablero[i][j].add_vecina(tablero[i + 1][j + 1])

                elif j == len(tablero[0]) - 1:
                    if tablero[i][j - 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i][j - 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i + 1][j].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i + 1][j].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i + 1][j - 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i + 1][j - 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if not tablero[i][j].get_celdas_vecinas():
                        tablero[i][j].add_vecina(tablero[i][j - 1])
                        tablero[i][j].add_vecina(tablero[i + 1][j])
                        tablero[i][j].add_vecina(tablero[i + 1][j - 1])

                else:
                    if tablero[i][j - 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i][j - 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i][j + 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i][j + 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i + 1][j].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i + 1][j].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i + 1][j + 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i + 1][j + 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if not tablero[i][j].get_celdas_vecinas():
                        tablero[i][j].add_vecina(tablero[i][j - 1])
                        tablero[i][j].add_vecina(tablero[i][j + 1])
                        tablero[i][j].add_vecina(tablero[i + 1][j])
                        tablero[i][j].add_vecina(tablero[i + 1][j + 1])

            # Parte inferior
            elif i == len(tablero) - 1:
                if i % 2 == 0:
                    if j == 0:
                        if tablero[i][j + 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j + 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j + 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j + 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if not tablero[i][j].get_celdas_vecinas():
                            tablero[i][j].add_vecina(tablero[i][j + 1])
                            tablero[i][j].add_vecina(tablero[i - 1][j])
                            tablero[i][j].add_vecina(tablero[i - 1][j + 1])

                    elif j == len(tablero[0]) - 1:
                        if tablero[i][j - 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j - 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if not tablero[i][j].get_celdas_vecinas():
                            tablero[i][j].add_vecina(tablero[i][j - 1])
                            tablero[i][j].add_vecina(tablero[i - 1][j])

                    else:
                        if tablero[i][j - 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j - 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i][j + 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j + 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j + 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j + 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if not tablero[i][j].get_celdas_vecinas():
                            tablero[i][j].add_vecina(tablero[i][j - 1])
                            tablero[i][j].add_vecina(tablero[i][j + 1])
                            tablero[i][j].add_vecina(tablero[i - 1][j])
                            tablero[i][j].add_vecina(tablero[i - 1][j + 1])

                else:
                    if j == 0:
                        if tablero[i][j + 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j + 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if not tablero[i][j].get_celdas_vecinas():
                            tablero[i][j].add_vecina(tablero[i][j + 1])
                            tablero[i][j].add_vecina(tablero[i - 1][j])

                    elif j == len(tablero[0]) - 1:
                        if tablero[i][j - 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j - 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j - 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j - 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if not tablero[i][j].get_celdas_vecinas():
                            tablero[i][j].add_vecina(tablero[i][j - 1])
                            tablero[i][j].add_vecina(tablero[i - 1][j])
                            tablero[i][j].add_vecina(tablero[i - 1][j - 1])

                    else:
                        if tablero[i][j - 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j - 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i][j + 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j + 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j - 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j - 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if not tablero[i][j].get_celdas_vecinas():
                            tablero[i][j].add_vecina(tablero[i][j - 1])
                            tablero[i][j].add_vecina(tablero[i][j + 1])
                            tablero[i][j].add_vecina(tablero[i - 1][j - 1])
                            tablero[i][j].add_vecina(tablero[i - 1][j])

            # Lateral izquierdo
            elif j == 0:
                if i != 0 and i != len(tablero) - 1:
                    if i % 2 == 0:
                        if tablero[i - 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j + 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j + 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i][j + 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j + 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i + 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i + 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i + 1][j + 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i + 1][j + 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if not tablero[i][j].get_celdas_vecinas():
                            tablero[i][j].add_vecina(tablero[i - 1][j])
                            tablero[i][j].add_vecina(tablero[i - 1][j + 1])
                            tablero[i][j].add_vecina(tablero[i][j + 1])
                            tablero[i][j].add_vecina(tablero[i + 1][j])
                            tablero[i][j].add_vecina(tablero[i + 1][j + 1])

                    else:
                        if tablero[i][j + 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j + 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i + 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i + 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if not tablero[i][j].get_celdas_vecinas():
                            tablero[i][j].add_vecina(tablero[i][j + 1])
                            tablero[i][j].add_vecina(tablero[i - 1][j])
                            tablero[i][j].add_vecina(tablero[i + 1][j])

            # Lateral derecho
            elif j == len(tablero[0]) - 1:
                if i != 0 and i != len(tablero) - 1:
                    if i % 2 == 0:
                        if tablero[i][j - 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j - 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i + 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i + 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if not tablero[i][j].get_celdas_vecinas():
                            tablero[i][j].add_vecina(tablero[i][j - 1])
                            tablero[i][j].add_vecina(tablero[i - 1][j])
                            tablero[i][j].add_vecina(tablero[i + 1][j])

                    else:
                        if tablero[i - 1][j - 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j - 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i - 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i - 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i][j - 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i][j - 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i + 1][j - 1].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i + 1][j - 1].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if tablero[i + 1][j].hay_mina():
                            celdas_vecinas_con_mina += 1
                        if tablero[i + 1][j].is_marcada():
                            celdas_vecinas_marcadas += 1

                        if not tablero[i][j].get_celdas_vecinas():
                            tablero[i][j].add_vecina(tablero[i - 1][j - 1])
                            tablero[i][j].add_vecina(tablero[i - 1][j])
                            tablero[i][j].add_vecina(tablero[i][j - 1])
                            tablero[i][j].add_vecina(tablero[i + 1][j - 1])
                            tablero[i][j].add_vecina(tablero[i + 1][j])

            # Interior
            else:
                if i % 2 == 0:
                    if tablero[i - 1][j].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i - 1][j].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i - 1][j + 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i - 1][j + 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i][j - 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i][j - 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i][j + 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i][j + 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i + 1][j].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i + 1][j].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i + 1][j + 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i + 1][j + 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if not tablero[i][j].get_celdas_vecinas():
                        tablero[i][j].add_vecina(tablero[i - 1][j])
                        tablero[i][j].add_vecina(tablero[i - 1][j + 1])
                        tablero[i][j].add_vecina(tablero[i][j - 1])
                        tablero[i][j].add_vecina(tablero[i][j + 1])
                        tablero[i][j].add_vecina(tablero[i + 1][j])
                        tablero[i][j].add_vecina(tablero[i + 1][j + 1])

                else:
                    if tablero[i - 1][j - 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i - 1][j - 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i - 1][j].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i - 1][j].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i][j - 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i][j - 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i][j + 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i][j + 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i + 1][j - 1].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i + 1][j - 1].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if tablero[i + 1][j].hay_mina():
                        celdas_vecinas_con_mina += 1
                    if tablero[i + 1][j].is_marcada():
                        celdas_vecinas_marcadas += 1

                    if not tablero[i][j].get_celdas_vecinas():
                        tablero[i][j].add_vecina(tablero[i - 1][j - 1])
                        tablero[i][j].add_vecina(tablero[i - 1][j])
                        tablero[i][j].add_vecina(tablero[i][j - 1])
                        tablero[i][j].add_vecina(tablero[i][j + 1])
                        tablero[i][j].add_vecina(tablero[i + 1][j - 1])
                        tablero[i][j].add_vecina(tablero[i + 1][j])

            minas_por_descubrir = celdas_vecinas_con_mina - celdas_vecinas_marcadas

            tablero[i][j].set_minas_por_descubrir(minas_por_descubrir)

            celdas_vecinas_con_mina = 0
            celdas_vecinas_marcadas = 0


def imprimir_tablero(tablero, minas, tiempo):
    """
    Imprime el tablero que se pasa como parámetro.

    :param tablero: tablero a imprimir
    """
    print "MINAS RESTANTES: %2d | MARCADAS: %2d | TIEMPO: %.1f" % (minas, Celda.get_celdas_marcadas(), tiempo)
    print "    ",

    for i in range(len(tablero[0])):
        print NOMBRE_COLUMNAS[i], " ",
    print

    # Primer bloque de caracteres unicode
    print "   ", CES + COE*3 + (COES + COE*3)*(len(tablero[0]) - 1) + CSO

    # Bloque de caracteres unicode del interior
    for i in range(len(tablero)):
        if i % 2 == 0:
            tab = "  "
        else:
            tab = ""

        print NOMBRE_FILAS[i] + tab,

        for j in range(len(tablero[0])):
            if j == 0:
                print CNS,

            print get_caracter_a_imprimir(tablero[i][j]) + " " + CNS,

            if j == len(tablero[0]) - 1:
                print

        if i % 2 == 0:
            if i != len(tablero) - 1:
                print "  " + CES + COE + CONE + COE + COES + \
                      (COE + CONE + COE + COES)*(len(tablero[0]) - 1) + \
                      COE + CON
        else:
            if i != len(tablero) - 1:
                print "  " + CNE + COE + COES + COE + CONE + \
                      (COE + COES + COE + CONE)*(len(tablero[0]) - 1) +\
                      COE + CSO

        # Último bloque de caracteres unicode
        if i == len(tablero) - 1:
            if i % 2 == 0:
                print "    " + CNE + COE*3 + (CONE + COE*3)*(len(tablero[0]) - 1) + CON
            else:
                print "  " + CNE + COE*3 + (CONE + COE*3)*(len(tablero[0]) - 1) + CON

    print


def get_caracter_a_imprimir(celda):
    """
    Devuelve el caracter a imprimir teniendo en cuenta el estado de las celdas, tal y como se especifica en el
    enunciado.

    :param celda: celda en la que se evalúa el estado
    :return: caracter a imprimir según el estado de la celda
    """
    caracter = ""

    if not celda.is_abierta() and not celda.is_marcada():
        caracter = CSOM
    elif not celda.is_abierta() and celda.is_marcada():
        caracter = "X"
    elif celda.is_abierta() and celda.get_minas_por_descubrir() == 0:
        caracter = " "
    elif celda.is_abierta() and celda.get_minas_por_descubrir() < 0:
        caracter = "?"
    elif celda.is_abierta() and celda.get_minas_por_descubrir() > 0:
        caracter = str(celda.get_minas_por_descubrir())

    if celda.is_abierta() and celda.is_marcada() and not celda.hay_mina():
        caracter = "#"
    elif celda.is_abierta() and not celda.is_marcada() and celda.hay_mina():
        caracter = "*"

    return caracter

def leer_tablero():
    """
    Devuelve un tablero creado a partir de la lectura de un fichero y el número de minas que tiene el tablero.

    :return: tablero implementado según el contenido del fichero y número de minas que contiene
    """
    nombre_fichero = raw_input("Introduce el nombre del fichero: ")
    tablero = []
    minas = 0

    print

    try:
        fich = open(nombre_fichero, "r")

        lineas_ficheros = fich.readlines()

        fich.close()

        filas, columnas = lineas_ficheros[0].split()

        lineas_ficheros.pop(0)

        for i in range(int(filas)):
            componentes_filas = []
            for j in range(int(columnas)):
                celda = Celda()
                if lineas_ficheros[i][j] == "*":
                    celda.poner_mina()
                    componentes_filas.append(celda)
                    minas += 1
                elif lineas_ficheros[i][j] == ".":
                    componentes_filas.append(celda)

            tablero.append(componentes_filas)

    except IOError:
        print 'No se ha encontrado ningún fichero con el nombre "' + nombre_fichero + '".'
    except:
        print "El fichero no cumple con el formato adecuado para la definición del tablero."

    return tablero, minas


def dividir_en_subjugadas(jugada):
    """
    Devuelve la lista resultante de dividir la cadena jugada que se pasa como parámetro, en bloques de jugadas
    independientes.

    :return: lista de jugadas
    """
    lista_jugadas = []
    cadena_jugada = ""

    # Dividimos las cadena jugada en bloques de 3 caracteres
    for i in range(len(jugada)):
        cadena_jugada += jugada[i]

        if len(cadena_jugada) == 3:
            lista_jugadas.append(cadena_jugada)
            cadena_jugada = ""

    jugada = list(jugada)

    # Borramos de la lista jugada todos los bloques de 3 caracteres que ya se han añadido a lista_jugadas
    for i in range(len(lista_jugadas)):
        jugada.pop(0)
        jugada.pop(0)
        jugada.pop(0)

    # En caso de que sigan existiendo elementos en la lista jugada, se añaden a la lista lista_jugdas
    if jugada:
        lista_jugadas.append("".join(jugada))

    return lista_jugadas


def validar_jugada(jugada, tablero, minas):
    """
    Determina si una jugada es válida o no, teniendo en cuenta las condiciones del enunciado.

    :param jugada: jugada a validar
    :param tablero: tablero en el que se comprobará si la jugada es válida
    :param minas: minas que tiene el tablero
    :return: True si la jugada es válida y False en caso de que no lo sea
    """
    if len(jugada) < 3 or jugada[0] not in NOMBRE_FILAS[:len(tablero)] or jugada[1] not in NOMBRE_COLUMNAS[:len(tablero[0])] or jugada[2] not in ACCIONES:
        print "ENTRADA ERRONEA\n"
        return False

    fila = DIC_FILAS.get(jugada[0])
    columna = DIC_COLUMNAS.get(jugada[1])
    accion = jugada[2]

    if accion == ACCIONES[0]:
        if not tablero[fila][columna].is_marcada():
            if Celda.get_celdas_marcadas() + 1 > minas:
                print "NO SE PUEDEN MARCAR MAS CELDAS QUE MINAS\n"
                return False

            if tablero[fila][columna].is_abierta():
                print "NO SE PUEDE MARCAR UNA CELDA ABIERTA\n"
                return False

    if accion == ACCIONES[1]:
        if tablero[fila][columna].is_marcada():
            print "NO SE PUEDE ABRIR UNA CELDA MARCADA\n"
            return False

        if tablero[fila][columna].is_abierta() and tablero[fila][columna].get_minas_por_descubrir() > 0:
            print "CELDA YA ABIERTA. NO SE PUEDEN ABRIR LAS CELDAS VECINAS POR NUMERO INSUFICIENTE DE MARCAS\n"
            return False

    return True


def hacer_jugada(jugada, tablero, primera_apertura):
    """
    Se realiza la jugada que se pasa como parámetro en el tablero que también se pasa como parámetro.

    :param jugada: jugada a realizar
    :param tablero: tablero donde se hará la jugada
    """
    fila = DIC_FILAS.get(jugada[0])
    columna = DIC_COLUMNAS.get(jugada[1])
    accion = jugada[2]

    if accion == "!":
        tablero[fila][columna].marcar()

    elif accion == "*":
        if tablero[fila][columna].is_abierta() and tablero[fila][columna].get_minas_por_descubrir() <= 0:
            abrir_recursivamente(tablero[fila][columna])
        else:
            if tablero[fila][columna].hay_mina() and primera_apertura:
                mover_mina_a_primera_posicion_sin_minas(tablero[fila][columna], tablero)

            tablero[fila][columna].abrir()


def abrir_recursivamente(celda):
    """
    Abre de forma recusiva las celdas vecinas de una celda en concreto que se pasa como parámetro si la celda vecina
    no está abierta ni marcada.

    :param celda: celda de la que se quieren abrir las celdas vecinas
    """
    if not celda.get_celdas_vecinas():
        return
    else:
        celda_vecina = celda.get_celdas_vecinas().pop()

        if not celda_vecina.is_abierta() and not celda_vecina.is_marcada():
            celda_vecina.abrir()

        abrir_recursivamente(celda_vecina)


def detectar_fin_de_partida(tablero, minas):
    """
    Determina si una partida ha llegado a su fin, y además si la partida se ha ganado o se ha perdido, según las
    condiciones que se detallan en el enunciado.

    :param tablero: tablero a detectar el fin de partida
    :param minas: minas que contiene el tablero
    :return: una tupla en la que el primer elemento determina si se ha detectado el final de la partida (True si se
    detecta y False en caso contrario), y el segundo indica si se ha ganado (True) o si se ha perdido (False)
    """
    todas_abiertas_o_marcadas = True
    fin_de_partida = False
    partida_ganada = False

    for i in range(len(tablero)):
        for j in range(len(tablero[0])):
            if tablero[i][j].hay_mina() and tablero[i][j].is_abierta():
                fin_de_partida = True

            if not tablero[i][j].is_marcada():
                if not tablero[i][j].is_abierta():
                    todas_abiertas_o_marcadas = False

    if Celda.get_celdas_marcadas() == minas and todas_abiertas_o_marcadas:
        partida_ganada = True
        fin_de_partida = True

    return fin_de_partida, partida_ganada


def abrir_celdas(tablero):
    """
    Abre todas las celdas de tablero.

    :param tablero: tablero del que se abren las celdas
    """
    for i in range(len(tablero)):
        for j in range(len(tablero[0])):
            if not tablero[i][j].is_abierta():
                tablero[i][j].abrir()


def mover_mina_a_primera_posicion_sin_minas(celda, tablero):
    """
    Mueve la mina que se pasa como parámetro a la primera celda que no contenga minas.

    :param celda: celda a mover
    :param tablero: tablero en el que se va a mover la celda
    """
    for i in range(len(tablero)):
        for j in range(len(tablero[0])):
            if not tablero[i][j].hay_mina():
                celda.quitar_mina()
                tablero[i][j].poner_mina()
                return


if __name__ == '__main__':
    main()