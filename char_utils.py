import pygame
import random
ATTACK = -1
PLAYER, MONSTER = 0,1
WEAPON_SLOT = 0
SHIELD_SLOT = 1
ARMOR_SLOT  = 2
GLOVE_SLOT  = 3
HEAD_SLOT   = 4
FEET_SLOT   = 5
TRINK1_SLOT = 6
TRINK2_SLOT = 7
INV_SLOT    = 8
  
class character(object):
    def __init__(self, char_name='Dongle',char_job='Fighter', sprite_file='dongle.png'):
        #!!!!! make sure character name is 10 chars or less
        self.name = str(char_name)
        self.job = char_job
        self.hp = 20
        self.mp = 20
        self.maxhp = 20
        self.maxmp = 20
        self.level = 1
        self.attack = 1
        self.defense = 1
        self.magic = 1
        self.gold = 0
        self.xp = 0
        self.nl = 20
        self.ap = 0

        self.equipped = equipment()
        self.inventory = inventory()
        self.abilities = []

        #character sprites
        sprites = pygame.image.load('dongle.png').convert()
        self.image = [sprites.subsurface((0,0,41,50)),sprites.subsurface((41,0,41,50))]
        self.image[0].set_colorkey((255,255,255))
        self.image[1].set_colorkey((255,255,255))
        self.state = 0

    #change the drawing state
    def state_change(self):
        self.state += 1
        if self.state >= len(self.image):
            self.state = 0

    #raise a level
    def level_up(self):
        self.xp = self.xp - self.nl
        self.level +=1
        self.nl = self.nl * 2
        self.maxhp = int(self.maxhp * 1.5)
        self.maxmp = int(self.maxmp * 1.25)
        #restore life and mana
        self.mp = self.maxhp
        self.hp = self.maxhp


        
        
#---------end character class----------

class ability(object):
    def __init__(self, name, description, target, area, element, mana, base, scale):
        self.name = name
        self.desc = description
        self.target = target
        self.area = area
        self.element = element
        self.base = base
        self.scale = scale
        self.mp = mana
        self.level = 1
        self.ap = 0
        self.nl = 5
#---------end abilities class
class equipment(object):
    def __init__(self):
        self.slots = []
        self.slots.append(item('None', WEAPON_SLOT, '', [0,0,0], 'No Weapon equipped',0))
        self.slots.append(item('None', SHIELD_SLOT, '', [0,0,0], 'No Shield equipped',0))
        self.slots.append(item('None', ARMOR_SLOT, '', [0,0,0], 'No Armor equipped',0))
        self.slots.append(item('None', GLOVE_SLOT, '', [0,0,0], 'No Gloves equipped',0))
        self.slots.append(item('None', HEAD_SLOT, '', [0,0,0], 'No Helmet equpiped',0))
        self.slots.append(item('None', FEET_SLOT, '', [0,0,0], 'No Boots equipped',0))
        self.slots.append(item('None', TRINK1_SLOT, '', [0,0,0], 'No Trinket equipped',0))
        self.slots.append(item('None', TRINK2_SLOT, '', [0,0,0], 'No Trinket equipped',0))

    #equip an item, old item gets returned (for moving to the inventory)
    def equip(self, slot, item):
        if self.slots[slot].slot == item.slot:
            old = self.slots[slot]            
            self.slots[slot] = item
            return old
        else:
            return 'equip_error'
    #sum the stats of the currently equipped gear
    def sum_stats(self):
        attack = 0
        defense = 0
        magic = 0
        for i in range(0, len(self.slots)):
            attack += self.slots[i].stats[0]
            defense += self.slots[i].stats[1]
            magic += self.slots[i].stats[2]
        return [attack, defense, magic]

    def get_status(self):
        ret = [0,0,0]
        for i in range(0, len(self.slots)):
            if 'A' in self.slots[i].flags:
                ret[0] += 1
            if 'a' in self.slots[i].flags:
                ret[0] -= 1
            if 'D' in self.slots[i].flags:
                ret[1] += 1
            if 'd' in self.slots[i].flags:
                ret[1] -= 1
            if 'M' in self.slots[i].flags:
                ret[2] += 1
            if 'm' in self.slots[i].flags:
                ret[2] -= 1

        if ret[0] > 3:
            ret[0] = 3
        if ret[0] < -3:
            ret[0] = -1
        if ret[1] > 3:
            ret[1] = 3
        if ret[1] < -3:
            ret[1] = -1
        if ret[2] > 3:
            ret[2] = 3
        if ret[2] < -3:
            ret[2] = -1
        
        return ret

                
