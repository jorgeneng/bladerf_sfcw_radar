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

Core Functionality
High Reconfigurability: The controller is highly configurable through parameters passed during its instantiation in a GNU Radio flowgraph or a Python script. Users can easily adjust the frequency plan, sample rate, gains, and sub-pulse waveform (CW or LFM chirp) . The class structure is also extensible, allowing for the easy implementation of custom waveforms.   

Fast Frequency Tuning: To minimize dead time between frequency steps, the system utilizes the bladeRF's quick tune mode. The hardware-specific tuning parameters for the entire frequency plan are pre-calculated and cached during initialization, allowing for near-instantaneous retuning during the sweep .   

Multi-Threaded I/O for Full-Duplex Operation: Transmit and receive operations (bladerf_sync_tx and bladerf_sync_rx) are initiated in separate, concurrent threads. This leverages the bladeRF's full-duplex capability and ensures that the high-bandwidth data reception on the host side does not block the time-sensitive transmission commands, contributing to overall system stability .   

Metadata Propagation: The controller attaches metadata to the output stream using GNU Radio's tagging system. Tags like "newScan" and "step" are added to the first sample of a new sweep and each new frequency step, respectively. This allows downstream processing blocks to perform operations like coherent integration with sample-level accuracy .   


