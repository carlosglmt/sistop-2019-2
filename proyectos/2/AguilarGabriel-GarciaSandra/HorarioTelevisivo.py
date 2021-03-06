import threading
import random
import time
numeroTeles = 2 #Indica  el numero de televisores en la casa
numeroIntegrantes = 4 #Indica el numero de integrantes de la familia que desean ver la television
tiempo = 0 #Este contador se utiliza para indicar la hora actual
pasillo = threading.Semaphore(numeroTeles) #Este semaforo sirve para indicar si hay televisiones disponibles, si un integrante desea una television pero todos estan ocupadas el hilo se queda esperando
queHoraEs = threading.Semaphore(1) #Mutex para acceder al contador de tiempo
tomarTele = threading.Semaphore(1)
canales = [] #Este arreglo sirve para indicar el numero de canales disponibles y el tamaño de sus bloques comerciales y la frecuencia de los mismos
programas = [] #Este arreglo idica los programas de los canales con su duracion [[[horaInicio, [bloquesComerciales], horaFin], ...], ...]
teles = [[]*3]*numeroTeles #En este arreglo se guarda el canal sintonizado en cada tele [[canal, programa, [usuarios]], ...]
control = [threading.Semaphore(0)]*numeroTeles
tiempoMax = 100
TelesEnUso = [0]*numeroTeles

def padreTiempo():
	global tiempo
	global tiempoMax
	continuar = True
	print('Inicia simulacion')
	while continuar:
		queHoraEs.acquire()
		ActualizarTeles()
		if tiempo < tiempoMax+20:
			tiempo += 1
		else:
			continuar = False
		queHoraEs.release()
		print(tiempo)
		time.sleep(0.5)
	return 'Fin simulacion'

def ActualizarTeles():
	global tiempo
	global programas
	global teles
	global TelesEnUso
	global numeroTeles
	for i in range(0,numeroTeles):
		tomarTele.acquire()
		if TelesEnUso[i] == 1:
			canal = teles[i][0]
			programa = teles[i][1]
			#queHoraEs.acquire()
			if programas[canal][programa][2] <= tiempo:
				for x in teles[i][2]:
					control[i].release()
			else:
				for x in  programas[canal][programa][1]:
					if x == tiempo:
						for j in teles[i][2]:
							control[i].release()
		tomarTele.release()
	print('En uso:', TelesEnUso, '\nTeles:', teles)

def Usuario(who):
	global canales
	global programas
	global tiempo
	global teles
	global TelesEnUso
	time.sleep(0.1)
	canal = random.randint(0,len(canales)-1)
	programa = random.randint(0,len(programas[canal])-1)
	otroPrograma = random.random() % 0.1
	print('Usuario:', str(who), '; quiero ver:', canal, programa, 'que empieza en', programas[canal][programa][0], 'y termina en', programas[canal][programa][2])
	queHoraEs.acquire()
	tiempoAux = tiempo
	queHoraEs.release()
	while programas[canal][programa][0] > tiempoAux:
		queHoraEs.acquire()
		tiempoAux = tiempo
		queHoraEs.release()
	while programas[canal][programa][2] > tiempoAux:
		print('soy usuario', str(who), 'estoy en el pasillo esperando')
		pasillo.acquire()
		time.sleep(0.1) #antes de entrar dejo salir
		print('¿¿¿¿¿¿¿¿¿Usuario', str(who),'termino mi programa')
		queHoraEs.acquire()
		print('Usuario', str(who),'termino mi programa?????????')
		tiempoAux = tiempo
		queHoraEs.release()
		if programas[canal][programa][2] > tiempoAux:
			print('-----------soy usuario', str(who), 'busco una tele')
			tomarTele.acquire()
			compartiendo = 0
			for x in range(0,len(TelesEnUso)):
				if TelesEnUso[x] == 1 and teles[x][0] == canal and teles[x][1] == programa:
					teles[x][2].append(who)
					lugar = x
					compartiendo += 1
					pasillo.release() 
					#tomarTele.release()
			if compartiendo == 0:
				#tomarTele.acquire()
				lugar = TelesEnUso.index(0)
				TelesEnUso[lugar] = 1
				if len(teles[lugar]) == 0:
					teles[lugar] = [canal, programa, [who]]
				else:
					teles[lugar][0] = canal
					teles[lugar][1] = programa
					teles[lugar][2].append(who)
			tomarTele.release()
			control[lugar].acquire()
			print('////////////////Usuario', str(who), 'Dejo la tele', lugar)
			tomarTele.acquire()
			TelesEnUso[lugar] = 0
			if len(teles[lugar][2]) == 1: #si soy el unico viendo la tele aviso a quienes esperan que la tele se desocupo
				pasillo.release()
			teles[lugar][2].remove(who)
			tomarTele.release()
		else:
			pasillo.release()
		queHoraEs.acquire()
		tiempoAux = tiempo
		queHoraEs.release()
	print('\n\t-----------Usuario', str(who), 'El programa que queria ver termino-----------')
	if random.random() <= otroPrograma:
		Usuario(who)
	print('\n\t*****************Usuario', str(who), 'termine*****************')

def generarProgramacion():
	global canales
	global programas
	global tiempoMax
	for i in range(0,10):
		canales.append([random.randint(1,3), random.randint(4,7)])
		programas.append([])
		acumulado = 0
		programa = 0
		while acumulado < tiempoMax:
			programas[i].append([])
			programas[i][programa].append(acumulado)
			programas[i][programa].append([])
			duracion = random.randint(1,5) #ATENCION
			for j in range(0,duracion):
				acumulado += canales[i][1]
				if acumulado > tiempoMax:
					programas[i][programa].append(tiempoMax)
					break
				programas[i][programa][1].append(acumulado)
				acumulado += canales[i][0]
			acumulado += canales[i][1]
			if acumulado > tiempoMax:
				programas[i][programa].append(tiempoMax)
				break
			programas[i][programa].append(acumulado)
			programa += 1
	print('Se generarron los canales y programas\ncanales:', canales, '\nprogramas:', programas)

generarProgramacion()
for i in range(0,numeroIntegrantes): #Se crea a los usuarios
	threading.Thread(target=Usuario, args=[i]).start()
threading.Thread(target=padreTiempo).start()