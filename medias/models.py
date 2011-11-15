
from os import *
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from PIL import Image as PilImage

from medias.settings import *

class File(models.Model):
    path = models.FileField(_('Path'), upload_to='medias/%Y/%m/%d/%H')
    title = models.CharField(_('Title'), max_length=255)
    #TODO: take upload_to from settings & include type
    size = models.IntegerField(_('Size'), db_index=True, blank=True)
    ext = models.CharField(_('Extension'), max_length=255, db_index=True, blank=True)
    type = models.CharField(_('Type'), max_length=255, db_index=True, blank=True)

    width = models.IntegerField(_('Width'), db_index=True, blank=True, default=0)
    height = models.IntegerField(_('Height'), db_index=True, blank=True, default=0)

    length = models.IntegerField(_('Length'), db_index=True, blank=True, default=0)
    bitrate = models.IntegerField(_('Bitrate'), db_index=True, blank=True, default=0)

    words = models.IntegerField(_('Words'), db_index=True, blank=True, default=0)

    created_at = models.DateTimeField(_('Date created'),
                                      auto_now_add=True, db_index=True,
                                      editable=False, default=datetime.now())
    created_by = models.ForeignKey(User, related_name='+',
                                   editable=False, blank=True,
                                   null=True, default=None)
    modified_at = models.DateTimeField(_('Date modified'),
                                       auto_now_add=True, auto_now=True, db_index=True,
                                       editable=False, default=datetime.now())
    modified_by = models.ForeignKey(User, related_name='+',
                                    editable=False, blank=True,
                                    null=True, default=None)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('File')
        verbose_name_plural = _('Files')


    def save(self, *args, **kwargs):
        image = False
        video = False
        audio = False
        doc = False
        file = self.path
        try:
            image = PilImage.open(file)
        except IOError:
            pass

        self.size = file.size
        self.ext = os.path.splitext(file.path)[1].lower()

        if image:
            self.width = image.size[0]
            self.height = image.size[1]
            self.type = 'image'


        #self.size = self.path.
        super(File, self).save(*args, **kwargs)

    def _filesize(self):
        return self.size
    filesize = property(_filesize)

    def _date(self):
        return self.modified_at
    date = property(_date)

    def _datetime(self):
        return datetime.datetime.fromtimestamp(self.date)
    datetime = property(_datetime)

    def _extension(self):
        return self.ext
    extension = property(_extension)

    def _url(self):
        return settings.MEDIA_URL + self.path.path.replace(settings.MEDIA_ROOT, "")
    url = property(_url)


    def _dimensions(self):
        if self.width != None:
            return [self.width, self.height]
        else:
            return False
    dimensions = property(_dimensions)

    def _orientation(self):
        if self.dimensions:
            if self.dimensions[0] >= self.dimensions[1]:
                return "Landscape"
            else:
                return "Portrait"
        else:
            return None
    orientation = property(_orientation)
