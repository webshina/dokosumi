import sys
import googlemaps
import pprint # list型やdict型を見やすくprintするライブラリ
import keys
import requests
import json
import googleImageScraping
import pandas as pd
import time
import os

r = googleImageScraping.collectCntAtStaion('パチンコ')