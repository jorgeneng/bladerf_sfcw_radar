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
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import sfcwRadar
import sip



class testMultitarget(gr.top_block, Qt.QWidget):

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

        self.settings = Qt.QSettings("GNU Radio", "testMultitarget")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32e3
        self.num_steps = num_steps = 64
        self.mf_size = mf_size = 2**8
        self.ini_offset = ini_offset = 0
        self.burst_len = burst_len = 2**11

        ##################################################
        # Blocks
        ##################################################

        self._ini_offset_range = qtgui.Range(0, (int(burst_len/2)), 1, 0, 200)
        self._ini_offset_win = qtgui.RangeWidget(self._ini_offset_range, self.set_ini_offset, "'ini_offset'", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._ini_offset_win)
        self.sfcwRadar_matchedFilter_0 = sfcwRadar.matchedFilter(mf_size)
        self.sfcwRadar_calibration_0 = sfcwRadar.calibration(num_steps, "cal_64k_0.npy", 0)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_c(
            num_steps, #size
            samp_rate, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(-1, 1)

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


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            (200*10), #size
            samp_rate, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

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


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, num_steps)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, mf_size)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, num_steps)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, mf_size)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, mf_size)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, mf_size)
        self.blocks_keep_m_in_n_0_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, mf_size, burst_len, ini_offset)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, mf_size, burst_len, ini_offset)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 1e3, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_keep_m_in_n_0_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.sfcwRadar_matchedFilter_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.sfcwRadar_matchedFilter_0, 1))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.sfcwRadar_calibration_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_keep_m_in_n_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_keep_m_in_n_0_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.qtgui_time_sink_x_0_0, 0))
        self.connect((self.sfcwRadar_calibration_0, 0), (self.blocks_vector_to_stream_1, 0))
        self.connect((self.sfcwRadar_matchedFilter_0, 0), (self.blocks_vector_to_stream_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "testMultitarget")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_0.set_samp_rate(self.samp_rate)

    def get_num_steps(self):
        return self.num_steps

    def set_num_steps(self, num_steps):
        self.num_steps = num_steps

    def get_mf_size(self):
        return self.mf_size

    def set_mf_size(self, mf_size):
        self.mf_size = mf_size
        self.blocks_keep_m_in_n_0.set_m(self.mf_size)
        self.blocks_keep_m_in_n_0_0.set_m(self.mf_size)
        self.blocks_keep_one_in_n_0.set_n(self.mf_size)

    def get_ini_offset(self):
        return self.ini_offset

    def set_ini_offset(self, ini_offset):
        self.ini_offset = ini_offset
        self.blocks_keep_m_in_n_0.set_offset(self.ini_offset)
        self.blocks_keep_m_in_n_0_0.set_offset(self.ini_offset)

    def get_burst_len(self):
        return self.burst_len

    def set_burst_len(self, burst_len):
        self.burst_len = burst_len
        self.blocks_keep_m_in_n_0.set_n(self.burst_len)
        self.blocks_keep_m_in_n_0_0.set_n(self.burst_len)




def main(top_block_cls=testMultitarget, options=None):

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
