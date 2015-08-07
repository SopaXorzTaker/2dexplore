import datetime
import config
from player_entity import PlayerEntity
# TODO: make a better random with probability
__author__ = 'mark'
import pygame
import sys
import os
from pygame.locals import *
import world
import block
import random
import time
from PIL import Image
just_started = True
class CloseInventory(Exception): pass

block.load_textures()  # ...
player_health = 20.0
SAVE_FILE = "explore_save.gz"
TILESIZE = 32
MAP_X = 48
MAP_Y = 48
screen = None
COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'grey': (127, 127, 127)
}
sx = 0
sy = 0

config.load()

def screenshot():
    filename = "2dexp-%s.png" % str(datetime.datetime.now()).replace(":", "-")
    f = open(filename, "w")  # Create the file
    f.close()
    pygame.image.save(display, filename)
    print "Saved screenshot"


def load(filename):
    import cPickle, gzip

    global wrl
    try:
        world_file = gzip.open(filename, "rb")
        wrl = cPickle.load(world_file)
    except IOError as err:
        print "Unable to open the file! \n %s" % err.message
    except cPickle.UnpicklingError as err:
        print "Error unpickling! \n %s" % err.message


def save(filename):
    import cPickle
    import gzip

    global wrl
    try:
        world_file = gzip.open(filename, "wb")
        cPickle.dump(wrl, world_file, cPickle.HIGHEST_PROTOCOL)
    except IOError as err:
        print "Unable to open the file! \n %s" % err.message
    except cPickle.PicklingError as err:
        print "Error pickling! \n %s" % err.message


def game_over():
    global just_started
    if not just_started:
        gameover_font = pygame.font.SysFont("FreeSansBold", 38)
        gameover_label = gameover_font.render("GAME OVER, press any key", True, COLORS['red'], COLORS['black'])
        display.blit(gameover_label, (32, 32))
        pygame.display.update()
        stop = False
        while not stop:
            for evt in pygame.event.get():
                if evt.type in [KEYDOWN, QUIT]:
                    stop = True
                    if evt.type == KEYDOWN:
                        wrl.new_world(MAP_X, MAP_Y)

