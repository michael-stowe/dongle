import pygame
import configparser
import random

TILE_WIDTH, TILE_HEIGHT = 30,30
AM_MENUE, AM_DETAIL, AM_DESCRIPTION, AM_ABILITY, AM_MONSTER, AM_SELECT = 0,1,2,3,4,5
MS_CHARACTER, MS_INVENTORY, MS_ABILITIES, MS_EQUIPMENT, MS_EXIT = 0,1,2,3,4
BM_ATTACK, BM_ABILITY, BM_ITEM, BM_FLEE = 0,1,2,3
PLAYER, MONSTER = 0,1
MM_MAX, AB_MAX = 12, 4
BATTLE_POS = [(130,110),(70,35),(15,120),(70,195),(350,135),(300,240)]
WEAPON_SLOT = 0
SHIELD_SLOT = 1
ARMOR_SLOT  = 2
GLOVE_SLOT  = 3
HEAD_SLOT   = 4
FEET_SLOT   = 5
TRINK1_SLOT = 6
TRINK2_SLOT = 7
INV_SLOT    = 8

IMAGE_DIR = 'images/'

#class for parsing map files
class map(object):
    def __init__(self, map_file):
        #!!!!!!add error checking for files
        self.load_map(map_file)
        self.load_tileset()
        self.render_background()
        self.tiles_x = 0
        self.tiles_y = 0
        self.tileset_file = ''
        
    def load_map(self, map_file):
        #map is the level map
        self.map = []
        #key is the set of keys, values, and tile locations
        self.key = {}
        parser = configparser.ConfigParser()
        parser.read(map_file)
        self.tileset_file = IMAGE_DIR + parser.get("floor", "tileset")
        self.map = parser.get("floor", "map").split("\n")
        #load exits
        self.exits = []
        exits = parser.get("floor","exits").split("\n")
        for line in exits:
            e = line.split(',')
            self.exits.append([e[0], (int(e[1]), int(e[2])), e[3]])
        #load sections
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
                self.width = len(self.map[0])
                self.height = len(self.map)
                
    def load_tileset(self):
        image = pygame.image.load(self.tileset_file).convert()
        image_width, image_height = image.get_size()
        self.tiles = []
        self.tiles_x = int(image_width / TILE_WIDTH)
        self.tiles_y = int(image_height / TILE_HEIGHT)
        #loop through height and width populating the tile table
        for tile_y in range(0, self.tiles_y):
            #clear the row to be added to the tileset next
            row = []
            for tile_x in range(0, self.tiles_x):
                tile = (tile_x * TILE_WIDTH, tile_y * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
                #append tiles to the row from left to right(increasing x)
                row.append(image.subsurface(tile))
            #append the completed row to the tileset
            self.tiles.append(row)

    #return map name if there is an exit in the given direction at map coordinates x,y. Return false otherwise
    def is_exit(self, direction, coordinates):
        for e in self.exits:
            if e[0] == direction:
                if e[1][0] == coordinates[0] and e[1][1] == coordinates[1]:
                    return e[2]
        #searched all the exits, none correspond
        return False
    
    #return the tile at x,y
    def get_tile(self, x, y):
        try:
            char = self.map[x][y]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}
        
    #render a backround stored in self
    def render_background(self, top=0, left=0, bottom=14, right=16):
        self.background = pygame.Surface((self.width * TILE_WIDTH, self.height * TILE_HEIGHT))
        self.walls = []
        #loop through the entire map        
        for y in range(top,bottom):
            row = []
            for x in range(left,right):
                #get the symbol at the next loaction in the map
                k = self.map[y][x]
                #grab the associated tile loaction
                tile = self.key[k]['tile'].split(',')
                tile = int(tile[0]), int(tile[1])
                #grab the tile from the tileset append to background
                self.background.blit(self.tiles[tile[0]][tile[1]], (x * TILE_WIDTH,y * TILE_HEIGHT))

                #build the next row of wall vaules
                #if key wall doesn't exist(error) add nowall value
                try:
                    if self.key[k]['wall'] == 'true':
                        row.append(1)
                except:
                    row.append(0)

            self.walls.append(row)
#---------end class map--------------
    
