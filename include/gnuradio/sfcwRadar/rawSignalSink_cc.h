/* -*- c++ -*- */
/*
 * Copyright 2024 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SFCWRADAR_RAWSIGNALSINK_CC_H
#define INCLUDED_SFCWRADAR_RAWSIGNALSINK_CC_H

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
class SFCWRADAR_API rawSignalSink_cc : virtual public gr::sync_block
{
public:
    typedef std::shared_ptr<rawSignalSink_cc> sptr;

    /*!
     * \brief Return a shared_ptr to a new instance of sfcwRadar::rawSignalSink_cc.
     *
     * To avoid accidental use of raw pointers, sfcwRadar::rawSignalSink_cc's
     * constructor is in a private implementation
     * class. sfcwRadar::rawSignalSink_cc::make is the public interface for
     * creating new instances.
     */
    static sptr make(std::string dir, 
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
};

} // namespace sfcwRadar
} // namespace gr

#endif /* INCLUDED_SFCWRADAR_RAWSIGNALSINK_CC_H */
