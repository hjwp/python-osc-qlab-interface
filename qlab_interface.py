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
        t.join(timeout=1)
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
        print('getting cue {} property {}'.format(cue_no, name))
        self.client.send_message('/cue/{cue_no}/{name}'.format(**locals()))
        response = self.server.get_message()
        if response:
            return response.get('data')


    def set_cue_property(self, cue_no, name, value):
        print('setting cue {} property {} to {}'.format(cue_no, name, value))
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


def main():
    interface = Interface()
    interface.client.send_message('/select/3.1.1')
    group_no = 0
    for _ in range(20):
        cue_no = interface.get_cue_property('selected', 'number')
        act, scene, number = cue_no.split('.', 3)
        cue_name = interface.get_cue_property('selected', 'name')
        cue_type = interface.get_cue_property('selected', 'type')
        if cue_type == 'Group':
            if 'Group' in cue_name:
                group_no += 1
                subgroup_no = 0
                item_no = 0
                new_no = '{act}.{scene}.{group_no}'.format(**locals())
            else:
                subgroup_no += 1
                new_no = '{act}.{scene}.{group_no}.{subgroup_no}'.format(**locals())
        else:
            item_no += 1
            new_no = '{group_name}.{item_no}'.format(group_name=new_no, item_no=item_no)
        print(cue_no, new_no)
        interface.client.send_message('/select/next')


if __name__ == '__main__':
    main()

