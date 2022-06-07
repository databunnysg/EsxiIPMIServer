# Databunny IPMIServer

Databunny ESXIIPMIServer connects to esxi servers read vms and start IPMI Server for each vm inside ESXI Server on localhost IP.
The typical use case is connect Databunny ESXIIPMIServer from MAAS.  

# Demo install

[![asciicast](https://asciinema.org/a/500145.png)]([https://asciinema.org/a/500145?t=25&speed=4&theme=solarized-dark])


# License
- Opensource IPMIServer release support 1 esxi server under AGPL license. For multiple esxi servers, close source license, integration development and commercial support please contact contact@databunny.sg.

# Usage

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
 
