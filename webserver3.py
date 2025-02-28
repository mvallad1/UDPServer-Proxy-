from socket import *
from _thread import *
import threading
import time
import sys
import random

#Flag to help terminate
should_terminate = False

def threaded_udp(serverSocket):
    serverSocket.settimeout(30)
    
    while True:
        try:
            rand = random.randint(0, 10)

            message, address = serverSocket.recvfrom(1024)

            if rand < 4:
                continue

            serverSocket.sendto(message, address)
            
        except timeout:
            print("Server echo timed out.")
            return

def threaded(connectionSocket):
    thread_id = threading.get_ident()
    while not should_terminate:
        try:
            message = connectionSocket.recv(1024).decode()
            
            filename = message.split()[1][1:]  
            extension = filename.split('.')[-1]  
            
            response = ''
            if extension == 'html':
                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'
                
            elif extension == 'pdf':
                response = 'HTTP/1.1 200 OK\r\nContent-Type: application/pdf\r\n\r\n'
            
            
            f = open(filename, 'rb')
            outputdata = f.read()
               
            
            connectionSocket.send(response.encode())
            
            TIMESTAMP1 = time.time()
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(TIMESTAMP1))

            print("server-response,", "200", ",", thread_id, ",",formatted_time)

            
            connectionSocket.send(outputdata)
            
            f.close()
            connectionSocket.close()
            return  
            
        except IOError:
            
            response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n'
            connectionSocket.send(response.encode())
            
            TIMESTAMP2 = time.time()
            formatted_time2 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(TIMESTAMP2))
            print("server-response,", "404", ",", thread_id, ",",formatted_time2)

            
            connectionSocket.close()
            return  



# Prepare a server socket
serverSocket = socket(AF_INET, SOCK_STREAM)
serverPort = 1444
serverSocket.bind(('0.0.0.0', serverPort))
serverSocket.listen(5)

print('Ready to serve...')

udp_serverSocket = socket(AF_INET, SOCK_DGRAM)
udp_serverSocket.bind(('149.125.46.145', 12000))

start_new_thread(threaded_udp, (udp_serverSocket,))

while not should_terminate:
    # Establish the connection
        
    connectionSocket, addr = serverSocket.accept()
    
    start_new_thread(threaded, (connectionSocket,))

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    should_terminate = True
    serverSocket.close()
    
    time.sleep(1)
    
    sys.exit()
