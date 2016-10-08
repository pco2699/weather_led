#! /usr/bin/python3
from urllib import request
import json
from pytz import timezone
from dateutil import parser
import RPi.GPIO as GPIO
import time

"""
OpenWeatherMap APIで東京の天気を取得してきて
Lチカ or Lピカしてくれる

直近の天気=> 晴れ and 9時間後の天気=> 晴れ
    青LEDがLチカ
直近の天気=> 雨 or 9時間後の天気=> 雨
    赤LEDがLピカ
"""

"""
OpenWeatherMapで取得したdateが基本UTCのため
JSTに変換する関数(デバッグ用)
Input: time_string:UTCの日付文字列
Output: JSTのdate
"""
def parse_jst(time_string):
    return parser.parse(time_string).replace(tzinfo=timezone('UTC')).astimezone(timezone('Asia/Tokyo'))

"""
取得してきたOpenWeatherMapAPIの天気予報のリストから
指定した添字の日付を取得する関数
Input: num:添字(詳細はOpenWeatherMapAPIdocを参照)
http://openweathermap.org/forecast5#JSON
Output: UTCの日付文字列
"""
def get_date(num):
    if content == "":
        return content
    else:
        return content["list"][num]["dt_txt"]

"""
取得してきたOpenWeatherMapAPIの天気予報のリストから
指定した添字の日付を取得する関数
Input: num:添字(詳細はOpenWeatherMapAPIdocを参照)
http://openweathermap.org/forecast5#JSON
Output: そのときの天気の状況を示す文字列
(ex. rain, cloudly等)
"""
def get_desc(num):
    if content == "":
        return content
    else:
        return content["list"][num]["weather"][0]["description"]

"""
指定したGPIO番号に接続されたLEDを点滅させる関数
Input: color:光らせるGPIO番号(後に定義した定数で色と紐付け) vtime:光らせる時間(おおよそsec)
Output: なし
"""
def blink_led(color, vtime):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(color, GPIO.OUT)
    cnt = 0
    while vtime > cnt:
       GPIO.output(color, True)
       time.sleep(0.5)
       GPIO.output(color, False)
       time.sleep(0.5)
       cnt += 1
    GPIO.cleanup()

"""
指定したGPIO番号に接続されたLEDを点灯させる関数
Input: color:光らせるGPIO番号(後に定義した定数で色と紐付け) vtime:光らせる時間(おおよそsec)
Output: なし
"""
def flash_led(color, vtime):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(color, GPIO.OUT)

    GPIO.output(color, True)

    cnt = 0
    while vtime > cnt:
        time.sleep(1)
        cnt += 1
    GPIO.cleanup()

# APIから取得してきたJSONを格納するグローバル変数(要改善かも)
content = ""

# GPIO番号と接続している色を対応させる。
RED = 22
BLUE = 23
GREEN = 24

# LEDが点灯・点滅し続ける時間
TIME = 3600

# OpenWeatherMapApiのパス(API_KEYは自分の取得したものを入れる)
API_KEY = ''
URL = 'http://api.openweathermap.org/data/2.5/forecast?q=Tokyo,jp&APPID='

if __name__ == '__main__':
    # APIで天気情報を取得する
    response = request.urlopen(URL+API_KEY)
    content = json.loads(response.read().decode('utf8'))

    # 朝時点で雨
    morning_rain_flag = False
    evening_rain_flag = False

    # 直近の天気情報を取得しプリント
    print(get_desc(0))
    # 9時間後の天気情報を取得しプリント
    print(get_desc(3))

    # 直近天気を検索、もしrainが含まれていたらフラグを真に
    if 'rain' in get_desc(0):
        morning_rain_flag = True

    # 直近天気を検索、もしrainが含まれていたらフラグを真に
    if 'rain' in get_desc(3):
        evening_rain_flag = True

    # 直近・9時間後のフラグをかけ合わせてresultに格納
    result = morning_rain_flag or evening_rain_flag

    if result:
        # 雨が降る場合
        blink_led(RED, TIME)
    else:
        # 晴れの場合
        flash_led(BLUE, TIME)