class menue(object):
    def __init__(self, menue_type, ilist, menue_file=IMAGE_DIR + 'menues.png'):
        #!!!!!!add error catching for bad filenames/menue types
        #load menue tiles, font and menue item list
        self.load_tiles(menue_file)   
        self.f = font()
        self.menue_items = ilist

        self.scroll_start = 0
        self.screen_max = 0

        if menue_type == 'main':
            self.menue = pygame.Surface((480,420))
            self.load_main_menue()

            self.active_menue = AM_MENUE

            self.menue_selected = MS_CHARACTER
            self.menue_max = 4

            self.detail_selected = 0
            self.detail_max = 0

            self.menue_pane = (18,18)
            self.detail_pane = (164,18)
            self.description_pane = (18,286)

            self.detail_scroll = scrollbar(13)
            self.xp = xpbar(15)
            self.ap = xpbar(8)
        elif menue_type == 'battle':
            self.menue = pygame.Surface((480,420))
            self.load_battle_menue()

            self.active_menue = AM_MENUE

            self.menue_selected = BM_ATTACK
            self.menue_max = 3

            self.monster_selected = 0
            self.monster_max = 0

            self.ability_selected = 0
            self.ability_max = 0

            #panes
            self.menue_pane = (226,318)
            self.char_pane = (345,318)
            self.monster_pane = (18,318)
            #bars
            self.select_scroll = scrollbar(4)
            self.health_bar = battle_bar('health', 1)
            self.mana_bar = battle_bar('mana',1)
                   
        
    def load_tiles(self, file):
        image = pygame.image.load(file).convert()
        #draw the menue outline onto a surface
        
        self.tiles = []
        #loop through the 18 border elements put them in tiles
        row = []
        for tile_x in range(0, 19):
            tile = (tile_x * 60, 0, 60,60)
            row.append(image.subsurface(tile))            
        #add row of menue borders to menue tileset    
        self.tiles.append(row)

    #create the frame for the battle menue stored in self.main_menue
    #!!!!!!!!replace hardcoded positions with vars
    def load_battle_menue(self):
        #corners
        self.menue.blit(self.tiles[0][0],(0,300))
        self.menue.blit(self.tiles[0][1],(420,300))
        self.menue.blit(self.tiles[0][2],(420,360))
        self.menue.blit(self.tiles[0][3],(0,360))
        #dividers
        self.menue.blit(self.tiles[0][10],(180,300))
        self.menue.blit(self.tiles[0][10],(300,300))   
        self.menue.blit(self.tiles[0][8],(180,360))
        self.menue.blit(self.tiles[0][8],(300,360))
        #top border
        self.menue.blit(self.tiles[0][4],(0,240))
        self.menue.blit(self.tiles[0][4],(60,240))
        self.menue.blit(self.tiles[0][4],(120,240))
        self.menue.blit(self.tiles[0][4],(180,240))
        self.menue.blit(self.tiles[0][4],(240,240))
        self.menue.blit(self.tiles[0][4],(300,240))
        self.menue.blit(self.tiles[0][4],(360,240))
        self.menue.blit(self.tiles[0][4],(420,240))
        #top
        self.menue.blit(self.tiles[0][6],(60,300))
        self.menue.blit(self.tiles[0][6],(120,300))
        self.menue.blit(self.tiles[0][6],(240,300))
        self.menue.blit(self.tiles[0][6],(360,300))
        #bottom
        self.menue.blit(self.tiles[0][4],(60,360))
        self.menue.blit(self.tiles[0][4],(120,360))
        self.menue.blit(self.tiles[0][4],(240,360))
        self.menue.blit(self.tiles[0][4],(360,360))
        
    #create the frame for the main menue stored in self.main_menue
    #!!!!!!!!replace hardcoded positions with vars
    def load_main_menue(self):
        #draw the main menue borders
        #corners
        self.menue.blit(self.tiles[0][0],(0,0))
        self.menue.blit(self.tiles[0][1],(420,0))
        self.menue.blit(self.tiles[0][2],(420,360))
        self.menue.blit(self.tiles[0][3],(0,360))

        self.menue.blit(self.tiles[0][9],(0,240))
        self.menue.blit(self.tiles[0][11],(420,240))
        self.menue.blit(self.tiles[0][10],(120,0))
        self.menue.blit(self.tiles[0][15],(120,240))

        #outside walls
        self.menue.blit(self.tiles[0][4],(60,360))
        self.menue.blit(self.tiles[0][4],(120,360))
        self.menue.blit(self.tiles[0][4],(180,360))
        self.menue.blit(self.tiles[0][4],(240,360))
        self.menue.blit(self.tiles[0][4],(300,360))
        self.menue.blit(self.tiles[0][4],(360,360))

        self.menue.blit(self.tiles[0][5],(0,60))
        self.menue.blit(self.tiles[0][5],(0,120))
        self.menue.blit(self.tiles[0][5],(0,180))
        self.menue.blit(self.tiles[0][5],(0,300))

        self.menue.blit(self.tiles[0][6],(60,0))
        self.menue.blit(self.tiles[0][6],(180,0))
        self.menue.blit(self.tiles[0][6],(240,0))
        self.menue.blit(self.tiles[0][6],(300,0))
        self.menue.blit(self.tiles[0][6],(360,0))

        self.menue.blit(self.tiles[0][7],(420,60))
        self.menue.blit(self.tiles[0][7],(420,120))
        self.menue.blit(self.tiles[0][7],(420,180))
        self.menue.blit(self.tiles[0][7],(420,300))

        #inside walls
        self.menue.blit(self.tiles[0][12],(120,60))
        self.menue.blit(self.tiles[0][12],(120,120))
        self.menue.blit(self.tiles[0][12],(120,180))

        self.menue.blit(self.tiles[0][13],(60,240))
        self.menue.blit(self.tiles[0][13],(180,240))
        self.menue.blit(self.tiles[0][13],(240,240))
        self.menue.blit(self.tiles[0][13],(300,240))
        self.menue.blit(self.tiles[0][13],(360,240))       

