from socket import *
from _thread import *
import threading
import time
import sys

cache = {}

should_terminate = False

WEB_HOST = '149.125.108.238'

def udp_pinger():
    serverAddress = ('149.125.108.238', 12000)

    clientSocket = socket(AF_INET, SOCK_DGRAM)

    clientSocket.settimeout(1)

    seqNum = 0
    numReceived = 0
    rttTimes = []
    minRTT = float('inf')
    maxRTT = 0
    totalRTT = 0
    numPackets = 0

    startTime = time.time()

    while time.time() - startTime < 180:

        try:
        
            seqNum += 1
        
            message = f'ping,{seqNum},{time.time()}'
        
            clientSocket.sendto(message.encode(), serverAddress)
            send_timestamp = time.time()
            send_formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(send_timestamp))

            print('ping,',  seqNum, ',', send_formatted_time)

            response, serverAddress = clientSocket.recvfrom(1024)
            res_timestamp = time.time()
            res_formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(res_timestamp))

            responseSeqNum, responseTime = response.decode().split(',')[1:]

            rtt = "{:.10f}".format((res_timestamp - send_timestamp) * 1000)

            rttTimes.append(float(rtt))
            totalRTT += float(rtt)
            numReceived += 1
            if float(rtt) < minRTT:
                minRTT = float(rtt)
            if float(rtt) > maxRTT:
                maxRTT = float(rtt)

            print('echo,', responseSeqNum, ',', res_formatted_time)
            print('RTT:', rtt)

        except timeout:
            print('Client ping timed out.')

        numPackets += 1
        time.sleep(3)

    packetLossRate = "{:.2f}".format((1 - (numReceived / numPackets)) * 100)
    avgRTT = "{:.10f}".format(totalRTT / numReceived)

    print('\n')
    print('Statistics::')
    print('Min RTT:', minRTT, '\n')
    print('Max RTT:', maxRTT, '\n')

    print('Total RTTs:', numReceived, '\n')
    print('Packet Loss Percentage:', packetLossRate, '%', '\n')

    print('Average RTT:', avgRTT, '\n')

    clientSocket.close()



def threaded(connectionSocket):
    thread_id = threading.get_ident()
    
    request = connectionSocket.recv(1024)
    
    path = request.decode().split(' ')[1]
    path = '/' + path.split('/')[1]     #changed from [3] to [1]
    
    
    request = f"Get {path} HTTP/1.1\r\nHost:http://1555\r\n\r\n".encode()
    
    if request in cache and time.time() - cache[request][0] < 5:
        response = cache[request][1]
        connectionSocket.send(response)

        threadnum = cache[request][2]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("proxy-cache, client ,", threadnum, ",", timestamp)
        
        connectionSocket.close()
        return
        
    else:
    
        #request_lines = request.decode().split('\r\n')
        #host_header = [line for line in request_lines if line.startswith('Host:')]
        
        #host = host_header[0].split(':')[1].strip()
        #ip = host
    
        web_socket = socket(AF_INET, SOCK_STREAM)
        web_socket.connect((WEB_HOST, 1444))
        web_socket.send(request)
        timestamp1 = time.time()
        formatted_time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp1))
    
        response = b''
        while True:
            data = web_socket.recv(1024)
            if not data:
                break
            response += data
    
    #print(response)
    
        if response.startswith(b'HTTP/1.1 404 Not Found'):
            response = response[response.find(b'HTTP/1.1 404 Not Found'):response.find(b'\r\n\r\n')]
    
        cache[request] = (time.time(), response, thread_id)
    
        connectionSocket.send(response)
        timestamp2 = time.time()
        formatted_time2 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp2))
    
        print("proxy-forward,", "server", ",", thread_id, ",", formatted_time1)
        print("proxy-forward,", "client", ",", thread_id, ",", formatted_time2)
    
        #print(content)
        #connectionSocket.send(content)
    
        connectionSocket.close()
        return
     
        


# Prepare a sever socket
proxySocket = socket(AF_INET, SOCK_STREAM)

start_new_thread(udp_pinger, ())


proxyPort = 1555
proxySocket.bind(('149.125.46.145', proxyPort))
proxySocket.listen(5)

print('Ready to serve...')

while not should_terminate:
    # Establish the connection
        
    connectionSocket, addr = proxySocket.accept()
    
    start_new_thread(threaded, (connectionSocket,))
    
    current_time = time.time()
    for key, value in list(cache.items()):
        timestamp, response, thread_id = value
        if current_time - timestamp > 120:
            del cache[key]

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    should_terminate = True
    proxySocket.close()
    
    time.sleep(1)
    
    sys.exit()
