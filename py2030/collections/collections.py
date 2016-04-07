from py2030.collections.collection import Collection
from py2030.collections.model import Model
# TODO: refactor these into this file?
from py2030.collections.change import Change
from py2030.collections.changes import Changes
from py2030.collections.broadcast import Broadcast
from py2030.collections.broadcasts import Broadcasts

class Update(Model):
    pass

class Updates(Collection):
    model = Update
