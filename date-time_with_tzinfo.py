#original src https://obsproject.com/forum/resources/date-time.906/
#py -m pip install python-dateutil

# 導入手順　https://photos.app.goo.gl/puPDpiXsFb41YjW77
#work on OBS  python312
#2024/05/21　zoneinfoのデータが2006年前でしかはいってないようなので除外（）
#2024/05/16 開始の変換でzone影響あり　tzdataからpythondateutil　変更
#2024/05/16 isoでのイベントタイマーに改造

import obspython as obs
import datetime
import math
import time
from dateutil import tz

#書式コード	説明	例 ゾーン影響あり
#%Y	西暦（4桁表記。0埋め）	2021
#%m	月（2桁表記。0埋め）	11
#%d	日（2桁表記。0埋め）	04
#%H	時（24時間制。2桁表記。0埋め）	17
#%M	分（2桁表記。0埋め）	37
#%S	秒（2桁表記。0埋め）	28
#%y	西暦の下2桁（0埋め）	21
#%l	AM／PMを表す文字列	PM
#%x	日付をMM/DD/YY形式にしたもの	11/04/21
#%X	時刻をhh:mm:ss形式にしたもの	17:37:28
#%a	曜日の短縮形	Thu
#%A	曜日	Thursday
#%z	現在のタイムゾーンとUTC（協定世界時）とのオフセット	+0900
#%Z	現在のタイムゾーン	JST

##拡張部分 ゾーン影響なし
#OS %OS　　awareなんでタイムゾーンは欠損　time_formatで出力
#JST %JST　　日本時間time_formatで出力
#UTC %UTC　　UTC MASTER  time_formatで出力
#ZULL %ZULL　UTC協定時間 ISO8601
#ISO %ISO　　zone影響あり ISO8601
#
#イベント名:%E
#開始時刻:%ST　zone影響あり
#終了時刻:%EN　zone影響あり
#イベ期間:%SP
#経過時間:%EL
#残り時間:%LF
#進捗状況:%Q %P%%

interval    = 10  #更新間隔0.1秒
source_name = ""
time_string = "%Y/%m/%d %H:%M:%S %z"
time_format = "%Y/%m/%d %H:%M:%S %Z %a"
iso_format = "%Y-%m-%dT%H:%M:%S%z"
zone        ="Asia/Tokyo"
zones       = ["Asia/Tokyo","Asia/Seoul","Asia/Taipei","America/Los_Angeles"]

ibe='星雲の窓辺'
st = '2024-04-30T17:00:00+09:00'
en = '2024-05-08T22:00:00+09:00'
obsbar =3
utc =9
JST=""
UTC=""

# ------------------------------------------------------------


def dtime(dt):
    if dt<0:
            return "0日0時間0分"
    dt=abs(dt)
    seconds  = math.floor((dt / 10) % 60)
    minutes  = math.floor((dt / 60) % 60)
    hours    = math.floor((dt / 3600) % 24)
    days     = math.floor(dt / 86400)
    tmp = str(days) +"日" +str(hours)+"時間"+str(minutes) +"分"
    return tmp


def makebar(p):
    global obsbar
    
    base ="="
    q=obsbar
    
    p=p/q
    
    p=math.floor(p)
    s=""
    
    for i in range(p):
        s= s + base
        
    s=s+">"
    
    q=math.floor(100/q)
    for i in range(p+1,q, 1):
        s= s +"_"

    bar = "["+s+"]"
    return bar


