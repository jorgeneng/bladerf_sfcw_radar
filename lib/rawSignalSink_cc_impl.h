/* -*- c++ -*- */
/*
 * Copyright 2024 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_RAWSIGNALSINK_CC_IMPL_H
#define INCLUDED_SFCWRADAR_RAWSIGNALSINK_CC_IMPL_H

#include <gnuradio/sfcwRadar/rawSignalSink_cc.h>
#include <libbladeRF.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <cstdio>

namespace gr {
namespace sfcwRadar {

class rawSignalSink_cc_impl : public rawSignalSink_cc
{
private:
    uint64_t scan_id = 0;

    const std::string rx_suffix = "_rx_";
    const std::string ref_suffix = "_ref_";
    std::string d_rx_dir_filename;
    std::string d_ref_dir_fielname;
    FILE* d_ref_handle = nullptr;
    FILE* d_rx_handle = nullptr;
    const size_t d_itemsize;

    /**
     * For meta data recording
     * */
    int d_num_steps;
    bladerf_frequency d_start_freq;
    bladerf_frequency d_freq_step;
    bladerf_gain d_tx_gain;
    bladerf_gain d_rx_gain;
    bladerf_gain d_ref_gain;
    int d_samp_rate;
    size_t d_burst_len;
    float d_cw_frequency;
    float d_cw_amplitude;

public:
    rawSignalSink_cc_impl(std::string dir, 
                          std::string prefix, 
                          int num_steps,
                          bladerf_frequency start_freq,
                          bladerf_frequency freq_step,
                          bladerf_gain tx_gain,
                          bladerf_gain rx_gain,
                          bladerf_gain ref_gain,
                          int samp_rate,
                          size_t burst_len,
                          float cw_frequency,
                          float cw_amplitude);
    ~rawSignalSink_cc_impl();

    // Where all the action really happens
    int work(int noutput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_RAWSIGNALSINK_CC_IMPL_H */
