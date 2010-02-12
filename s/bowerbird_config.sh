# global variables automatically generated by
# /home/camerons/projects/taylor/core/s/python/convert_config_for_sh.pyc
# from 
# ../../bowerbird_config
# to permit easy access for shell scripts

# Do not edit directly as it will be overwritten

# This section stores the times for scheduled captures.
# It will always be moved back to the top, so don't bother moving it.
scheduled_capture__Bowerbirds="9:00 -  11:00"
scheduled_capture__Gray Tree Frogs="R -8:00 - S -5:00"
scheduled_capture__Poison Dart Frogs="18:00 -  18:30"
scheduled_capture__Cane Toads="R -4:00 - R -2:00"

# don't change this section name without changing the parameter in controller.py
# Station Information
# don't change this key name without changing the parameter in controller.py
# Location, Name, string, 
station_information__name="Nourlangie Rock"
# Location, Timezone offset, float, hours
station_information__tz_offset="10"
# Location, Latitude, float, degrees
station_information__latitude="-33.216666"
# Location, Longitude, float, degrees
station_information__longitude="150.83333"

# Spectral Analysis
# FFTW, Enable, bool, 
spectral_analysis__use_fftw="1"
# changed appropriately when files read
# FFTW, Sampling Rate, int, Hz
spectral_analysis__sampling_rate="16000"
# FFTW, Points, int, 
spectral_analysis__fft_points="1024"
# FFTW, Window, int, 
spectral_analysis__fft_window="128"
# FFTW, Overlap.05
# Maximum Gap Size, , float, seconds
spectral_analysis__max_gap_size="0.005"
# hertz
spectral_analysis__peak_radius="265"
# FIXME should be DB?
spectral_analysis__peak_min_height="0.0001"
# hertz
spectral_analysis__relative_relief_inside_radius="150"
# hertz
spectral_analysis__relative_relief_outside_radius="265"
# minimum ratio of peak to bins between inside and outside radius
spectral_analysis__min_relative_relief="5"
# minimum relative power of non-peaks incorporated into tracks
spectral_analysis__min_power_between_track_bins="0.2"

# Section call:
call__output_directory="."
call__pathname_prefix="%s/unit"
call__index_filename="%s.html"
call__sound_filename="%s%05d.wav"
call__image_filename="%s%05d.jpg"
call__image_size="4096x2048"
call__peaks_image_filename="%s_peaks_c%d_%02d.jpg"
call__peaks_image_maximum_length="8000"
call__database="%s.db"
call__details_filename="%s%05d.details"
call__track_filename="%s%05d.track"
#spectrum_filename = %s%05d.spectrum
call__spectrum_filename=""""
call__calculate_power="1"
call__calculate_phase="0"
call__refine_sinusoid_parameters="0"
call__spectrum_radius="5"
call__max_sound_buffer_size="2400000"
# seconds
call__prefix_seconds="0.1"
call__suffix_seconds="0.1"
call__ignore_channel_bitmap="0"

# Section database:
database__start_cmd="create table if not exists sources (source_id INTEGER PRIMARY KEYname TEXTsampling_rate DOUBLEfft_n_bins INTEGERfft_step_size INTEGERfft_window_size INTEGER);create table if not exists units (unit_id INTEGER PRIMARY KEYsource_id INTEGERchannel INTEGERfirst_frame INTEGERn_frames INTEGERfrequency BLOBamplitude BLOBphase BLOB);create index if not exists unit_source_index on units(source_id);create index if not exists source_name_index on sources(name);begin transaction;"
database__source_insert="insert into sources values(NULL, ?, ?, ?, ?, ?)"
database__unit_insert="insert into units values(NULL, ?, ?, ?, ?, ?, ?, ?)"
database__finish_cmd="commit"
database__busy_timeout="60000"

# Section tonal_model:
tonal_model__sampling_rate="16000"

# Section localization:
localization__base_dir="/raid/data/barren_grounds/"
localization__date_dir="2008_03_19"
localization__station0_dir="barren_grounds0"
localization__station1_dir="barren_grounds1"
localization__station2_dir="barren_grounds2"
localization__breathing_space="0.1"
localization__station0_position="S34 40.521250658394003 E150 42.541497945786006"
localization__station1_position="S34 40.588880601453603 E150 42.648518085480006"
localization__station2_position="S34 40.622232015313799 E150 42.528945207595797"
localization__result_file="result.succinct"
localization__click_threshold="0.2"
localization__compress_clicktracks="0"
localization__kml_file="new.kml"
localization__kml_name="Ground Parrot Localization"
localization__kml_desc="More information at http://bioacoustics.cse.unsw.edu.au"


# Sound Capture
# Buffer, Size, int, 
sound_capture__sound_buffer_size="64000"
# Buffer, Frames, int, 
sound_capture__sound_buffer_frames="960000"
# Storage, Root Dir, string, 
sound_capture__sound_file_root_dir="/var/lib"
# Storage, File Ext., string, 
sound_capture__sound_file_ext="wv"
# Storage, Details File Ext., string, 
sound_capture__sound_details_ext="details"
# 0: raw wav, 1: use builtin wavpack, 2: use shellcmd
# Storage, Compression Type, int, 
sound_capture__sound_compression_type="2"
# Storage, Compression Shell Cmd, string, 
sound_capture__sound_compressor_shellcmd="/usr/bin/wavpack -q -f - >%s"
# Alsa, PCM Device Name, string, 
sound_capture__alsa_pcm_name="hw:10"
# Alsa, Channels, int, 
sound_capture__alsa_n_channels="4"
# Alsa, Sampling Rate, int, Hz
sound_capture__alsa_sampling_rate="32000"
# Alsa, Period Size, int, 
sound_capture__alsa_periods_size="32000"
# Alsa, Periods, int, 
sound_capture__alsa_n_periods="2"
# Alsa, Buffer Size, int, 
sound_capture__alsa_buffer_size="128000"
sound_capture__beep="false"
sound_capture__active_high="false"
sound_capture__sound_n_files="4"
# Scheduling, Command, string, 
sound_capture__schedule_command="sound_capture -orecording_duration=%s"
# Scheduling, User, string, 
sound_capture__schedule_user="root"
# Scheduling, Days to Plan, int, days
sound_capture__schedule_days="3"

# Section beagleboard_watchdog:
beagleboard_watchdog__prefix="avr://"
beagleboard_watchdog__feed="watchdog pulse"
beagleboard_watchdog__reboot="REALLY reset the Beagleboard"
beagleboard_watchdog__tty="/dev/ttyS2"
beagleboard_watchdog__files="/var/lib/bowerbird/status/network_up:100000"
beagleboard_watchdog__feed_seconds="300"
beagleboard_watchdog__granularity_seconds="60"
beagleboard_watchdog__startup_seconds="7200"