#=================Common Menue draw functions===================
    #alert to the top of a menue
    def alert(self,alert):
        self.clear('alert')
        x_pos = 240 - (len(alert) * 15) / 2
        self.menue.blit(self.f.write(alert),(x_pos,0))
        
    #clear a pane
    def clear(self,pane):
        if pane == 'details':
            blank = pygame.Surface((300,240))
            location = self.detail_pane
        elif pane == 'description':
            blank = pygame.Surface((450,118))
            location = self.description_pane
        elif pane == 'monster':
            blank = pygame.Surface((180,93))
            location = (self.monster_pane[0],self.monster_pane[1] -3)
        elif pane == 'alert':
            blank = pygame.Surface((480,20))
            location = (0,0)
        elif pane == 'battle':
            blank = pygame.Surface((400,220))
            location = (0,25)
        elif pane == 'status_bar':
            blank = pygame.Surface((120,40))
            location = (BATTLE_POS[5])
        #fill and draw
        blank.fill((0,0,0))
        self.menue.blit(blank,location)
            
    #draw a list of menue 
    #FONT_HEIGHT not used because caller may want to specify different spacing
    def draw_menue_items(self, height=20, selected=0):
        for item in range(0,len(self.menue_items)):
            if item == selected:
                list_image = self.f.write(self.menue_items[item], True)
            else:
                list_image = self.f.write(self.menue_items[item])
            #draw to the correct menue
            self.menue.blit(list_image, (self.menue_pane[0],item * height + self.menue_pane[1]))
            
