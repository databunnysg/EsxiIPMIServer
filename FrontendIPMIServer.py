import pyghmi.ipmi.bmc as bmc
import redis
from io import StringIO
import pandas as pd
import json

POWEROFF = 0
POWERON = 1
# Boot device maps
GET_BOOT_DEVICES_MAP = {
    'network': 4,
    'hd': 8,
    'cdrom': 0x14,
}

SET_BOOT_DEVICES_MAP = {
    'network': 'network',
    'hd': 'hd',
    'optical': 'cdrom',
}
IPMI_COMMAND_NODE_BUSY = 0xC0
# Invalid data field in request
IPMI_INVALID_DATA = 0xcc


class VirtualBMC(bmc.Bmc):

    def __init__(self, port="", username='admin', password='password',ip="", vmid="",  esxusername='root',
                 esxpassword='password123!', address="0.0.0.0"):
        super(VirtualBMC, self).__init__({username: password},
                                         port=port, address=address)
        self.ip = ip
        self.username = username
        self.password = password
        self.esxusername = esxusername
        self.esxpassword = esxpassword
        self.vmid = vmid
        self.port = port
        self.r = redis.Redis(host='localhost', port=8003, db=0)

    def get_boot_device(self):
        return 0

    def _remove_boot_elements(self, parent_element):
        return 0

    def set_boot_device(self, bootdevice):
        return 0

    def get_power_state(self):
        print("Getting power state from BMC Server for %s" % self.vmid)
        df = pd.read_csv(StringIO(self.r.hget("hypervisoripmistatus", self.ip).decode("utf-8")))
        # df = pd.read_csv(StringIO(r.hget("hypervisoripmistatus", "10.0.50.48")))
        result = df.query(f"Vmid=={self.vmid}")
        ddf = result.copy()
        ddf['Password'] = "*****"
        print(ddf)
        #result = df.query(f"Vmid==3")
        if result.iat[0, 3].find("on")>0:
            print("Return POWER status ON")
            return POWERON
        if result.iat[0, 3].find("off")>0:
            print("Return POWER status OFF")
            return POWEROFF
        return POWEROFF

    def pulse_diag(self):
        return ''

    def power_off(self):
        print("Execute power off from BMC %s" % self.vmid)
        self.r.lpush("hypervisoripmiaction",
                     f'{{"action":"off","username":"{self.esxusername}","password":"{self.esxpassword}","vmid":"{self.vmid}","ip":"{self.ip}"}}')

    def power_on(self):
        print("Execute power on from BMC %s" % self.vmid)
        self.r.lpush("hypervisoripmiaction",
                     f'{{"action":"on","username":"{self.esxusername}","password":"{self.esxpassword}","vmid":"{self.vmid}","ip":"{self.ip}"}}')

    def power_shutdown(self):
        print("Execute power shutdown from BMC %s" % self.vmid)
        self.r.lpush("hypervisoripmiaction",
                     f'{{"action":"shutdown","username":"{self.esxusername}","password":"{self.esxpassword}","vmid":"{self.vmid}","ip":"{self.ip}"}}')

    def power_reset(self):
        print("Execute reset from BMC %s" % self.vmid)
        self.r.lpush("hypervisoripmiaction",
                     f'{{"action":"reset","username":"{self.esxusername}","password":"{self.esxpassword}","vmid":"{self.vmid}","ip":"{self.ip}"}}')
"""
    def power_reboot(self):
        print("Execute reboot from BMC %s" % self.vmid)
        self.r.lpush("hypervisoripmiaction",
                     f'{{"action":"reboot","username":"{self.esxusername}","password":"{self.esxpassword}","vmid":"{self.vmid}","ip":"{self.ip}"}}')
"""

def testVirtualBMC():
    vbmc = VirtualBMC(ip="10.0.50.48", username="root", password="password123!", port="7624", vmid="3")
    vbmc.power_on()
    result = json.loads(vbmc.r.lpop("hypervisoripmiaction"))
    print(result["action"] == 'on')
    vbmc.power_off()
    result = json.loads(vbmc.r.lpop("hypervisoripmiaction"))
    print(result["action"] == 'off')
    vbmc.power_shutdown()
    result = json.loads(vbmc.r.lpop("hypervisoripmiaction"))
    print(result["action"] == 'shutdown')
    vbmc.power_reset()
    result = json.loads(vbmc.r.lpop("hypervisoripmiaction"))
    print(result["action"] == 'reset')
    vbmc.power_reboot()
    result = json.loads(vbmc.r.lpop("hypervisoripmiaction"))
    print(result["action"] == 'reboot')
