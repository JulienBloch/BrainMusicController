# BrainMusicController for CalHacks 4.0
# Authors: Julien Bloch, Ashton Teng, Julie Deng, Aditya Palacharla

## Inspiration
Want to empower people, especially those who cannot use their hands, to take control of their music by using their brain waves

## What it Does
Controls music playback via blinking and brain wave changes
Blinking twice in succession will pause/play the current song, and changing brain waves between a calm/excited state will switch you into a calm/excited playlist, respectively.

## How did you Make It
- The Muse headset was used to collect EEG and EMG data from the head via four electrodes on the forehead.
- Data from the Muse is streamed real time to the Muse Monitor app, which then streams it via WiFi to a specific IP and port via UDP and OSC.
- A computer listens in on the port and receives the EEG data via the python package python-osc. Specifically, we receive information from each of the four electrode on the raw EEG trace data, and five frequency bands - alpha, beta, theta, gamma, and delta waves, which are associated with different brain states.
- The real time streaming EEG and frequency data is formatted as Python Deque which keeps a fixed size memory of 3 seconds of data. The memory is read every second to determine whether there was a blink or a brain state change.
- A blink is registered when the raw EEG signal from the appropriate electrodes register a drop of sufficient magnitude, followed by a return to baseline, followed by a similar drop. This is tested in a scrolling window to register when the user blinks twice in succession.
- An ordinary least squares binary classifier determines whether the user’s eyes are open or closed. The weights for the classifier were generated from running OLS on tens of thousands of data points and can be calibrated for individuals with a single scan (code provided). A three second scrolling window determines whether the user purposely changed their eyes to open or closed.

## Challenges we ran into
- Gathering non-noise EEG data is considerably difficult. We tried both the OpenBCI Ganglion and the Muse, which a variety of software packages and APIs. In the end we found reliable eye blink and simple brain state change from calm/alert signal with the Muse.
- Streaming data from Muse to Python is difficult due to little developer support from Muse. We tried a variety of possible mediums to transmit data - over WiFi, over Bluetooth. 

## Accomplishments that we're proud of
-Collected, transmitted, processed, and classified reliable eye blink and brain stage signals. Reliability is arguably the biggest challenge in building brain computer interfaces.

## What we learned
-Reading EEG is complicated and inconsistent
-How to implement Spotify API

## What's next for BrainMusicController
Adding new functionalities such as being able to sort songs that you listen to into playlists based on emotions, which will be determined using EEG.

##Prizes that we would like to be considered for
All Overall Prizes, Best Beginner Hack, Best Entertainment Hack, Best Health Hack, Best Hardware Hack
