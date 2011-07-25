# coding: utf-8

import os
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

try:
    import ckeditor
except ImportError:
    pass
