# -*- coding: utf-8 -*-
"""Common Controller"""
from cattle_monitor.lib.base import BaseController
from cattle_monitor.lib.crud_utils import ModelForm
from cattle_monitor.lib.tg_utils import *
from cattle_monitor.model import *

FILENAME = os.path.abspath(resource_filename('cattle_monitor', 'public'))
PUBLIC_DIRNAME = os.path.join(FILENAME)
IMAGES_DIRNAME = os.path.join(PUBLIC_DIRNAME, 'img')
DOCX_DIRNAME = os.path.join(PUBLIC_DIRNAME, 'docx')
UPLOADS_DIRNAME = os.path.join(IMAGES_DIRNAME, 'uploads')


class CommonController(BaseController):

   def get_threshold_temperature_form(self, *args, **kwargs):
      threshold_temperature_id = kwargs.get('threshold_temperature_id', None)
      threshold_temp = ThresholdTemperature.by_id(threshold_temperature_id)

      mf = ModelForm(**{'model': ThresholdTemperature, 'record': threshold_temp})
      return mf.get_form()





