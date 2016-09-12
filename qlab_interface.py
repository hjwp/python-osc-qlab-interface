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
        t.join(timeout=0.3)
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


    def select_next_cue(self):
        old = self.get_cue_property('selected', 'number')
        self.client.send_message('/select/next')
        cue_no = self.get_cue_property('selected', 'number')
        while  cue_no == old:
            cue_no = self.get_cue_property('selected', 'number')
        return cue_no




def main():
    # example script using the interface to 
    # run through cues one by one and print
    # any titles' cue numbers and text
    interface = Interface()
    interface.client.send_message('/select/0')
    while True:
        caption_type = interface.get_cue_property('selected', 'type')
        if caption_type == 'Titles':
            text = interface.get_cue_text('selected')
            cue_no = interface.get_cue_property('selected', 'number')
            print(cue_no, text)
            if text.lower().strip() == 'the end':
                break
        print()
        interface.select_next_cue()


if __name__ == '__main__':
    main()