#=================Battle Menue draw functions===================
        
    def draw_encounter(self, encounter, character, selected=0, aoe=False):
        self.clear('battle')
        #draw the monsters
        for i in range(0,len(encounter.monsters)):
            if encounter.monsters[i].alive == True:
                if aoe == True:
                    self.menue.blit(encounter.monsters[i].image[2],BATTLE_POS[i])
                else:
                    if i == selected and self.active_menue == AM_MONSTER:
                        self.menue.blit(encounter.monsters[i].image[2],BATTLE_POS[i])
                    else:
                        self.menue.blit(encounter.monsters[i].image[encounter.monsters[i].state],BATTLE_POS[i])
                    
        #draw the characeter
        self.menue.blit(character.image[character.state],BATTLE_POS[4])
        #draw the statusbar
        image = pygame.image.load(IMAGE_DIR + "status.png").convert()
        self.clear('status_bar')
        status_bar = pygame.Surface((len(encounter.status) * 40, 40))

        #attack up
        if encounter.status[0] != 0:
            #buffs
            if encounter.status[0] > 0:
                tile = (0,(encounter.status[0] -1) * 40,40,40)
            #debuffs
            else:
                tile = (40,(abs(encounter.status[0]) -1) * 40,40,40)
            status_bar.blit(image.subsurface(tile),(0,0))

        #defense up
        if encounter.status[1] != 0:
            #buffs
            if encounter.status[1] > 0:
                tile = (80,(encounter.status[1] -1) * 40,40,40)
            #debuffs
            else:
                tile = (120,(abs(encounter.status[1]) -1) * 40,40,40)
            status_bar.blit(image.subsurface(tile),(40,0))

        #magic up
        if encounter.status[2] != 0:
            #buffs
            if encounter.status[2] > 0:
                tile = (160,(encounter.status[2] -1) * 40,40,40)
            #debuffs
            else:
                tile = (200,(abs(encounter.status[2]) -1) * 40,40,40)

            status_bar.blit(image.subsurface(tile),(80,0))

        status_bar.set_colorkey((255,255,255))
        self.menue.blit(status_bar,BATTLE_POS[5])
        
                
    def draw_ability_choose(self, abilities, selected=0, height=20):
        #update ability max
        item_num = len(abilities)
        self.ability_max = item_num
        if item_num < AB_MAX:
            self.screen_max = item_num
        else:
            self.screen_max = AB_MAX
        self.clear('monster')
        #loop through abilities
        for i in range(0, self.screen_max):
            #compile the string to be printed
            outstr = abilities[i + self.scroll_start].name + ' ' + str(abilities[i + self.scroll_start].mp)
            if i==selected:
                #print the selected ability
                self.menue.blit(self.f.write(outstr, True),(self.monster_pane[0],i * height + self.monster_pane[1]))
            else:
                self.menue.blit(self.f.write(outstr, False),(self.monster_pane[0],i * height + self.monster_pane[1]))

            #update and draw the scrollbar
            self.select_scroll.draw((self.ability_selected + self.scroll_start) / self.ability_max)
            self.menue.blit(self.select_scroll.bar,(self.monster_pane[0] + 163, self.monster_pane[1] - 3))

    def draw_item_choose(self, inventory, selected=0, height=20):
        #update ability max
        item_num = len(inventory.items)
        self.ability_max = item_num
        if item_num < AB_MAX:
            self.screen_max = item_num
        else:
            self.screen_max = AB_MAX
        self.clear('monster')
        #loop through inventory
        for i in range(0, self.screen_max):
            #compile the string to be printed
            outstr = inventory.items[i + self.scroll_start].name + 'x' + str(inventory.counts[i + self.scroll_start])
            if i==selected:
                #print the selected ability
                self.menue.blit(self.f.write(outstr, True),(self.monster_pane[0],i * height + self.monster_pane[1]))
            else:
                self.menue.blit(self.f.write(outstr, False),(self.monster_pane[0],i * height + self.monster_pane[1]))

            #update and draw the scrollbar
            self.select_scroll.draw((self.ability_selected + self.scroll_start) / self.ability_max)
            self.menue.blit(self.select_scroll.bar,(self.monster_pane[0] + 163, self.monster_pane[1] - 3))
            
    def draw_char_bars(self, character):
        #update the health bars' filled status
        self.health_bar = battle_bar('health', character.hp / character.maxhp)
        self.mana_bar = battle_bar('mana', character.mp / character.maxmp)
        #blit the hp bar and label
        self.menue.blit(self.f.write('HP'),self.char_pane)
        self.menue.blit(self.health_bar.bar, (self.char_pane[0] + 35, self.char_pane[1] -1))
        #blit the mp bar and label
        self.menue.blit(self.f.write('MP'),(self.char_pane[0], self.char_pane[1] + 20))
        self.menue.blit(self.mana_bar.bar, (self.char_pane[0] + 35, self.char_pane[1] + 20 -1))

    def draw_monster_bars(self, encounter, selected=0):
        self.clear('monster')
        #update monster max
        self.monster_max = len(encounter.monsters) - 1
        #loop through all the monsters in the encounter drawing name and health bar
        for i in range(0, len(encounter.monsters)):
            if encounter.monsters[i].alive == True:
                monster_bar = battle_bar('health',encounter.monsters[i].hp / encounter.monsters[i].maxhp)
                #hightlight the selected monster if the monster pane is active
                if self.active_menue==AM_MONSTER and i==selected:
                    self.menue.blit(self.f.write(encounter.monsters[i].name,True),(self.monster_pane[0],self.monster_pane[1] + i * 20))
                else:
                    self.menue.blit(self.f.write(encounter.monsters[i].name,False),(self.monster_pane[0],self.monster_pane[1] + i * 20))
                #blit the health bar for the current monster
                self.menue.blit(monster_bar.bar,(self.monster_pane[0] + 110, self.monster_pane[1] + i * 20 - 1 ))
            
            
