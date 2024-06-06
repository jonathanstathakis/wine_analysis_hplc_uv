---
date: 2024-04-12
---


## The Scientist and Engineer's Guide to Digital Signal Processing

[homepage](https://www.dspguide.com/)



### Chapter 1

- Digital Signal Processing arose from and is influenced by a diverse array of allied fields and industries, as fundamentally it is how computers see and communicate with the outside world.
- Each observation of a sample over time is known as a 'sample'.
- In telecommunications, DSP has enabled companies to generate and detect signaling tones, frequency band shifting, and filtering to remove noise such as power line hum.
    - Multiplexing:
        - using one channel to transmit multiple signals simultaneously. Telecom companies use this to maximise transmission capacity.
    - Compression:
        - In audio signals, the majority of the signal is redundant in that it is shared by neighboring samples. Algorithms can be used to 'compress' the signal, i.e. removing redundancy, and then 'uncompressing' at the destination.
    - Echo Control:
        - Antisignals to the input signal can be generated to cancel out echos. This is also used to handle 'squealing', and environmental noise, known as 'antinoise'.


- Speech recognition. Signals are processed via 'feature extraction' followed by 'feature matching': 
      - feature extraction involves the isolation of, for example, words, which are then analysed to determine its excitation and resonate frequencies.
      - Once analysed, it is **matched** to features in a collection to find the closest match.
  