# import asyncio
import json
import socket
import sys
import time
from pythonosc import osc_message_builder
from pythonosc import udp_client

import threading


class Listener: 
    def __init__(self):
        print('starting listener')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', 53001))
        self.last_message = None


    def _get_message(self):
        data, address = self.sock.recvfrom(4096)
        raw = data.decode('utf8')
        parts = filter(bool, raw.split('\x00'))
        json_message = list(parts)[2]
        try:
            self.last_message = json.loads(json_message)
        except json.decoder.JSONDecodeError as e:
            print('Error. server raw response:', repr(raw))
            self.last_message = None

    def get_message(self):
        t = threading.Thread(target=self._get_message, daemon=True)
        t.start()
        t.join(timeout=0.2)
        return self.last_message
        

        


class Client:
    def __init__(self):
        self.client = udp_client.UDPClient('localhost', 53000)


    def send_message(self, address, value=None):
        msg = osc_message_builder.OscMessageBuilder(address=address)
        if value:
            msg.add_arg(value)
        self.client.send(msg.build())


    def get_cue_text(self, cue_no):
        self.send_message(address='/cue/{}/text'.format(cue_no))

    

class Interface:
    def __init__(self):
        self.server = Listener()
        self.client = Client()

    def get_cue_text(self, cue_no):
        self.client.get_cue_text(10102)
        return self.server.get_message()


    def get_cue_property(self, cue_no, name):
        self.client.send_message('/cue/{cue_no}/{name}'.format(**locals()))
        response = self.server.get_message()
        if response:
            return response.get('data')


    def set_cue_property(self, cue_no, name, value):
        self.client.send_message('/cue/{cue_no}/{name}'.format(**locals()), value=value)


def _fix_simple_cue_numbers():
    interface.client.send_message('/select/31003')
    while True:
        cue_no = interface.get_cue_property('selected', 'number')
        print(cue_no)
        if cue_no:
            act = int(cue_no[:1])
            if act > 3:
                break
            scene = int(cue_no[1:3])
            number = int(cue_no[3:])
            new_no = '{}.{}.{}'.format(act, scene, number)
            interface.set_cue_property('selected', 'number', new_no)
            

        interface.client.send_message('/select/next')


def process_group(interface, group_cue_no, prefix):
    group_cues = interface.get_cue_property(group_cue_no, 'children')
    subgroup_no = 0
    item_no = 0
    for cue_info in group_cues:
        cue_no = cue_info.get('number')
        item_no += 1
        new_no = '{}.{}'.format(prefix, item_no)
        cue_name = interface.get_cue_property(cue_no, 'name')
        cue_type = interface.get_cue_property(cue_no, 'type')

        if cue_type == 'Group':
            process_group(interface, cue_no, new_no)

        elif cue_type == 'Fade':
            target = interface.get_cue_property(cue_no, 'cueTargetNumber')
            new_no = '{}.off'.format(target)

        if cue_name:
            print(cue_no, new_no, cue_name)
        else:
            text = interface.get_cue_property(cue_no, 'text')
            print(cue_no, new_no, repr(text))
        interface.client.send_message('/select/{}'.format(cue_no))




def main():
    interface = Interface()
    interface.client.send_message('/select/3.5.58')
    current_group_cue_no = None
    item_no = 0

    for _ in range(20):
        item_no += 1
        cue_no = interface.get_cue_property('selected', 'number')
        act, scene, _ = cue_no.split('.', 3)
        cue_name = interface.get_cue_property('selected', 'name')
        cue_type = interface.get_cue_property('selected', 'type')
        new_no  = '{act}.{scene}.{item_no}'.format(**locals())

        if cue_name:
            print(cue_no, new_no, cue_name)
        else:
            text = interface.get_cue_property('selected', 'text')
            print(cue_no, new_no, repr(text))

        if cue_type == 'Group':
            process_group(interface, cue_no, new_no)

        interface.client.send_message('/select/next')


if __name__ == '__main__':
    main()

