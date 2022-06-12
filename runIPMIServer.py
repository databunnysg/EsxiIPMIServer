import time

import pandas
import sys
import subprocess
import FrontendIPMIServer as vbmcs
import BMCUtil as bmcutil
def startBMC(port="7623",ipmiusername="admin",ipmipassword="admin",ip="",vmid="",username="root",password="password123!"):
    bmcinstance = vbmcs.VirtualBMC(port,ipmiusername,ipmipassword,ip,vmid,username,password,"0.0.0.0")
    bmcinstance.listen(timeout=30)

if __name__ == '__main__':


    esxserverconfig = pandas.read_csv("esxiserverconfig.csv")
    #print(f'loading parameters: {sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7]}')
    if sys.argv[1]=="startallserver":
        stat =bmcutil.readBMCAllValue(esxserverconfig.iat[0,0],esxserverconfig.iat[0,1],esxserverconfig.iat[0,2])
        print("cleaning existing Frontend IPMI process")
        subprocess.Popen(["pkill","-f", "EsxiIPMIFrontendprocess"])
        print("starting Frontend IPMI servers")
        for index, row in stat.iterrows():
            print(f"Starting Frontend IPMI Server for {row['Hypervisorip']} {row['Name']} on port {row['Port']}")
            result = subprocess.Popen([sys.executable, "runIPMIServer.py",str(row['Port']),"admin","admin", row['Hypervisorip'],str(row['Vmid']),row['Username'],row['Password'],"EsxiIPMIFrontendprocess"])
    if len(sys.argv)>=7:
        # check existing BackendIPMIServer
        re=subprocess.Popen("ps -aux | grep BackendIPMIServer",stdout=subprocess.PIPE,shell=True)
        out,err= re.communicate()
        #if out.decode("utf-8").find(f"BackendIPMIServer 10.0.50.48") < 0:
        #print(out)
        #print(out.decode("utf-8").find(f"BackendIPMIServer.py {sys.argv[4]}"))
        output=out.decode("utf-8")
        print(output)
        print(len(output.split(f"BackendIPMIServer.py {sys.argv[4]}")))
        if len(output.split(f"BackendIPMIServer.py {sys.argv[4]}"))==1 :
            # Not found BackendIPMIServer in running process then we start new one
            print("starting BackendIPMIServer")
            print(f"BackendIPMIServer.py {sys.argv[4]} {sys.argv[6]} {sys.argv[7]}")
            subprocess.Popen([sys.executable, "BackendIPMIServer.py",sys.argv[4],sys.argv[6],sys.argv[7]])
        print(f"Subprocess Starting Frontend IPMI Server on port {sys.argv[1]} to BMC server {sys.argv[4]} vmid {sys.argv[5]}  ")
        startBMC(port=int(sys.argv[1]),ipmiusername=sys.argv[2],ipmipassword=sys.argv[3],ip=sys.argv[4],vmid=sys.argv[5],username=sys.argv[6],password=sys.argv[7])