#=================Main Menue draw functions======================
    #draw a box containing the character info
    def draw_char_info(self, character, height=20):
        #compile a list of strings to be drawn
        stats = []
        stats.append('Name: ' + character.name)
        stats.append('Job: ' + character.job)
        stats.append('Level: ' + str(character.level))
        stats.append('Hp: ' + str(character.hp) + '/' + str(character.maxhp) + '  Mp: ' + str(character.mp) + '/' + str(character.maxmp)) 
        stats.append('Attack:  ' + str(character.attack) + '(' + str(character.equipped.sum_stats()[0]) + ')')
        stats.append('Defense: ' + str(character.defense) + '(' + str(character.equipped.sum_stats()[1]) + ')')
        stats.append('Magic:   ' + str(character.magic) + '(' + str(character.equipped.sum_stats()[2]) + ')')
        
        stats.append('Gold: ' + str(character.gold))
        stats.append('AP: ' + str(character.ap))
        stats.append('Experience:')
        #draw list of strings
        for s in range(0,len(stats)):
            self.menue.blit(self.f.write(stats[s]),(self.detail_pane[0],s * height + self.detail_pane[1]))

        #draw experience bar
        self.xp.complete = character.xp / character.nl
        self.xp.draw()
        self.menue.blit(self.xp.bar,(self.detail_pane[0], self.detail_pane[1] + 195))
        
    def draw_equipment(self, equipment, selected=0, height=20):
        item_num = len(equipment.slots)
        self.detail_max = item_num
        if item_num < MM_MAX:
            self.screen_max = item_num
        else:
            self.screen_max = MM_MAX
            
        equip = []
        equip.append('Weapon: ' + equipment.slots[WEAPON_SLOT].name)   
        equip.append('Shield: ' + equipment.slots[SHIELD_SLOT].name)
        equip.append('Armor : ' + equipment.slots[ARMOR_SLOT].name)
        equip.append('Gloves: ' + equipment.slots[GLOVE_SLOT].name)
        equip.append('Head  : ' + equipment.slots[HEAD_SLOT].name)
        equip.append('Feet  : ' + equipment.slots[FEET_SLOT].name)        
        equip.append('Trinket 1: ' + equipment.slots[TRINK1_SLOT].name)
        equip.append('Trinket 2: ' + equipment.slots[TRINK2_SLOT].name)
            
        for s in range(0,len(equipment.slots)):
            #print out the equippment slot
            if self.active_menue == AM_DETAIL and self.menue_selected == MS_EQUIPMENT and s==selected:
                #print out the items description to the description pane if active and selected
                self.menue.blit(self.f.write(equipment.slots[s].desc),self.description_pane)
                if equipment.slots[s].name != 'NONE':
                    statsstr = 'ATK:' + str(equipment.slots[s].stats[0]) + ' DEF:' + str(equipment.slots[s].stats[1]) + ' MAG:' + str(equipment.slots[s].stats[2])
                    self.menue.blit(self.f.write(statsstr),(self.description_pane[0], self.description_pane[1]+20))
                #if the current selected item matches the item we are printing, print it as selected
                if s == selected:
                    self.menue.blit(self.f.write(equip[s], True),(self.detail_pane[0],s * height + self.detail_pane[1]))
            else:
                #if not active or selected, or not currently selected, print out without description
                self.menue.blit(self.f.write(equip[s], False),(self.detail_pane[0],s * height + self.detail_pane[1]))
            
    def draw_inventory(self, inventory, selected=0, height=20):
        #update detail max
        item_num = len(inventory.items)
        self.detail_max = item_num
        if item_num < MM_MAX:
            self.screen_max = item_num
        else:
            self.screen_max = MM_MAX
        
        #loop through inventory
        for i in range(0, self.screen_max):
            #compile the string to be printed
            outstr = str(inventory.counts[i + self.scroll_start]) + 'x ' + inventory.items[i + self.scroll_start].name
            if self.active_menue == AM_DETAIL and self.menue_selected == MS_INVENTORY and i==selected:
                #print out the items description to the description pane if active and selected
                self.menue.blit(self.f.write(inventory.items[i+self.scroll_start].desc),self.description_pane)
                #print out as selected
                self.menue.blit(self.f.write(outstr, True),(self.detail_pane[0],i * height + self.detail_pane[1]))
            else:
                #if not active or selected, or not currently selected, print out without description
                self.menue.blit(self.f.write(outstr, False),(self.detail_pane[0],i * height + self.detail_pane[1]))

            #update and draw the scrollbar
            self.detail_scroll.draw((self.detail_selected + self.scroll_start) / self.detail_max)
            self.menue.blit(self.detail_scroll.bar,(448,21))
            
    def draw_abilities(self, abilities, selected=0, height=20):
        item_num = len(abilities)
        self.detail_max = item_num
        if item_num < MM_MAX:
            self.screen_max = item_num
        else:
            self.screen_max = MM_MAX


        for a in range(0,len(abilities)):
            #compile the string to be printed
            outstr = abilities[a].name + ' Lvl:' + str(abilities[a].level) + ' Mp:' + str(abilities[a].mp)
            if self.active_menue == AM_DETAIL and self.menue_selected == MS_ABILITIES and a==selected:
                #print out the items description to the description pane if active and selected
                self.menue.blit(self.f.write(abilities[a].desc),self.description_pane)
                self.menue.blit(self.f.write('Ability Level:'), (self.description_pane[0],self.description_pane[1]+30))
                #print out as selected
                self.menue.blit(self.f.write(outstr, True),(self.detail_pane[0],a * height + self.detail_pane[1]))

                #draw ability ap bar for selected skill
                self.ap.complete = abilities[a].ap / abilities[a].nl
                self.ap.draw()
                self.menue.blit(self.ap.bar,(self.description_pane[0], self.description_pane[1] + 50))

            else:
                #if not active or selected, or not currently selected, print out without description
                self.menue.blit(self.f.write(outstr, False),(self.detail_pane[0],a * height + self.detail_pane[1]))

        #update and draw the scrollbar
        self.detail_scroll.draw(0)
        self.menue.blit(self.detail_scroll.bar,(448,21))
        
