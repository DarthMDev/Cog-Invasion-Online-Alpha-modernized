# Filename: DistributedGagShopInteriorAI.py
# Created by:  blach (06Nov15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from . import DistributedToonInteriorAI

class DistributedGagShopInteriorAI(DistributedToonInteriorAI.DistributedToonInteriorAI):
    notify = directNotify.newCategory('DistributedGagShopInteriorAI')
