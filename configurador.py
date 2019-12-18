'''
Programa Python que lee los datos del router y equipos terminales de una red y lanza
los comandos necesarios para modificar las IPs, Mascaras de red y Puertas de enlace.

Autor: Javier Garcia Gonzalez
Organizacion: Universidad de Burgos
Version: 3.1
Fecha ultima version: 04/02/2019
'''

import os
import numpy as np
from StringIO import StringIO
import telnetlib
import time
import getpass
import sys
import telnetlib



archivo = open("fichero.txt")
archivo.seek(0)
datos = archivo.read()
archivo.close()

#Esta funcion nos permite guardar los datos leidos del fichero en un array de arrays.
array = np.genfromtxt(StringIO(datos), delimiter=",", dtype="|U20", autostrip=True)
#Numero de interfaces a configurar
numConfigs = len(array)



'''
telnet(ip)
Funcion que recibe una direccion IP y realiza una conexion mediante telnet para configurar las interfaces
del componente.

'''

def telnet(ip):
	wait = 2
	HOST = "192.168.122.192"
	user = raw_input("Enter your username: ")
	password = getpass.getpass()

	tn = telnetlib.Telnet(HOST)

	tn.read_until("alberto-VirtualBox login: ")
	tn.write(user + "\n")
	if password:
	    tn.read_until("Password: ")
	    tn.write(password + "\n")

	tn.write("sudo ifconfig enp0s3 192.168.122.193 netmask 255.255.255.0 \n")
	tn.write(password + "\n")
	tn.write("exit\n")

	print tn.read_all()
            

'''
menu()
Funcion que nos muestra una serie de opciones para ver leer el fichero de configuracion
o lanzar las configuraciones.


'''
def menu():
    
    os.system('clear')
    
    print("Opciones")
    print("\t1 - Leer configuracion")
    print("\t2 - Lanzar Configuracion")
    print("\t9 - Salir")
    

while True:
    menu()
    opcionMenu = input("Inserta numero -> ")
    if opcionMenu == 1:
        
        print("ifconfig " + array[6][2] + " " + array[6][7] + " netmask " + array[6][8] + " broadcast " + array[6][9] + " up" + "\n")

        
        break
                
        
    elif opcionMenu == 2:
        print("")
        print("Lanzando configuracion...\n pulsa enter para continuar")
        j=0
        while j <= numConfigs-1:
            telnet(array[j][4])
            j+=1
        print("Configuracion realizada correctamente.")
        
        break
    
        
        
    elif opcionMenu == 9:
        print("Cerrando conexion...")
        break
    
    else: 
        print("")
        input("No has pulsado ninguna opcion correcta...\npulsa una tecla para volver al menu")
        

    
