import socket
import re
import time
import pandas
 
def subscribe(sock, *sensors):
    while type(sensors[0]) == tuple: # If input was given as tuple rather than series of strings...
        sensors = sensors[0] # Remove extraneous tuple layer
    
    streamsDictionary = {   
        'acc': ["device_subscribe acc ON\r\n", "device_subscribe acc OFF\r\n"],
        'bvp': ["device_subscribe bvp ON\r\n", "device_subscribe bvp OFF\r\n"],
        'gsr': ["device_subscribe gsr ON\r\n", "device_subscribe gsr OFF\r\n"],
        'ibi': ["device_subscribe ibi ON\r\n", "device_subscribe ibi OFF\r\n"],
        'tmp': ["device_subscribe tmp ON\r\n", "device_subscribe tmp OFF\r\n"],
        'tag': ["device_subscribe tag ON\r\n", "device_subscribe tag OFF\r\n"]
    }
    for msg in sensors:
        print(streamsDictionary[msg][0].encode())
        sock.sendall( streamsDictionary[msg][0].encode() )
        isConnected = False
        attempts = 0
        resp = sock.recv(1024)
        print(resp.decode())
        isConnected = "R device_subscribe {} OK".format(msg) in resp.decode()
        attempts += 1
    
    return sock.recv(1024)

def getval(sock):
    resp = sock.recv(1024)
    print(resp.decode())
    spltresp = resp.decode().split("\n")
    val = list()
    for row in spltresp:
        row = row.strip("\r")
        spltrow = row.replace("'", " ").split(" ")
        try:
            val.append({spltrow[0].strip("E4_"): float(spltrow[2:]), "Time": float(spltrow[1])})
        except:
            val.append({spltrow[0].strip("E4_"): []})
    return val

def unsubscribe(sock, *sensors):
    while type(sensors[0]) == tuple: # If input was given as tuple rather than series of strings...
        sensors = sensors[0] # Remove extraneous tuple layer
        
    streamsDictionary = {   
        'acc': ["device_subscribe acc ON\r\n", "device_subscribe acc OFF\r\n"],
        'bvp': ["device_subscribe bvp ON\r\n", "device_subscribe bvp OFF\r\n"],
        'gsr': ["device_subscribe gsr ON\r\n", "device_subscribe gsr OFF\r\n"],
        'ibi': ["device_subscribe ibi ON\r\n", "device_subscribe ibi OFF\r\n"],
        'tmp': ["device_subscribe tmp ON\r\n", "device_subscribe tmp OFF\r\n"],
        'tag': ["device_subscribe tag ON\r\n", "device_subscribe tag OFF\r\n"]
    }
    for msg in sensors:
        sock.sendall( streamsDictionary[msg][1].encode() )
        isConnected = False
        attempts = 0
        while not isConnected & attempts < 20:
            resp = sock.recv(1024)
            isConnected = "R device_subscribe {} OK".format(msg) in resp.decode()
            attempts += 1
        
    return sock.recv(1024)



def run(sock, dur, *sensors):
    while type(sensors[0]) == tuple: # If input was given as tuple rather than series of strings...
        sensors = sensors[0] # Remove extraneous tuple layer
    
    raw = [] # Create blank data structure
    
    start = time.time() # Start timer
    subscribe(sock, sensors) # Subscribe to feed
    while time.time() < start + dur: # Until the timer reaches dur
        val = getval(sock) # Receive value
        raw.extend(val) # Append it to an overall data structure
    unsubscribe(sock, sensors) # Unsubscribe from feed
    
    data = pandas.DataFrame(raw) # Convert to data frame
    data.Time = data.Time - data.Time[0] # Adjust times to start at 0
    data.sort_values("Time") # Reorder data chronologically
    data.index = range(len(data)) # Replace indices
    
    return data

def main():
    serverAddress = ("127.0.0.1", 28000) # Setup server ip and port, by defaul it uses localhost
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Initialise socket object
    sock.connect(serverAddress) # Connect socket to server
    
    sock.sendall( "device_list\r\n".encode() ) # Request list of devices
    resp = sock.recv(1024) # Get response
    devices = re.search(r'\|(.*?)Empatica_E4', resp.decode()).group(1).strip() # Strip response for just device ID
    sock.sendall( "device_connect {}\r\n".format(devices).encode() ) # Send connection request to device
    sock.settimeout(10)