#----------end equipment class---------
class monster(object):
    def __init__(self, name, level, image_row):
        self.name = name
        self.maxhp = level * 10
        self.hp = self.maxhp
        self.level = level
        self.alive = True
        self.state = 0
        self.abilities = []
        #load the sprite image
        sprites = pygame.image.load('monsters.png').convert()
        self.image = []
        self.image.append(sprites.subsurface((0,image_row * 50,50,50)))
        self.image.append(sprites.subsurface((50,image_row * 50,50,50)))
        self.image.append(sprites.subsurface((100,image_row * 50,50,50)))
        self.image.append(sprites.subsurface((150,image_row * 50,50,50)))
        self.image[0].set_colorkey((255,255,255))
        self.image[1].set_colorkey((255,255,255))
        self.image[2].set_colorkey((255,255,255))
        self.image[3].set_colorkey((255,255,255))

    #change the drawing state
    def state_change(self):
        if self.state == 0:
            self.state = 1
        else:
            self.state = 0
        
        
#-----------end monster class----------
class encounter(object):
    def __init__(self, character, escape, rarity='low'):
        self.monsters = []
        self.droptable = []
        self.goldmod = 1
        self.rarity = rarity
        self.turn = PLAYER
        self.escape = escape
        self.status = character.equipped.get_status()
        
        if rarity == 'low':
            self.goldmod = 1
        elif rarity == 'med':
            self.goldmod = 2
        elif rarity == 'high':
            self.goldmod = 3

    #fuction for deciding if flee was sucessfull
    def escaped(self):
        if random.random() > self.escape:
            return True
        else:
            return False
        
    #update the state of all the monsters in the encounter. return number of living monsters
    def update_state(self):
        monsters = 0
        for i in range(0,len(self.monsters)):
            if self.monsters[i].hp <=0:
                self.monsters[i].alive = False
            else:
                monsters += 1
        return monsters
    
    def get_xp(self):
        xp = 0
        for i in range(0, len(self.monsters)):
            xp += self.monsters[i].level * 3
        xp = int(xp) + 1
        return xp
        
    def get_gold(self):
        gold = 0
        for i in range(0, len(self.monsters)):
            gold += self.monsters[i].level * self.goldmod + self.monsters[i].level * random.random()
        gold = int(gold) + 1
        return gold
    #call when item is used in combat
    def use_item(self, character, item):
        if character.inventory.items[item].name == 'Potion':
            character.mp += 15
            if character.mp > character.maxmp:
                character.mp = character.maxmp
        character.inventory.use_item(item)
        
    #call when ability is used in combat returns damage/healing done
    def char_ability(self, character, target, ability=ATTACK, monster=-1):
        ATT_MOD = 0.25
        DEF_MOD = 0.25
        MAG_MOD = 0.25
        stats = character.equipped.sum_stats()
        #attacking a monster
        if target == MONSTER:
            damage = 0
            if ability == ATTACK:
                damage = character.attack * character.level + stats[0] + random.randint(0,character.level)
                #adjust for attack bonus
                #buff
                if self.status[0] > 0:
                    damage = int(damage * (1 + self.status[0] * ATT_MOD))  
                #debuff
                elif self.status[0] < 0:
                    damage = int(damage * ATT_MOD * (4+self.status[0]))
                self.monsters[monster].hp -= damage
            else:
                damage = int(character.abilities[ability].base * (stats[2] + character.abilities[ability].scale))
                #adjust for magic bonus
                #buff
                if self.status[2] > 0:
                    damage = int(damage * (1 + self.status[2] * MAG_MOD))  
                #debuff
                elif self.status[2] < 0:
                    damage = int(damage * MAG_MOD * (4+self.status[2]))
                    
                character.mp -= character.abilities[ability].mp
                character.ap += 1

                #single target
                if character.abilities[ability].area == 1:
                    self.monsters[monster].hp -= damage

                #all targets
                elif character.abilities[ability].area == 0:
                    for i in range(0,len(self.monsters)):
                        if self.monsters[i].alive == True:
                            self.monsters[i].hp -= damage
            return damage
        #using ability on self
        else:
            healing = 0
            return healing

#------------end counter class---------      
class inventory(object):
    def __init__(self):
        self.items = []
        self.counts = []
    def add_item(self,item,quantity=1):
        self.items.append(item)
        self.counts.append(quantity)
    def use_item(self,item):
        #if its the last item in the stack remove it
        if self.counts[item] == 1:
            self.items.pop(item)
            self.counts.pop(item)
        #otherwise decrement count
        else:
            self.counts[item] -=1
#---------end inventory class----------
class item(object):
    def __init__(self, i_name, i_slot, i_flags, i_stats, description, item_id):
        self.name = i_name
        self.slot = i_slot
        self.flags = i_flags
        self.stats = i_stats
        self.desc = description
        self.item_id = item_id
#----------end item class--------------
