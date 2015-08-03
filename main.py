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

just_started = True

block.load_textures()  # ...

SAVE_FILE = "explore_save.gz"
TILESIZE = 32
MAP_X = 48
MAP_Y = 48
screen = pygame.display.set_mode((800, 800))
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
    global display, start_time, fall_delay, map_display, block_above, block_under, block_index, wrl, xs, ys,\
        just_started
    ys = 0
    xs = 0
    font = pygame.font.SysFont("UbuntuMono", 13)  # Fonts should be inited after pygame.init()
    start_time = 0
    clk = pygame.time.Clock()
    if wrl.player.coords[1] < 12:
        xboundmax=(wrl.player.coords[1] + 12)
    else:
        xboundmax=((wrl.player.coords[1]-(wrl.player.coords[1]*2))+12)
    xboundmin=0
    if wrl.player.coords[1] < 8:
        yboundmax=(wrl.player.coords[0])
    else:
        yboundmax=((wrl.player.coords[0]-(wrl.player.coords[0]*2))+8)
    yboundmin=0
    while True:
        has_displayed=0
        if wrl.player.coords[1] < 12:
            xboundmax=(wrl.player.coords[1] + 12)
        else:
            xboundmax=((wrl.player.coords[1]-(wrl.player.coords[1]*2))+12)
        xboundmin=0
        if wrl.player.coords[0] < 8:
             yboundmax=(wrl.player.coords[0] + 8)
        else:
            yboundmax=((wrl.player.coords[0]-(wrl.player.coords[0]*2))+8)
        yboundmin=0

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
                    if not wrl.level[wrl.player.coords[1]][wrl.player.coords[0]] in block.BLOCK_NONSOLID and not keys[K_LSHIFT]:
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
                    xboundmax, xboundmin, yboundmax, yboundmin = 0, 0, -10, 0
                    wrl.new_world(MAP_X, MAP_Y)
                      # F1 KEY - GODMODE
                elif event.key == K_F1:
                    wrl.player.god_mode = not wrl.player.god_mode
                    # E KEY - EXPLODE
                elif event.key == K_e and wrl.player.god_mode:
                    wrl.explode(px, py, 5, False)
                    # N KEY - DESPAWN ENTITY
                elif event.key == K_n: #and wrl.player.god_mode:
                    if len(wrl.entities) > 1:
                        wrl.remove_entity(len(wrl.entities) - 1)  # last
                        # M KEY - SPAWN ENTITY
                elif event.key == K_m: #and wrl.player.god_mode:
                    ent = PlayerEntity(bounding_box=(0, 0, MAP_X, MAP_Y), name="Testificate")
                    wrl.spawn_entity(ent)
                    ent.coords = wrl.player.coords
                    # F5 KEY - SCREENSHOT (possibly bugged)
                elif event.key == K_F5:
                    screenshot()

        map_display.fill(Color(154, 198, 255, 0))
        for x in range(MAP_X):
            for y in range(MAP_Y):
                map_display.blit(block.BLOCK_TEXTURES[wrl.level[x][y]], (x * 32, y * 32))

        debug_text = "Coords: %d, %d   %d fps, block: " % (
            wrl.player.coords[0], wrl.player.coords[1], clk.get_fps()) + "**%d, %d**" % (xboundmax, yboundmax)
        inventory_text = (" x %d" % wrl.player.inventory.get(wrl.player.current_block,
                                                             -1)) + " " + block.BLOCK_NAMES.get(
             block.BLOCK_INVENTORY[wrl.player.current_block], "unknown")
        debug_label = font.render(debug_text, True, COLORS['white'], COLORS['black'])
        inventory_label = font.render(inventory_text, True, COLORS['white'], COLORS['black'])
        display.blit(debug_label, (0, 0))
        display.blit(block.BLOCK_TEXTURES[block.BLOCK_INVENTORY[wrl.player.current_block]], (0, 25 * TILESIZE + 5))
        display.blit(inventory_label, (32, MAP_Y * TILESIZE + 5))
        if block_under in block.BLOCK_DEADLY and not wrl.player.god_mode:
            game_over()
        for ent in wrl.entities:
            ent.render(map_display, TILESIZE, TILESIZE)
        pygame.display.update()
        display.fill(0)
        if xboundmax <= 0 and xboundmax <= -12:
            fx=(xboundmax*32)
            has_displayed=1 
            if xboundmax < -23: fx = -736
        else: fx = 0
        if yboundmax <= 0 and yboundmax <= -8:
            fy=(yboundmax*32)
        else: fy = 0
        display.blit(map_display, (fx, fy))
        display.fill(0x101010, (0, 600 - 48, 800, 600))
        display.blit(block.BLOCK_TEXTURES[block.BLOCK_INVENTORY[wrl.player.current_block]], (8, 600 - 40))
        display.blit(inventory_label, (40, 600 - 32))


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
