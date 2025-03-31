# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT sfcwRadar_sources)
    message(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT sfcwRadar_sources)

########################################################################
# Check for pygccxml
########################################################################
gr_python_check_module_raw("pygccxml" "import pygccxml" PYGCCXML_FOUND)

include(GrPybind)

########################################################################
# Python Bindings
########################################################################
list(APPEND sfcwRadar_python_files
    bladerfRadarMIMO_python.cc
    bladerfRadarController_cc_python.cc
    sfcw_radar_mimo_cc_python.cc
    sfcw_radar_miso_cc_python.cc python_bindings.cc)

gr_pybind_make_oot(sfcwRadar ../../.. gr::sfcwRadar "${sfcwRadar_python_files}")

# copy bindings extension for use in QA test module
add_custom_command(
    TARGET sfcwRadar_python
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:sfcwRadar_python>
            ${PROJECT_BINARY_DIR}/test_modules/gnuradio/sfcwRadar/)

install(
    TARGETS sfcwRadar_python
    DESTINATION ${GR_PYTHON_DIR}/gnuradio/sfcwRadar
    COMPONENT pythonapi)
