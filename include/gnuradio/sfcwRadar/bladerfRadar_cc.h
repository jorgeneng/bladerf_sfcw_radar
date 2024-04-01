/* -*- c++ -*- */
/*
 * Copyright 2024 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_BLADERFRADAR_CC_H
#define INCLUDED_SFCWRADAR_BLADERFRADAR_CC_H

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
class SFCWRADAR_API bladerfRadar_cc : virtual public gr::sync_block
{
public:
    typedef std::shared_ptr<bladerfRadar_cc> sptr;

    /*!
     * \brief Return a shared_ptr to a new instance of sfcwRadar::bladerfRadar_cc.
     *
     * To avoid accidental use of raw pointers, sfcwRadar::bladerfRadar_cc's
     * constructor is in a private implementation
     * class. sfcwRadar::bladerfRadar_cc::make is the public interface for
     * creating new instances.
     */
    static sptr make(bladerf_frequency start_freq,
                     int num_steps,
                     bladerf_frequency freq_step,
                     int samp_rate,
                     float rx_gain,
                     float tx_gain,
                     int tune_th);
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_BLADERFRADAR_CC_H */
