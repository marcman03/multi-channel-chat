import socket
import threading

# Configuración del cliente
host = 'localhost'
port = 55555

# Solicitar al usuario un nombre de usuario
username = input('Ingresa un nombre de usuario: ')

# Crear un socket para el cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
client.send(username.encode('ascii'))



# Función para recibir mensajes del servidor
def receive():
    while True:
        try:
            # Recibir mensaje del servidor
            message = client.recv(1024).decode('ascii')
            # Imprimir mensaje en la consola del cliente
            print(message)
        except:
            # Si hay un error en la conexión, cerrar el cliente
            print('Ha ocurrido un error en la conexión al servidor.')
            client.close()
            break

# Función para enviar mensajes al servidor
def write():
    while True:
        # Escribir mensaje en la consola del cliente y enviarlo al servidor
        message = f'{input("")}'
        client.send(message.encode('ascii'))

# Iniciar un nuevo hilo para recibir mensajes del servidor
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Iniciar un nuevo hilo para enviar mensajes al servidor
write_thread = threading.Thread(target=write)
write_thread.start()

