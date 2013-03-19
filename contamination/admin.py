from contamination.models import Substance
from contamination.models import DVS
from contamination.models import K7
from contamination.models import K4
from contamination.models import SpeedOfTransfer
from contamination.models import DepthZone
from contamination.models import Wind
from contamination.models import Temperature

from django.contrib import admin

admin.site.register(Substance)
admin.site.register(DVS)
admin.site.register(K7)
admin.site.register(K4)
admin.site.register(SpeedOfTransfer)
admin.site.register(DepthZone)
admin.site.register(Wind)
admin.site.register(Temperature)