find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_SFCWRADAR gnuradio-sfcwRadar)

FIND_PATH(
    GR_SFCWRADAR_INCLUDE_DIRS
    NAMES gnuradio/sfcwRadar/api.h
    HINTS $ENV{SFCWRADAR_DIR}/include
        ${PC_SFCWRADAR_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_SFCWRADAR_LIBRARIES
    NAMES gnuradio-sfcwRadar
    HINTS $ENV{SFCWRADAR_DIR}/lib
        ${PC_SFCWRADAR_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-sfcwRadarTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_SFCWRADAR DEFAULT_MSG GR_SFCWRADAR_LIBRARIES GR_SFCWRADAR_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_SFCWRADAR_LIBRARIES GR_SFCWRADAR_INCLUDE_DIRS)
