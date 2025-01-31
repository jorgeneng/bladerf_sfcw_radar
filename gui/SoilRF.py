#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: v3.10.9.2-39-gcf065ee5

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
import bladeRF
import time
import datetime
import os
import sip



class SoilRF(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "SoilRF")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 5e6
        self.central_freq = central_freq = 1e9
        self.tx_ref_gain = tx_ref_gain = 0
        self.tx_gain = tx_gain = 40
        self.rx_ref_gain = rx_ref_gain = 0
        self.rx_gain = rx_gain = 35
        self.rx_bandwidth = rx_bandwidth = samp_rate
        self.root_dir = root_dir = "/home/hui/SoilRF_project/soilRF_cw/"
        self.rec_button = rec_button = 0
        self.offset = offset = 0
        self.note = note = 'phase_24_'
        self.monitoringLength = monitoringLength = 2**12
        self.filename = filename = "cal_"
        self.c_freq_tx = c_freq_tx = central_freq
        self.baseband = baseband = 500e3

        ##################################################
        # Blocks
        ##################################################

        self._tx_ref_gain_range = qtgui.Range(0, 60, 1, 0, 200)
        self._tx_ref_gain_win = qtgui.RangeWidget(self._tx_ref_gain_range, self.set_tx_ref_gain, "tx_ref_gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._tx_ref_gain_win)
        self._tx_gain_range = qtgui.Range(0, 66, 1, 40, 200)
        self._tx_gain_win = qtgui.RangeWidget(self._tx_gain_range, self.set_tx_gain, "tx_gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._tx_gain_win)
        self._rx_ref_gain_range = qtgui.Range(0, 60, 1, 0, 200)
        self._rx_ref_gain_win = qtgui.RangeWidget(self._rx_ref_gain_range, self.set_rx_ref_gain, "rx_ref_gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rx_ref_gain_win)
        self._rx_gain_range = qtgui.Range(0, 60, 1, 35, 200)
        self._rx_gain_win = qtgui.RangeWidget(self._rx_gain_range, self.set_rx_gain, "rx_gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rx_gain_win)
        _rec_button_push_button = Qt.QPushButton('RECORD')
        _rec_button_push_button = Qt.QPushButton('RECORD')
        self._rec_button_choices = {'Pressed': 1, 'Released': 0}
        _rec_button_push_button.pressed.connect(lambda: self.set_rec_button(self._rec_button_choices['Pressed']))
        _rec_button_push_button.released.connect(lambda: self.set_rec_button(self._rec_button_choices['Released']))
        self.top_grid_layout.addWidget(_rec_button_push_button, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._offset_range = qtgui.Range(0, 20e6, 100e3, 0, 3)
        self._offset_win = qtgui.RangeWidget(self._offset_range, self.set_offset, "offset", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._offset_win)
        self._c_freq_tx_range = qtgui.Range(800e6, 6e9, 40e6, central_freq, 3)
        self._c_freq_tx_win = qtgui.RangeWidget(self._c_freq_tx_range, self.set_c_freq_tx, "c_freq_tx", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._c_freq_tx_win)
        self.qtgui_time_sink_x_1_0 = qtgui.time_sink_c(
            monitoringLength, #size
            samp_rate, #samp_rate
            "rx", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1_0.set_update_time(0.10)
        self.qtgui_time_sink_x_1_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_1_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1_0.enable_tags(True)
        self.qtgui_time_sink_x_1_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1_0.enable_autoscale(False)
        self.qtgui_time_sink_x_1_0.enable_grid(False)
        self.qtgui_time_sink_x_1_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_1_0.enable_control_panel(False)
        self.qtgui_time_sink_x_1_0.enable_stem_plot(False)


        labels = ['rx1 real', 'rx1 img', 'rx2 real', 'rx2 img', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(4):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_1_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_1_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_1_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_0_win = sip.wrapinstance(self.qtgui_time_sink_x_1_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_1_0_win)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_f(
            monitoringLength, #size
            samp_rate, #samp_rate
            "Phase", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(-4, 4)

        self.qtgui_time_sink_x_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_win, 2, 0, 2, 2)
        for r in range(2, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            monitoringLength, #size
            samp_rate, #samp_rate
            "Mag", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(0, 0.5)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 2, 2, 2, 2)
        for r in range(2, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_ledindicator_0 = self._qtgui_ledindicator_0_win = qtgui.GrLEDIndicator("RED=RECORDING", "red", "green", True if rec_button==1 else False, 40, 1, 1, 1, self)
        self.qtgui_ledindicator_0 = self._qtgui_ledindicator_0_win
        self.top_grid_layout.addWidget(self._qtgui_ledindicator_0_win, 0, 3, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            8192, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            2,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self._note_tool_bar = Qt.QToolBar(self)
        self._note_tool_bar.addWidget(Qt.QLabel("RECORDING NOTE" + ": "))
        self._note_line_edit = Qt.QLineEdit(str(self.note))
        self._note_tool_bar.addWidget(self._note_line_edit)
        self._note_line_edit.editingFinished.connect(
            lambda: self.set_note(str(str(self._note_line_edit.text()))))
        self.top_grid_layout.addWidget(self._note_tool_bar, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.filter_fft_low_pass_filter_0 = filter.fft_filter_ccc(1, firdes.low_pass(1, samp_rate, (baseband*1.2), (baseband/2), window.WIN_KAISER, 6.76), 1)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(1)
        self.blocks_complex_to_magphase_0 = blocks.complex_to_magphase(1)
        self.bladeRF_source_0 = bladeRF.source(
            args="numchan=" + str(2)
                 + ",metadata=" + 'False'
                 + ",bladerf=" +  str('')
                 + ",verbosity=" + 'verbose'
                 + ",feature=" + 'default'
                 + ",sample_format=" + '16bit'
                 + ",fpga=" + str('')
                 + ",fpga-reload=" + 'True'
                 + ",use_ref_clk=" + 'False'
                 + ",ref_clk=" + str(int(10e6))
                 + ",buflen=" + str(int(4096))
                 + ",buffers=" + str(int(1024))
                 + ",in_clk=" + 'ONBOARD'
                 + ",out_clk=" + str(False)
                 + ",use_dac=" + 'False'
                 + ",dac=" + str(7231)
                 + ",xb200=" + 'none'
                 + ",tamer=" + 'internal'
                 + ",sampling=" + 'internal'
                 + ",lpf_mode="+'disabled'
                 + ",smb="+str(int(38.4e6))
                 + ",dc_calibration="+'LPF_TUNING'
                 + ",trigger0="+'False'
                 + ",trigger_role0="+'master'
                 + ",trigger_signal0="+'J51_1'
                 + ",trigger1="+'False'
                 + ",trigger_role1="+'master'
                 + ",trigger_signal1="+'J51_1'
                 + ",bias_tee0="+'False'
                 + ",bias_tee1="+'False'


        )
        self.bladeRF_source_0.set_sample_rate(samp_rate)
        self.bladeRF_source_0.set_center_freq((c_freq_tx+offset),0)
        self.bladeRF_source_0.set_bandwidth(samp_rate,0)
        self.bladeRF_source_0.set_dc_offset_mode(0, 0)
        self.bladeRF_source_0.set_iq_balance_mode(0, 0)
        self.bladeRF_source_0.set_gain_mode(False, 0)
        self.bladeRF_source_0.set_gain(rx_gain, 0)
        self.bladeRF_source_0.set_if_gain(20, 0)
        self.bladeRF_source_0.set_dc_offset_mode(0, 1)
        self.bladeRF_source_0.set_iq_balance_mode(0, 1)
        self.bladeRF_source_0.set_gain_mode(False, 1)
        self.bladeRF_source_0.set_gain(rx_ref_gain, 1)
        self.bladeRF_source_0.set_if_gain(20, 1)
        self.bladeRF_sink_0 = bladeRF.sink(
            args="numchan=" + str(2)
                 + ",metadata=" + 'False'
                 + ",bladerf=" +  str('')
                 + ",verbosity=" + 'verbose'
                 + ",feature=" + 'default'
                 + ",sample_format=" + '16bit'
                 + ",fpga=" + str('')
                 + ",fpga-reload=" + 'True'
                 + ",use_ref_clk=" + 'True'
                 + ",ref_clk=" + str(int(10e6))
                 + ",buflen=" + str(int(4096))
                 + ",buffers=" + str(int(1024))
                 + ",in_clk=" + 'ONBOARD'
                 + ",out_clk=" + str(False)
                 + ",use_dac=" + 'False'
                 + ",dac=" + str(7231)
                 + ",xb200=" + 'none'
                 + ",tamer=" + 'internal'
                 + ",sampling=" + 'internal'
                 + ",lpf_mode="+'disabled'
                 + ",smb="+str(int(38.4e6))
                 + ",dc_calibration="+'LPF_TUNING'
                 + ",trigger0="+'False'
                 + ",trigger_role0="+'master'
                 + ",trigger_signal0="+'J51_1'
                 + ",trigger1="+'False'
                 + ",trigger_role1="+'master'
                 + ",trigger_signal1="+'J51_1'
                 + ",bias_tee0="+'False'
                 + ",bias_tee1="+'False'


        )
        self.bladeRF_sink_0.set_sample_rate(samp_rate)
        self.bladeRF_sink_0.set_center_freq(c_freq_tx,0)
        self.bladeRF_sink_0.set_bandwidth(samp_rate,0)
        self.bladeRF_sink_0.set_gain(tx_gain, 0)
        self.bladeRF_sink_0.set_if_gain(20, 0)
        self.bladeRF_sink_0.set_gain(tx_ref_gain, 1)
        self.bladeRF_sink_0.set_if_gain(20, 1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, baseband, 0.8, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.bladeRF_source_0, 1), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.bladeRF_source_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.bladeRF_source_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.bladeRF_source_0, 1), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.bladeRF_source_0, 1), (self.qtgui_time_sink_x_1_0, 1))
        self.connect((self.bladeRF_source_0, 0), (self.qtgui_time_sink_x_1_0, 0))
        self.connect((self.blocks_complex_to_magphase_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_complex_to_magphase_0, 1), (self.qtgui_time_sink_x_0_0, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.filter_fft_low_pass_filter_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.bladeRF_sink_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.bladeRF_sink_0, 1))
        self.connect((self.filter_fft_low_pass_filter_0, 0), (self.blocks_complex_to_magphase_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "SoilRF")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_rx_bandwidth(self.samp_rate)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.bladeRF_sink_0.set_sample_rate(self.samp_rate)
        self.bladeRF_sink_0.set_bandwidth(self.samp_rate, 0)
        self.bladeRF_source_0.set_sample_rate(self.samp_rate)
        self.bladeRF_source_0.set_bandwidth(self.samp_rate, 0)
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.filter_fft_low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.baseband*1.2), (self.baseband/2), window.WIN_KAISER, 6.76))
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_1_0.set_samp_rate(self.samp_rate)

    def get_central_freq(self):
        return self.central_freq

    def set_central_freq(self, central_freq):
        self.central_freq = central_freq
        self.set_c_freq_tx(self.central_freq)

    def get_tx_ref_gain(self):
        return self.tx_ref_gain

    def set_tx_ref_gain(self, tx_ref_gain):
        self.tx_ref_gain = tx_ref_gain
        self.bladeRF_sink_0.set_gain(self.tx_ref_gain, 1)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.bladeRF_sink_0.set_gain(self.tx_gain, 0)

    def get_rx_ref_gain(self):
        return self.rx_ref_gain

    def set_rx_ref_gain(self, rx_ref_gain):
        self.rx_ref_gain = rx_ref_gain
        self.bladeRF_source_0.set_gain(self.rx_ref_gain, 1)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.bladeRF_source_0.set_gain(self.rx_gain, 0)

    def get_rx_bandwidth(self):
        return self.rx_bandwidth

    def set_rx_bandwidth(self, rx_bandwidth):
        self.rx_bandwidth = rx_bandwidth

    def get_root_dir(self):
        return self.root_dir

    def set_root_dir(self, root_dir):
        self.root_dir = root_dir

    def get_rec_button(self):
        return self.rec_button

    def set_rec_button(self, rec_button):
        self.rec_button = rec_button
        self.qtgui_ledindicator_0.setState(True if self.rec_button==1 else False)

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset
        self.bladeRF_source_0.set_center_freq((self.c_freq_tx+self.offset), 0)

    def get_note(self):
        return self.note

    def set_note(self, note):
        self.note = note
        Qt.QMetaObject.invokeMethod(self._note_line_edit, "setText", Qt.Q_ARG("QString", str(self.note)))

    def get_monitoringLength(self):
        return self.monitoringLength

    def set_monitoringLength(self, monitoringLength):
        self.monitoringLength = monitoringLength

    def get_filename(self):
        return self.filename

    def set_filename(self, filename):
        self.filename = filename

    def get_c_freq_tx(self):
        return self.c_freq_tx

    def set_c_freq_tx(self, c_freq_tx):
        self.c_freq_tx = c_freq_tx
        self.bladeRF_sink_0.set_center_freq(self.c_freq_tx, 0)
        self.bladeRF_source_0.set_center_freq((self.c_freq_tx+self.offset), 0)

    def get_baseband(self):
        return self.baseband

    def set_baseband(self, baseband):
        self.baseband = baseband
        self.analog_sig_source_x_0.set_frequency(self.baseband)
        self.filter_fft_low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.baseband*1.2), (self.baseband/2), window.WIN_KAISER, 6.76))




def main(top_block_cls=SoilRF, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
