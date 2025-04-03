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
from gnuradio import eng_notation
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
from gnuradio import sfcwRadar
import sip



class sfcw_radar_gui(gr.top_block, Qt.QWidget):

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

        self.settings = Qt.QSettings("GNU Radio", "sfcw_radar_gui")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.burst_len = burst_len = 2**9
        self.recv_buf_len = recv_buf_len = burst_len+64
        self.chirp_bandwidth = chirp_bandwidth = 1e6
        self.tx_gain = tx_gain = 20
        self.transition_width = transition_width = chirp_bandwidth
        self.start_freq = start_freq = 1e9
        self.scale = scale = 0
        self.samp_rate = samp_rate = 5e6
        self.rx_gain = rx_gain = 20
        self.ref_gain = ref_gain = 20
        self.pulse_amp = pulse_amp = 1
        self.num_steps = num_steps = 128
        self.mf_size = mf_size = recv_buf_len
        self.lp_dec = lp_dec = 1
        self.freq_step = freq_step = 10e6
        self.file_prefix = file_prefix = '0'
        self.cw_freq = cw_freq = 100e3
        self.cut_off = cut_off = chirp_bandwidth

        ##################################################
        # Blocks
        ##################################################

        self._tx_gain_range = qtgui.Range(0, 60, 1, 20, 200)
        self._tx_gain_win = qtgui.RangeWidget(self._tx_gain_range, self.set_tx_gain, "'tx_gain'", "eng", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._tx_gain_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._transition_width_range = qtgui.Range(0, chirp_bandwidth, 1, chirp_bandwidth, 200)
        self._transition_width_win = qtgui.RangeWidget(self._transition_width_range, self.set_transition_width, "'transition_width'", "eng", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._transition_width_win, 1, 2, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._scale_range = qtgui.Range(0, 1, 0.01, 0, 200)
        self._scale_win = qtgui.RangeWidget(self._scale_range, self.set_scale, "B-scan scale", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._scale_win)
        self._rx_gain_range = qtgui.Range(0, 60, 1, 20, 200)
        self._rx_gain_win = qtgui.RangeWidget(self._rx_gain_range, self.set_rx_gain, "'rx_gain'", "eng", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rx_gain_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._ref_gain_range = qtgui.Range(0, 60, 1, 20, 200)
        self._ref_gain_win = qtgui.RangeWidget(self._ref_gain_range, self.set_ref_gain, "'ref_gain'", "eng", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._ref_gain_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._cut_off_range = qtgui.Range(0, chirp_bandwidth*2, 1, chirp_bandwidth, 200)
        self._cut_off_win = qtgui.RangeWidget(self._cut_off_range, self.set_cut_off, "'cut_off'", "eng", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._cut_off_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.sfcwRadar_sfcw_radar_cc_0 = sfcwRadar.sfcw_radar_cc(int(start_freq), num_steps, int(freq_step), int(samp_rate), rx_gain, tx_gain, ref_gain, True, burst_len, recv_buf_len, 8, 2048, 4, pulse_amp, cw_freq, True, int(chirp_bandwidth), 1)
        self.sfcwRadar_matchedFilter_0 = sfcwRadar.matchedFilter((int(mf_size/lp_dec)))
        self.sfcwRadar_findPeak_0 = sfcwRadar.findPeak((int(mf_size/lp_dec)))
        self.scan_once = _scan_once_toggle_button = qtgui.MsgPushButton('scan_once', '',1,"default","default")
        self.scan_once = _scan_once_toggle_button

        self.top_grid_layout.addWidget(_scan_once_toggle_button, 2, 3, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.scan_cont = _scan_cont_toggle_button = qtgui.MsgPushButton('scan_cont', '',2,"default","default")
        self.scan_cont = _scan_cont_toggle_button

        self.top_grid_layout.addWidget(_scan_cont_toggle_button, 1, 3, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_1_0_0 = qtgui.time_sink_f(
            num_steps, #size
            samp_rate, #samp_rate
            "Range profile(A-Scan)", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_1_0_0.set_y_axis(0, 1)

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
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_1_0_0_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_1 = qtgui.time_sink_c(
            (int(recv_buf_len*num_steps/lp_dec)), #size
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


        labels = ['out0_real', 'out0_imag', 'out1_real', 'out1_imag', 'Signal 5',
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
        self.top_layout.addWidget(self._qtgui_time_sink_x_1_win)
        self.qtgui_time_raster_sink_x_0 = qtgui.time_raster_sink_f(
            samp_rate,
            15,
            num_steps,
            [scale],
            [],
            "B-Scan",
            1,
            None
        )

        self.qtgui_time_raster_sink_x_0.set_update_time(0.1)
        self.qtgui_time_raster_sink_x_0.set_intensity_range(0, 1)
        self.qtgui_time_raster_sink_x_0.enable_grid(True)
        self.qtgui_time_raster_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_raster_sink_x_0.set_x_label("")
        self.qtgui_time_raster_sink_x_0.set_x_range(0.0, 0.0)
        self.qtgui_time_raster_sink_x_0.set_y_label("")
        self.qtgui_time_raster_sink_x_0.set_y_range(0.0, 0.0)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
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
        self.top_grid_layout.addWidget(self._qtgui_time_raster_sink_x_0_win, 0, 2, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.low_pass_filter_0_0 = filter.fir_filter_ccf(
            lp_dec,
            firdes.low_pass(
                1,
                samp_rate,
                cut_off,
                transition_width,
                window.WIN_HAMMING,
                6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            lp_dec,
            firdes.low_pass(
                1,
                samp_rate,
                cut_off,
                transition_width,
                window.WIN_HAMMING,
                6.76))
        self._file_prefix_tool_bar = Qt.QToolBar(self)
        self._file_prefix_tool_bar.addWidget(Qt.QLabel("'file_prefix'" + ": "))
        self._file_prefix_line_edit = Qt.QLineEdit(str(self.file_prefix))
        self._file_prefix_tool_bar.addWidget(self._file_prefix_line_edit)
        self._file_prefix_line_edit.editingFinished.connect(
            lambda: self.set_file_prefix(str(str(self._file_prefix_line_edit.text()))))
        self.top_grid_layout.addWidget(self._file_prefix_tool_bar, 2, 2, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.fft_vxx_0 = fft.fft_vcc(num_steps, False, window.blackmanharris(num_steps), True, 1)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, num_steps)
        self.blocks_stream_to_vector_1_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (int(mf_size/lp_dec)))
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (int(mf_size/lp_dec)))
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, num_steps)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.scan_cont, 'pressed'), (self.sfcwRadar_sfcw_radar_cc_0, 'scan'))
        self.msg_connect((self.scan_once, 'pressed'), (self.sfcwRadar_sfcw_radar_cc_0, 'scan'))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.qtgui_time_raster_sink_x_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.qtgui_time_sink_x_1_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.sfcwRadar_matchedFilter_0, 0))
        self.connect((self.blocks_stream_to_vector_1_0, 0), (self.sfcwRadar_matchedFilter_0, 1))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.low_pass_filter_0, 0), (self.qtgui_time_sink_x_1, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.blocks_stream_to_vector_1_0, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.qtgui_time_sink_x_1, 1))
        self.connect((self.sfcwRadar_findPeak_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.sfcwRadar_matchedFilter_0, 0), (self.sfcwRadar_findPeak_0, 0))
        self.connect((self.sfcwRadar_sfcw_radar_cc_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.sfcwRadar_sfcw_radar_cc_0, 1), (self.low_pass_filter_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "sfcw_radar_gui")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_burst_len(self):
        return self.burst_len

    def set_burst_len(self, burst_len):
        self.burst_len = burst_len
        self.set_recv_buf_len(self.burst_len+64)

    def get_recv_buf_len(self):
        return self.recv_buf_len

    def set_recv_buf_len(self, recv_buf_len):
        self.recv_buf_len = recv_buf_len
        self.set_mf_size(self.recv_buf_len)

    def get_chirp_bandwidth(self):
        return self.chirp_bandwidth

    def set_chirp_bandwidth(self, chirp_bandwidth):
        self.chirp_bandwidth = chirp_bandwidth
        self.set_cut_off(self.chirp_bandwidth)
        self.set_transition_width(self.chirp_bandwidth)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.sfcwRadar_sfcw_radar_cc_0.set_radar_tx_gain(self.tx_gain)

    def get_transition_width(self):
        return self.transition_width

    def set_transition_width(self, transition_width):
        self.transition_width = transition_width
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))

    def get_start_freq(self):
        return self.start_freq

    def set_start_freq(self, start_freq):
        self.start_freq = start_freq

    def get_scale(self):
        return self.scale

    def set_scale(self, scale):
        self.scale = scale
        self.qtgui_time_raster_sink_x_0.set_multiplier([self.scale])

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))
        self.qtgui_time_sink_x_1.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_1_0_0.set_samp_rate(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.sfcwRadar_sfcw_radar_cc_0.set_radar_rx_gain(self.rx_gain)

    def get_ref_gain(self):
        return self.ref_gain

    def set_ref_gain(self, ref_gain):
        self.ref_gain = ref_gain
        self.sfcwRadar_sfcw_radar_cc_0.set_ref_tx_gain(self.ref_gain)
        self.sfcwRadar_sfcw_radar_cc_0.set_ref_rx_gain(self.ref_gain)

    def get_pulse_amp(self):
        return self.pulse_amp

    def set_pulse_amp(self, pulse_amp):
        self.pulse_amp = pulse_amp

    def get_num_steps(self):
        return self.num_steps

    def set_num_steps(self, num_steps):
        self.num_steps = num_steps
        self.qtgui_time_raster_sink_x_0.set_num_cols(self.num_steps)

    def get_mf_size(self):
        return self.mf_size

    def set_mf_size(self, mf_size):
        self.mf_size = mf_size

    def get_lp_dec(self):
        return self.lp_dec

    def set_lp_dec(self, lp_dec):
        self.lp_dec = lp_dec

    def get_freq_step(self):
        return self.freq_step

    def set_freq_step(self, freq_step):
        self.freq_step = freq_step

    def get_file_prefix(self):
        return self.file_prefix

    def set_file_prefix(self, file_prefix):
        self.file_prefix = file_prefix
        Qt.QMetaObject.invokeMethod(self._file_prefix_line_edit, "setText", Qt.Q_ARG("QString", str(self.file_prefix)))

    def get_cw_freq(self):
        return self.cw_freq

    def set_cw_freq(self, cw_freq):
        self.cw_freq = cw_freq

    def get_cut_off(self):
        return self.cut_off

    def set_cut_off(self, cut_off):
        self.cut_off = cut_off
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cut_off, self.transition_width, window.WIN_HAMMING, 6.76))




def main(top_block_cls=sfcw_radar_gui, options=None):

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
