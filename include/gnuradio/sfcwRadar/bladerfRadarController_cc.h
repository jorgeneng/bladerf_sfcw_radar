/* -*- c++ -*- */
/*
 * Copyright 2025 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_BLADERFRADARCONTROLLER_CC_H
#define INCLUDED_SFCWRADAR_BLADERFRADARCONTROLLER_CC_H

#include <gnuradio/sfcwRadar/api.h>
#include <gnuradio/sync_block.h>
#include <libbladeRF.h>

namespace gr {
namespace sfcwRadar {

/*!
 * \brief <+description of block+>
 * \ingroup sfcwRadar
 *
 */
class SFCWRADAR_API bladerfRadarController_cc : virtual public gr::sync_block
{
public:
    typedef std::shared_ptr<bladerfRadarController_cc> sptr;

    /*!
     * \brief Return a shared_ptr to a new instance of
     * sfcwRadar::bladerfRadarController_cc.
     *
     * To avoid accidental use of raw pointers, sfcwRadar::bladerfRadarController_cc's
     * constructor is in a private implementation
     * class. sfcwRadar::bladerfRadarController_cc::make is the public interface for
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
                     size_t num_transfers,
                     float cw_amplitude,
                     float cw_frequency,
                     float ts_inc_send,
                     float ts_inc_recv,
                     float ts_inc_tune);
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_BLADERFRADARCONTROLLER_CC_H */
