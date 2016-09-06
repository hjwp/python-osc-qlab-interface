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
        data, address = self.sock.recvfrom(8192)
        raw = data.decode('utf8')
        parts = list(filter(bool, raw.split('\x00')))
        json_message = parts[2]
        try:
            self.last_message = json.loads(json_message)
        except json.decoder.JSONDecodeError as e:
            print('Error. server raw response:', repr(raw))
            print('parts', parts)
            print(e)
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



class Interface:
    def __init__(self):
        self.server = Listener()
        self.client = Client()

    def get_cue_text(self, cue_no):
        return self.get_cue_property(cue_no, 'text')


    def get_cue_property(self, cue_no, name):
        self.client.send_message('/cue/{cue_no}/{name}'.format(**locals()))
        response = self.server.get_message()
        if response:
            return response.get('data')


    def set_cue_property(self, cue_no, name, value):
        self.client.send_message('/cue/{cue_no}/{name}'.format(**locals()), value=value)


def _fix_simple_cue_numbers(interface):
    interface.client.send_message('/select/40818')
    while True:
        cue_no = interface.get_cue_property('selected', 'number')
        print(cue_no)
        if cue_no:
            act = int(cue_no[:1])
            if act > 4:
                break
            scene = int(cue_no[1:3])
            number = int(cue_no[3:])
            new_no = '{}.{}.{}'.format(act, scene, number)
            interface.set_cue_property('selected', 'number', new_no)

        interface.client.send_message('/select/next')


def process_group(interface, group_cue_no):
    group_cues = interface.get_cue_property(group_cue_no, 'children')
    subgroup_no = 0
    item_no = 0
    for cue_info in group_cues:
        cue_no = cue_info.get('number')
        item_no += 1
        new_no = '{}.{}'.format(group_cue_no, item_no)
        cue_name = interface.get_cue_property(cue_no, 'name')
        cue_type = interface.get_cue_property(cue_no, 'type')

        if cue_type == 'Fade':
            target = interface.get_cue_property(cue_no, 'cueTargetNumber')
            new_no = '{}.off'.format(target)

        interface.set_cue_property(cue_no, 'number', new_no)
        if cue_name:
            print(cue_no, new_no, cue_name)
        else:
            text = interface.get_cue_property(new_no, 'text')
            print(cue_no, new_no, repr(text))
        interface.client.send_message('/select/{}'.format(new_no))

        if cue_type == 'Group':
            process_group(interface, new_no)





def _recursive_group_numbers(interface):
    start_act = 4
    start_scene = 3
    interface.client.send_message('/select/{act}.{scene}.1'.format(act=start_act, scene=start_scene))

    current_group_cue_no = None
    last_act, last_scene = None, None
    while True:
        cue_no = interface.get_cue_property('selected', 'number')
        act, scene, _ = cue_no.split('.', 3)
        if act != last_act or scene != last_scene:
            item_no = 1
        else:
            item_no += 1
        last_act, last_scene = act, scene

        cue_name = interface.get_cue_property('selected', 'name')
        cue_type = interface.get_cue_property('selected', 'type')
        new_no  = '{act}.{scene}.{item_no}'.format(**locals())

        interface.set_cue_property(cue_no, 'number', new_no)
        if cue_name:
            print(cue_no, new_no, cue_name)
        else:
            text = interface.get_cue_property('selected', 'text')
            print(cue_no, new_no, repr(text))

        if cue_type == 'Group':
            process_group(interface, new_no)

        if cue_no == '41551':
            break

        interface.client.send_message('/select/next')


def main():
    interface = Interface()
    # _fix_simple_cue_numbers(interface)
    # _recursive_group_numbers(interface)
    interface.client.send_message('/select/1.1.1')
    while True:
        caption_type = interface.get_cue_property('selected', 'type')
        if caption_type == 'Titles':
            print(interface.get_cue_text('selected'))
        print()
        interface.client.send_message('/select/next')

if __name__ == '__main__':
    main()

