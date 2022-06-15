import time

from redislite import Redis
import redis as red
import BMCUtil as bmcutil
from io import StringIO
from paramiko import SSHClient,AutoAddPolicy
import pandas as pd
import json
import sys
import psutil
if __name__ == '__main__':
    if len(sys.argv)!=4:
        print("Require esxi ip, username, password to start. Now exit.")
        exit(-1)
    esxip = sys.argv[1]
    esxusername = sys.argv[2]
    esxpassword = sys.argv[3]
    if len(str([proc.cmdline() for proc in psutil.process_iter()]).split("BackendIPMIServerPowerStatus"))> 2:
        # Not found BackendIPMIServer in running process then we start new one
        print("BackendIPMIServerPowerStatus already started, only one instance should exists, now existing...")
        exit(0)

    print(f"Starting BackendIPMIServer for {esxip} connecting to esxi server ...")
# try create embeded redis server on port 8002
# if port already taken assume redis already running and connect with redis client instead
try:
    redis=Redis(serverconfig={'port': '8003'})
except:
    print("Redis Server Already Started")
    # sys.exit(0)
    redis = red.Redis(host='localhost', port=8003, db=0)
#   redis=Redis()

#redis.lpush("actionqueue",'{"action":"poweron","hostid":"00:E0:7A:68:07:57"}')


def checkhoststatus():

    #df = bmcutil.readBMCAllValue("10.0.50.48", "root", "password123!")
    df = bmcutil.readBMCAllValue(esxip,esxusername,esxpassword)
    redis.hset("hypervisoripmistatus",df.iat[0,5],df.to_csv(index=False))

def checkactionqueue():
    action = redis.rpop("hypervisoripmiaction")
    #print(f"Received IPMI action {action}")
    #action = """{"ip":"10.0.50.48","action":"on","vmid":"3","username":"root","password":"password123!"}"""
    if action is not None:
        # action = '{"poweron":"00:E0:7A:68:07:57"}'
        actiondict=json.loads(action)
        statusstr = redis.hget("hypervisoripmistatus", actiondict['ip']).decode("utf-8")
        if statusstr:
            df = pd.read_csv(StringIO(statusstr))
        else:
            return

        if actiondict['action']=="on":
            print(f"Execute power on to BMC {actiondict['ip']} {actiondict['vmid']}")
            #if df.query(f"Vmid=={actiondict['vmid']}").iat[0,3].find("on")>0:
            #    print("already on")
            #else:
            #    # vmid=3
            bmcutil.writeBMCValue(actiondict['ip'],actiondict['username'],actiondict['password'],actiondict['vmid'],"on")
        if actiondict['action']=="off":
            print(f"Execute power off to BMC {actiondict['ip']} {actiondict['vmid']}")
            #if df.query(f"Vmid=={actiondict['vmid']}").iat[0,3].find("off")>0:
            #    print("already off")
            #else:
                # vmid=3
            bmcutil.writeBMCValue(actiondict['ip'],actiondict['username'],actiondict['password'],actiondict['vmid'],"off")
        if actiondict['action'] == "shutdown":
            print(f"Execute shutdown to BMC {actiondict['ip']} {actiondict['vmid']}")
            if df.query(f"Vmid=={actiondict['vmid']}").iat[0,3].find("off")>0:
                print("already off")
            else:
                # vmid=3
                bmcutil.writeBMCValue(actiondict['ip'],actiondict['username'],actiondict['password'],actiondict['vmid'],"shutdown")
        if actiondict['action'] == "reboot":
            print(f"Execute reboot to BMC {actiondict['ip']} {actiondict['vmid']}")
            if df.query(f"Vmid=={actiondict['vmid']}").iat[0,3].find("off")>0:
                print("already off")
            else:
                # vmid=3
                bmcutil.writeBMCValue(actiondict['ip'],actiondict['username'],actiondict['password'],actiondict['vmid'],"reboot")
        if actiondict['action'] == "reset":
            print(f"Execute reset to BMC {actiondict['ip']} {actiondict['vmid']}")
            if df.query(f"Vmid=={actiondict['vmid']}").iat[0,3].find("off")>0:
                print("already off")
            else:
                # vmid=3
                bmcutil.writeBMCValue(actiondict['ip'],actiondict['username'],actiondict['password'],actiondict['vmid'],"reset")
'''

{'action':'poweron','hostid':''}
{'action':'poweroff','hostid':''}
{'action':'reset','hostid':''}
{'action':'shutdown','hostid':''}

'''

while True:
    try:
        checkhoststatus()
        #checkactionqueue()
    finally:
        pass

    #time.sleep(0.1)

