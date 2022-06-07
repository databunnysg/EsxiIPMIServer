import pandas as pd
import json
from io import StringIO
from paramiko import SSHClient,AutoAddPolicy

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





