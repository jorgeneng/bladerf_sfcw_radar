/* -*- c++ -*- */
/*
 * Copyright 2024 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_RAWSIGNALSINK_CC_IMPL_H
#define INCLUDED_SFCWRADAR_RAWSIGNALSINK_CC_IMPL_H

#include <gnuradio/sfcwRadar/rawSignalSink_cc.h>
#include <cstdio>

namespace gr {
namespace sfcwRadar {

class rawSignalSink_cc_impl : public rawSignalSink_cc
{
private:
    // Nothing to declare in this block.
    uint64_t scan_id = 0;

    FILE* d_ref_handle = nullptr;
    FILE* d_rx_handle = nullptr;
    const size_t d_itemsize;

public:
    rawSignalSink_cc_impl();
    ~rawSignalSink_cc_impl();

    // Where all the action really happens
    int work(int noutput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_RAWSIGNALSINK_CC_IMPL_H */
