import socket
import threading

# Configuración del servidor
host = 'localhost'
port = 55555

# Crear un socket para el servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lista de clientes conectados
clients = []

# Lista de nombres de usuario de los clientes conectados
usernames = []
# Función para manejar la conexión de cada cliente
# Diccionario de canales, con el nombre del canal como clave y la lista de clientes como valor
channels = {}
#Diccionario de creadores, con el nombre del canal como clave y 1 creador por cada canal como valor
creators={}

# Función para enviar un mensaje a todos los clientes en un canal
def broadcast(message,cl,username,channel):
	#añade al mensage username: mensage
	message = username.encode('ascii') + ': '.encode('ascii') + message
	if channel not in channels:
		return
	for client in channels[channel]:
		try:
			if client != cl:
				#manda el mensage a todos los clientes menos así mismo
				client.send(message)
		except socket.error:
			channels[channel].remove(client)
    		
# Función para manejar la conexión de cada cliente
def handle(client,address,username):
	 # Enviamos un mensaje de bienvenida al cliente
	client.send(f'Bienvenido {username}, escribe AYUDA si quieres ver los comandos existentes.'.encode('ascii'))
	while True:
		try:
			# Recibir mensaje del cliente
			message = client.recv(1024)
			# Verificar si se recibió un mensaje
			if message:
				# Si el mensaje comienza con "CREA", crear un nuevo canal
				if message.decode('ascii').startswith('CREA'):
					#obtener el nombre del canal
					channel_name = message.decode('ascii')[5:].strip()
					if channel_name not in channels:
						#si el canal no esta creado crea el canal, y se une a el
						channels[channel_name] = []
						client.send(f'Se ha creado el canal "{channel_name}".'.encode('ascii'))
						print(f'Se ha creado el canal "{channel_name}".')
						username2 = usernames[clients.index(client)]
						channel_name2 = ''
						#recorrido para saber si el cliente esta dentro de un canal
						for name, clients_list in channels.items():
							if client in clients_list:
								channel_name2 = name
								break
						if channel_name2:
							#si estaba dentro de un canal se elimina como miembro de ese canal
							channels[channel_name2].remove(client)	
						channels[channel_name].append(client)
						client.send(f'Te has unido al canal "{channel_name}".'.encode('ascii'))
						print(f'{client.getpeername()} se ha unido al canal "{channel_name}".')
						#se añade al creador del canal
						creators[channel_name]=username	
					else:
					#si el canal ya existe lo notifica
						client.send(f'Ya existe un canal con el nombre "{channel_name}".'.encode('ascii'))
				
				
				elif message.decode('ascii').startswith('ELIMINAR'):
					channel_name = message.decode('ascii')[9:].strip()
					if channel_name in channels:
						# Obtener el nombre de usuario del cliente actual
						username2 = usernames[clients.index(client)]
						# Obtener el nombre de usuario del creador del canal
						creator_username = creators[channel_name]
						if username2 == creator_username:
							#si el usuario actual es igual que el usuario crador elimina el canal
							client.send(f'Se ha eliminado el canal "{channel_name}".'.encode('ascii'))
							# Eliminar a los clientes del canal eliminado
							for c in clients:
								if c in channels[channel_name]:
									channels[channel_name].remove(c)
							# Eliminar el canal y notificar al cliente
							del channels[channel_name]
							del creators[channel_name]
							print(f'Se ha eliminado el canal "{channel_name}".')
							chanel_name=''
						else:
							client.send('No tienes permiso para eliminar este canal.'.encode('ascii'))
					else:
				        	client.send(f'El canal "{channel_name}" no existe.'.encode('ascii'))
				       

				elif message.decode('ascii').startswith('MOSTRA_TOTS'):
				#muestra tots els usuaris y en que canal esta cada usuari
					message = "Lista de usuarios y sus canales:\n"
					#recorre todos los clientes
					for client2, username2 in zip(clients, usernames):
						channel_name = ''
						#recorrido para saber si el cliente esta dentro de un canal
						for name, clients_list in channels.items():
							 if client2 in clients_list:
							 	#si esta dentro de un canal pone en channel_name el nombrede canal
							 	channel_name = name
							 	break
						if channel_name:
							#si el cliente esta dentro de un canal
							message += f"Usuario: {username2} | Canal: {channel_name}\n"
						else:
							#si el cliento no tiene canal
							message += f"Usuario: {username2} | No esta en ningun canal\n"
					client.send(message.encode('ascii'))
						
				elif message.decode('ascii').startswith('MOSTRA_USUARIS'):
				#muestra todos los clientes que tiene el canal donde esta el cliente
					username2 = usernames[clients.index(client)]
					channel_name = ''
					#recorrido para saber si el cliente esta dentro de un canal
					for name, clients_list in channels.items():
						if client in clients_list:
						#si esta dentro de un canal pone en channel_name el nombrede canal
							channel_name = name
							break
					if channel_name:
						#si el cliente esta dentro de un canal
						channel_clients = channels[channel_name]
						#muestra todos los clientes que tiene ese canal
						usernames_in_channel = [username2 for username2, c in zip(usernames, clients) if c in channel_clients]
						message = f'Clientes en "{channel_name}": {", ".join(usernames_in_channel)}'
					else:
						message = "No estas en ningun canal"
					client.send(message.encode('ascii'))
				
				elif message.decode('ascii').startswith('CANVIA'):
					#obtiene el nombre del canal donde se va a canviar
					channel_name = message.decode('ascii')[6:].strip()
					#recorre el canal donde se va a canviar entre los canales que tenemos disponibles
					if channel_name in channels:
						username2 = usernames[clients.index(client)]
						channel_name2 = ''
						for name, clients_list in channels.items():
							if client in clients_list:
							#mira si el cliente esta en algun canal
								channel_name2 = name
								break
						if channel_name2:
							#si esta en algun canal se va del canal anterior 
							channels[channel_name2].remove(client)
						#se canvia al canal nuevo
						channels[channel_name].append(client)
						client.send(f'Te has unido al canal "{channel_name}".'.encode('ascii'))
						print(f'{client.getpeername()} se ha unido al canal "{channel_name}".')
					else:
						client.send(f'El canal "{channel_name}" no existe.'.encode('ascii'))
						
				elif message.decode('ascii').startswith('MOSTRA_CANALS'):
				#muestra todos los canales
					if (len(channels)>0):
						client.send("els canals son:".encode('ascii'))
						client.send(f', '.join(channels).encode('ascii'))
					else:
						client.send("no hay canales".encode('ascii'))
						
				
				elif message.decode('ascii').startswith('PRIVADO'):
				#Escribe un mensaje privado a un usuario pero tiene que estar en su mismo canal
					#divide el mensaje en partes
					message_parts = message.decode('ascii').split(' ',2)
					if len(message_parts) == 3:
						#obtiene a quien le manda el mensaje
						recipient = message_parts[1].strip()
						#obriene el mensaje que le quiere mandar
						message_text = message_parts[2].strip()
						if recipient in usernames:
						#mira si a quien le quieres mandar el mensaje existe y esta en el mismo canal
							recipient_index = usernames.index(recipient)
							recipient_client = clients[recipient_index]
							sender = usernames[clients.index(client)]
							recipient_client.send(f'(PRIVADO) {sender}: {message_text}'.encode('ascii'))
						else:
								client.send(f'El destinatario "{recipient}" no existe.'.encode('ascii'))
							
				elif message.decode('ascii') == 'AYUDA':
					client.send('CREA nombre_canal --> Crea un canal\nELIMINA nombre_canal --> Elimina un canal que has creado\nCANVIA nombre_canal --> Unete a un canal\nMOSTRA_CANALS --> Muestra una lista de los canales\nMOSTRA_USUARIS --> Muestra una lista de los usuarios del canal\nMOSTRA_TOTS --> Muestra una lista de todos los usuarios conectados y en que canal estan\nPRIVADO username mensaje --> Envia un mensaje privado a un cliente'.encode('ascii')) 
				# Si el mensaje no es una solicitud de creación o unión a un canal, transmitirlo a los demás clientes del canal actual
				else:
				#escribe un mensaje normal a todos los que estan en su mismo canal
					username2 = usernames[clients.index(client)]
					channel_name = ''
					for name, clients_list in channels.items():
						if client in clients_list:
						#mira si el cliente esta en algun canal
							channel_name = name
							break
					if channel_name:
					#si esta en algun canal envia a todos el mensaje
						channel_clients = channels[channel_name]
						usernames_in_channel = [username2 for username2, c in zip(usernames, clients) if c in channel_clients]
						broadcast(message,client,username,channel_name)
					else:
					#si no estas en ningun canal comunica que no puedes escribir
						message = "No puedes escribir, Unete a un canal"
						client.send(message.encode('ascii'))
	
			else:
				# Si hay un error en la conexión, eliminar el cliente de la lista
				index = clients.index(client)
				clients.remove(client)
				client.close()
				username = usernames[index]
				usernames.remove(username)
				
				# Si el cliente estaba en un canal, eliminarlo del canal
				for channel_name in channels:
					if client in channels[channel_name]:
						channels[channel_name].remove(client)
						print(f'{client.getpeername()} ha salido del canal "{channel_name}".')
						break
				
				# Transmitir mensaje de salida del cliente a los demás clientes del canal
				channel_clients = [c for c in channels.get(username, []) if c != client]
				broadcast(f'{username} ha salido del chat.'.encode('ascii'), channel_clients,username,channel_name)
				break

		except Exception as e:
			print(f'Se ha producido un error en la conexión: {e}')
			break

# Función para aceptar nuevas conexiones de clientes
def receive():
    while True:
        # Aceptar conexión de cliente
        client, address = server.accept()
        #print(f'Conexión establecida con {str(address)}')

        # Solicitar al cliente un nombre de usuario
        username = client.recv(1024).decode('ascii')

        # Agregar cliente y nombre de usuario a las listas
        clients.append(client)
        usernames.append(username)

        # Transmitir mensaje de bienvenida a los demás clientes
        print(f'Nombre de usuario del nuevo cliente: {username}')
        #broadcast(f'{username} se ha unido al chat!'.encode('ascii'),client,username,'')
         
        # Iniciar un nuevo hilo para manejar la conexión del cliente
        thread = threading.Thread(target=handle, args=(client,address,username))
        thread.start()

print('Servidor activo en el puerto', port)
receive()