#---------end class main_menue-------

class battle_bar(object):
    def __init__(self, bar_type, filled, file=IMAGE_DIR + 'bars.png'):
        image = pygame.image.load(file).convert()
        self.bar_type = bar_type
        if self.bar_type == 'health':
            self.full_bar = image.subsurface((30,0,70,15))
            self.mid_bar = image.subsurface((30,30,70,15))
            self.low_bar = image.subsurface((30,45,70,15))
        elif self.bar_type == 'mana':
            self.full_bar = image.subsurface((30,15,70,15))
            self.mid_bar = image.subsurface((30,15,70,15))
            self.low_bar = image.subsurface((30,15,70,15))
        self.bar_fill = image.subsurface((100,0,1,11))
        self.filled = filled

        self.bar = pygame.Surface((70,15))
        self.draw()
        
    def draw(self):
        #depending on the fullness of the bar, draw drifferent images
        if self.filled > 0.66:
            self.bar.blit(self.full_bar,(0,0))
        elif self.filled > 0.33:
            self.bar.blit(self.mid_bar,(0,0))
        else:
            self.bar.blit(self.low_bar,(0,0))
        self.bar.set_colorkey((255,255,255))
        #cover the portion of the bar that has be used/lost
        for i in range(int(66 * self.filled), 66):
            self.bar.blit(self.bar_fill,(i+2,2))

#end class battle_bar
            
class xpbar(object):
    def __init__(self,width,file=IMAGE_DIR + 'bars.png'):
        image = pygame.image.load(file).convert()
        
        self.width = width
        self.complete = 0

        #load bar elements into self
        self.tiles = []
        self.tiles.append(image.subsurface(15, 0, 15, 15))
        self.tiles.append(image.subsurface(15, 15, 15, 15))

        self.bar = pygame.Surface((15 * width,15))

    def draw(self):
        for i in range(0, self.width):
            #if the tile is to the left of the completed mark, draw completed
            if i < self.complete * self.width:
                self.bar.blit(self.tiles[1],(i*15,0))
            #else draw incomplete
            else:
                self.bar.blit(self.tiles[0],(i*15,0))
        
