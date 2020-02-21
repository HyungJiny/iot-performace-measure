import requests
import json
import time

from configparser import ConfigParser


class HueLocalController():
    def __init__(self, bridge_ip, username):
        self.bridge_ip = bridge_ip
        self.bridge_id = ''
        if len(bridge_ip)==0: self._bridge_scan()
        self.username = username
        if len(username)==0: self._add_new_user()
        self.lights = {}

    def _bridge_scan(self):
        r = requests.get('https://discovery.meethue.com')
        bridge = json.loads(r.content.decode('utf-8')[1:-2])
        self.bridge_ip = bridge['internalipaddress']
        self.bridge_id = bridge['id']

    def _add_new_user(self):
        body = '{"devicetype":"local_control_hue_app"}'
        r = requests.post('http://{bridge}/api'.format(bridge=self.bridge_ip), data=body)
        r = json.loads(r.content.decode('utf-8')[1:-1])
        if 'error' in r.keys(): print(r['error']['description'])
        else: 
            self.username = r['success']['username']
            print('New username : {0}'.format(self.username))

    def lights_scan(self):
        r = requests.get('http://{bridge}/api/{username}/lights'.format(bridge=self.bridge_ip, username=self.username))
        self.lights = json.loads(r.content.decode('utf-8'))

    def turn_on(self, lightnumber=1, sat=254, bri=254, hue=10000):
        data_on = '{{"on":true, "sat":{sat}, "bri":{bri}, "hue":{hue}}}'.format(sat=sat, bri=bri, hue=hue)
        url = "http://{bridge}/api/{username}/lights/{lightnumber}/state".format(
                                                                        bridge=self.bridge_ip, 
                                                                        username=self.username,
                                                                        lightnumber=lightnumber)
        requests.put(url, data=data_on)

    def reading_mod(self, lightnumber=1):
        self.turn_on(lightnumber=lightnumber, sat=254, bri=178, hue=21241)

    def turn_off(self, lightnumber=1):
        data_off = '{"on":false}'
        url = "http://{bridge}/api/{username}/lights/{lightnumber}/state".format(
                                                                        bridge=self.bridge_ip, 
                                                                        username=self.username,
                                                                        lightnumber=lightnumber)
        requests.put(url, data=data_off)

    def all_lights_on(self):
        for light in self.lights.keys():
            self.turn_on(lightnumber=light)

    def all_lights_off(self):
        for light in self.lights.keys():
            self.turn_off(lightnumber=light)

if __name__ == "__main__":
    parser = ConfigParser()
    parser.read('hue_info.ini')

    hueLocalController = HueLocalController(parser.get('LOCALBRIDGE','bridge_ip'),
                                             parser.get('LOCALBRIDGE','username'))

    starttime = time.time()
    hueLocalController.lights_scan()
    hueLocalController.all_lights_off()
    print(time.time() - starttime)

