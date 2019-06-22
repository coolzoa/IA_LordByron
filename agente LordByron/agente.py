import speech_recognition as sr
import pyttsx3
import tkinter as tk
from tkinter import *
import threading
import time
from sys import platform
import os
import random

activo = True


        
comandos = ["largo", "alto", "tamaño",\
            "ayuda", "salir", "crear", \
            "mostrar", "mover", "poner",\
            "quitar", "limpiar"]


class Nodo(object):
    posActual = list()
    posPrevia = list()
    costo = 0
    

class Cuadricula(object):
    alto = 0
    largo = 0
    tamano = 0
    
    matriz = list()

    openList = list()
    closedList = list()

    inicio = (0, 0)
    final = (0, 0)
    
    diagonales = False
    creado = False
    solucionado = False

    porcentajeBloqueos = 25
    

    def crearLista(self, n):
        lista = list()
        while (n != 0):
            lista.append(0)
            n = n - 1
        return lista

    def crearMatriz(self, filas, columnas):
        matriz = self.crearLista(filas)
        for i in range(filas):
            matriz[i] = self.crearLista(columnas)
        return matriz

    def iniciarCuadricula(self):
        self.openList.clear()
        self.closedList.clear()
        app.limpiarTodo()

        self.matriz = self.crearMatriz(self.alto, self.largo)
        for i in range(0, self.alto):
            for j in range(0, self.largo):
                if (random.randint(0, 100) < self.porcentajeBloqueos):
                    self.matriz[i][j] = 1
                    obsId = "obstaculo" + str(i) + str(j)
                    app.ponerPieza(obsId, i, j)
        

        xInicio = cuadricula.largo // 2
        yInicio = cuadricula.alto // 2
        
        self.matriz[yInicio][xInicio] = 0
        self.inicio = [yInicio, xInicio]

        app.ponerPieza("inicio", yInicio, xInicio)

        xFin = random.randint(0, cuadricula.largo - 1)
        yFin = random.randint(0, cuadricula.alto - 1)
        
        while ((yFin, xFin) == (yInicio, xInicio)):
            xFin = random.randint(0, cuadricula.largo - 1)
            yFin = random.randint(0, cuadricula.alto - 1)
            
        self.final = [yFin, xFin]
        self.matriz[yFin][xFin] = 0
        app.ponerPieza("fin", yFin, xFin)
        app.actualizar()
        self.creado = True

    def findIndex(self, lista, ele):
        largo = len(lista)
            
        for i in range(largo):
            if (type(ele) != list and type(ele) != tuple):

                if (lista[i].posActual[0] == ele.posActual[0] and \
                   lista[i].posActual[1] == ele.posActual[1]):
                    return i
            else:
                if (lista[i].posActual[0] == ele[0] and \
                    lista[i].posActual[1] == ele[1]):
                    return i
        return -1
                
    def manhattan(self):
        self.openList.clear()
        self.closedList.clear()

        #se agrega el nodo inicial a openList
        nodo = Nodo()
        
        nodo.posActual = self.inicio
        nodo.posPrevia = self.inicio
        nodo.costo = 0
        
        self.openList.append(nodo)

        while (len(self.openList) != 0):
            #obtengo nodo menor de openList, se elimina y agrega a closedList
            nodoActual = self.getCostoMenor(self.openList)
            
            self.openList.remove(nodoActual)
            self.closedList.append(nodoActual)

            if (self.tienePosFinal(self.closedList)):
                self.solucionado = True
                return True
            
            adyacentes = self.getAdyacentes(nodoActual.posActual, nodoActual.costo)
            for item in adyacentes:
                index = self.findIndex(self.closedList, item)
                if (index >= 0):
                    continue
                index = self.findIndex(self.openList, item)

                if (index == -1):
                    self.openList.append(item)
                else:
                    indice = self.findIndex(self.openList, item)
                    nodoAntiguo = self.openList[indice]
                    if (nodoAntiguo.costo < item.costo):
                        self.openList.remove(nodoAntiguo)
                        self.openList.append(item)
        self.solucionado = False
        return False

    def getAdyacentes(self, posActual, costo):
        largo = [-1, 0, 1]
        alto = [-1, 0, 1]
        listaSalida = list()
        for x in largo:
            for y in alto:
                if (self.diagonales):
                    if ((x != 0 or y != 0) and (self.dentroLimites(posActual, x, y))):
                        try:
                            if (self.matriz[posActual[0] + y][posActual[1] + x] == 0):
                                nodo = Nodo()
                                nodo.posActual = (posActual[0] + y, posActual[1] + x)
                                nodo.posPrevia = posActual
                                nodo.costo = costo + self.heuristicaConDiagonales([posActual[0] + y, posActual[1] + x]) 
                                listaSalida.append(nodo)
                        except IndexError:
                            pass
                else:
                    if ((x == 0 or y == 0) and (x != y) and (self.dentroLimites(posActual, y, x))):
                        try:
                            if (self.matriz[posActual[0] + y][posActual[1] + x] == 0):
                                nodo = Nodo()
                                nodo.posActual = [posActual[0] + y, posActual[1] + x]
                                nodo.posPrevia = posActual
                                nodo.costo = costo + self.heuristicaSinDiagonales([posActual[0] + y, posActual[1] + x])
                                listaSalida.append(nodo)
                        except IndexError:
                            pass
                        
        return listaSalida

    def dentroLimites(self, posActual, y, x):
        try:
            self.matriz[posActual[0] + y][posActual[1] + x]
            return True
        except IndexError:
            return False

    def dentroLimitesCampoVacio(self, x, y):
        if (x >= 0 and x < self.largo and y >= 0 and y < self.alto):
            if (self.matriz[y][x] == 0):
                return True
            
        return False

    def tienePosFinal(self, lista):
        for actual in lista:
            if (actual.posActual[0] == self.final[0] and \
                actual.posActual[1] == self.final[1]):
                return True
        return False

    def getCostoMenor(self, lista):
        menor = lista[0]
        for nodo in lista:
            if (nodo.costo < menor.costo):
                menor = nodo
        return menor

    def heuristicaSinDiagonales(self, posActual):
        final = self.final
        return abs(posActual[0] - final[0]) + abs(posActual[1] - final[1])

    def heuristicaConDiagonales(self, posActual):
        final = self.final
        return pow(posActual[0] - final[0], 2) + pow(posActual[1] - final[1], 2)

    def getValor(self, i, j):
        return self.matriz[i][j]

    def moverInicio(self, pos):
        x = self.inicio[1]
        y = self.inicio[0]
        if (pos == "izq"):
            x = x - 1
        elif (pos == "der"):
            x = x + 1
        elif (pos == "arr"):
            y = y - 1
        elif (pos == "aba"):
            y = y + 1
        elif (pos == "diagIzqArr"):
            x = x - 1
            y = y - 1
        elif (pos == "diagDerArr"):
            x = x  + 1
            y = y - 1
        elif (pos == "diagIzqAba"):
            x = x - 1
            y = y + 1
        elif (pos == "diagDerAba"):
            x = x  + 1
            y = y + 1
        if (self.dentroLimitesCampoVacio(x, y) and [y, x] != self.final) :
            self.inicio = [y, x]
            return True
        else:
            return False

    def moverFin(self, pos):
        x = self.final[1]
        y = self.final[0]
        if (pos == "izq"):
            x = x - 1
        elif (pos == "der"):
            x = x + 1
        elif (pos == "arr"):
            y = y - 1
        elif (pos == "aba"):
            y = y + 1
        elif (pos == "diagIzqArr"):
            x = x - 1
            y = y - 1
        elif (pos == "diagDerArr"):
            x = x  + 1
            y = y - 1
        elif (pos == "diagIzqAba"):
            x = x - 1
            y = y + 1
        elif (pos == "diagDerAba"):
            x = x  + 1
            y = y + 1
        if (self.dentroLimitesCampoVacio(x, y) and [y, x] != self.inicio):
            self.final = [y, x]
            return True
        else:
            return False

    def crearRuta(self):
        time.sleep(1)
        salida = True
        indice = self.findIndex(self.closedList, self.final)
        
        
        actual = self.closedList[indice]
        while (salida):
            temp = actual
            ind = self.findIndex(self.closedList, temp.posPrevia)
            actual = self.closedList[ind]
            idCamino = "camino" + str(actual.posActual[0]) + str(actual.posActual[1])
            app.ponerPieza(idCamino, actual.posActual[0], actual.posActual[1])
            app.actualizar()

            if (actual.posPrevia[1] == self.inicio[1] and actual.posPrevia[0] == self.inicio[0]):
                salida = False        
                    
            
        
        
            
    

