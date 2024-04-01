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
from gnuradio import analog
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import sfcwRadar
import sip



class test(gr.top_block, Qt.QWidget):

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

        self.settings = Qt.QSettings("GNU Radio", "test")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.burst_len = burst_len = 2**16
        self.tone_freq = tone_freq = [-10e6,10e6]
        self.samp_rate = samp_rate = 25e6
        self.fft_size = fft_size = int(burst_len/2)
        self.tune_th = tune_th = int(samp_rate/20)
        self.tone_fft_indices = tone_fft_indices = [int(((samp_rate/2)+tone_freq[0])/(samp_rate/fft_size)),int(tone_freq[1]/(samp_rate/fft_size)+fft_size/2)]
        self.start_freq = start_freq = 1.2e9
        self.num_steps = num_steps = 64
        self.min_output_items = min_output_items = burst_len*2
        self.integrate_lenth = integrate_lenth = 1024
        self.freq_step = freq_step = 30e6
        self.freq_list_0 = freq_list_0 = 4096*10
        self.amp = amp = 0.3

        ##################################################
        # Blocks
        ##################################################

        self.sfcwRadar_bladerfRadarBurst_cc_0 = sfcwRadar.bladerfRadarBurst_cc(int(start_freq), num_steps, int(freq_step), int(samp_rate), 60, 20, 20, burst_len, 8, 2048, 4)
        self.sfcwRadar_bladerfRadarBurst_cc_0.set_min_output_buffer(min_output_items)
        self.qtgui_time_sink_x_3_0 = qtgui.time_sink_f(
            num_steps, #size
            samp_rate, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_3_0.set_update_time(0.10)
        self.qtgui_time_sink_x_3_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_3_0.set_y_label('phase', "")

        self.qtgui_time_sink_x_3_0.enable_tags(True)
        self.qtgui_time_sink_x_3_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_3_0.enable_autoscale(False)
        self.qtgui_time_sink_x_3_0.enable_grid(False)
        self.qtgui_time_sink_x_3_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_3_0.enable_control_panel(False)
        self.qtgui_time_sink_x_3_0.enable_stem_plot(False)


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
                self.qtgui_time_sink_x_3_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_3_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_3_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_3_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_3_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_3_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_3_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_3_0_win = sip.wrapinstance(self.qtgui_time_sink_x_3_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_3_0_win)
        self.qtgui_time_sink_x_3 = qtgui.time_sink_f(
            num_steps, #size
            samp_rate, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_3.set_update_time(0.10)
        self.qtgui_time_sink_x_3.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_3.set_y_label('phase', "")

        self.qtgui_time_sink_x_3.enable_tags(True)
        self.qtgui_time_sink_x_3.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_3.enable_autoscale(False)
        self.qtgui_time_sink_x_3.enable_grid(False)
        self.qtgui_time_sink_x_3.enable_axis_labels(True)
        self.qtgui_time_sink_x_3.enable_control_panel(False)
        self.qtgui_time_sink_x_3.enable_stem_plot(False)


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
                self.qtgui_time_sink_x_3.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_3.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_3.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_3.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_3.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_3.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_3.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_3_win = sip.wrapinstance(self.qtgui_time_sink_x_3.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_3_win)
        self.qtgui_time_sink_x_2 = qtgui.time_sink_f(
            (num_steps*2), #size
            samp_rate, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_2.set_update_time(0.10)
        self.qtgui_time_sink_x_2.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_2.set_y_label('Amplitude', "")

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
        self.top_layout.addWidget(self._qtgui_time_sink_x_2_win)
        self.qtgui_time_sink_x_1_0_0_1 = qtgui.time_sink_f(
            (int(num_steps*2)), #size
            samp_rate, #samp_rate
            "combined", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1_0_0_1.set_update_time(0.10)
        self.qtgui_time_sink_x_1_0_0_1.set_y_axis(-4, 4)

        self.qtgui_time_sink_x_1_0_0_1.set_y_label('Phase', "")

        self.qtgui_time_sink_x_1_0_0_1.enable_tags(True)
        self.qtgui_time_sink_x_1_0_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1_0_0_1.enable_autoscale(True)
        self.qtgui_time_sink_x_1_0_0_1.enable_grid(False)
        self.qtgui_time_sink_x_1_0_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_1_0_0_1.enable_control_panel(False)
        self.qtgui_time_sink_x_1_0_0_1.enable_stem_plot(False)


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
                self.qtgui_time_sink_x_1_0_0_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_1_0_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1_0_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1_0_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1_0_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1_0_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1_0_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_0_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_1_0_0_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_1_0_0_1_win)
        self.fft_vxx_2 = fft.fft_vcc((num_steps*2), False, window.blackmanharris(num_steps*2), True, 1)
        self.fft_vxx_0_0 = fft.fft_vcc(fft_size, True, window.blackmanharris(fft_size), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(fft_size, True, window.blackmanharris(fft_size), True, 1)
        self.blocks_vector_to_stream_2 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, (num_steps*2))
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_tag_gate_1_0_0 = blocks.tag_gate(gr.sizeof_gr_complex * fft_size, False)
        self.blocks_tag_gate_1_0_0.set_single_key("burst")
        self.blocks_tag_gate_1_0 = blocks.tag_gate(gr.sizeof_gr_complex * fft_size, False)
        self.blocks_tag_gate_1_0.set_single_key("burst")
        self.blocks_stream_to_vector_2 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, (num_steps*2))
        self.blocks_stream_to_vector_1_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, burst_len, "burst")
        self.blocks_stream_to_tagged_stream_0.set_min_output_buffer(min_output_items)
        self.blocks_skiphead_0_0 = blocks.skiphead(gr.sizeof_gr_complex*1, tone_fft_indices[1])
        self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_gr_complex*1, tone_fft_indices[0])
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(fft_size)
        self.blocks_keep_one_in_n_0_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_interleave_1 = blocks.interleave(gr.sizeof_gr_complex*1, 1)
        self.blocks_integrate_xx_0_0 = blocks.integrate_cc((int(burst_len/fft_size)), 1)
        self.blocks_integrate_xx_0 = blocks.integrate_cc((int(burst_len/fft_size)), 1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_arg_0_0_0 = blocks.complex_to_arg(1)
        self.blocks_complex_to_arg_0_0 = blocks.complex_to_arg(1)
        self.blocks_complex_to_arg_0 = blocks.complex_to_arg(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.blocks_add_xx_0.set_min_output_buffer(min_output_items)
        self.analog_sig_source_x_0_0_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, tone_freq[1], amp, 0, 0)
        self.analog_sig_source_x_0_0_0.set_min_output_buffer(min_output_items)
        self.analog_sig_source_x_0_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, tone_freq[0], amp, 0, 0)
        self.analog_sig_source_x_0_0.set_min_output_buffer(min_output_items)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.analog_sig_source_x_0_0_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.qtgui_time_sink_x_3, 0))
        self.connect((self.blocks_complex_to_arg_0_0, 0), (self.qtgui_time_sink_x_3_0, 0))
        self.connect((self.blocks_complex_to_arg_0_0_0, 0), (self.qtgui_time_sink_x_1_0_0_1, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.qtgui_time_sink_x_2, 0))
        self.connect((self.blocks_integrate_xx_0, 0), (self.blocks_complex_to_arg_0, 0))
        self.connect((self.blocks_integrate_xx_0, 0), (self.blocks_interleave_1, 0))
        self.connect((self.blocks_integrate_xx_0_0, 0), (self.blocks_complex_to_arg_0_0, 0))
        self.connect((self.blocks_integrate_xx_0_0, 0), (self.blocks_interleave_1, 1))
        self.connect((self.blocks_interleave_1, 0), (self.blocks_complex_to_arg_0_0_0, 0))
        self.connect((self.blocks_interleave_1, 0), (self.blocks_stream_to_vector_2, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_keep_one_in_n_0_0, 0), (self.blocks_integrate_xx_0_0, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.blocks_vector_to_stream_1, 0))
        self.connect((self.blocks_skiphead_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_skiphead_0_0, 0), (self.blocks_keep_one_in_n_0_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.sfcwRadar_bladerfRadarBurst_cc_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.blocks_tag_gate_1_0_0, 0))
        self.connect((self.blocks_stream_to_vector_1_0, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.blocks_stream_to_vector_2, 0), (self.fft_vxx_2, 0))
        self.connect((self.blocks_tag_gate_1_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.blocks_tag_gate_1_0_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.blocks_skiphead_0, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.blocks_skiphead_0_0, 0))
        self.connect((self.blocks_vector_to_stream_2, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.fft_vxx_0_0, 0), (self.blocks_tag_gate_1_0, 0))
        self.connect((self.fft_vxx_2, 0), (self.blocks_vector_to_stream_2, 0))
        self.connect((self.sfcwRadar_bladerfRadarBurst_cc_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.sfcwRadar_bladerfRadarBurst_cc_0, 1), (self.blocks_stream_to_vector_1_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "test")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_burst_len(self):
        return self.burst_len

    def set_burst_len(self, burst_len):
        self.burst_len = burst_len
        self.set_fft_size(int(self.burst_len/2))
        self.set_min_output_items(self.burst_len*2)
        self.blocks_stream_to_tagged_stream_0.set_packet_len(self.burst_len)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(self.burst_len)

    def get_tone_freq(self):
        return self.tone_freq

    def set_tone_freq(self, tone_freq):
        self.tone_freq = tone_freq
        self.set_tone_fft_indices([int(((self.samp_rate/2)+self.tone_freq[0])/(self.samp_rate/self.fft_size)),int(self.tone_freq[1]/(self.samp_rate/self.fft_size)+self.fft_size/2)])
        self.analog_sig_source_x_0_0.set_frequency(self.tone_freq[0])
        self.analog_sig_source_x_0_0_0.set_frequency(self.tone_freq[1])

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_tone_fft_indices([int(((self.samp_rate/2)+self.tone_freq[0])/(self.samp_rate/self.fft_size)),int(self.tone_freq[1]/(self.samp_rate/self.fft_size)+self.fft_size/2)])
        self.set_tune_th(int(self.samp_rate/20))
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_0_0_0.set_sampling_freq(self.samp_rate)
        self.qtgui_time_sink_x_1_0_0_1.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_2.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_3.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_3_0.set_samp_rate(self.samp_rate)

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.set_tone_fft_indices([int(((self.samp_rate/2)+self.tone_freq[0])/(self.samp_rate/self.fft_size)),int(self.tone_freq[1]/(self.samp_rate/self.fft_size)+self.fft_size/2)])
        self.blocks_keep_one_in_n_0.set_n(self.fft_size)
        self.blocks_keep_one_in_n_0_0.set_n(self.fft_size)

    def get_tune_th(self):
        return self.tune_th

    def set_tune_th(self, tune_th):
        self.tune_th = tune_th

    def get_tone_fft_indices(self):
        return self.tone_fft_indices

    def set_tone_fft_indices(self, tone_fft_indices):
        self.tone_fft_indices = tone_fft_indices

    def get_start_freq(self):
        return self.start_freq

    def set_start_freq(self, start_freq):
        self.start_freq = start_freq

    def get_num_steps(self):
        return self.num_steps

    def set_num_steps(self, num_steps):
        self.num_steps = num_steps

    def get_min_output_items(self):
        return self.min_output_items

    def set_min_output_items(self, min_output_items):
        self.min_output_items = min_output_items

    def get_integrate_lenth(self):
        return self.integrate_lenth

    def set_integrate_lenth(self, integrate_lenth):
        self.integrate_lenth = integrate_lenth

    def get_freq_step(self):
        return self.freq_step

    def set_freq_step(self, freq_step):
        self.freq_step = freq_step

    def get_freq_list_0(self):
        return self.freq_list_0

    def set_freq_list_0(self, freq_list_0):
        self.freq_list_0 = freq_list_0

    def get_amp(self):
        return self.amp

    def set_amp(self, amp):
        self.amp = amp
        self.analog_sig_source_x_0_0.set_amplitude(self.amp)
        self.analog_sig_source_x_0_0_0.set_amplitude(self.amp)




def main(top_block_cls=test, options=None):

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