def main_loop():
    global display, start_time, fall_delay, map_display, block_above, block_under, block_index, wrl, xs, ys, \
        just_started, player_health
    ys = 0
    xs = 0
    wantsInventory = False
    font = pygame.font.SysFont("UbuntuMono", 13)  # Fonts should be inited after pygame.init()
    start_time = 0
    clk = pygame.time.Clock()
    if wrl.player.coords[1] < 12:
        xboundmax = (wrl.player.coords[1] + 12)
    else:
        xboundmax = ((wrl.player.coords[1] - (wrl.player.coords[1] * 2)) + 12)
    xboundmin = 0
    if wrl.player.coords[1] < 8:
        yboundmax = (wrl.player.coords[0])
    else:
        yboundmax = ((wrl.player.coords[0] - (wrl.player.coords[0] * 2)) + 8)
    yboundmin = 0
    Inventory = pygame.Surface((100, 200))
    InvBack = pygame.Surface((100, 200))
    InvBack.set_alpha(64)
    InvBack.fill(0x000000)
    InventoryBounds = pygame.Rect((700, 0), (100, 200))
    def inv_out(out, x, y):
        text = font.render(out, True, COLORS['white'])
        Inventory.blit(text, (x, y))
    textlev = 0
    def pilgame(image_path, dimensions, type):
        image = Image.open(image_path)
        pygame_image = pygame.image.fromstring(image.tobytes(), dimensions, type)
        return pygame_image
    while True:
        for i in xrange(14):
            if i >= 10: ii = (i - 10)*-1
            else: ii = i
            blockToDisplay = block.BLOCK_NAMES_VERBOSE.get(block.BLOCK_INVENTORY[ii], "unknown")
            Inventory.blit(pilgame((("textures/inventory_thumb/%s.png") % blockToDisplay), (16, 16), "RGBA"), (2, textlev))
            inv_out(str(wrl.player.inventory.get(i)), 30, textlev)
            textlev += 23
        has_displayed = 0
        if wrl.player.coords[1] < 12:
            xboundmax = (wrl.player.coords[1] + 12)
        else:
            xboundmax = ((wrl.player.coords[1] - (wrl.player.coords[1] * 2)) + 12)
        xboundmin = 0
        if wrl.player.coords[0] < 8:
            yboundmax = (wrl.player.coords[0] + 8)
        else:
            yboundmax = ((wrl.player.coords[0] - (wrl.player.coords[0] * 2)) + 8)
        yboundmin = 0

        clk.tick(20)
        if pygame.time.get_ticks() - start_time >= 50:
            wrl.tick()
        start_time = pygame.time.get_ticks()
        px = wrl.player.coords[1]
        py = wrl.player.coords[0]
        block_under = wrl.level[px][py]
        block_above = wrl.level[px][py - 1] if py < 0 else -1
        prev_pos = wrl.player.coords[:]  # lists are mutable
        for event in pygame.event.get():
            if event.type == QUIT:
                save(SAVE_FILE)
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                keys = pygame.key.get_pressed()
                just_started = False
                # W KEY - UP
                if event.key == K_w and wrl.player.coords[0] in range(1, MAP_X) and (
                            not wrl.player.falling or wrl.player.god_mode):
                    wrl.player.coords[0] -= 1
                    yboundmax += 1
                    if yboundmin != 0:
                        yboundmin += 1
                    if not wrl.level[wrl.player.coords[1]][wrl.player.coords[0]] in block.BLOCK_NONSOLID and not keys[
                        K_LSHIFT] and \
                            not wrl.player.god_mode:
                        wrl.player.coords = prev_pos
                    if keys[K_LSHIFT]:
                        bx, by = wrl.player.coords[1], wrl.player.coords[0]
                        wrl.destroy_block(bx, by)
                        # S KEY - DOWN
                elif event.key == K_s and wrl.player.coords[0] in range(0, MAP_X - 1):
                    wrl.player.coords[0] += 1
                    yboundmax -= 1
                    if yboundmin != 0:
                        yboundmin -= 1
                    if not wrl.level[wrl.player.coords[1]][wrl.player.coords[0]] in block.BLOCK_NONSOLID and not keys[
                        K_LSHIFT]:
                        wrl.player.coords = prev_pos
                    if keys[K_LSHIFT]:
                        bx, by = wrl.player.coords[1], wrl.player.coords[0]
                        wrl.destroy_block(bx, by)
                        # A KEY - LEFT
                elif event.key == K_a and wrl.player.coords[1] in range(1, MAP_Y):
                    wrl.player.falling = False
                    fall_delay = 0
                    wrl.player.coords[1] -= 1
                    xboundmax += 1
                    if xboundmin != 0:
                        xboundmin += 1

                    if not wrl.level[wrl.player.coords[1]][wrl.player.coords[0]] in block.BLOCK_NONSOLID and not keys[
                        K_LSHIFT]:
                        wrl.player.coords = prev_pos
                    if keys[K_LSHIFT]:
                        bx, by = wrl.player.coords[1], wrl.player.coords[0]
                        wrl.destroy_block(bx, by)
                    wrl.player.set_walk(0)
                    # D KEY - RIGHT
                elif event.key == K_d and wrl.player.coords[1] in range(0, MAP_Y - 1):
                    wrl.player.falling = False
                    fall_delay = 0
                    wrl.player.coords[1] += 1
                    xboundmax -= 1
                    if xboundmax <= -24:
                        xboundmin -= 1
                    if not wrl.level[wrl.player.coords[1]][wrl.player.coords[0]] in block.BLOCK_NONSOLID and not keys[
                        K_LSHIFT]:
                        wrl.player.coords = prev_pos
                    if keys[K_LSHIFT]:
                        bx, by = wrl.player.coords[1], wrl.player.coords[0]
                        wrl.destroy_block(bx, by)
                    wrl.player.set_walk(1)
                    # Z KEY - PLACE BLOCK
                elif event.key == K_z:
                    # print "Debug: placing block at %d %d, previous was %d" % (px, py, wrl.level[px][py])
                    if (wrl.player.inventory[
                            wrl.player.current_block] > 0 or wrl.player.god_mode) and block_under == block.BLOCK_AIR:
                        wrl.level[px][py] = block.BLOCK_INVENTORY[wrl.player.current_block]
                        if not wrl.player.god_mode:
                            wrl.player.inventory[wrl.player.current_block] -= 1
                            # X KEY - DESTROY BLOCK STANDING ON
                elif event.key == K_x:
                    if wrl.level[px][py] in block.BLOCK_INVENTORY:
                        if block_under in block.BLOCK_INVENTORY:
                            block_index = block.BLOCK_INVENTORY.index(block_under)
                            wrl.player.inventory[block_index] += 1
                            wrl.level[px][py] = block.BLOCK_AIR
                            # 1 KEY - SCROLL INVENTORY
                elif event.key == K_1:
                    wrl.player.current_block = (wrl.player.current_block + 1) % len(block.BLOCK_INVENTORY)
                    # ESC KEY - RESET
                elif event.key == K_ESCAPE:
                    xboundmax, xboundmin, yboundmax, yboundmin = 0, 0, 0, 0
                    wrl.new_world(MAP_X, MAP_Y)
                    # F1 KEY - GODMODE
                elif event.key == K_F1:
                    wrl.player.god_mode = not wrl.player.god_mode
                    # E KEY - EXPLODE
                elif event.key == K_e and wrl.player.god_mode:
                    wrl.explode(px, py, 5, False)
                    # N KEY - DESPAWN ENTITY
                elif event.key == K_n:  # and wrl.player.god_mode:
                    if len(wrl.entities) > 1:
                        wrl.remove_entity(len(wrl.entities) - 1)  # last
                        # M KEY - SPAWN ENTITY
                elif event.key == K_m:  # and wrl.player.god_mode:
                    ent = PlayerEntity(bounding_box=(0, 0, MAP_X, MAP_Y), name="Testificate")
                    wrl.spawn_entity(ent)
                    ent.coords = (wrl.player.coords[0], wrl.player.coords[1]-1)
                    # F5 KEY - SCREENSHOT (possibly bugged)
                elif event.key == K_F5:
                    screenshot()
                    #I KEY - INVENTORY
                elif event.key == K_i:
                    wantsInventory = True
                    display.blit(InvBack, InventoryBounds)
                    display.blit(Inventory, InventoryBounds)
        map_display.fill(Color(154, 198, 255, 0))
        py, px = wrl.player.coords
        for x in xrange(px - 26, px + 26):
            for y in xrange(py - 20, py + 20):
               if x in xrange(MAP_X) and y in xrange(MAP_Y):                   	
                map_display.blit(block.BLOCK_TEXTURES[wrl.level[x][y]], (x * 32, y * 32))
                
        debug_backing = pygame.Surface((175,53))
        debug_backing.set_alpha(64)
        debug_backing.fill(0x000000)
        debug_text_row_1 = "COORDS      %d, %d  " % (wrl.player.coords[0], wrl.player.coords[1])
        debug_text_row_2 = "FPS         %d      " % clk.get_fps()
        debug_text_row_3 = "BOUNDS      %d, %d  " % (xboundmax, yboundmax)
        debug_text_row_4 = "HEALTH      %d      " % (player_health)
        inventory_text = (" x %d" % wrl.player.inventory.get(wrl.player.current_block,
                                                             -1)) + " " + block.BLOCK_NAMES.get(
            block.BLOCK_INVENTORY[wrl.player.current_block], "unknown")
        def debug_out(out, x, y):
            debug_label = font.render(out, True, COLORS['white'])
            display.blit(debug_label, (x, y))
        inventory_label = font.render(inventory_text, True, COLORS['white'], COLORS['black'])
        display.blit(debug_backing, (0, 0))
        debug_out(debug_text_row_1, 0, 0)
        debug_out(debug_text_row_2, 0, 13)
        debug_out(debug_text_row_3, 0, 26)
        debug_out(debug_text_row_4, 0, 39)
        display.blit(block.BLOCK_TEXTURES[block.BLOCK_INVENTORY[wrl.player.current_block]], (0, 25 * TILESIZE + 5))
        display.blit(inventory_label, (32, MAP_Y * TILESIZE + 5))
        if block_under in block.BLOCK_DEADLY and not wrl.player.god_mode:
            player_health -= 0.20
            if player_health <= 0:
                game_over()
        if player_health <= 20.0:
            player_health += 0.05
        for ent in wrl.entities:
            ent.render(map_display, TILESIZE, TILESIZE)
        pygame.display.update()
        display.fill(0)
        if xboundmax <= 0:
            fx = (xboundmax * 32)
            if xboundmax < -23:
                fx = -736
        else:
            fx = 0
        if yboundmax <= 0 and yboundmax <= -8:
            fy = (yboundmax * 32)
        else:
            fy = 0
        display.blit(map_display, (fx, fy))
        display.fill(0x101010, (0, 600 - 48, 800, 600))
        display.blit(block.BLOCK_TEXTURES[block.BLOCK_INVENTORY[wrl.player.current_block]], (8, 600 - 40))
        display.blit(inventory_label, (40, 600 - 32))
        def exitInventoryError():
            print "You must press X to exit the inventory before preforming any other actions!"
        if wantsInventory:
            try:
                while 1:
                    for event in pygame.event.get():
                        if event.type == KEYDOWN:
                            if event.key == K_x:
                                raise CloseInventory
                            else: exitInventoryError()
            except CloseInventory: pass
            wantsInventory = False


pygame.init()
display = pygame.display.set_mode((800, 600))
map_display = pygame.Surface((MAP_X * 32, MAP_Y * 32))
pygame.display.set_caption("2DExplore")

wrl = world.World()
if os.path.isfile(SAVE_FILE):
    load(SAVE_FILE)
else:
    wrl.new_world(MAP_X, MAP_Y)

main_loop()
