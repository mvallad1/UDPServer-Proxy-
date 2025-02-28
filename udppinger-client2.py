from socket import *
import time

serverAddress = ('149.125.45.15', 12000)

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
        timestamp = time.time()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

        print('ping,',  seqNum, ',', formatted_time)

        response, serverAddress = clientSocket.recvfrom(1024)
        res_timestamp = time.time()
        res_formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(res_timestamp))

        responseSeqNum, responseTime = response.decode().split(',')[1:]

        rtt = "{:.10f}".format((res_timestamp - timestamp) * 1000)

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
