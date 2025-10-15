## Summary
SCORA (Stepped-frequency Coherent Radar Architecture) is a complete, open-source framework for building a high-range-resolution, coherent radar system using low-cost, commercial-off-the-shelf (COTS) hardware. The project is motivated by the need to make advanced radar technology more accessible for research, education, and community-driven development by providing a fully reconfigurable and replicable platform.   

The system architecture is based on a Nuand bladeRF Software-Defined Radio (SDR), chosen for its affordability and 2x2 MIMO capability, and is implemented within the GNU Radio framework. To achieve high range resolution on the bandwidth-limited SDR, SCORA employs the Stepped-Frequency Continuous-Wave (SFCW) technique, which synthesizes a wide effective bandwidth from a series of narrow-band sub-pulses.   

A key feature of the framework is its solution to the phase incoherence problem inherent in low-cost SDRs. By leveraging the bladeRF's 2x2 MIMO capability to create a reference channel (via loopback), the system measures and cancels the random phase errors introduced by the SDR's unsynchronized local oscillators, enabling fully coherent operation.   

The software uses a hybrid C++/Python design. A custom C++ block in GNU Radio handles real-time, low-latency hardware control, while a flexible Python chain performs the signal processing, calibration, and data logging.
