from PyQt5.QtCore import QObject, pyqtSignal

from gamelogic import items, gamespace, weapons


class BodyType:
    Humanoid = 1
    SmallAnimal = 2
    LargeAnimal = 3
    Monstrosity = 4
    Mechanical = 5


class Actor:

    def __init__(self, parentworld, hp: int = 0,mp: int = 0, name: str = "", body_type: int = 1, myStr: int = 1, myDex: int = 1, myInt: int = 0, myLck: int = 1):
        self.ParentWorld = parentworld
        self._HitPoints = self.HitPointsMax = hp
        self._MagicPoints = self.MagicPointsMax = mp
        self.StrPoints = myStr
        self.DexPoints = myDex
        self.IntPoints = myInt
        self.LckPoints = myLck
        self.Name = name
        self.BodyType = body_type
        self.Location: gamespace.Space = None
        self.FOV_Default = 1
        self.TimeLastMoved = 0

    def attemptMove(self, shift: (int, int)) -> bool:
        new_space = self.Location + shift
        new_space = self.ParentWorld.Map[new_space.Y][new_space.X]
        if not self.ParentWorld.isSpaceValid(new_space):
            return False
        else:
            self.Location = new_space
            map_space = self.ParentWorld.Map[self.Location.Y][self.Location.X]
            if isinstance(map_space, gamespace.Wilds):
                map_space.runEvent(pc=self)
            return True

    @property
    def HitPoints(self):
        return self._HitPoints

    @HitPoints.setter
    def HitPoints(self, value):
        self._HitPoints = min(max(value, 0), self.HitPointsMax)
        if self._HitPoints == 0:
            self.onDeath

    @property
    def MagicPoints(self):
        return self._MagicPoints

    @MagicPoints.setter
    def MagicPoints(self, value):
        self._MagicPoints = min(max(value, 0), self.MagicPointsMax)


    @property
    def isDead(self) -> bool:
        return self.HitPoints <= 0

    def onDeath(self):
        pass


class NPC(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Inventory: [] = []
        self.FlavorText = ""


class Enemy(NPC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.BaseAttack: int = 0
        self.Abilities: {} = {}
        self.Loot: [] = []


class PlayerClass:
    def __init__(self, name=None, hitpoints_max_base=1,magicpoints_max_base=1,strpoints_base=1,dexpoints_base=1,intpoints_base=1,lckpoints_base=1,**kwargs):
        self.Name: str = name
        self.HitPointsMaxBase = hitpoints_max_base
        self.MagicPointsMaxBase = magicpoints_max_base
        self.StrPointsBase = strpoints_base
        self.DexPointsBase = dexpoints_base
        self.IntPointsBase = intpoints_base
        self.LckPointsBase = lckpoints_base


    def __str__(self):
        return self.Name

#PLAYER CLASSES

class WandererClass(PlayerClass):
    """ Default player class with nothing special. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, hitpoints_max_base=50,magicpoints_max_base=5, **kwargs)
        self.Name = "Wanderer"

class WarriorClass(PlayerClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, hitpoints_max_base=70,magicpoints_max_base=5,strpoints_base = 5,dexpoints_base = 3 **kwargs)
        self.Name = "Warrior"

class MagicianClass(PlayerClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, hitpoints_max_base=30,magicpoints_max_base=10,intpoints_base = 5,lckpoints_base = 2 **kwargs)
        self.Name = "Magician"


######################################################













class PlayerCharacter(Actor):

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.UserId: str = user_id
        if self.Name is None:
            self.Name: str = "Unnamed"
        self.Class: PlayerClass = WandererClass()
        self._HitPoints = self.HitPointsMax = self.Class.HitPointsMaxBase
        self._MagicPoints = self.MagicPointsMax = self.Class.MagicPointsMaxBase
        self.EquipmentSet: items.EquipmentSet = items.EquipmentSet()
        self.FOV: int = self.FOV_Default
        self.Inventory: [items.Equipment] = []
        self.Currency: int = 1000

    @property
    def weapon(self):
        w = self.EquipmentSet.MainHand
        if not isinstance(w, weapons.Weapon):
            return None
        else:
            return w

    @property
    def hasWeaponEquiped(self):
        return self.weapon is not None

    def equip(self, equipment):
        self.EquipmentSet.equip(equipment)
        equipment.onEquip(self)

    def unequip(self, equipment):
        self.EquipmentSet.unequip(equipment)
        equipment.onUnequip(self)

    def take_damage(self, damage: int):
        damage -= self.EquipmentSet.ArmorCount
        self.HitPoints -= damage  # TODO Finish this

    def onDeath(self):
        self.ParentWorld.handlePlayerDeath(self.UserId)
