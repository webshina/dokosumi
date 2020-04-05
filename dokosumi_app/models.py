from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from stdimage.models import ImageField
from stdimage.models import StdImageField

class ResultRank(models.Model):
    rank =  models.IntegerField(default=None)
    station_name = models.CharField(max_length=999, default=None)
    lat = models.FloatField(default=0.0)
    lon = models.FloatField(default=0.0)
    dist_to_office = models.FloatField(default=None)
    access = models.FloatField(default=None)
    landPrice = models.FloatField(default=None)
    park = models.FloatField(default=None)
    flood = models.FloatField(default=None)
    security = models.FloatField(default=None)
    score = models.FloatField(default=None)