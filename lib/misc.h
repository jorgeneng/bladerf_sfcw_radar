/* -*- c++ -*- */
/*
 * Author: Hui HUANG
 * Email: hui.huang@uni.lu
 *
 * Copyright 2025 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef MISC_H
#define MISC_H

#include <libbladeRF.h>

struct channel_config {
    bladerf_channel channel;
    unsigned int frequency;
    unsigned int bandwidth;
    unsigned int samplerate;
    bladerf_gain gain;
    bladerf_gain_mode gain_mode = BLADERF_GAIN_MANUAL;
};

struct bladerf_quick_tune_info{
    bladerf_frequency freq;
    bladerf_quick_tune quick_tune;
};

struct libbladeRF_buffer_config{
    size_t num_buffers;
    size_t buffer_size;
    size_t num_transfers;
};

struct frequency_plan_config{
    bladerf_frequency start_freq;
    int num_steps;
    bladerf_frequency step_size;
};

#endif

