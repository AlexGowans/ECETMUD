from gamelogic.items import Armor, HeadArmor, ChestArmor, LegArmor, FootArmor, MainHandEquipment, OffHandEquipment, \
    FullyImplemented
from random import random


class Helmet(HeadArmor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def ArmorCount(self):
        # Determine if the bullet hits or misses
        return self._ArmorCount

    @ArmorCount.setter
    def ArmorCount(self, val):
        self._ArmorCount = val


class clothHeadband(Helmet, FullyImplemented):

    Name: str = "Cloth Headband"

    def __init__(self):
        super().__init__(armor_count=1,
                         name=self.Name,
                         weightlb=3.31)

class leatherHelmet(Helmet, FullyImplemented):

    Name: str = "Leather Helmet"

    def __init__(self):
        super().__init__(armor_count=1,
                         name=self.Name,
                         weightlb=3.31)


ImplementedArmorList: list = FullyImplemented.__subclasses__()

ImplementedArmorDict: dict = {cls.Name: cls for cls in FullyImplemented.__subclasses__()}
