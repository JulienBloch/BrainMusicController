"""
OSC server that receives on osc.udp://localhost:5000 from muse-io.

Command to start the Muse OSC server on UDP port 5000:
muse-io --device Muse-9294 --osc osc.udp://localhost:5000

"""

import threading
import argparse
import numpy as np
import os
from datetime import timedelta, datetime

from pythonosc import dispatcher
from pythonosc import osc_server

from collections import deque
EEG_MEM = deque(maxlen=750) #3 seconds at 250 packets per second
ALPHA_MEM = deque(maxlen=750)
THETA_MEM = deque(maxlen=750)
BETA_MEM = deque(maxlen=750)
GAMMA_MEM = deque(maxlen=750)
DELTA_MEM = deque(maxlen=750)
COUNT = 0

def encode_memory(memory, packet):
    memory.append(packet)

def retrieve_memory(memory):
    return np.array(memory)

def alpha_handler(x, y, a0, a1, a2, a3):
    global ALPHA_M
    alpha_packet = np.around(np.array([a0, a1, a2, a3]), decimals=3)
    encode_memory(ALPHA_MEM, alpha_packet)

def theta_handler(x, y, t0, t1, t2, t3):
    global THETA_MEM
    theta_packet = np.around(np.array([t0, t1, t2, t3]), decimals=3)
    encode_memory(THETA_MEM, theta_packet)

def beta_handler(x, y, b0, b1, b2, b3):
    global BETA_MEM
    beta_packet = np.around(np.array([b0, b1, b2, b3]), decimals=3)
    encode_memory(BETA_MEM, beta_packet)

def gamma_handler(x, y, g0, g1, g2, g3):
    global GAMMA_MEM
    gamma_packet = np.around(np.array([g0, g1, g2, g3]), decimals=3)
    encode_memory(GAMMA_MEM, gamma_packet)

def delta_handler(x, y, d0, d1, d2, d3):
    global DELTA_MEM
    delta_packet = np.around(np.array([d0, d1, d2, d3]), decimals=3)
    encode_memory(DELTA_MEM, delta_packet)

def eeg_handler(x, y, ch0, ch1, ch2, ch3, AUX):
    """
    Event handler that gets called for every data point sent over from the Muse headset.
    """
    eeg_packet = np.around(np.array([ch0, ch1, ch2, ch3]), decimals=3)
    encode_memory(EEG_MEM, eeg_packet)
    global COUNT
    COUNT += 1

def start():
    """
    Starts a UDP server on localhost:5000 listening for incoming OSC data on /muse/eeg.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="192.168.1.97",
                        help="The ip to listen on")

    parser.add_argument("--port",
                        type=int,
                        default=5000,
                        help="The port to listen on")
    args = parser.parse_args()
    print("listening on ip", args.ip, "with port", args.port)

    d = dispatcher.Dispatcher()
    d.map("/debug", print)
    d.map("/muse/eeg", eeg_handler, "EEG")
    d.map("/muse/elements/alpha_absolute", alpha_handler, "ALPHA")
    d.map("/muse/elements/beta_absolute", beta_handler, "BETA")
    d.map("/muse/elements/theta_absolute", theta_handler, "THETA")
    d.map("/muse/elements/gamma_absolute", gamma_handler, "GAMMA")
    d.map("/muse/elements/delta_absolute", delta_handler, "DELTA")

    server = osc_server.BlockingOSCUDPServer((args.ip, args.port), d)

    print("OSC server started {}".format(server.server_address))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")

if __name__ == '__main__':

    try:
        osc_thread = threading.Thread(target=start)
        start()

    except KeyboardInterrupt:
        print("Stopped.")