def update_text():
    global interval
    global source_name
    global time_string
    global time_format
    global zone
    global ibe
    global st
    global en
    global iso_format
    global UTC
    global JST

    s=st.replace('Z', '+00:00')
    ss=en.replace('Z', '+00:00')
    stt  = datetime.datetime.fromisoformat(s)
    ent  = datetime.datetime.fromisoformat(ss)
    # 変換前後のタイムゾーンを指定
    cv_tz = tz.gettz(zone)
    stt = stt.astimezone(cv_tz)
    ent = ent.astimezone(cv_tz)
    ts = stt.strftime(time_format)
    te = ent.strftime(time_format)

    sttmp=stt.timestamp()
    stt=datetime.datetime.fromtimestamp(sttmp)
    entmp=ent.timestamp()
    ent=datetime.datetime.fromtimestamp(entmp)
    span= abs(ent-stt)
    
    nn=time.time()
    elapsed=dtime(nn-sttmp)
    left= dtime(entmp-nn)
    x = (nn-sttmp)/abs(entmp-sttmp)*100
    n = 2
    y = math.floor(x * 10 ** n) / (10 ** n)
    if y>100:
             y=100
    if y<0:
             y=0
     
    bar=makebar(y)

    temp=time_string.replace('%ST',ts)
    temp=temp.replace('%EN',te)
    temp=temp.replace('%SP',str(span))
    temp=temp.replace('%EL',elapsed)
    temp=temp.replace('%LF',left)
    temp=temp.replace('%P',str(y))
    temp=temp.replace('%E',ibe)
    temp=temp.replace('%Q',bar)
    temp=temp.replace('%OS',datetime.datetime.now(tz=None).strftime(time_format))
    temp=temp.replace('%JST',datetime.datetime.now(JST).strftime(time_format))
    temp=temp.replace('%UTC',datetime.datetime.now(UTC).strftime(time_format))
    temp=temp.replace('%ZULL',datetime.datetime.now(datetime.timezone.utc).strftime(iso_format))
    temp=temp.replace('%ISO',datetime.datetime.now().astimezone(cv_tz).strftime(iso_format))
    

    source = obs.obs_get_source_by_name(source_name)
    if source is not None:
        settings = obs.obs_data_create()
        now = datetime.datetime.now()
        now=now.astimezone(cv_tz)
        obs.obs_data_set_string(settings, "text", now.strftime(temp))
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
    obs.obs_data_set_default_int(settings, "utc",utc)
    obs.obs_data_set_default_string(settings, "format", time_string)
    obs.obs_data_set_default_string(settings, "time_format", time_format)
    obs.obs_data_set_default_string(settings, "zone", zone )
    obs.obs_data_set_default_string(settings, "eve", ibe)
    obs.obs_data_set_default_string(settings, "start", st)
    obs.obs_data_set_default_string(settings, "end", en)
    obs.obs_data_set_default_int(settings, "bar", obsbar)

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

    obs.obs_properties_add_int(props, "utc", "UTC MASTER", -14, 14, 1)
    time_zone_list = obs.obs_properties_add_list(
        props, "zone", "Time zone", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING
    )
    for timezone in zones:
        obs.obs_property_list_add_string(time_zone_list, timezone, timezone)
    
    obs.obs_properties_add_text(props, "format", "time_string", obs.OBS_TEXT_MULTILINE) 
    obs.obs_properties_add_text(props, "time_format", "time_format", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "eve", "EVENT", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "start", "START", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "end", "END", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "bar", "BAR LENGTH(100÷X)", 1, 10, 1)
    
    obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)
    return props

def script_update(settings):
    global interval
    global source_name
    global time_string
    global time_format
    global zone
    global st
    global en
    global obsbar
    global utc
    global UTC
    global JST
    
    utc    = obs.obs_data_get_int(settings, "utc")
    interval    = obs.obs_data_get_int(settings, "interval")
    source_name = obs.obs_data_get_string(settings, "source")
    time_string = obs.obs_data_get_string(settings, "format")
    time_format = obs.obs_data_get_string(settings, "time_format")
    zone = obs.obs_data_get_string(settings, "zone")
    st = obs.obs_data_get_string(settings, "start")
    en = obs.obs_data_get_string(settings, "end")
    obsbar = obs.obs_data_get_int(settings, "bar")
    
    t_delta = datetime.timedelta(hours=9)  # 9時間
    JST = datetime.timezone(t_delta, 'JST') 
    t_delta = datetime.timedelta(hours=utc)
    UTC = datetime.timezone(t_delta, 'UTC') 
    
    obs.timer_remove(update_text)
    
    if source_name != "":
        obs.timer_add(update_text, interval * 100)
