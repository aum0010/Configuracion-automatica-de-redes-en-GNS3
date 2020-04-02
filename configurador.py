'''
Programa Python que lee los datos del router y equipos terminales de una red y lanza
los comandos necesarios para modificar las IPs, Mascaras de red y Puertas de enlace.

Autor: Javier Garcia Gonzalez
Organizacion: Universidad de Burgos
Version: 3.1
Fecha ultima version: 04/02/2019
'''
import random
import os
import numpy as np
from StringIO import StringIO
import telnetlib
import time
import getpass
import sys
import telnetlib
import socket
import platform    # For getting the operating system name
import subprocess  # For executing a shell command



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

def telnet():
	todo_ok=False
	wait = 2
	hostname = socket.gethostname()
	IPAddr = get_ip()
	print("Your Computer Name is: " + hostname)    
	print("Your Computer IP Address is: " + IPAddr)
	while todo_ok == False:
		ip,host,netmask,gateway,todo_ok=subnet_calc()
	

	ping(host)
	user = raw_input("Introduce tu nombre de usuario: ")
	password = getpass.getpass()

	tn = telnetlib.Telnet(host)

	tn.read_until(hostname+" login: ")
	tn.write(user + "\n")
	if password:
		   tn.read_until("Password: ")
		   tn.write(password + "\r\n")

	tn.write("sudo su root\r\n")
	tn.read_until("[sudo] password for "+user+": ")
	tn.write(password + "\n")

	tn.write("nmcli connection modify eth0 ipv4.addresses " + str(ip) + "/"+ str(netmask) + " ipv4.gateway " + str(gateway) + " ipv4.method manual connection.autoconnect yes\r\n")

	tn.write("nmcli connection up eth0\r\n")
		
	tn.write("ping " + ip +"\r\n")
		
	tn.read_all()
		
	tn.close()
            
def convert_ipv4(ip):
    return tuple(int(n) for n in ip.split('.'))

def check_ipv4_in(addr, start, end):
    return convert_ipv4(start) < convert_ipv4(addr) < convert_ipv4(end)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '4', host]

    return subprocess.call(command) == 0

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

def subnet_calc():
   
    try:

        while True:
            # Take IP as input
            input_ip = get_ip()
	    dest_ip = raw_input("\nIntroduce IP destino: ")

            # Validate the IP
            octet_ip = input_ip.split(".")
            #print octet_ip
            int_octet_ip = [int(i) for i in octet_ip]

            if (len(int_octet_ip) == 4) and \
                    (int_octet_ip[0] != 127) and \
                    (int_octet_ip[0] != 169) and  \
                    (0 <= int_octet_ip[1] <= 255) and \
                    (0 <= int_octet_ip[2] <=255) and \
                    (0 <= int_octet_ip[3] <= 255):
                break
            else:
                print "Invalid IP, retry \n"
                continue

        # Predefine possible subnet masks
        masks = [0, 128, 192, 224, 240, 248, 252, 254, 255]
        while True:

            # Take subnet mask as input
            input_subnet = raw_input("\nIntroduce mascara de subred: ")

            # Validate the subnet mask
            octet_subnet = [int(j) for j in input_subnet.split(".")]
            # print octet_subnet
            if (len(octet_subnet) == 4) and \
                    (octet_subnet[0] == 255) and \
                    (octet_subnet[1] in masks) and \
                    (octet_subnet[2] in masks) and \
                    (octet_subnet[3] in masks) and \
                    (octet_subnet[0] >= octet_subnet[1] >= octet_subnet[2] >= octet_subnet[3]):
                break
            else:
                print "Invalid subnet mask, retry\n"
                continue

