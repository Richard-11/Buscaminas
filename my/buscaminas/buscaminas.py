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


EVALUACIÓN DE UNA ACCIÓN VÁLIDA

El pedir marcar una celda cambia su estado de no marcada o marcada o viceversa. Atención porque
esto cambiará el número mostrado en las celdas vecinas abiertas.

El pedir abrir una celda puede tener las siguientes consecuencias, aparte de cambiar su estado:
    - Si la celda contiene una mina, se termina la partida.

    - Si el número de minas a descubrir de la celda es menor o igual que cero entonces se
      abren recursivamente todas sus celdas vecinas no abiertas ni marcadas.


DETECCIÓN DE FIN DE PARTIDA

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

"""

from celda import Celda
import random

# Caracteres para el nombre de las filas y las columnas
NOMBRE_FILAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&"
NOMBRE_COLUMNAS = "abcdefghijklmnopqrstuvwxyz=+-:/"

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


def jugar(filas, columnas, minas):
    tablero = crear_tablero(filas, columnas, minas)
    imprimir_tablero(tablero)


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
            componentes_fila.append(Celda(i, j))

        tablero.append(componentes_fila)

    # Una vez el tablero está relleno de objeto Celda, lo rellenamos con las minas adecuadas según el modo de juego
    while minas != 0:
        i = random.randint(0, filas - 1)
        j = random.randint(0, columnas - 1)

        if not tablero[i][j].hay_mina():
            tablero[i][j].poner_mina()
            minas = minas - 1

    return tablero


def imprimir_tablero(tablero):
    """
    Imprime el tablero que se pasa como parámetro.

    :param tablero: tablero a imprimir
    """
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
            print CSOM + " " + CNS,

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


def leer_fichero():
    return None, None, None


# main
while True:
    print "BUSCAMINAS"
    print "----------"
    print " 1. Principiante (9x9, 10 minas)"
    print " 2. Intermedio (16x16, 40 minas)"
    print " 3. Experto (16x30, 99 minas)"
    print " 4. Leer de fichero"
    print " 5. Salir"

    modo = int(raw_input("\nEscoja opción: "))

    if modo == 1:
        jugar(9, 9, 10)
    elif modo == 2:
        jugar(16, 16, 40)
    elif modo == 3:
        jugar(16, 30, 99)
    elif modo == 4:
        filas, columnas, minas = leer_fichero()
        jugar(filas, columnas, minas)
    elif modo == 5:
        print "¡Hasta la próxima!"
        break
    else:
        print "Por favor, seleccione una opción válida.\n"

    print '\n'
