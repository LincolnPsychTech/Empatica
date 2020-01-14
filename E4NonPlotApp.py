from PyQt5 import QtGui, QtWidgets, QtCore  # Import the PyQt4 module we'll need
from PyQt5.QtWidgets import QFileDialog 
import simpleUI
import sys # We need sys so that we can pass argv to QApplication
import socket
from functools import partial
import re
import numpy as np
import multiprocessing as mp
import csv

class E4AppNoPlot(QtWidgets.QMainWindow, simpleUI.Ui_MainWindow):
    def __init__(self, pool):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
        self.dataBuffer = []
        # processes pool for sorting data in parallel
        self.pool = pool

        self.streamList = ["acc", "bvp", "gsr", "temp", "ibi","tag"]

        self.streamsDictionary = {   
            'acc': ["device_subscribe acc ON\r\n", "device_subscribe acc OFF\r\n"],
            'bvp': ["device_subscribe bvp ON\r\n", "device_subscribe bvp OFF\r\n"],
            'gsr': ["device_subscribe gsr ON\r\n", "device_subscribe gsr OFF\r\n"],
            'ibi': ["device_subscribe ibi ON\r\n", "device_subscribe ibi OFF\r\n"],
            'tmp': ["device_subscribe tmp ON\r\n", "device_subscribe tmp OFF\r\n"],
            'tag': ["device_subscribe tag ON\r\n", "device_subscribe tag OFF\r\n"]
        }

        # Setup server ip and port, by defaul it uses localhost
        self.host_ip, self.server_port = "127.0.0.1", 28000
        self.server_address = (self.host_ip, self.server_port)
        # Initialise socket object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect socket to server
        self.sock.connect(self.server_address)

        # A few of the commands that can be sent to the server
        self.deviceList = "device_list\r\n"
        # Variable that holds the device's identifier
        # It should be different for each device
        # THIS WILL ONLY WORK WITH A SINGLE DEVICE
        # TODO
        # FOR MORE DEVICES : maybe treat the app as a node and just launch more nodes?
        # For more devices a streaming service that collects, computes and stores the data is prefereable.
        self.deviceIdentifier = self.GetDeviceList(self.deviceList, self.sock)
        self.conn = "device_connect {}\r\n".format(self.deviceIdentifier)
        self.ConnectToDevice()
        self.isRecording = False

        # Stream Dump lists
        self.accData = []
        self.bvpData = []
        self.gsrData = []
        self.ibiData = []
        self.tmpData = []
        self.tagData = []

        # Setup Status Label
        self.statusLabel.setStyleSheet("color: blue")
        self.statusLabel.setText("Connecting to Server")

        self.ConnectToServer()

        # Setup button controls
        self.resetButton.clicked.connect(self.ConnectToServer)

        self.CloseButton.clicked.connect(self.CloseAndSave)
    
    def CloseAndSave(self):
        self.isRecording = False
        self.pool.close()
        self.pool.join()
        self.SaveData()
        # print("My take: {}".format(self.bvpData))
        print("Dying")

    def ConnectToServer(self):
        # Here we keep a list of the output of the ConnectToStream function
        truthTable = []
        for sensor in self.streamList:
            truthTable.append(self.ConnectToStream(sensor, self.sock, self.streamsDictionary ))

        if all(truthTable):
            self.statusLabel.setStyleSheet("color: green")
            self.statusLabel.setText("Connectd")
            self.isRecording = True
        elif not all(truthTable):
            self.statusLabel.setStyleSheet("color: red")
            self.statusLabel.setText("Disconnected, please reset")
        else:
            self.statusLabel.setStyleSheet("color: orange")
            self.statusLabel.setText("Partially connected, please reset")

    def ConnectToStream(self,msg, sock, streamsDictionary):
        
        sock.sendall(streamsDictionary[msg][0].encode())
        isConnecting = True
        i = 0
        isConnected = False
        # 
        while isConnecting & (i < 20):
            recieved = sock.recv(1024)
            streamBuffer = recieved.decode()
            if "R device_subscribe {} OK".format(msg) in streamBuffer:
                isConnecting = False
                isConnected = True
            print(streamBuffer)
            i += 1
            print(i)
        if isConnected:
            print("{} stream subscribed OK".format(msg))
            return True
        else:
            print("{} stream subscribed OK".format(msg))
            return False

    def ConnectToDevice(self):
        self.sock.sendall(self.conn.encode())
        recieved = self.sock.recv(1024)
        print("Bytes Recieved: {}".format(recieved.decode()))

    def GetDeviceList(self,msg, sock):
        sock.sendall(msg.encode())
        recieved = sock.recv(1024)
        recieved = recieved.decode()
        inputDump = re.search(r'\|(.*?)Empatica_E4', recieved).group(1).strip()
        print(inputDump)
        return inputDump

    def SplitDump(self, input):
        tempSplit = input.split()
        result = []
        for item in tempSplit:
            if 'E4_' in item:
                result.append([])
            result[-1].append(item)
        return result
    
    def SaveData(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        accFile = file + "\\ACC.csv"
        
        with open(accFile, 'w',newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(["Sensor","TimeStamp", "X", "Y", "Z"])
            for row in self.accData:
                writer.writerow(row)

        bvpFile = file + "\\BVP.csv"
        
        with open(bvpFile, 'w',newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(["Sensor","TimeStamp", "Value"])
            for row in self.bvpData:
                writer.writerow(row)
        
        gsrFile = file + "\\GSR.csv"
        
        with open(gsrFile, 'w',newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(["Sensor","TimeStamp", "Value"])
            for row in self.gsrData:
                writer.writerow(row)

        ibiFile = file + "\\IBI.csv"
        
        with open(ibiFile, 'w',newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(["Sensor","TimeStamp", "Value"])
            for row in self.ibiData:
                writer.writerow(row)
        
        tmpFile = file + "\\Temp.csv"
        
        with open(tmpFile, 'w',newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(["Sensor","TimeStamp", "Value"])
            for row in self.tmpData:
                writer.writerow(row)
        
        tagFile = file +"\\Tag.csv"

        with open(tagFile, 'w',newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(["Sensor","TimeStamp"])
            for row in self.tagData:
                writer.writerow(row)

def GetResults(app, x, streamType=""):
        # print("I gots results")
        if streamType == "acc":
            app.accData.extend(x)
        elif streamType == "bvp":
            app.bvpData.extend(x)
        elif streamType == "gsr":
            app.gsrData.extend(x)
        elif streamType == "temp":
            app.tmpData.extend(x)
        elif streamType == "ibi":
            app.ibiData.extend(x)
        elif streamType == "tag":
            app.tagData.extend(x)

def SortData(data, streamType):
        if data:
            if streamType == "acc":
                acc = [a for a in data if a[0] == 'E4_Acc']
                result = [[a[0], float(a[1]), float(a[2]), float(a[3]), float(a[4])] for a in acc]
                return result
            elif streamType == "bvp":
                bvp = [ a for a in data if a[0] == 'E4_Bvp']
                result = [[a[0], float(a[1]), float(a[2])] for a in bvp]
                return result
            elif streamType == "gsr":
                gsr = [ a for a in data if a[0] == 'E4_Gsr']
                result = [[a[0], float(a[1]), float(a[2])] for a in gsr]
                return result
            elif streamType == "temp":
                temp = [a for a in data if a[0] == 'E4_Temperature']
                result = [[a[0], float(a[1]), float(a[2])] for a in temp]
                return result
            elif streamType == "ibi":
                ibi = [a for a in data if a[0] == 'E4_Ibi' or a[0] == 'E4_Hr']
                result = [[a[0], float(a[1]), float(a[2])] for a in ibi]
                return result
            elif streamType == "tag":
                tag = [a for a in data if a[0] == 'E4_Tag']
                result = [[a[0], float(a[1]), float(a[2])] for a in tag]
                return result
            else:
                return []
        else:
            return []

def update(app, pool):
    if app.isRecording:
        try:
            recieved = app.sock.recv(2048)
            tempData = recieved.decode()
            # print("Recieved")
            tempData = app.SplitDump(tempData)
            # print("split Success")
            
            # print("GOTCHA!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            app.dataBuffer.append(tempData)
        except:
            print("No Data Recieved")
    if app.dataBuffer:
        # partialSort = partial(SortData, data=dataBuffer[0])
        # print(app.dataBuffer[0])
        results = [pool.apply_async(SortData, args=(app.dataBuffer[0], typeStream), callback=partial(GetResults, app, streamType=typeStream)) for typeStream in app.streamList]
        for r in results:
            r.wait()
        

        del app.dataBuffer[0]

def main():
    
    pool = mp.Pool()
    
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = E4AppNoPlot(pool)          

    
    
    timer = QtCore.QTimer()
    timer.timeout.connect(partial(update, form, pool))
    timer.start(0)
    

    form.show()                         # Show the form
    sys.exit(app.exec_()) 
    
if __name__ == '__main__':              # if we're running file directly and not importing it
    main()                 