from PyQt5.QtCore import QObject, pyqtSignal

from gamelogic import items, gamespace, weapons


class BodyType:
    Humanoid = 1
    SmallAnimal = 2
    LargeAnimal = 3
    Monstrosity = 4
    Mechanical = 5


class Actor:

    def __init__(self, parentworld, hp: int = 0,mp: int = 0, name: str = "", body_type: int = 1, myStr: int = 1, myDex: int = 1, myInt: int = 1, myLck: int = 1):
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
    def __init__(self, name=None, hitpoints_max_multi=1,magicpoints_max_multi=1,strpoints_multi=1,dexpoints_multi=1,intpoints_multi=1,lckpoints_multi=1,**kwargs):
        self.Name: str = name
        self.HitPointsMaxMulti = hitpoints_max_multi
        self.MagicPointsMaxMulti = magicpoints_max_multi
        self.StrPointsMulti = strpoints_multi
        self.DexPointsMulti = dexpoints_multi
        self.IntPointsMulti = intpoints_multi
        self.LckPointsMulti = lckpoints_multi


    def __str__(self):
        return self.Name

#PLAYER CLASSES

class WandererClass(PlayerClass):
    """ Default player class with nothing special. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Name = "Wanderer"

class WarriorClass(PlayerClass):
    """ Some garbage """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, hitpoints_max_multi=1.3,magicpoints_max_multi=0.8,strpoints_multi=1.5,dexpoints_multi=1.2,intpoints_multi=0.6,**kwargs)   #these are % values
        self.Name = "Warrior"

class MagicianClass(PlayerClass):
    """ Some garbage """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, hitpoints_max_multi=0.9,magicpoints_max_multi=1.3,strpoints_multi = 0.6,dexpoints_multi=0.9,intpoints_multi=1.8,**kwargs)
        self.Name = "Magician"


######################################################













class PlayerCharacter(Actor):

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.UserId: str = user_id
        if self.Name is None:
            self.Name: str = "Unnamed"
        self.Class: PlayerClass = MagicianClass()
        self._HitPoints = self.HitPointsMax = 50
        self._MagicPoints = self.MagicPointsMax = 100
        self.StrPoints = 10
        self.DexPoints = 10
        self.IntPoints = 10
        self.LckPoints = 10
        self.EquipmentSet: items.EquipmentSet = items.EquipmentSet()
        self.FOV: int = self.FOV_Default
        self.Inventory: [items.Equipment] = []
        self.Currency: int = 1000

    #trying to make a var that is just StrPoints * Class multiplyer
    @property
    def Strength(self):
       me = self.StrPoints*self.Class.StrPointsMulti
       return me
    @property
    def Dexterity(self):
       me = self.DexPoints*self.Class.DexPointsMulti
       return me
    @property
    def Intelligence(self):
       me = self.IntPoints*self.Class.IntPointsMulti
       return me
    @property
    def Luck(self):
       me = self.LckPoints*self.Class.LckPointsMulti
       return me


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