#----------end xpbar class-----------
class scrollbar(object):
    def __init__(self, height, file=IMAGE_DIR + 'bars.png'):
        image = pygame.image.load(file).convert()
        #chop up the last element of the menues tileset into scroll elements
        self.tiles = []
        self.tiles.append(image.subsurface(0, 0, 15, 15))        #top
        self.tiles.append(image.subsurface(0, 15, 15, 15))       #bottom
        self.tiles.append(image.subsurface(0, 30, 15, 15))       #back
        self.tiles.append(image.subsurface(0, 45, 15, 15))       #slider

        self.height = height
        self.scroll_loc = 0

        #draw the initial scrollbar
        self.bar = pygame.Surface((15, 30 + self.height * 15))

    #draw the scrollbar 
    def draw(self, scroll):
        self.scroll_loc = int(scroll * (self.height) * 15)
        if self.scroll_loc > (self.height-1) * 15:
            self.scroll_loc = (self.height-1) * 15
        bar = pygame.Surface((15, 30 + self.height * 15))
        #top icon
        bar.blit(self.tiles[0],(0,0))
        #bar back
        for i in range(0,self.height):
            bar.blit(self.tiles[2],(0,(i+1) * 15))
        #bar bottom
        bar.blit(self.tiles[1],(0, (self.height + 1) * 15))
        #slider
        bar.blit(self.tiles[3],(0, 15 + self.scroll_loc))
        self.bar = bar

    
#-----------end scrollbar class---------
class animation(object):
    def __init__(self, row, aoe=False, file=IMAGE_DIR + 'animations.png'):
        image = pygame.image.load(file).convert()
        width, height = image.get_size()

        self.width = width
        self.height = 50
        self.image = image.subsurface((0, row*50,width, 50))

        self.delay = 20
        self.frame = 0
        self.max = int(width / 50)
        self.targets = []
        self.draw = False
        self.aoe = aoe

    def next_frame(self):
        ret = self.image.subsurface((self.frame * 50, 0, 50,50))
        ret.set_colorkey((255,255,255))
        self.frame +=1
        if self.frame >= self.max:
            self.frame = 0
        return ret

        