class Reconocedor(threading.Thread):

    def __init__(self):
        super(Reconocedor, self).__init__()
        self.mic = sr.Microphone()
        self.rec = sr.Recognizer()
        self.eng = pyttsx3.init()
        #self.rec.energy_threshold = 400
        #self.rec.dynamic_energy_threshold = False

    def validarComando(self, comando):
        comando = comando.lower()
        listaStr = comando.split()
        print(listaStr)
        global activo
        if (len(listaStr) > 0):
            nombreComando = listaStr[0]
            if (nombreComando in comandos):
                if (nombreComando == "largo"):
                    self.validarLargo(listaStr)

                elif (nombreComando == "alto"):
                    self.validarAlto(listaStr)

                elif (nombreComando == "tamaño"):
                    self.validarTamano(listaStr)

                elif (nombreComando == "ayuda"):
                    self.decir("Déjame ayudarte, estos son los comandos disponibles.")
                    app.showComandos()

                elif (nombreComando == "crear"):
                    self.validarCrearCuadricula(listaStr)

                elif (nombreComando == "mostrar"):
                    self.validarMostrarRuta(listaStr)

                elif (nombreComando == "mover"):
                    self.validarMoverPieza(listaStr)

                elif (nombreComando == "poner"):
                    self.validarPonerDiagonales(listaStr)

                elif (nombreComando == "quitar"):
                    self.validarQuitarDiagonales(listaStr)

                elif (nombreComando == "limpiar"):
                    self.validarLimpiar(listaStr)

                elif (nombreComando == "salir"):
                    self.decir("Hasta la próxima")
                    activo = False
                    app.cerrar()
            else:
                self.decir (comando + " " + "inválido")
                        

    def validarLargo(self, comando):
        if (len(comando) == 2):
            try:
                numero = int(comando[1])
                if (numero > 10):
                    self.decir("Uff, estableciendo valor de largo")
                else:
                    self.decir("Estableciendo el valor de largo")
                    
                app.setLargo(numero)
            except ValueError:
                self.decir("Ay, el valor para largo no es un número")


    def validarAlto(self, comando):
        if (len(comando) == 2):
            try:
                numero = int(comando[1])
                self.decir("Estableciendo valor de alto")
                app.setAlto(numero)
            except ValueError:
                self.decir("Ay, el valor para alto no es un número")

    def validarTamano(self, comando):
        if (len(comando) == 2):
            try:
                numero = int(comando[1])
                if (numero > 30):
                    self.decir("Uff, estableciendo valor de tamaño")
                else:
                    self.decir("Estableciendo valor de tamaño")
                    
                app.setTamano(numero)
            except ValueError:
                self.decir("Ay, el valor para tamaño no es un número")

    def validarCrearCuadricula(self, comando):
        if (len(comando) == 2):
            if (comando[1] == "cuadrícula"):
                if (cuadricula.alto == 0):
                    self.decir("Ay, el valor de alto debe ser un número mayor a cero")
                elif (cuadricula.largo == 0):
                    self.decir("Ay, el valor de largo debe ser un número mayor a cero")
                elif (cuadricula.tamano == 0):
                    self.decir ("Ay, el valor de tamaño debe ser un número mayor a cero")
                else:
                    
                    self.decir("Creando cuadrícula")
                    app.mostrarCuadricula(cuadricula.alto, cuadricula.largo, cuadricula.tamano)
                    cuadricula.iniciarCuadricula()
                    app.actualizar()
                    
                    
                    app.actualizar()

    def validarMostrarRuta(self, comando):
        if (len(comando) == 2):
            if (comando[1] == "ruta" or comando[1] == "camino"):
                if (cuadricula.creado == False):
                    self.decir("Ay, no ha creado la cuadrícula")
                else:
                    if (cuadricula.manhattan()):
                        self.decir("Mostrando ruta")
                        cuadricula.crearRuta()
                    else:
                        self.decir("Ay, no pude generar la ruta")
                        

    def validarMoverPieza(self, comando):

        if (cuadricula.creado == False):
            self.decir("Ay, no ha creado la cuadrícula")
        else:
            if (len(comando) == 3):
                pieza = comando[1]
                direccion = comando[2]
     
                if (pieza == "inicio"):
                    permitido = self.validarPiezaInicioSimple(direccion)
                    if (permitido):
                        self.decir("Moviendo inicio")
                        app.ponerPieza("inicio", cuadricula.inicio[0], cuadricula.inicio[1])
                        if (cuadricula.solucionado == True):
                            app.limpiarCamino()
                            if (cuadricula.manhattan()):
                                cuadricula.crearRuta()
                        app.actualizar()

                        
                        app.actualizar()
                elif (pieza == "fin" or pieza == "final"):
                    permitido = self.validarPiezaFinSimple(direccion)
                    if (permitido):
                        self.decir("moviendo fin")
                        app.ponerPieza("fin", cuadricula.final[0], cuadricula.final[1])
                        if (cuadricula.solucionado == True):
                            app.limpiarCamino()
                            if (cuadricula.manhattan()):
                                cuadricula.crearRuta()
                        app.actualizar()

                else:
                        self.decir("Ay, esa pieza no es ni el inicio ni el fin")

            elif (len(comando) == 4):
                pieza = comando[1]
                direccion1 = comando[2]
                direccion2 = comando[3]

   
                if (pieza == "inicio"):
                    permitido = self.validarPiezaInicioDiagonales(direccion1, direccion2)
                    if (permitido):
                        self.decir("Moviendo inicio")
                        app.ponerPieza("inicio", cuadricula.inicio[0], cuadricula.inicio[1])
                        app.actualizar()

                elif (pieza == "fin" or pieza == "final"):
                    permitido = self.validarPiezaFinDiagonales(direccion1, direccion2)
                    if (permitido):
                        self.decir("Moviendo fin")
                        app.ponerPieza("fin", cuadricula.final[0], cuadricula.final[1])
                        app.actualizar()

                else:
                    self.decir("Ay, esa pieza no es ni el inicio ni el fin")
                   
                            
    def validarPiezaInicioSimple(self, direccion):
        if (direccion == "arriba"):
            if (cuadricula.moverInicio("arr")):
                 return True
            else:
                self.decir("Ay, no se puede mover el inicio arriba")
                
        elif (direccion == "abajo"):
            if (cuadricula.moverInicio("aba")):
                return True
            else:
                self.decir("Ay, no se puede mover el inicio abajo")
                
        elif (direccion == "izquierda"):
            if (cuadricula.moverInicio("izq")):
                return True
            else:
                self.decir("Ay, no se puede mover el inicio a la izquierda")

        elif (direccion == "derecha"):
            if (cuadricula.moverInicio("der")):
                return True
            else:
                self.decir("Ay, no se puede mover el inicio a la derecha")
        return False

    def validarPiezaFinSimple(self, direccion):
        if (direccion == "arriba"):
            if (cuadricula.moverFin("arr")):
                 return True
            else:
                self.decir("Ay, no se puede mover el fin arriba")
                
        elif (direccion == "abajo"):
            if (cuadricula.moverFin("aba")):
                return True
            else:
                self.decir("Ay, no se puede mover el fin abajo")
                
        elif (direccion == "izquierda"):
            if (cuadricula.moverFin("izq")):
                return True
            else:
                self.decir("Ay, no se puede mover el fin a la izquierda")

        elif (direccion == "derecha"):
            if (cuadricula.moverFin("der")):
                return True
            else:
                self.decir("Ay, no se puede mover el fin a la derecha")
        return False
                                          

    def validarPiezaInicioDiagonales(self, direccion1, direccion2):
        if (direccion1 == "izquierda"):
            if (direccion2 == "arriba"):
                if (cuadricula.moverInicio("diagIzqArr")):
                    return True
                else:
                    self.decir("Ay, no se puede mover el inicio a la izquierda y luego arriba")

            elif (direccion2 == "abajo"):
                    if (cuadricula.moverInicio("diagIzqAba")):
                        return True
                    else:
                        self.decir("Ay, no se puede mover el inicio a la izquierda abajo")
            else:
                self.decir("Esa combinacion no es valida")

        elif (direccion1 == "derecha"):
            if (direccion2 == "arriba"):
                if (cuadricula.moverInicio("diagDerArr")):
                    return True
                else:
                    self.decir("Ay, no se puede mover el inicio a la derecha y luego arriba")

            elif (direccion2 == "abajo"):
                    if (cuadricula.moverInicio("diagDerAba")):
                        return True
                    else:
                        self.decir("Ay, no se puede mover el inicio a la derecha abajo")
            else:
                self.decir("Esa combinacion no es valida")
                
        return False

    def validarPiezaFinDiagonales(self, direccion1, direccion2):
        if (direccion1 == "izquierda"):
            if (direccion2 == "arriba"):
                if (cuadricula.moverFin("diagIzqArr")):
                    return True
                else:
                    self.decir("Ay, no se puede mover el fin a la izquierda y luego arriba")

            elif (direccion2 == "abajo"):
                    if (cuadricula.moverFin("diagIzqAba")):
                        return True
                    else:
                        self.decir("Ay, no se puede mover el fin a la izquierda abajo")
            else:
                self.decir("Esa combinacion no es valida")

        elif (direccion1 == "derecha"):
            if (direccion2 == "arriba"):
                if (cuadricula.moverFin("diagDerArr")):
                    return True
                else:
                    self.decir("Ay, no se puede mover el fin a la derecha y luego arriba")

            elif (direccion2 == "abajo"):
                    if (cuadricula.moverFin("diagDerAba")):
                        return True
                    else:
                        self.decir("Ay, no se puede mover el fin a la derecha y luego abajo")
            else:
                self.decir("Esa combinacion no es valida")
                
        return False


    def validarPonerDiagonales(self, comando):
        if (len(comando) == 2):
            if (comando[1] == "diagonales"):
                if (cuadricula.diagonales):
                    self.decir("Las diagonales ya estan puestas")
                else:
                    cuadricula.diagonales = True
                    self.decir("Diagonales habilitadas")
                    if (cuadricula.solucionado == True):
                        app.limpiarCamino()
                        if (cuadricula.manhattan()):
                            cuadricula.crearRuta()

    def validarQuitarDiagonales(self, comando):
        if (len(comando) == 2):
            if (comando[1] == "diagonales"):
                if (cuadricula.diagonales == False):
                    self.decir("Las diagonales ya estan deshabilitadas")
                else:
                    cuadricula.diagonales = False
                    self.decir("Diagonales deshabilitadas")
                    if (cuadricula.solucionado == True):
                            app.limpiarCamino()
                            if (cuadricula.manhattan()):
                                cuadricula.crearRuta()

    def validarLimpiar(self, comando):
        if (len(comando) == 1):
            if (cuadricula.creado == False):
                self.decir("Ay, la cuadricula no ha sido creada")
            else:
                app.limpiarCamino()
                app.actualizar()
                cuadricula.solucionado = False
                self.decir("Camino removido")
        
    def decir(self, mensaje):
        if (platform != 'darwin'):
            self.eng.say(mensaje)
            self.eng.runAndWait()
        else:
            mensaje = 'say ' + mensaje
            os.system(mensaje)
                
    def run(self):
        global activo
        while (activo):
            #time.sleep(1)
            with self.mic as source:
                self.decir("Espero comando")
                #self.rec.adjust_for_ambient_noise(source)
                self.audio = self.rec.listen(source)
                try:
                    comando = self.rec.recognize_google(self.audio, language = "es-CR")
                    self.validarComando(comando)
                            
                except sr.UnknownValueError:
                    self.decir("Ay, lo siento, no pude entender eso")
    
                except sr.RequestError:
                    self.decir('Ay, parece que tuve un problema interno, que pena hehe')
        return



