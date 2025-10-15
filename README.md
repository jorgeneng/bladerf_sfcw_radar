## Summary
SCORA (Stepped-frequency Coherent Radar Architecture) is a complete, open-source framework for building a high-range-resolution, coherent radar system using low-cost, commercial-off-the-shelf (COTS) hardware. The project is motivated by the need to make advanced radar technology more accessible for research, education, and community-driven development by providing a fully reconfigurable and replicable platform.   

The system architecture is based on a Nuand bladeRF Software-Defined Radio (SDR), chosen for its affordability and 2x2 MIMO capability, and is implemented within the GNU Radio framework. To achieve high range resolution on the bandwidth-limited SDR, SCORA employs the Stepped-Frequency Continuous-Wave (SFCW) technique, which synthesizes a wide effective bandwidth from a series of narrow-band sub-pulses.   

A key feature of the framework is its solution to the phase incoherence problem inherent in low-cost SDRs. By leveraging the bladeRF's 2x2 MIMO capability to create a reference channel (via loopback), the system measures and cancels the random phase errors introduced by the SDR's unsynchronized local oscillators, enabling fully coherent operation.   

The software uses a hybrid C++/Python design. A custom C++ block in GNU Radio handles real-time, low-latency hardware control, while a flexible Python chain performs the signal processing, calibration, and data logging.

## Radar Controller (C++)
The core of the SCORA framework is the Radar Controller, a custom C++ source block designed to run within the GNU Radio environment. It operates the bladeRF as a fully coherent Stepped-Frequency Continuous-Wave (SFCW) radar and is responsible for all real-time hardware control, waveform generation, and data streaming.   

The controller's architecture is built on a key design principle: the separation of high-level radar logic from low-level hardware control. This is achieved through two main C++ components:   

- BladerfDevice Class: This class serves as a dedicated hardware abstraction layer (HAL), encapsulating all direct API calls to the bladeRF library for device discovery, configuration, and control. Its most critical function is managing synchronous, timed data transmission and reception. It leverages the bladeRF's internal hardware timestamp counter to schedule transmit and receive events at precise future moments, which is essential for achieving phase coherence. This modular design provides the fundamental building blocks for any coherent radar system. Developers can extend this class to readily implement other radar modalities, such as Frequency-Modulated Continuous-Wave (FMCW), Doppler, or Multiple-Frequency Continuous-Wave (MFCW) radar, simply by building new logic blocks that use this underlying hardware control layer .   

- sfcw_radar_cc Block: This is a GNU Radio synchronous source block (gr::sync_block) that contains the primary SFCW logic and state machine. It controls the entire frequency sweep by generating the appropriate waveform for each step (e.g., CW or LFM chirp), commanding frequency changes via the BladerfDevice instance, and processing the raw I/Q streams from the SDR. It de-interleaves the data from the two receive channels and passes the echo and reference streams to separate output ports for downstream processing in Python.   

Core Functionality of the radar controller includes:

- High Reconfigurability: The controller is highly configurable through parameters passed during its instantiation in a GNU Radio flowgraph or a Python script. Users can easily adjust the frequency plan, sample rate, gains, and sub-pulse waveform (CW or LFM chirp) . The class structure is also extensible, allowing for the easy implementation of custom waveforms.   

- Fast Frequency Tuning: To minimize dead time between frequency steps, the system utilizes the bladeRF's quick tune mode. The hardware-specific tuning parameters for the entire frequency plan are pre-calculated and cached during initialization, allowing for near-instantaneous retuning during the sweep .   

- Multi-Threaded I/O for Full-Duplex Operation: Transmit and receive operations (bladerf_sync_tx and bladerf_sync_rx) are initiated in separate, concurrent threads. This leverages the bladeRF's full-duplex capability and ensures that the high-bandwidth data reception on the host side does not block the time-sensitive transmission commands, contributing to overall system stability .   

- Metadata Propagation: The controller attaches metadata to the output stream using GNU Radio's tagging system. Tags like "newScan" and "step" are added to the first sample of a new sweep and each new frequency step, respectively. This allows downstream processing blocks to perform operations like coherent integration with sample-level accuracy .   

## Prerequisites
- Gnuradio 3.10
- python 3
- cmake
- libvolk
- Boost
- gcc > 9.3.0
- gxx
- libbladeRF 1.5.0

## Installation
- Clone this repository
	```sh
	git clone [https://github.com/tapparelj/gr-lora_sdr.git](https://github.com/huiyellow/bladerf_sfcw_radar.git)
	```
- Go to the cloned repository
	```sh
	cd bladerf_sfcw_radar/
	```
- To build the code, create an appropriate folder and go in it:
	```sh
	mkdir build
	cd build
	```
- Run the main CMakeLists.txt
	```sh
	cmake ..
	```
- Finally compile the custom GNU Radio blocks composing the LoRa transceiver. Replacing \<X> with the number of core you want to use to speed up the compilation.
	```sh
	(sudo) make install -j<X>
	```
- if you installed as sudo run
	```sh
	sudo ldconfig 
	```
- Now you should be able to run some codes. For example, open the GNU Radio Companion user interface and check if the blocks of gr-lora_sdr are available on the blocks list (e.g. under LoRa_TX).
	```sh
	gnuradio-companion &
	```

## Hardware configuration
The SCORA radar system is constructed from commercially available components to ensure low cost, ease of replication, and a clear path for open-source distribution. A complete bill of materials (BOM) is provided as follows"   



- The heart of the system is a Nuand bladeRF Micro A4, which serves as the central RF front-end and handles all RF operations. This device was selected for its affordability, wide continuous tuning range (47 MHz to 6 GHz), and full-duplex 2x2 MIMO capability.   



- Host Computer: A standard laptop or single-board computer (SBC) provides the computational back-end, connecting to the bladeRF via a high-speed USB 3.0 interface to stream I/Q samples and run the control software.   



- Antennas: Two RFSpace TSA600 Vivaldi antennas are used for transmission and reception. They are arranged in a pseudo-monostatic configuration to maximize isolation and minimize direct signal leakage.   



- Optional Components: The system can be augmented with optional amplifiers to enhance performance. A power amplifier (e.g., BT100) can be added to the transmit path to increase range, and a low-noise amplifier (LNA) (e.g., BT200) can be added to the receive path to improve the signal-to-noise ratio (SNR).   

## Reference Channel Implementation
A crucial aspect of the hardware design is the reference signal path, which is created to compensate for the LO phase incoherence inherent in the SDR. This path can be configured in one of two ways:   

- MIMO Loopback Configuration: If an external coupler is not used, the reference path can be created by directly connecting the second transmitter port (TX2) to the second receiver port (RX2) through an attenuator. In this mode, the control software configures the bladeRF to transmit an identical waveform from both TX1 and TX2 simultaneously. This approach minimizes hardware cost and complexity at the expense of increased data throughput from the host computer to the SDR. 

- Directional Coupler Configuration: In this setup, a portion of the transmitted signal from TX1 is tapped off by an external directional coupler. This tapped reference signal is then passed through an attenuator and fed directly into the second receiver port (RX2). This configuration reduces the data load on the host computer, as only one waveform needs to be streamed to the SDR.   

 ## Usage
- An example of the sfcw radar can be found in bladerf_sfcw_radar/gui/ (.grc).
- The .grc files can be opened with gnuradio-companion to set the different transmission parameters.
