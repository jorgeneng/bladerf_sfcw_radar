/* -*- c++ -*- */
/*
 * Copyright 2024 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_BLADERFRADARBURST_CC_H
#define INCLUDED_SFCWRADAR_BLADERFRADARBURST_CC_H

#include <gnuradio/sfcwRadar/api.h>
#include <gnuradio/tagged_stream_block.h>
#include <libbladeRF.h>

namespace gr {
namespace sfcwRadar {

/*!
 * \brief <+description of block+>
 * \ingroup sfcwRadar
 *
 */
class SFCWRADAR_API bladerfRadarBurst_cc : virtual public gr::tagged_stream_block
{
public:
    typedef std::shared_ptr<bladerfRadarBurst_cc> sptr;

    /*!
     * \brief Return a shared_ptr to a new instance of sfcwRadar::bladerfRadarBurst_cc.
     *
     * To avoid accidental use of raw pointers, sfcwRadar::bladerfRadarBurst_cc's
     * constructor is in a private implementation
     * class. sfcwRadar::bladerfRadarBurst_cc::make is the public interface for
     * creating new instances.
     */
    static sptr make(bladerf_frequency start_freq,
                     int num_steps,
                     bladerf_frequency freq_step,
                     int samp_rate,
                     bladerf_gain rx_gain,
                     bladerf_gain tx_gain,
                     bladerf_gain ref_gain,
                     size_t burst_len,
                     size_t num_buffers,
                     size_t buffer_size,
                     size_t num_transfers);

    virtual int set_rx_gain(bladerf_gain gain) = 0;
    virtual int set_ref_gain(bladerf_gain gain) = 0;
    virtual int set_tx_gain(bladerf_gain gain) = 0;
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_BLADERFRADARBURST_CC_H */
