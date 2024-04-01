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
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import sfcwRadar
import sip



class cw_radar_simulation(gr.top_block, Qt.QWidget):

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

        self.settings = Qt.QSettings("GNU Radio", "cw_radar_simulation")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.burst_len = burst_len = 2**14
        self.tone_freq = tone_freq = [-5e6,5e6]
        self.samp_rate = samp_rate = 15e6
        self.fft_size_cor = fft_size_cor = int(burst_len/2)
        self.tone_fft_indices = tone_fft_indices = [int(((samp_rate/2)+tone_freq[0])/(samp_rate/fft_size_cor)),int(tone_freq[1]/(samp_rate/fft_size_cor)+fft_size_cor/2)]
        self.ob_range_ = ob_range_ = 1
        self.ob_range = ob_range = 1
        self.num_steps = num_steps = 64
        self.freq_index = freq_index = 1
        self.burst_offset = burst_offset = 1
        self.amp = amp = 0.2
        self.LO_freq = LO_freq = 1e9

        ##################################################
        # Blocks
        ##################################################

        self._ob_range_range = qtgui.Range(1, 15, 0.1, 1, 200)
        self._ob_range_win = qtgui.RangeWidget(self._ob_range_range, self.set_ob_range, "'ob_range'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._ob_range_win)
        self._burst_offset_range = qtgui.Range(1, 1024, 1, 1, 200)
        self._burst_offset_win = qtgui.RangeWidget(self._burst_offset_range, self.set_burst_offset, "'burst_offset'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._burst_offset_win)
        self.sfcwRadar_responseCollector_0_0 = sfcwRadar.responseCollector("burst", burst_offset)
        self.sfcwRadar_responseCollector_0 = sfcwRadar.responseCollector("burst", burst_offset)
        self.sfcwRadar_radarTxRxSimulator_0 = sfcwRadar.radarTxRxSimulator(burst_len, 2e9, samp_rate, 12e6, num_steps, tone_freq, ob_range)
        self.qtgui_time_sink_x_1_0_0_0_0 = qtgui.time_sink_f(
            (int(num_steps*2)), #size
            samp_rate, #samp_rate
            "range_profile", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1_0_0_0_0.set_update_time(1)
        self.qtgui_time_sink_x_1_0_0_0_0.set_y_axis(-4, 10000)

        self.qtgui_time_sink_x_1_0_0_0_0.set_y_label('Mag', "")

        self.qtgui_time_sink_x_1_0_0_0_0.enable_tags(True)
        self.qtgui_time_sink_x_1_0_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1_0_0_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_1_0_0_0_0.enable_grid(False)
        self.qtgui_time_sink_x_1_0_0_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_1_0_0_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_1_0_0_0_0.enable_stem_plot(False)


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
                self.qtgui_time_sink_x_1_0_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_1_0_0_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1_0_0_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1_0_0_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1_0_0_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1_0_0_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1_0_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_0_0_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_1_0_0_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_1_0_0_0_0_win)
        self.qtgui_time_sink_x_1_0_0_0 = qtgui.time_sink_f(
            (int(num_steps*2)), #size
            samp_rate, #samp_rate
            "combined", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1_0_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_1_0_0_0.set_y_axis(-4, 4)

        self.qtgui_time_sink_x_1_0_0_0.set_y_label('Mag', "")

        self.qtgui_time_sink_x_1_0_0_0.enable_tags(True)
        self.qtgui_time_sink_x_1_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1_0_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_1_0_0_0.enable_grid(False)
        self.qtgui_time_sink_x_1_0_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_1_0_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_1_0_0_0.enable_stem_plot(False)


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
                self.qtgui_time_sink_x_1_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_1_0_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1_0_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1_0_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1_0_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1_0_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_0_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_1_0_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_1_0_0_0_win)
        self.qtgui_time_sink_x_1_0_0 = qtgui.time_sink_f(
            (int(num_steps*2)), #size
            samp_rate, #samp_rate
            "combined", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_1_0_0.set_y_axis(-4, 4)

        self.qtgui_time_sink_x_1_0_0.set_y_label('Phase', "")

        self.qtgui_time_sink_x_1_0_0.enable_tags(True)
        self.qtgui_time_sink_x_1_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_1_0_0.enable_grid(False)
        self.qtgui_time_sink_x_1_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_1_0_0.enable_control_panel(False)
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
        self.top_layout.addWidget(self._qtgui_time_sink_x_1_0_0_win)
        self._ob_range__tool_bar = Qt.QToolBar(self)
        self._ob_range__tool_bar.addWidget(Qt.QLabel("ob_range" + ": "))
        self._ob_range__line_edit = Qt.QLineEdit(str(self.ob_range_))
        self._ob_range__tool_bar.addWidget(self._ob_range__line_edit)
        self._ob_range__line_edit.editingFinished.connect(
            lambda: self.set_ob_range_(eng_notation.str_to_num(str(self._ob_range__line_edit.text()))))
        self.top_layout.addWidget(self._ob_range__tool_bar)
        self._freq_index_range = qtgui.Range(1, 1024, 1, 1, 200)
        self._freq_index_win = qtgui.RangeWidget(self._freq_index_range, self.set_freq_index, "'freq_index'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_index_win)
        self.fft_vxx_1 = fft.fft_vcc((int(num_steps*2)), False, window.blackmanharris(int(num_steps*2)), False, 1)
        self.fft_vxx_0_0 = fft.fft_vcc(fft_size_cor, True, window.blackmanharris(fft_size_cor), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(fft_size_cor, True, window.blackmanharris(fft_size_cor), True, 1)
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, (int(num_steps*2)))
        self.blocks_vector_to_stream_0_1 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, fft_size_cor)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, fft_size_cor)
        self.blocks_throttle2_0_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (int(num_steps*2)))
        self.blocks_stream_to_vector_0_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size_cor)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size_cor)
        self.blocks_skiphead_0_1 = blocks.skiphead(gr.sizeof_gr_complex*1, tone_fft_indices[0])
        self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_gr_complex*1, tone_fft_indices[1])
        self.blocks_multiply_conjugate_cc_1 = blocks.multiply_conjugate_cc(fft_size_cor)
        self.blocks_keep_one_in_n_0_1 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, fft_size_cor)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, fft_size_cor)
        self.blocks_interleave_0 = blocks.interleave(gr.sizeof_gr_complex*1, 1)
        self.blocks_integrate_xx_0_0 = blocks.integrate_cc((int(burst_len/fft_size_cor)), 1)
        self.blocks_integrate_xx_0 = blocks.integrate_cc((int(burst_len/fft_size_cor)), 1)
        self.blocks_complex_to_magphase_2 = blocks.complex_to_magphase(1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.analog_sig_source_x_1 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, tone_freq[1], amp, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, tone_freq[0], amp, 0, 0)
        self._LO_freq_range = qtgui.Range(1e9, 2e9, 20e6, 1e9, 200)
        self._LO_freq_win = qtgui.RangeWidget(self._LO_freq_range, self.set_LO_freq, "'LO_freq'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._LO_freq_win)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_throttle2_0_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.qtgui_time_sink_x_1_0_0_0_0, 0))
        self.connect((self.blocks_complex_to_magphase_2, 1), (self.qtgui_time_sink_x_1_0_0, 0))
        self.connect((self.blocks_complex_to_magphase_2, 0), (self.qtgui_time_sink_x_1_0_0_0, 0))
        self.connect((self.blocks_integrate_xx_0, 0), (self.sfcwRadar_responseCollector_0, 0))
        self.connect((self.blocks_integrate_xx_0_0, 0), (self.sfcwRadar_responseCollector_0_0, 0))
        self.connect((self.blocks_interleave_0, 0), (self.blocks_complex_to_magphase_2, 0))
        self.connect((self.blocks_interleave_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_integrate_xx_0_0, 0))
        self.connect((self.blocks_keep_one_in_n_0_1, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_multiply_conjugate_cc_1, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.blocks_multiply_conjugate_cc_1, 0), (self.blocks_vector_to_stream_0_1, 0))
        self.connect((self.blocks_skiphead_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_skiphead_0_1, 0), (self.blocks_keep_one_in_n_0_1, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_stream_to_vector_0_1, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.fft_vxx_1, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.sfcwRadar_radarTxRxSimulator_0, 0))
        self.connect((self.blocks_throttle2_0_0, 0), (self.sfcwRadar_radarTxRxSimulator_0, 1))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_skiphead_0, 0))
        self.connect((self.blocks_vector_to_stream_0_1, 0), (self.blocks_skiphead_0_1, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_conjugate_cc_1, 0))
        self.connect((self.fft_vxx_0_0, 0), (self.blocks_multiply_conjugate_cc_1, 1))
        self.connect((self.fft_vxx_1, 0), (self.blocks_vector_to_stream_1, 0))
        self.connect((self.sfcwRadar_radarTxRxSimulator_0, 1), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.sfcwRadar_radarTxRxSimulator_0, 0), (self.blocks_stream_to_vector_0_1, 0))
        self.connect((self.sfcwRadar_responseCollector_0, 0), (self.blocks_interleave_0, 0))
        self.connect((self.sfcwRadar_responseCollector_0_0, 0), (self.blocks_interleave_0, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "cw_radar_simulation")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_burst_len(self):
        return self.burst_len

    def set_burst_len(self, burst_len):
        self.burst_len = burst_len
        self.set_fft_size_cor(int(self.burst_len/2))

    def get_tone_freq(self):
        return self.tone_freq

    def set_tone_freq(self, tone_freq):
        self.tone_freq = tone_freq
        self.set_tone_fft_indices([int(((self.samp_rate/2)+self.tone_freq[0])/(self.samp_rate/self.fft_size_cor)),int(self.tone_freq[1]/(self.samp_rate/self.fft_size_cor)+self.fft_size_cor/2)])
        self.analog_sig_source_x_0.set_frequency(self.tone_freq[0])
        self.analog_sig_source_x_1.set_frequency(self.tone_freq[1])

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_tone_fft_indices([int(((self.samp_rate/2)+self.tone_freq[0])/(self.samp_rate/self.fft_size_cor)),int(self.tone_freq[1]/(self.samp_rate/self.fft_size_cor)+self.fft_size_cor/2)])
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_1.set_sampling_freq(self.samp_rate)
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle2_0_0.set_sample_rate(self.samp_rate)
        self.qtgui_time_sink_x_1_0_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_1_0_0_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_1_0_0_0_0.set_samp_rate(self.samp_rate)

    def get_fft_size_cor(self):
        return self.fft_size_cor

    def set_fft_size_cor(self, fft_size_cor):
        self.fft_size_cor = fft_size_cor
        self.set_tone_fft_indices([int(((self.samp_rate/2)+self.tone_freq[0])/(self.samp_rate/self.fft_size_cor)),int(self.tone_freq[1]/(self.samp_rate/self.fft_size_cor)+self.fft_size_cor/2)])
        self.blocks_keep_one_in_n_0.set_n(self.fft_size_cor)
        self.blocks_keep_one_in_n_0_1.set_n(self.fft_size_cor)

    def get_tone_fft_indices(self):
        return self.tone_fft_indices

    def set_tone_fft_indices(self, tone_fft_indices):
        self.tone_fft_indices = tone_fft_indices

    def get_ob_range_(self):
        return self.ob_range_

    def set_ob_range_(self, ob_range_):
        self.ob_range_ = ob_range_
        Qt.QMetaObject.invokeMethod(self._ob_range__line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.ob_range_)))

    def get_ob_range(self):
        return self.ob_range

    def set_ob_range(self, ob_range):
        self.ob_range = ob_range
        self.sfcwRadar_radarTxRxSimulator_0.set_ob_range(self.ob_range)

    def get_num_steps(self):
        return self.num_steps

    def set_num_steps(self, num_steps):
        self.num_steps = num_steps

    def get_freq_index(self):
        return self.freq_index

    def set_freq_index(self, freq_index):
        self.freq_index = freq_index

    def get_burst_offset(self):
        return self.burst_offset

    def set_burst_offset(self, burst_offset):
        self.burst_offset = burst_offset

    def get_amp(self):
        return self.amp

    def set_amp(self, amp):
        self.amp = amp
        self.analog_sig_source_x_0.set_amplitude(self.amp)
        self.analog_sig_source_x_1.set_amplitude(self.amp)

    def get_LO_freq(self):
        return self.LO_freq

    def set_LO_freq(self, LO_freq):
        self.LO_freq = LO_freq




def main(top_block_cls=cw_radar_simulation, options=None):

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
