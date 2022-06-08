# Databunny IPMIServer

IPMIServer expose itself as BMC server runs with IPMI LAN 2.0 IPMI protocal. IPMIServer connects to vmware esxi servers read vms power status and perform power on/off/reset/shutdown action. 

The typical use case is connect Databunny IPMIServer from bare metal controll system from MAAS. 

# Demo install

[![asciicast](https://asciinema.org/a/500145.svg)](https://asciinema.org/a/500145?t=25&speed=4&theme=solarized-dark)

# Use case in MAAS 
- Select IPMI power options
- Fill in IPMI server address, port, admin/admin
<img width="568" alt="image" src="https://user-images.githubusercontent.com/53151832/172476589-3a95342d-b57f-4c12-9d39-aba8560087ac.png">
- MAAS now connected to vm through IPMI server just like a real BMC enabled physical server.
<img width="730" alt="image" src="https://user-images.githubusercontent.com/53151832/172476875-acebb6a5-d614-4c92-9325-97495a6f64b5.png">

# Usage

<pre><code>
conda create --name ipmiserver
conda activate ipmiserver
git pull https://github.com/databunnysg/EsxiIPMIServer.git
cd EsxiIPMIServer
start.sh
</code></pre>

- Edit the esxi server ip, username, password in esxiserverconfig.csv file.  Enable ssh access from esxi server web management interface. 

- Start IPMI Server

- Option1: Start IPMI Server for all vms inside esxi server
  start.sh 
- Option2: Start IPMI server for individual vm inside esxi server  
  python BackendIPMIServer.py esxiipserverip esxiusername esxipassword
  python runIPMIServer.py port ipmiusername ipmipassword esxiserverip esxiusername esxipassword

# Components
- FrontendIPMIServer.py 
Start one or all IPMIServer from port 7623+ and receive IPMI connection and communicate with backend BMCServer through redis port 8002
- BackendBMCServer.py 
Start a redis server on port 8002 as message broker, use BMCUtil receive update ESXI server vm status.
- BMCUtil.py 
Utility tool to communicate with esxi server.
- runIPMIServer.py
Subprocess manager to start and stop FrontendIPMIServer and BackendIPMIServer
 
# License
- Opensource IPMIServer release support 1 esxi server under AGPL license. For multiple esxi servers, close source license, integration development and commercial support please contact contact@databunny.sg.