#-----------end animation class---------
class font(object):
    def __init__(self, font_file=IMAGE_DIR + 'font.png', width=13, height=13):
        #!!!!!!!add error checking for file
        self.FONT_WIDTH = width
        self.FONT_HEIGHT = height
        self.load_font(font_file)

    #load the font file
    def load_font(self, file):
        image = pygame.image.load(file).convert()
        self.chars = []
        row = []
        #loop through image and parse out individual characters for the font
        for font_y in range(0,2):
            for font_x in range(0, 45):
                tile = (font_x * self.FONT_WIDTH, font_y * self.FONT_HEIGHT, self.FONT_WIDTH,self.FONT_HEIGHT)
                row.append(image.subsurface(tile))
            #add row of menue borders to menue tileset    
            self.chars.append(row)
            row = []
                                     
    #returns a surface with string st written on it
    def write(self, st, selected=False):
        stlen = len(st)
        out = pygame.Surface((self.FONT_WIDTH * stlen,self.FONT_HEIGHT))
            
        for c in range (0,stlen):     
            if st[c] == 'A':
                out.blit(self.chars[0][0],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'B':
                out.blit(self.chars[0][1],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'C':
                out.blit(self.chars[0][2],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'D':
                out.blit(self.chars[0][3],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'E':
                out.blit(self.chars[0][4],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'F':
                out.blit(self.chars[0][5],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'G':
                out.blit(self.chars[0][6],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'H':
                out.blit(self.chars[0][7],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'I':
                out.blit(self.chars[0][8],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'J':
                out.blit(self.chars[0][9],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'K':
                out.blit(self.chars[0][10],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'L':
                out.blit(self.chars[0][11],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'M':
                out.blit(self.chars[0][12],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'N':
                out.blit(self.chars[0][13],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'O':
                out.blit(self.chars[0][14],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'P':
                out.blit(self.chars[0][15],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'Q':
                out.blit(self.chars[0][16],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'R':
                out.blit(self.chars[0][17],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'S':
                out.blit(self.chars[0][18],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'T':
                out.blit(self.chars[0][19],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'U':
                out.blit(self.chars[0][20],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'V':
                out.blit(self.chars[0][21],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'W':
                out.blit(self.chars[0][22],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'X':
                out.blit(self.chars[0][23],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'Y':
                out.blit(self.chars[0][24],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'Z':
                out.blit(self.chars[0][25],(self.FONT_WIDTH * c, 0))
            elif st[c] == '1':
                out.blit(self.chars[0][26],(self.FONT_WIDTH * c, 0))
            elif st[c] == '2':
                out.blit(self.chars[0][27],(self.FONT_WIDTH * c, 0))
            elif st[c] == '3':
                out.blit(self.chars[0][28],(self.FONT_WIDTH * c, 0))
            elif st[c] == '4':
                out.blit(self.chars[0][29],(self.FONT_WIDTH * c, 0))
            elif st[c] == '5':
                out.blit(self.chars[0][30],(self.FONT_WIDTH * c, 0))
            elif st[c] == '6':
                out.blit(self.chars[0][31],(self.FONT_WIDTH * c, 0))
            elif st[c] == '7':
                out.blit(self.chars[0][32],(self.FONT_WIDTH * c, 0))
            elif st[c] == '8':
                out.blit(self.chars[0][33],(self.FONT_WIDTH * c, 0))
            elif st[c] == '9':
                out.blit(self.chars[0][34],(self.FONT_WIDTH * c, 0))
            elif st[c] == '0':
                out.blit(self.chars[0][35],(self.FONT_WIDTH * c, 0))
            elif st[c] == '?':
                out.blit(self.chars[0][36],(self.FONT_WIDTH * c, 0))
            elif st[c] == '!':
                out.blit(self.chars[0][37],(self.FONT_WIDTH * c, 0))
            elif st[c] == '.':
                out.blit(self.chars[0][38],(self.FONT_WIDTH * c, 0))
            elif st[c] == '$':
                out.blit(self.chars[0][39],(self.FONT_WIDTH * c, 0))
            elif st[c] == ',':
                out.blit(self.chars[0][40],(self.FONT_WIDTH * c, 0))
            elif st[c] == ':':
                out.blit(self.chars[0][41],(self.FONT_WIDTH * c, 0))
            elif st[c] == '(':
                out.blit(self.chars[0][42],(self.FONT_WIDTH * c, 0))
            elif st[c] == ')':
                out.blit(self.chars[0][43],(self.FONT_WIDTH * c, 0))
            elif st[c] == ' ':
                out.blit(self.chars[0][44],(self.FONT_WIDTH * c, 0))
            ####lower case######
            elif st[c] == 'a':
                out.blit(self.chars[1][0],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'b':
                out.blit(self.chars[1][1],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'c':
                out.blit(self.chars[1][2],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'd':
                out.blit(self.chars[1][3],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'e':
                out.blit(self.chars[1][4],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'f':
                out.blit(self.chars[1][5],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'g':
                out.blit(self.chars[1][6],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'h':
                out.blit(self.chars[1][7],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'i':
                out.blit(self.chars[1][8],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'j':
                out.blit(self.chars[1][9],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'k':
                out.blit(self.chars[1][10],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'l':
                out.blit(self.chars[1][11],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'm':
                out.blit(self.chars[1][12],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'n':
                out.blit(self.chars[1][13],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'o':
                out.blit(self.chars[1][14],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'p':
                out.blit(self.chars[1][15],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'q':
                out.blit(self.chars[1][16],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'r':
                out.blit(self.chars[1][17],(self.FONT_WIDTH * c, 0))
            elif st[c] == 's':
                out.blit(self.chars[1][18],(self.FONT_WIDTH * c, 0))
            elif st[c] == 't':
                out.blit(self.chars[1][19],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'u':
                out.blit(self.chars[1][20],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'v':
                out.blit(self.chars[1][21],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'w':
                out.blit(self.chars[1][22],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'x':
                out.blit(self.chars[1][23],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'y':
                out.blit(self.chars[1][24],(self.FONT_WIDTH * c, 0))
            elif st[c] == 'z':
                out.blit(self.chars[1][25],(self.FONT_WIDTH * c, 0))
            elif st[c] == '/':
                out.blit(self.chars[1][26],(self.FONT_WIDTH * c, 0))
        

        #modify the surface if it is selected
        if selected == True:
            temp = pygame.Surface((self.FONT_WIDTH * stlen,self.FONT_HEIGHT))
            temp.fill((255,255,255))
            out.set_colorkey((0,0,0))
            temp.blit(out,(0,0))
            return temp
        else:        
            return out

