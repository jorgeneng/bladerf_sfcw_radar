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
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import sfcwRadar
import sip



class sfcwRadarGUI(gr.top_block, Qt.QWidget):

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

        self.settings = Qt.QSettings("GNU Radio", "sfcwRadarGUI")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.recv_buf_len = recv_buf_len = 2**10+512
        self.chirp_bandwidth = chirp_bandwidth = 2e6
        self.y_max = y_max = 1000
        self.tx_gain = tx_gain = 60
        self.transition_width = transition_width = 200e3
        self.start_freq = start_freq = 1e9
        self.samp_rate = samp_rate = 10e6
        self.rx_gain = rx_gain = 40
        self.ref_gain = ref_gain = 30
        self.num_steps = num_steps = 64
        self.mf_size = mf_size = recv_buf_len
        self.mf_delay = mf_delay = 0
        self.freq_step = freq_step = 40e6
        self.cw_freq = cw_freq = 100e3
        self.cw_amp = cw_amp = 0.5
        self.cut_off = cut_off = chirp_bandwidth/2
        self.burst_len = burst_len = 2**10

        ##################################################
        # Blocks
        ##################################################

        self._transition_width_range = qtgui.Range(0, 1e6, 1, 200e3, 200)
        self._transition_width_win = qtgui.RangeWidget(self._transition_width_range, self.set_transition_width, "'transition_width'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._transition_width_win)
        self._cut_off_range = qtgui.Range(0, chirp_bandwidth, 1, chirp_bandwidth/2, 200)
        self._cut_off_win = qtgui.RangeWidget(self._cut_off_range, self.set_cut_off, "'cut_off'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._cut_off_win)
        self.sfcwRadar_rawSamplesSink_0 = sfcwRadar.rawSamplesSink('chirp', int(start_freq), num_steps, int(samp_rate), rx_gain, tx_gain, ref_gain, False, burst_len, recv_buf_len, cw_amp, cw_freq, True, chirp_bandwidth)
        self.sfcwRadar_matchedFilter_0 = sfcwRadar.matchedFilter(mf_size)
        self.sfcwRadar_findPeak_0 = sfcwRadar.findPeak(mf_size)
        self.sfcwRadar_bladerfRadarController_cc_0 = sfcwRadar.bladerfRadarController_cc(int(start_freq), num_steps, int(freq_step), int(samp_rate), rx_gain, tx_gain, ref_gain, False, burst_len, recv_buf_len, 8, 2048, 4, cw_amp, cw_freq, True, chirp_bandwidth, 1, 0)
        self.scan_once = _scan_once_toggle_button = qtgui.MsgPushButton('scan_once', '',1,"default","default")
        self.scan_once = _scan_once_toggle_button

        self.top_layout.addWidget(_scan_once_toggle_button)
        self.scan_cont = _scan_cont_toggle_button = qtgui.MsgPushButton('scan_cont', '',2,"default","default")
        self.scan_cont = _scan_cont_toggle_button

        self.top_layout.addWidget(_scan_cont_toggle_button)
        self.qtgui_time_sink_x_2 = qtgui.time_sink_f(
            num_steps, #size
            samp_rate, #samp_rate
            "Phase of each frequency step", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_2.set_update_time(0.10)
        self.qtgui_time_sink_x_2.set_y_axis(-4, 4)

        self.qtgui_time_sink_x_2.set_y_label('Phase', "")

        self.qtgui_time_sink_x_2.enable_tags(True)
        self.qtgui_time_sink_x_2.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_2.enable_autoscale(False)
        self.qtgui_time_sink_x_2.enable_grid(False)
        self.qtgui_time_sink_x_2.enable_axis_labels(True)
        self.qtgui_time_sink_x_2.enable_control_panel(False)
        self.qtgui_time_sink_x_2.enable_stem_plot(False)


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
                self.qtgui_time_sink_x_2.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_2.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_2.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_2.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_2.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_2.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_2.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_2_win = sip.wrapinstance(self.qtgui_time_sink_x_2.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_2_win, 0, 2, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_1_0_0 = qtgui.time_sink_f(
            num_steps, #size
            samp_rate, #samp_rate
            "Range profile(A-Scan)", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_1_0_0.set_y_axis(0, y_max)

        self.qtgui_time_sink_x_1_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1_0_0.enable_tags(True)
        self.qtgui_time_sink_x_1_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_1_0_0.enable_grid(True)
        self.qtgui_time_sink_x_1_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_1_0_0.enable_control_panel(True)
        self.qtgui_time_sink_x_1_0_0.enable_stem_plot(False)


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
                self.qtgui_time_sink_x_1_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_1_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_1_0_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_1_0_0_win, 2, 0, 5, 2)
        for r in range(2, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_1 = qtgui.time_sink_c(
            (int(recv_buf_len*num_steps)), #size
            samp_rate, #samp_rate
            "Reference/Echo signals in time domain", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1.set_update_time(0.10)
        self.qtgui_time_sink_x_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1.enable_tags(True)
        self.qtgui_time_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1.enable_autoscale(False)
        self.qtgui_time_sink_x_1.enable_grid(False)
        self.qtgui_time_sink_x_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_1.enable_control_panel(False)
        self.qtgui_time_sink_x_1.enable_stem_plot(False)


        labels = ['rx_real_rx', 'rx_img_rx', 'rx_real_ref', 'rx_imag_ref', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'cyan', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 2, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(4):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_1.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_1.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_win = sip.wrapinstance(self.qtgui_time_sink_x_1.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_1_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_raster_sink_x_0 = qtgui.time_raster_sink_f(
            samp_rate,
            15,
            num_steps,
            [],
            [],
            "B-Scan",
            1,
            None
        )

        self.qtgui_time_raster_sink_x_0.set_update_time(0.1)
        self.qtgui_time_raster_sink_x_0.set_intensity_range(0, y_max)
        self.qtgui_time_raster_sink_x_0.enable_grid(True)
        self.qtgui_time_raster_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_raster_sink_x_0.set_x_label("")
        self.qtgui_time_raster_sink_x_0.set_x_range(0.0, 0.0)
        self.qtgui_time_raster_sink_x_0.set_y_label("")
        self.qtgui_time_raster_sink_x_0.set_y_range(0.0, 0.0)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [2, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_raster_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_raster_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_raster_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_time_raster_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_raster_sink_x_0_win = sip.wrapinstance(self.qtgui_time_raster_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_raster_sink_x_0_win, 2, 2, 5, 2)
        for r in range(2, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._mf_delay_range = qtgui.Range(0, mf_size, 1, 0, 200)
        self._mf_delay_win = qtgui.RangeWidget(self._mf_delay_range, self.set_mf_delay, "'mf_delay'", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._mf_delay_win)
        self.low_pass_filter_0_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                (chirp_bandwidth/1.8),
                (chirp_bandwidth/10),
                window.WIN_KAISER,
                6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                cut_off,
                transition_width,
                window.WIN_KAISER,
                6.76))
        self.fft_vxx_0 = fft.fft_vcc(num_steps, False, window.hamming(num_steps), True, 1)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, num_steps)
        self.blocks_stream_to_vector_1_0_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (recv_buf_len*num_steps))
        self.blocks_stream_to_vector_1_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (recv_buf_len*num_steps))
        self.blocks_stream_to_vector_1_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, mf_size)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, mf_size)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, num_steps)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_arg_1 = blocks.complex_to_arg(1)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.scan_cont, 'pressed'), (self.sfcwRadar_bladerfRadarController_cc_0, 'scan'))
        self.msg_connect((self.scan_once, 'pressed'), (self.sfcwRadar_bladerfRadarController_cc_0, 'scan'))
        self.connect((self.blocks_complex_to_arg_1, 0), (self.qtgui_time_sink_x_2, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_time_raster_sink_x_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_time_sink_x_1_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.sfcwRadar_matchedFilter_0, 0))
        self.connect((self.blocks_stream_to_vector_1_0, 0), (self.sfcwRadar_matchedFilter_0, 1))
        self.connect((self.blocks_stream_to_vector_1_0_0, 0), (self.sfcwRadar_rawSamplesSink_0, 0))
        self.connect((self.blocks_stream_to_vector_1_0_1, 0), (self.sfcwRadar_rawSamplesSink_0, 1))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_stream_to_vector_1_0_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.qtgui_time_sink_x_1, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.blocks_stream_to_vector_1_0, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.blocks_stream_to_vector_1_0_1, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.qtgui_time_sink_x_1, 1))
        self.connect((self.sfcwRadar_bladerfRadarController_cc_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.sfcwRadar_bladerfRadarController_cc_0, 1), (self.low_pass_filter_0_0, 0))
        self.connect((self.sfcwRadar_findPeak_0, 0), (self.blocks_complex_to_arg_1, 0))
        self.connect((self.sfcwRadar_findPeak_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.sfcwRadar_matchedFilter_0, 0), (self.sfcwRadar_findPeak_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "sfcwRadarGUI")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_recv_buf_len(self):
        return self.recv_buf_len

    def set_recv_buf_len(self, recv_buf_len):
        self.recv_buf_len = recv_buf_len
        self.set_mf_size(self.recv_buf_len)

    def get_chirp_bandwidth(self):
        return self.chirp_bandwidth

    def set_chirp_bandwidth(self, chirp_bandwidth):
        self.chirp_bandwidth = chirp_bandwidth
        self.set_cut_off(self.chirp_bandwidth/2)
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.chirp_bandwidth/1.8), (self.chirp_bandwidth/10), window.WIN_KAISER, 6.76))

    def get_y_max(self):
        return self.y_max

    def set_y_max(self, y_max):
        self.y_max = y_max
        self.qtgui_time_sink_x_1_0_0.set_y_axis(0, self.y_max)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain

    def get_transition_width(self):
        return self.transition_width

    def set_transition_width(self, transition_width):
        self.transition_width = transition_width
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_KAISER, 6.76))

    def get_start_freq(self):
        return self.start_freq

    def set_start_freq(self, start_freq):
        self.start_freq = start_freq

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_KAISER, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.chirp_bandwidth/1.8), (self.chirp_bandwidth/10), window.WIN_KAISER, 6.76))
        self.qtgui_time_sink_x_1.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_1_0_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_2.set_samp_rate(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain

    def get_ref_gain(self):
        return self.ref_gain

    def set_ref_gain(self, ref_gain):
        self.ref_gain = ref_gain

    def get_num_steps(self):
        return self.num_steps

    def set_num_steps(self, num_steps):
        self.num_steps = num_steps
        self.qtgui_time_raster_sink_x_0.set_num_cols(self.num_steps)

    def get_mf_size(self):
        return self.mf_size

    def set_mf_size(self, mf_size):
        self.mf_size = mf_size

    def get_mf_delay(self):
        return self.mf_delay

    def set_mf_delay(self, mf_delay):
        self.mf_delay = mf_delay

    def get_freq_step(self):
        return self.freq_step

    def set_freq_step(self, freq_step):
        self.freq_step = freq_step

    def get_cw_freq(self):
        return self.cw_freq

    def set_cw_freq(self, cw_freq):
        self.cw_freq = cw_freq

    def get_cw_amp(self):
        return self.cw_amp

    def set_cw_amp(self, cw_amp):
        self.cw_amp = cw_amp

    def get_cut_off(self):
        return self.cut_off

    def set_cut_off(self, cut_off):
        self.cut_off = cut_off
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_KAISER, 6.76))

    def get_burst_len(self):
        return self.burst_len

    def set_burst_len(self, burst_len):
        self.burst_len = burst_len




def main(top_block_cls=sfcwRadarGUI, options=None):

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
