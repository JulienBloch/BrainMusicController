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

MEM_SIZE = 40
MEM_SIZE2 = 500
OPEN_EYES_CHECK_PERIOD = 500
BLINK_CHECK_PERIOD = 250
INIT_ZEROS = MEM_SIZE*[np.array([0.001, 0.001, 0.001, 0.001])]
EEG_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE2)
ALPHA_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE)
THETA_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE)
BETA_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE)
GAMMA_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE)
DELTA_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE)
COUNT = 0

weight_map = np.loadtxt('weights.csv', delimiter=',')

delta_open_weights = weight_map[0:4]
theta_open_weights = weight_map[4:8]
alpha_open_weights = weight_map[8:12]
beta_open_weights = weight_map[12:16]
gamma_open_weights = weight_map[16:20]
open_weights = [delta_open_weights, theta_open_weights, alpha_open_weights, beta_open_weights, gamma_open_weights]

EYE_STATE = True

def is_open():
    i = 0
    open_value = 0
    for mem in [DELTA_MEM, THETA_MEM, ALPHA_MEM, BETA_MEM, GAMMA_MEM]:
        open_value += np.sum(np.mean(np.exp(retrieve_memory(mem)), axis=0) * open_weights[i])
        i += 1
    print(open_value)
    if (open_value >= .1):
        return True
    return False

def encode_memory(memory, packet):
    memory.append(packet)

def retrieve_memory(memory):
    return np.array(memory)

def clear_eeg_memory():
    global EEG_MEM
    EEG_MEM.clear()
    EEG_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE)

def clear_freq_memory():
    global ALPHA_MEM, THETA_MEM, BETA_MEM, GAMMA_MEM, DELTA_MEM
    ALPHA_MEM.clear()
    THETA_MEM.clear()
    BETA_MEM.clear()
    GAMMA_MEM.clear()
    DELTA_MEM.clear()
    ALPHA_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE)
    THETA_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE)
    BETA_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE)
    GAMMA_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE)
    DELTA_MEM = deque(INIT_ZEROS, maxlen=MEM_SIZE)

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
    global COUNT
    global EEG_MEM
    eeg_packet = np.around(np.array([ch0, ch1, ch2, ch3]), decimals=3)
    encode_memory(EEG_MEM, eeg_packet)
    COUNT += 1
    if COUNT % BLINK_CHECK_PERIOD == 0:
        if is_double_blink():
            pause_play_song()
            # clear_eeg_memory()
    if COUNT % OPEN_EYES_CHECK_PERIOD == 0:
        if eye_changed():
            next_song()
            # clear_freq_memory()


def is_double_blink():
    # first compare average of last 150 packets to new packet
    emem = np.mean(retrieve_memory(EEG_MEM)[:, [0, 3]], axis=1)
    for i in range(len(emem) - 150 - 10 - 20 - 150 - 20):
        avg = np.mean(emem[i:i+150], axis=0)
        for j in range(10):
            intens_ratio = emem[i+150+j] / avg
            # print(j)
            if (intens_ratio < .945 and intens_ratio != 0):
                # print('a')
                for k in range(5, 25):
                    # print(intens_ratio)
                    if (emem[i+150+j+k] > avg / intens_ratio / 1.04):
                        for l in range(20, 170):
                            if (emem[i+150+j+k+l] < intens_ratio * avg):
                                for k in range(5, 25):
                                    if (emem[i+150+j+k] > avg / intens_ratio / 1.04):
                                        print('Pause / Play')
                                        return True
    return False

def eye_changed():
    global EYE_STATE
    new_eye_state = is_open()
    if (EYE_STATE != new_eye_state):
        changed = True
        EYE_STATE = new_eye_state
        print('Changing')
        return True
    return False

def pause_play_song():
    os.system("pytify -pp")

def next_song():
    os.system("pytify -n")

def start():
    """
    Starts a UDP server on localhost:5000 listening for incoming OSC data on /muse/eeg.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="192.168.1.86",
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
