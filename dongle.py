import sys
import pygame
import random
from pygame.locals import *

import draw_utils
import char_utils

SCREEN_WIDTH, SCREEN_HEIGHT = 480,420
MAP_CHANGE_FRAMES = 40
MAP_CHANGE_DELAY = 20
MAP_DIR = 'maps/'
X_MOVE, Y_MOVE = 10,10
#----main----
if __name__=='__main__':
    #initialize screen
    screen_size = SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.init()
    screen = pygame.display.set_mode(screen_size, RESIZABLE)
    screen.fill((255, 255, 255))

    sprites = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
    sprites.fill((255,255,255))
    sprites.set_colorkey((255,255,255))

    #animations
    anim = draw_utils.animation(0)
    
    #initialize a game map
    gamemap = draw_utils.map(MAP_DIR + 'L1_00.map')
       
    #character starting position
    char_x = 150
    char_y = 150
    
    #initialize character and stuff
    dongle = char_utils.character()
    #initial inventory
    dongle.inventory.add_item(char_utils.item('Potion',8,'u',[0,0,0],'Potion restores 15 Mp',1),3)
    dongle.inventory.add_item(char_utils.item('Potion',8,'u',[0,0,0],'Potion restores 15 Mp',1),3)
    
    #initial equipment
    dongle.equipped.equip(char_utils.WEAPON_SLOT, char_utils.item('Wet Noodle',0,'eADM',[1,0,0],'Some limp wet linguini.',1))
    dongle.equipped.equip(char_utils.SHIELD_SLOT, char_utils.item('Day Old Bread',1,'eM',[0,1,0],'It is hard as the day is long.',1))
    #initial abilities
    dongle.abilities.append(char_utils.ability('Cure', 'Restore some Hp',char_utils.PLAYER,1,'holy',5,10,1)) 
    dongle.abilities.append(char_utils.ability('Fire', 'Shoot some fire',char_utils.MONSTER,1,'fire',5,5,1.5))
    dongle.abilities.append(char_utils.ability('Blizzard', 'Ice storm all enemies',char_utils.MONSTER,0,'ice',10,4,1.1))
    
    #enc = char_utils.encounter()

    #initialze menues
    #main menue
    mm = draw_utils.menue('main', ['Character','Inventory','Abilities','Equipment','Quit'])
    #battle menue
    bm = draw_utils.menue('battle',['Attack','Ability','Items','Flee'])

    #initalize game variables
    clock = pygame.time.Clock()
    game_over = False
    counter = 0
    encounter_chance = 0
    threshold = 100
    foot = True
    #gamestate flags
    GS_OUTSIDE = 0
    GS_MENUE = 1
    GS_BATTLE = 2
    GS_FLEEING = 3
    gamestate = GS_OUTSIDE
    #screen resize flag
    resizer = (0,0)
    #flag for aoe abilities in battle menue
    aoe = False
    #flag for recently traveling stairs
    RECENT_STAIRS = False

    #------main game loop---------------
    #-----------------------------------
    while game_over == False:
        clock.tick(15)
        counter +=1
        if counter == 100:
            counter = 0

   
        #event handlers
        for event in pygame.event.get():
            #quit
            if event.type == pygame.locals.QUIT:
                game_over = True
                pygame.display.quit()
                sys.exit(0)
            #resize
            elif event.type==VIDEORESIZE:
                screen=pygame.display.set_mode(event.dict['size'],RESIZABLE)
                resizer = event.dict['size']
        
            
        #all keypress events for all gamestates handles here
        keys = pygame.key.get_pressed()
        #-----key up------
        if keys[pygame.K_UP]:
            if gamestate == GS_OUTSIDE:
                char_y -= Y_MOVE
            elif gamestate == GS_MENUE:
                #move selected item in the active menue
                if mm.active_menue == draw_utils.AM_MENUE:
                    mm.menue_selected -= 1
                    mm.detail_selected = 0
                    mm.scroll_start = 0
                    #wrap selected item around once it reaches the top
                    if mm.menue_selected < 0:
                        mm.menue_selected = mm.menue_max
                #move selected item in the detail menue       
                elif mm.active_menue == draw_utils.AM_DETAIL:
                    mm.detail_selected -= 1
                    if mm.detail_selected < 0:
                        #wrap around for top
                        if mm.scroll_start > 0:
                            mm.detail_selected += 1
                            mm.scroll_start -= 1
                        else:
                            mm.detail_selected = mm.screen_max -1
                            mm.scroll_start = mm.detail_max - mm.screen_max
                    #clear the description field when equipment selected changes
                    mm.clear('description')
                #clear the detail pane whenever a menue item is moved
                mm.clear('details')
            elif gamestate == GS_BATTLE:
                if bm.active_menue == draw_utils.AM_MENUE:
                    bm.menue_selected -= 1
                    if bm.menue_selected < 0:
                        bm.menue_selected = bm.menue_max
                elif bm.active_menue == draw_utils.AM_SELECT:
                    bm.ability_selected -=1
                    if bm.ability_selected < 0:
                        #wrap around top
                        if bm.scroll_start > 0:
                            bm.ability_selected +=1
                            bm.scroll_start -=1
                        else:
                            bm.ability_selected = bm.screen_max -1
                            bm.scroll_start = bm.ability_max - bm.screen_max                        
                elif bm.active_menue == draw_utils.AM_MONSTER:
                    bm.monster_selected -=1
                    if bm.monster_selected < 0:
                        bm.monster_selected = bm.monster_max
                    #move past dead monsters
                    while enc.monsters[bm.monster_selected].alive == False:
                        bm.monster_selected -= 1
                        if bm.monster_selected < 0:
                            bm.monster_selected = bm.monster_max
                        
        #-----key down------
        if keys[pygame.K_DOWN]:
            if gamestate == GS_OUTSIDE:
                char_y += Y_MOVE
            elif gamestate == GS_MENUE:
                #move selected item in the active menue
                if mm.active_menue == draw_utils.AM_MENUE:
                    mm.detail_selected = 0
                    mm.scroll_start = 0
                    mm.menue_selected += 1
                    if mm.menue_selected > mm.menue_max:
                        #wrap around bottom
                        mm.menue_selected = 0
                elif mm.active_menue == draw_utils.AM_DETAIL:
                    mm.detail_selected += 1
                    #move scroll area or wrap around bottom
                    if mm.detail_selected > mm.screen_max - 1:
                        if mm.detail_selected + mm.scroll_start <= mm.detail_max - 1:
                            mm.scroll_start += 1
                            mm.detail_selected -= 1
                        else:
                            mm.scroll_start = 0
                            mm.detail_selected = 0
                    #clear the description field when equipment selected changes
                    mm.clear('description')
                #clear the detail pane whenever a menue item is moved
                mm.clear('details')
            elif gamestate == GS_BATTLE:
                if bm.active_menue == draw_utils.AM_MENUE:
                    bm.menue_selected += 1
                    if bm.menue_selected > bm.menue_max:
                        bm.menue_selected = 0
                elif bm.active_menue == draw_utils.AM_SELECT:
                    bm.ability_selected +=1
                    if bm.ability_selected > bm.screen_max - 1:
                        if bm.ability_selected + bm.scroll_start <= bm.ability_max - 1:
                            bm.scroll_start += 1
                            bm.ability_selected -= 1
                        else:
                            bm.scroll_start = 0
                            bm.ability_selected = 0
                elif bm.active_menue == draw_utils.AM_MONSTER:
                    bm.monster_selected +=1
                    if bm.monster_selected > bm.monster_max:
                        bm.monster_selected = 0
                    #move past dead monsters
                    while enc.monsters[bm.monster_selected].alive == False:
                        bm.monster_selected +=1
                        if bm.monster_selected > bm.monster_max:
                            bm.monster_selected = 0

        #-----key left------
        if keys[pygame.K_LEFT]:
            if gamestate == GS_OUTSIDE:
                char_x -= X_MOVE
            elif gamestate == GS_MENUE:
                #return control to main menue from detail menue
                if mm.active_menue == draw_utils.AM_DETAIL:
                    mm.active_menue = draw_utils.AM_MENUE
                    mm.clear('description')
        #-----key right------
        if keys[pygame.K_RIGHT]:
            if gamestate == GS_OUTSIDE:
                char_x += X_MOVE
            elif gamestate == GS_MENUE:
                #transfer menue control to detail
                if mm.active_menue == draw_utils.AM_MENUE:
                    if mm.menue_selected == draw_utils.MS_EQUIPMENT or mm.menue_selected == draw_utils.MS_INVENTORY or mm.menue_selected == draw_utils.MS_ABILITIES:
                        mm.detail_selected = 0
                        mm.active_menue = draw_utils.AM_DETAIL
                
        #-----key return------
        if keys[pygame.K_RETURN]:
            #gamestate MENUE=========================
            if gamestate == GS_MENUE:
                if mm.menue_selected == draw_utils.MS_EXIT:
                    #!!!!!!!!!!!add a confirmation yes/no
                    pygame.display.quit()
                    sys.exit(0)
            #gamestate BATTLE========================
            if gamestate == GS_BATTLE:
                aoe = False
                #active menue: menue
                if bm.active_menue == draw_utils.AM_MENUE:
                    #if attacking, switch control to monsters pane
                    if bm.menue_selected == draw_utils.BM_ATTACK:
                        bm.active_menue = draw_utils.AM_MONSTER
                        bm.monster_selected = 0
                        while enc.monsters[bm.monster_selected].alive == False:
                            bm.monster_selected +=1
                    #if using ability or item, switch to select menue
                    elif bm.menue_selected == draw_utils.BM_ABILITY or bm.menue_selected == draw_utils.BM_ITEM:
                         bm.active_menue = draw_utils.AM_SELECT
                         bm.ability_selected = 0
                    #if fleeing
                    elif bm.menue_selected == draw_utils.BM_FLEE:
                        #escape was successfull
                        if enc.escaped() == True:
                            bm.alert('Escaped!')
                            gamestate = GS_FLEEING
                        else:
                            bm.alert('Could not flee!')
                            enc.turn = draw_utils.MONSTER
                            bm.menue_selected = 0
                #active menue: ability select
                elif bm.active_menue == draw_utils.AM_SELECT:
                    #adjust the ability selected
                    bm.ability_selected += bm.scroll_start
                    #if ability is selected
                    if bm.menue_selected == draw_utils.BM_ABILITY:
                        #make sure there is enough mana
                        if dongle.mp >= dongle.abilities[bm.ability_selected].mp:
                            #if ability is targeting player, use on player. else switch to monster select
                            if dongle.abilities[bm.ability_selected].target == draw_utils.PLAYER:
                                #use the ability
                                healing = enc.char_ability(dongle,char_utils.PLAYER, bm.ability_selected)
                                #print out alert
                                bm.alert('Dongle cast ' + dongle.abilities[bm.ability_selected].name + ' for ' + str(healing) + '.')
                                #update animation
                                if dongle.abilities[bm.ability_selected].name == 'Cure':
                                    anim = draw_utils.animation(2)
                                    anim.delay = 60

                                anim.draw = True
                                anim.targets.append(draw_utils.BATTLE_POS[4])
                                
                                #return active menue to menue
                                bm.active_menue = draw_utils.AM_MENUE
                                bm.ability_selected = 0
                                bm.menue_selected = 0
                                #set turn to monster
                                enc.turn = draw_utils.MONSTER
                            else:
                                bm.active_menue = draw_utils.AM_MONSTER
                                bm.monster_selected = 0
                                while enc.monsters[bm.monster_selected].alive == False:
                                    bm.monster_selected +=1
                                #set aoe flag to true
                                if dongle.abilities[bm.ability_selected].area == 0:
                                    aoe = True
                        #not enough mana
                        else:
                            bm.alert('Not enough mana!')
                            bm.menue_selected = 0
                            bm.ability_selected = 0
                            bm.active_menue = draw_utils.AM_MENUE
                    #if item is selected
                    else:
                        healing = enc.use_item(dongle, bm.ability_selected)
                        #print out alert
                        bm.alert('Dongle used a ' + dongle.inventory.items[bm.ability_selected].name + '.')
                            
                        #return active menue to menue
                        bm.active_menue = draw_utils.AM_MENUE
                        bm.ability_selected = 0
                        bm.menue_selected = 0
                        enc.turn = draw_utils.MONSTER
                #select a monster
                elif bm.active_menue == draw_utils.AM_MONSTER:
                    #attacking a monster
                    if bm.menue_selected == draw_utils.BM_ATTACK:
                        #attack the selected monster
                        damage = enc.char_ability(dongle,char_utils.MONSTER,-1,bm.monster_selected)
                        #print out alert
                        bm.alert('Dongle attacked ' + enc.monsters[bm.monster_selected].name + ' for ' + str(damage))
                        #update the animation
                        anim = draw_utils.animation(0)
                        anim.delay = 20
                        anim.draw = True
                        anim.targets.append(draw_utils.BATTLE_POS[bm.monster_selected])
                        enc.monsters[bm.monster_selected].state = 3
                        #set turn to monster
                        enc.turn = draw_utils.MONSTER
                        bm.menue_selected = 0
                        bm.active_menue = draw_utils.AM_MENUE

                    #used ability on monster
                    elif bm.menue_selected == draw_utils.BM_ABILITY:
                        #print out alert
                        damage = enc.char_ability(dongle,char_utils.MONSTER, bm.ability_selected,bm.monster_selected)
                        bm.alert('Cast ' + dongle.abilities[bm.ability_selected].name + ' on ' + enc.monsters[bm.monster_selected].name + ' for ' + str(damage) + '.')
                        #update animation
                        if dongle.abilities[bm.ability_selected].name == 'Fire':
                            anim = draw_utils.animation(1)
                            anim.delay = 20
                            anim.targets.append(draw_utils.BATTLE_POS[bm.monster_selected])
                            enc.monsters[bm.monster_selected].state = 3

                        if dongle.abilities[bm.ability_selected].name == 'Blizzard':
                            anim = draw_utils.animation(3,True)
                            anim.delay = 75
                            for i in range(0, len(enc.monsters)):
                                if enc.monsters[i].alive == True:
                                    enc.monsters[i].state = 3
                                    anim.targets.append(draw_utils.BATTLE_POS[i])
                                    anim.targets.append((draw_utils.BATTLE_POS[i][0]+20, draw_utils.BATTLE_POS[i][1]+20))
                                    anim.targets.append((draw_utils.BATTLE_POS[i][0]+20, draw_utils.BATTLE_POS[i][1]-20))
                                    anim.targets.append((draw_utils.BATTLE_POS[i][0]-20, draw_utils.BATTLE_POS[i][1]+20))

                        anim.draw = True

                        #set turn to monster
                        enc.turn = draw_utils.MONSTER
                        bm.menue_selected = 0
                        bm.ability_selected = 0
                        bm.active_menue = draw_utils.AM_MENUE
                
        #-----key escape------
        if keys[pygame.K_ESCAPE]:
            if gamestate == GS_OUTSIDE:
                gamestate = GS_MENUE
                mm.menue_selected = draw_utils.MS_CHARACTER
                mm.active_menue = draw_utils.AM_MENUE
                
            elif gamestate == GS_MENUE:
                gamestate = GS_OUTSIDE
            elif gamestate == GS_BATTLE:
                if bm.active_menue == draw_utils.AM_MONSTER or bm.active_menue == draw_utils.AM_SELECT:
                    bm.active_menue = draw_utils.AM_MENUE
                    bm.clear('monster')
                    aoe = False
 
        #--------Gamestate Outside--------
        if gamestate == GS_OUTSIDE:
            #encounter chance
            #if random.randint(0,5) == 0:
            if False:
                encounter_chance += 1
            if encounter_chance * encounter_chance / threshold > 1:
                encounter_chance = 0
                enc = char_utils.encounter(dongle,0.5)
                #set the status from equipment
                for i in range(0,random.randint(1,4)):
                    enc.monsters.append(char_utils.monster('Goob',1,0))
                gamestate = GS_BATTLE        
            #bounds checking for character sprite / exit checking
            #!!!!! change 41/50 to constants (character sprite dimensions)
            #get the current tile
            current_tile = (int((char_x+20)/ 30),int((char_y+15)/ 30))
            #tile for checking stairs differs from side exits current_tile due to using the middle of the sprite for current_tile
            stairs_tile = (current_tile[0],current_tile[1] +1)
            #reset RECENT_STAIRS once character has moved off of current tile
            if RECENT_STAIRS != False:
                if stairs_tile != RECENT_STAIRS:
                    print('off the stairs')
                    RECENT_STAIRS = False

            #check to see if character is on stairs
            isexit = gamemap.is_exit('s',stairs_tile)
            if isexit != False:
                #check recent stairs flag in order to avoid bounching between two maps
                if RECENT_STAIRS == False:
                    print('on some stairs')
                    #fade out, fade back in on new map.
                    fade_rect = pygame.Surface(screen.get_size())
                    fade_rect.fill((0,0,0))
                    print(gamemap.background.get_alpha())
                    #fade out
                    for i in range(MAP_CHANGE_FRAMES):
                        fade_rect.set_alpha(i)
                        screen.blit(fade_rect,(0,0))
                        pygame.display.flip()
                        pygame.time.delay(MAP_CHANGE_DELAY)
                    #change map
                    gamemap = draw_utils.map(MAP_DIR + isexit)
                    fade_rect = gamemap.background

                    #fade in
                    for i in range(MAP_CHANGE_FRAMES):
                        fade_rect.set_alpha(MAP_CHANGE_FRAMES-10 + i)
                        screen.blit(pygame.transform.scale(fade_rect, resizer),(0,0))
                        screen.blit(pygame.transform.scale(sprites,resizer),(0,0))
                        pygame.display.flip()
                        pygame.time.delay(MAP_CHANGE_DELAY)
                    
                    #set recent stairs flag to true\
                    gamemap.background.set_alpha(None)
                    RECENT_STAIRS = stairs_tile
                    print(gamemap.background.get_alpha())
            
            #screen bounds check left
            if char_x < 0:
                isexit = gamemap.is_exit('l',current_tile)
                if isexit == False:
                    char_x = 0
                else:
                    old_screen = screen.copy()
                    gamemap = draw_utils.map(MAP_DIR + isexit)
                    for i in range(0,MAP_CHANGE_FRAMES):
                        screen.fill((255,255,255))
                        screen.blit(pygame.transform.scale(old_screen,resizer),(int(SCREEN_WIDTH/MAP_CHANGE_FRAMES * i),0))
                        screen.blit(pygame.transform.scale(gamemap.background, resizer),((SCREEN_WIDTH * -1) + int(SCREEN_WIDTH/MAP_CHANGE_FRAMES * i),0))
                        pygame.display.flip()
                        pygame.time.delay(MAP_CHANGE_DELAY)
                        char_x = SCREEN_WIDTH - 41
            #screen bounds check right
            if char_x > SCREEN_WIDTH - 41:
                isexit = gamemap.is_exit('r',current_tile)
                if isexit == False:
                    char_x = SCREEN_WIDTH - 41
                else:
                    old_screen = screen.copy()
                    gamemap = draw_utils.map(MAP_DIR + isexit)
                    for i in range(0,MAP_CHANGE_FRAMES):
                        screen.fill((255,255,255))
                        screen.blit(pygame.transform.scale(old_screen,resizer),(int(SCREEN_WIDTH/MAP_CHANGE_FRAMES * i) * -1,0))
                        screen.blit(pygame.transform.scale(gamemap.background, resizer),(SCREEN_WIDTH + int(SCREEN_WIDTH/MAP_CHANGE_FRAMES * i) * -1,0))
                        pygame.display.flip()
                        pygame.time.delay(MAP_CHANGE_DELAY)
                        char_x = 0
            #sceen bounds check up
            if char_y < 0:
                isexit = gamemap.is_exit('u',current_tile)
                if isexit == False:
                    char_y = 0
                else:
                    old_screen = screen.copy()
                    gamemap = draw_utils.map(MAP_DIR + isexit)
                    for i in range(0,MAP_CHANGE_FRAMES):
                        screen.fill((255,255,255))
                        screen.blit(pygame.transform.scale(old_screen,resizer),(0,int(SCREEN_HEIGHT/MAP_CHANGE_FRAMES * i)))
                        screen.blit(pygame.transform.scale(gamemap.background, resizer),(0,(SCREEN_HEIGHT * -1) + int(SCREEN_HEIGHT/MAP_CHANGE_FRAMES * i)))
                        pygame.display.flip()
                        pygame.time.delay(MAP_CHANGE_DELAY)
                        char_y = SCREEN_HEIGHT - 50
            #sceen bounds check down
            if char_y > SCREEN_HEIGHT - 50:
                isexit = gamemap.is_exit('d',current_tile)
                if isexit == False:
                    char_y = SCREEN_HEIGHT - 50
                else:
                    old_screen = screen.copy()
                    gamemap = draw_utils.map(MAP_DIR + isexit)
                    for i in range(0,MAP_CHANGE_FRAMES):
                        screen.fill((255,255,255))
                        screen.blit(pygame.transform.scale(old_screen,resizer),(0,int(SCREEN_HEIGHT/MAP_CHANGE_FRAMES * i) * -1))
                        screen.blit(pygame.transform.scale(gamemap.background, resizer),(0,SCREEN_HEIGHT + int(SCREEN_HEIGHT/MAP_CHANGE_FRAMES * i) * -1))
                        pygame.display.flip()
                        pygame.time.delay(MAP_CHANGE_DELAY)
                        char_y = 0

            #clear the sprite map
            sprites.fill((255,255,255))
            #animate walking
            if counter % 5 == 1:
                foot = not foot    
            if foot:
                sprites.blit(dongle.image[0],(char_x,char_y))
            else:
                sprites.blit(dongle.image[1],(char_x,char_y))

            #blit background,sprites to screen resize and display
            screen.blit(pygame.transform.scale(gamemap.background,resizer),(0,0))
            screen.blit(pygame.transform.scale(sprites,resizer),(0,0))
            pygame.display.flip()

        #--------Gamestate Menue----------
        elif gamestate == GS_MENUE:
            #active main menue
            if mm.menue_selected == draw_utils.MS_CHARACTER:
                mm.draw_char_info(dongle)
            #active inventory
            if mm.menue_selected == draw_utils.MS_INVENTORY:
                mm.draw_inventory(dongle.inventory,mm.detail_selected)
            if mm.menue_selected == draw_utils.MS_ABILITIES:
                mm.draw_abilities(dongle.abilities,mm.detail_selected)
            #active equipment menue
            elif mm.menue_selected == draw_utils.MS_EQUIPMENT:
                mm.draw_equipment(dongle.equipped,mm.detail_selected)

            #redraw the menue with the current selected menue item
            mm.draw_menue_items(20,mm.menue_selected)
            screen.blit(pygame.transform.scale(mm.menue,resizer),(0,0))
            pygame.display.flip()
        #---------Gamestate Fleeing---------
        elif gamestate == GS_FLEEING:
            bm.draw_char_bars(dongle)
            bm.draw_menue_items(20,bm.menue_selected)
            screen.blit(pygame.transform.scale(bm.menue,resizer),(0,0))
            pygame.display.flip()
            pygame.time.delay(1000)
            gamestate = GS_OUTSIDE
            bm.menue_selected = 0
            bm.alert("")
            
        #---------Gamestate Battle----------
        elif gamestate == GS_BATTLE:
            bm.draw_char_bars(dongle)
            bm.draw_menue_items(20,bm.menue_selected)
            #draw a select menue or the monster health bars
            if bm.active_menue == draw_utils.AM_SELECT:
                #draw the ability select or the item select menues
                if bm.menue_selected == draw_utils.BM_ABILITY:
                    bm.draw_ability_choose(dongle.abilities, bm.ability_selected)
                else:
                    bm.draw_item_choose(dongle.inventory, bm.ability_selected)
            else:
                bm.draw_monster_bars(enc, bm.monster_selected)

            #pick a random monster every now and then to change drawing state
            if counter % 5 == 1:
                enc.monsters[random.randint(0, len(enc.monsters)-1)].state_change()
                #change the character drawing state
                dongle.state_change()
            #draw monsters and character
            if aoe == True:
                bm.draw_encounter(enc, dongle, bm.monster_selected, True)
            else:
                bm.draw_encounter(enc, dongle, bm.monster_selected)
                
            #draw any animations and update the screen
            if anim.draw == True:
                for i in range(0,anim.max):
                    #clear then redraw sprites
                    sprites.fill((255,255,255))
                    for t in range(0, len(anim.targets)):
                        sprites.blit(anim.next_frame(),anim.targets[t])
                    #blit the background, then the animation sprites
                    screen.blit(pygame.transform.scale(bm.menue,resizer),(0,0))
                    screen.blit(pygame.transform.scale(sprites,resizer),(0,0))
                    #display then pause
                    pygame.display.flip()
                    pygame.time.delay(anim.delay)
                anim.draw = False
                
            #update battle state, check for battle won
            if enc.update_state() == 0:
                #battle won! congrats!
                gold = enc.get_gold()
                xp = enc.get_xp()
                
                win_write = bm.f.write('You won the fight!')
                xp_write = bm.f.write('You earned ' + str(xp) + ' Experience.')
                gold_write = bm.f.write('You found ' + str(gold) + ' Gold.')

                dongle.xp += xp
                dongle.gold += gold
                
                bm.clear('battle')
                bm.clear('status_bar')
                bm.clear('alert')
                bm.menue.blit(win_write,(5,5))
                bm.menue.blit(xp_write,(5,40))
                bm.menue.blit(gold_write,(5,55))

                #gained a level
                if dongle.xp >= dongle.nl:
                    dongle.level_up()
                    bm.menue.blit(bm.f.write('You gained a level!'),(5,85))
                    bm.menue.blit(bm.f.write('Hp and Mp restored!'),(5,100))
                
                screen.blit(pygame.transform.scale(bm.menue,resizer),(0,0))
                pygame.display.flip()
                pygame.time.delay(5000)

                bm.clear('alert')

                gamestate = GS_OUTSIDE
                
            #reset monsters, redraw once more to clear sprites
            for i in range(0, len(enc.monsters)):
                if enc.monsters[i].state == 3:
                    enc.monsters[i].state = 0
            if aoe == True:
                bm.draw_encounter(enc, dongle, bm.monster_selected, True)
            else:
                bm.draw_encounter(enc, dongle, bm.monster_selected)
            screen.blit(pygame.transform.scale(bm.menue,resizer),(0,0))
            pygame.display.flip()
            #--------Monster Turn---------
            if enc.turn == draw_utils.MONSTER:
                #loop through each monster
                for i in range(0,len(enc.monsters)):
                    if enc.monsters[i].alive == True:
                        pygame.time.delay(1000)
                        bm.alert(enc.monsters[i].name + ' Attacked Dongle')
                        #switch the anim target to player animate for each monster
                        anim = draw_utils.animation(0)
                        anim.delay = 20
                        anim.target = draw_utils.BATTLE_POS[4]
                        for i in range(0,anim.max):
                            #clear then redraw sprites
                            sprites.fill((255,255,255))
                            sprites.blit(anim.next_frame(),anim.target)
                            #blit the background, then the animation sprites
                            screen.blit(pygame.transform.scale(bm.menue,resizer),(0,0))
                            screen.blit(pygame.transform.scale(sprites,resizer),(0,0))
                            #display then pause
                            pygame.display.flip()
                            pygame.time.delay(anim.delay)
                        #redraw to clear sprites
                        screen.blit(pygame.transform.scale(bm.menue,resizer),(0,0))
                        pygame.display.flip()
                #mosnter turn over
                enc.turn = draw_utils.PLAYER

        

