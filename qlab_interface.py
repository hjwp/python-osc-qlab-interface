# import asyncio
import json
import socket
import sys
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
        parts = raw.split('\x00')
        json_message = parts[5]
        try:
            self.last_message = json.loads(json_message)
        except json.decoder.JSONDecodeError as e:
            print('Error. server response:', repr(json_message))
            self.last_message = None

    def get_message(self):
        t = threading.Thread(target=self._get_message, daemon=True)
        t.start()
        t.join(timeout=1)
        return self.last_message
        

        


class Client:
    def __init__(self):
        self.client = udp_client.UDPClient('localhost', 53000)


    def send_message(self, address):
        print('sending message to', address)
        msg = osc_message_builder.OscMessageBuilder(address=address)
        self.client.send(msg.build())


    def get_cue_text(self, cue_no):
        print('getting cue text', cue_no)
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
        return self.server.get_message()



def main():
    interface = Interface()
    cue_text = interface.get_cue_text(10102)
    print(cue_text)
    cue_surface = interface.get_cue_property(10102, 'surfaceID')
    print(cue_surface)


if __name__ == '__main__':
    main()

