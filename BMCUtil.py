import pandas as pd
import json
from io import StringIO
from paramiko import SSHClient,AutoAddPolicy






'''
Databunny BMC board supports controlling 16 motherboard poweron/off/reset action and power status reading from usb serial port. 
BMC board contains 22-53 digital i/o pin and A0-15 analog pin.
Pin 22-53 used for control motherboard power on/off and reset pin.
Pin A0-15 used for read motherboard power led voltage output to check power status.

BMC output result in below format every 1 second, need to remove <linebreak> and convert it to json
The value of A0-A15 represent the voltage 0-1023 (0v-5v) reading from power pin reading from power status pin. BMC power status reading might be inaccurate when BMC and motherboard is not connected or motherboard PSU is not connected with standby power. 
After BMC connected with motherboard and PSU read, if machine power status off status reading should be a very low value 0-10, after poweron reading should be exactly 1023.  

Sample output of reading: b'{"COUNTER":2,"HARDWAREID":"DATABUNNY-BMC-02-A0-A15-D22-D53","A0":0,"A1":0,"A2":0,"A3":0,"A4":1014,"A5":1022,"A6":1017,"A7":1017,"A8":1023,"A9":1021,"A10":0,"A11":1012,"A12":1023,"A13":1023,"A14":1022,"A15":1023}<linebreak>\r\n'

COUNTER WILL AUTO INCREASE BY 1 FOR EACH SECOND AFTER CONNECTION WAS MADE
HARDWAREID IS THE BMC ID UNIQUE TO EACH BMC

'''
def readBMCPinValue(hostid=None,action=None):
    pass
def readBMCAllValue(ip, username, password):
    client = SSHClient()
    # client.load_system_host_keys()
    # client.load_host_keys('~/.ssh/known_hosts')
    client.set_missing_host_key_policy(AutoAddPolicy())
    # client.connect('10.0.50.48', username='root', password='password123!')
    client.connect(ip, username=username, password=password)
    # stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/getallvms')
    stdin, stdout, stderr = client.exec_command(
        """vim-cmd vmsvc/getallvms | tail -n+1 | awk '{print $1","$2}'""")

    # Optionally, send data via STDIN, and shutdown when done
    output = stdout.read().decode("utf8")
    sio = StringIO(output)
    df = pd.read_csv(sio, sep=",")
    df = df.sort_values(df.keys()[0])
    df['Port'] = [7623 + int(df.iat[i, 0]) for i in list(range(0, len(df)))]
    # print(df)
    for i, row in df.iterrows():
        stdin, stdout, stderr = client.exec_command("""vim-cmd vmsvc/power.getstate %s | tail -n 1 """ % row[0])
        #print("""vim-cmd vmsvc/power.getstate %s""" % df.iat[i, 0])
        out = stdout.read().decode("utf8")
        #print(f'STDOUT: {out}')
        df.at[i, "Status"] = out.rstrip()

    stdin, stdout, stderr = client.exec_command("""hostname""")
    hostname = stdout.read().decode("utf8").rstrip()
    df['Hypervisorname'] = hostname
    df['Hypervisorip']=ip
    df['Username']=username
    df['Password']=password
    ddf = df.copy()
    ddf['Password']="*****"
    print(ddf)
    #print(df[["Vmid","Name","Port","Status","Hypervisorname","Hypervisorip"]])
    # Print output of command. Will wait for command to finish.
    #print(f'STDOUT: {stdout.read().decode("utf8")}')
    #print(f'STDERR: {stderr.read().decode("utf8")}')

    client.close()
    return df


def readBMCAllHostDataFrame():
    pass

'''
BMC accept json as input in this format:
{actionname:pinnumber} follow by \r\n (\r\n is required, BMC will check \r 13 to parse JSON) 

poweron/reset action will set pin with low voltage for 1 second then give back high voltage back to pin 
poweroff action will set pin with low voltage for 4 second then give back high voltage back to pin 

{'poweron':'22'}
{'poweroff':'22'}
{'reset':'24'}

'''
def writeBMCValue(ip=None,username=None,password=None,vmid=None,action=None):
    print(f"Execute writeBMCValue {ip} {username} {password} {vmid} {action}")
    client = SSHClient()
    # client.load_system_host_keys()
    # client.load_host_keys('~/.ssh/known_hosts')
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(ip, username=username, password=password)
    # client.connect('10.0.50.48', username='root', password='password123!')
    stdin, stdout, stderr = client.exec_command(f'vim-cmd vmsvc/power.{action} {vmid}')
    # Optionally, send data via STDIN, and shutdown when done
    output = stdout.read().decode("utf8")
    print(output)
def testPowerOn():
    writeBMCValue("10.0.50.48","root","password123!","3","on")
def testPowerOff():
    writeBMCValue("10.0.50.48","root","password123!","3","off")
def testGetPowerStatus():
    pass
def testreadBMCPinValue():
    readBMCAllValue("10.0.50.48", "root", "password123!")