class App(object):

    def __init__(self, root):
        
        self.root = root
        self.root.title("Menu")
        self.root.geometry("1200x800")

        topFrame = tk.Frame(self.root)
        topFrame.pack()

        
        bottomFrame = tk.Frame(self.root)
        bottomFrame.pack(side = "top", pady = 3)

        self.lblCuadrosLargo = tk.Label(topFrame, \
            text = " Largo de cuadros", \
            font=("Times New Roman",24))
        #self.lblCuadrosLargo.pack(side = 'left')
        
        self.txtCuadrosLargo = tk.Entry(topFrame, \
            state = 'readonly')
        #self.txtCuadrosLargo.pack(side = 'left')

        self.lblCuadrosAlto = tk.Label(topFrame, \
            text = " Alto de cuadros", \
            font=("Times New Roman",24))        
        #self.lblCuadrosAlto.pack(side = 'left')
        
        self.txtCuadrosAlto = tk.Entry(topFrame, \
            state = 'readonly')
        #self.txtCuadrosAlto.pack(side = 'left')

        self.lblCuadrosTam = tk.Label(topFrame, \
            text ="Tamaño de cuadros", \
            font = ("Times New Roman", 24))
        #self.lblCuadrosTam.pack(side = 'left')
        
        self.txtCuadrosTam = tk.Entry(topFrame, \
            state = 'readonly')
        #self.txtCuadrosTam.pack(side = 'left')

        self.canvas = tk.Canvas(bottomFrame)



    def setLargo(self, numero):
        """
        self.txtCuadrosLargo.config(state = 'normal')
        self.txtCuadrosLargo.delete(0, END)
        self.txtCuadrosLargo.insert(0, numero)
        self.txtCuadrosLargo.config(state = 'readonly')
        """
        cuadricula.largo = numero

    def setAlto(self, numero):
        """
        self.txtCuadrosAlto.config(state = 'normal')
        self.txtCuadrosAlto.delete(0, END)
        self.txtCuadrosAlto.insert(0, numero)
        self.txtCuadrosAlto.config(state = 'readonly')
        """
        cuadricula.alto = numero
        

    def setTamano(self, numero):
        """
        self.txtCuadrosTam.config(state = 'normal')
        self.txtCuadrosTam.delete(0, END)
        self.txtCuadrosTam.insert(0, numero)
        self.txtCuadrosTam.config(state = 'readonly')
        """
        cuadricula.tamano = numero

    def showComandos(self):
        if (platform != 'darwin'):
            os.startfile('agente.pdf')
        else:
            os.system('open agente.pdf')

    def cerrar(self):
        self.root.destroy()

    def mostrarCuadricula(self, filas, columnas, tamano):
        self.canvas.delete("all")
        self.filas = filas
        self.columnas = columnas
        self.tamano = tamano
        self.color = "white"
        self.piezas = {}

        canvas_ancho = columnas * tamano
        canvas_alto = filas * tamano

        self.canvas.config( borderwidth = 2, \
            highlightthickness = 1, width = canvas_ancho, \
            height = canvas_alto, background = "black")
        self.canvas.pack(side = "top", fill = "both", \
            expand = True, padx = 4, pady = 4)

        self.canvas.bind("<Configure>", self.refresh)

    def ponerPieza(self, nombre, fila, columna):

        self.piezas[nombre] = (fila, columna)
        x0 = (columna * self.tamano) + int(self.tamano / 2)
        y0 = (fila * self.tamano) + int(self.tamano / 2)
        self.canvas.coords(nombre, x0, y0)

    def actualizar(self):
        self.canvas.delete("square")
        color = "white"
        for fila in range(self.filas):
            
            for columna in range(self.columnas):
                x1 = (columna * self.tamano)
                y1 = (fila * self.tamano)
                x2 = x1 + self.tamano
                y2 = y1 + self.tamano
                self.canvas.create_rectangle(x1, y1, x2, y2,\
                    outline = "black", fill = color, tags = "square")

        for pieza in self.piezas:
            x1 = (self.piezas[pieza][1] * self.tamano)
            y1 = (self.piezas[pieza][0] * self.tamano)
            x2 = x1 + self.tamano
            y2 = y1 + self.tamano
            if (pieza == "inicio"):

                self.canvas.create_rectangle(x1, y1, x2, y2, \
                    outline = "black", fill = "red", tags = "square")
                
            elif (pieza == "fin"):
                self.canvas.create_rectangle(x1, y1, x2, y2, \
                    outline = "black", fill = "green", tags = "square")
                
            elif ("obstaculo" in pieza):
                self.canvas.create_rectangle(x1, y1, x2, y2, \
                    outline = "black", fill = "black", tags = "square")

            elif ("camino" in pieza):
                self.canvas.create_rectangle(x1, y1, x2, y2, \
                    outline = "black", fill = "yellow", tags = "square")

    def refresh(self, event):
        #por si se hace resize
        xsize = int((event.width - 1) / self.columnas)
        ysize = int((event.height - 1) / self.filas)
        self.tamano = min(xsize, ysize)
        self.canvas.delete("square")
        color = "white"
        for fila in range(self.filas):
            
            for columna in range(self.columnas):
                x1 = (columna * self.tamano)
                y1 = (fila * self.tamano)
                x2 = x1 + self.tamano
                y2 = y1 + self.tamano
                self.canvas.create_rectangle(x1, y1, x2, y2,\
                    outline = "black", fill = color, tags = "square")

        for pieza in self.piezas:
            x1 = (self.piezas[pieza][1] * self.tamano)
            y1 = (self.piezas[pieza][0] * self.tamano)
            x2 = x1 + self.tamano
            y2 = y1 + self.tamano
            if (pieza == "inicio"):

                self.canvas.create_rectangle(x1, y1, x2, y2, \
                    outline = "black", fill = "red", tags = "square")
                
            elif (pieza == "fin"):
                self.canvas.create_rectangle(x1, y1, x2, y2, \
                    outline = "black", fill = "green", tags = "square")
                
            elif ("obstaculo" in pieza):
                self.canvas.create_rectangle(x1, y1, x2, y2, \
                    outline = "black", fill = "black", tags = "square")

            elif ("camino" in pieza):
                self.canvas.create_rectangle(x1, y1, x2, y2, \
                    outline = "black", fill = "yellow", tags = "square")

    def limpiarCamino(self):
        listaCaminos = list()
        for pieza in self.piezas:
            if ("camino" in pieza):
                listaCaminos.append(pieza)

        for pieza in listaCaminos:
            self.piezas.pop(pieza, None)

    def limpiarTodo(self):
        listaPiezas = list()
        for pieza in self.piezas:
            listaPiezas.append(pieza)

        for pieza in listaPiezas:
            self.piezas.pop(pieza, None)

            
                
root = tk.Tk()

app = App(root)


reconocedor = Reconocedor()
reconocedor.start()
reconocedor.validarCrearCuadricula("crear cuadrícula")


cuadricula = Cuadricula()

reconocedor.decir("Hola, soy, Eva. Estoy a tu servicio")

root.mainloop()



           
    
