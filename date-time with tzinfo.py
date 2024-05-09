#original src https://obsproject.com/forum/resources/date-time.906/
#need py -m pip install tzdata   導入手順　https://photos.app.goo.gl/puPDpiXsFb41YjW77
#work on OBS  python312

import obspython as obs
import datetime
from zoneinfo import *

interval    = 10
source_name = ""
time_string = "%Y/%m/%d %H:%M:%S %z"
zone        ="Asia/Tokyo"
zones       = ["Asia/Tokyo","Asia/Seoul","Asia/Taipei","America/Los_Angeles"]

# ------------------------------------------------------------

def update_text():
    global interval
    global source_name
    global time_string
    global zone

    source = obs.obs_get_source_by_name(source_name)
    if source is not None:
        now = datetime.datetime.now(ZoneInfo(zone))
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", now.strftime(time_string))
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)

def refresh_pressed(props, prop):
    update_text()

# ------------------------------------------------------------

def script_description():
    return "Updates a text source to the current date and time"

def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "interval", interval)
    obs.obs_data_set_default_string(settings, "format", time_string )
    obs.obs_data_set_default_string(settings, "zone", zone )

def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_int(props, "interval", "Update Interval (seconds)", 1, 3600, 1)


    # Add sources select dropdown
    p = obs.obs_properties_add_list(props, "source", "Text Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    # Make a list of all the text sources
    obs.obs_property_list_add_string(p, "[No text source]", "[No text source]")
    
    sources = obs.obs_enum_sources()

    if sources is not None:
        for source in sources:
            name = obs.obs_source_get_name(source)
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)
        obs.source_list_release(sources)


    obs.obs_properties_add_text(props, "format", "format", obs.OBS_TEXT_MULTILINE) 
    time_zone_list = obs.obs_properties_add_list(
        props, "zone", "Time zone", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING
    )
    for timezone in zones:
        obs.obs_property_list_add_string(time_zone_list, timezone, timezone)

    obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)
    return props

def script_update(settings):
    global interval
    global source_name
    global time_string
    global zone

    interval    = obs.obs_data_get_int(settings, "interval")
    source_name = obs.obs_data_get_string(settings, "source")
    time_string = obs.obs_data_get_string(settings, "format")
    zone = obs.obs_data_get_string(settings, "zone")

    obs.timer_remove(update_text)
    
    if source_name != "":
        obs.timer_add(update_text, interval * 100)
