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
        self.last_message = json.loads(json_message)

    def get_message(self):
        t = threading.Thread(target=self._get_message, daemon=True)
        t.start()
        t.join(timeout=1)
        return self.last_message
        

        


class Client:
    def __init__(self):
        self.client = udp_client.UDPClient('localhost', 53000)

    def get_cue_text(self, cue_no):
        print('getting cue text', cue_no)
        msg = osc_message_builder.OscMessageBuilder(address='/cue/{}/text'.format(cue_no))
        self.client.send(msg.build())



class Interface:
    def __init__(self):
        self.server = Listener()
        self.client = Client()



def main():
    interface = Interface()
    interface.client.get_cue_text(10102)
    message = interface.server.get_message()
    print(message)


if __name__ == '__main__':
    main()

