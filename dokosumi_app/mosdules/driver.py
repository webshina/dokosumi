import sys
import googlemaps
import pprint # list型やdict型を見やすくprintするライブラリ
import keys
import requests
import json
import collectCntAtStaion
import pandas as pd
import time
import os

collectCntAtStaion = collectCntAtStaion.CollectCntAtStaion()
r = collectCntAtStaion.collectCntAtStaion('パチンコ')