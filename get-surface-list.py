# coding: utf-8
from pythonosc import osc_message_builder
from pythonosc import udp_client
client = udp_client.UDPClient('localhost', 53000)
# needs at least 1 cue to be in system
client.send(osc_message_builder.OscMessageBuilder(address='/cue/1/surfaceList').build())

