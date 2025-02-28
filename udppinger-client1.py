from socket import *
import time

serverAddress = ('149.125.45.15', 12000)

clientSocket = socket(AF_INET, SOCK_DGRAM)

clientSocket.settimeout(1)

seqNum = 0
startTime = time.time()

while time.time() - startTime < 180:

    try:
        
        seqNum += 1
        
        message = f'ping,{seqNum},{time.time()}'
        
        clientSocket.sendto(message.encode(), serverAddress)
        timestamp = time.time()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

        print('ping,',  seqNum, ',', formatted_time)

        response, serverAddress = clientSocket.recvfrom(1024)
        res_timestamp = time.time()
        res_formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(res_timestamp))

        
        responseSeqNum, responseTime = response.decode().split(',')[1:]

        #print("{:.10f}".format(res_timestamp), "{:.10f}".format(timestamp))
        rtt = "{:.10f}".format((res_timestamp - timestamp) * 1000)
      
        print('echo,', responseSeqNum, ',', res_formatted_time)
        print('RTT:', rtt)

    except timeout:
        print('Client ping timed out.')

    time.sleep(3)

clientSocket.close()