# Converting IP and subnet to binary

        ip_in_binary = []

        # Convert each IP octet to binary
        ip_in_bin_octets = [bin(i).split("b")[1] for i in int_octet_ip]

        # make each binary octet of 8 bit length by padding zeros
        for i in range(0,len(ip_in_bin_octets)):
            if len(ip_in_bin_octets[i]) < 8:
                padded_bin = ip_in_bin_octets[i].zfill(8)
                ip_in_binary.append(padded_bin)
            else:
                ip_in_binary.append(ip_in_bin_octets[i])

        # join the binary octets
        ip_bin_mask = "".join(ip_in_binary)

        # print ip_bin_mask

        sub_in_bin = []

        # convert each subnet octet to binary
        sub_bin_octet = [bin(i).split("b")[1] for i in octet_subnet]

        # make each binary octet of 8 bit length by padding zeros
        for i in sub_bin_octet:
            if len(i) < 8:
                sub_padded = i.zfill(8)
                sub_in_bin.append(sub_padded)
            else:
                sub_in_bin.append(i)

        # print sub_in_bin
        sub_bin_mask = "".join(sub_in_bin)

        # calculating number of hosts
        no_zeros = sub_bin_mask.count("0")
        no_ones = 32 - no_zeros
        no_hosts = abs(2 ** no_zeros - 2)

        # Calculating the network and broadcast address
        network_add_bin = ip_bin_mask[:no_ones] + "0" * no_zeros
        broadcast_add_bin = ip_bin_mask[:no_ones] + "1" * no_zeros

        network_add_bin_octet = []
        broadcast_binoct = []

        [network_add_bin_octet.append(i) for i in [network_add_bin[j:j+8]
                                                   for j in range(0, len(network_add_bin), 8)]]
        [broadcast_binoct.append(i) for i in [broadcast_add_bin[j:j+8]
                                              for j in range(0,len(broadcast_add_bin),8)]]

        network_add_dec_final = ".".join([str(int(i,2)) for i in network_add_bin_octet])
        broadcast_add_dec_final = ".".join([str(int(i,2)) for i in broadcast_binoct])

        # Calculate the host IP range
        first_ip_host = network_add_bin_octet[0:3] + [(bin(int(network_add_bin_octet[3],2)+1).split("b")[1].zfill(8))]
        first_ip = ".".join([str(int(i,2)) for i in first_ip_host])

        last_ip_host = broadcast_binoct[0:3] + [bin(int(broadcast_binoct[3],2) - 1).split("b")[1].zfill(8)]
        last_ip = ".".join([str(int(i,2)) for i in last_ip_host])

        # print all the computed results
        print "\nLa ip de destino es: " + dest_ip
        print "La mascara de subred es: " + input_subnet
        print "Numero de maquinas por subred: {0}".format(str(no_hosts))
        print "Numero de bits de la mascara: {0}".format(str(no_ones))
        print "Direccion de red: {0}".format(network_add_dec_final)
        print "Direccion de broadcast: {0}".format(broadcast_add_dec_final)
        print "Rango de direcciones de la subred: {0} - {1}".format(first_ip, last_ip)
        print "Maximo numero de subredes: " + str(2**abs(24 - no_ones))
        list_ip = []

        print ""

	#aviso de si esta en rango
	en_rango= check_ipv4_in(dest_ip, first_ip, last_ip)
	if en_rango:
		print "La ip esta en la misma subred. "
		todo_ok = True
	else:
		print "La ip no esta en la misma subred. "
		cambiar=raw_input("Desea cambiar la ip destino? [y/n]")
		if cambiar == 'y':
			todo_ok = False	
		else:
			todo_ok = True

	#al archivo de log
	file1 = open("logs.txt","w")
	file1.write("Ip de destino: "+ dest_ip +"\n")
	file1.write("Mascara de subred : "+ input_subnet +"\n")
	file1.close()

        # ask to generate a random ip in the range
	
        if todo_ok == True:
	    todo_ok2=False
            cambiar2=True		
            while todo_ok2 == False:
                new_ip = raw_input("Introduce nueva ip para el destino: ") 
		en_rango= check_ipv4_in(new_ip, first_ip, last_ip)
		if en_rango:
			print "La ip esta en la misma subred. "
			todo_ok2 = True
		else:
			print "La ip no esta en la misma subred. "
			cambiar2=raw_input("Desea cambiar la nueva ip destino? [y/n]")
		if cambiar2 == 'y':
			todo_ok2 = False	
		else:
			todo_ok2 = True
	#nueva ip a archivo de log
	file1 = open("logs.txt","a")
	file1.write("Nueva Ip de destino: "+ new_ip +"\n")
	file1.close()
	
                # Check if the octet bit is same in first and last host address.
                # If same, append it. else generate random IP
                #for i in range(0,len(first_ip_host)):
                #    for j in range(0,len(last_ip_host)):
                #        if i == j:
                #            if first_ip_host[i] == last_ip_host[j]:
                #                randip.append(int(first_ip_host[i],2))
                #            else:
                #                randip.append(random.randint(int(first_ip_host[i],2),int(last_ip_host[j],2)))

                #random_ip_final = ".".join(str(i) for i in randip)

                # check if generated IP has already been printed. If so, compute again till unique IP is obtained
               # if random_ip_final in list_ip:

                    # if all IPs in the host range are used, exit
               #     if len(list_ip) == no_hosts:
               #         print "All IPs in the range used up, exiting\n"
               #         break
                #    continue

                #else:
                #    print random_ip_final + '\n'

                #list_ip.append(random_ip_final)
               # print "Lista de IPs generadas:" , sorted(list_ip) ,'\n'

               # if raw_input("\nGenerar otra IP? [y/n]") == 'y':
               #     continue
               # else:
               #     break
	
	return new_ip, dest_ip, no_ones, first_ip, todo_ok
    except KeyboardInterrupt:
        print "Interrupted by the User, exiting\n"
    except ValueError:
        print "Seem to have entered an incorrect value, exiting\n"


    

while True:
    menu()
    opcionMenu = input("Inserta numero -> ")
    if opcionMenu == 1:
        
        print("ifconfig " + array[6][2] + " " + array[6][7] + " netmask " + array[6][8] + " broadcast " + array[6][9] + " up" + "\n")

        
        break
                
        
    elif opcionMenu == 2:
        print("")
        print("Lanzando configuracion...\n pulsa enter para continuar")
       
        telnet()
        print("Configuracion realizada correctamente.")
        
        break
    
        
        
    elif opcionMenu == 9:
        print("Cerrando conexion...")
        break
    
    else: 
        print("")
        input("No has pulsado ninguna opcion correcta...\npulsa una tecla para volver al menu")
        

    
