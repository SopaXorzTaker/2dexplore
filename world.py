import config

__author__ = 'mark'

import world_generator, block, player_entity


class World(object):
    def __init__(self):
        self.level = None
        self.entities = None
        self.player = None

    def get_entities(self):
        return self.entities

    def set_entities(self, entities):
        self.entities = entities

    def new_world(self, x_size, y_size):
        self.level = world_generator.WorldGenerator((x_size, y_size)).generate_world()
        self.entities = [player_entity.PlayerEntity()]
        self.player = self.entities[0]
        self.player.spawn_hook()
        self.player.inventory = {x: 0 for x in xrange(len(block.BLOCK_INVENTORY))}
        conf = config.get_config()
        self.player.name = conf["name"] if "name" in conf else ""

    def tick(self):
        
        level_x, level_y = self.get_level_size()
        for en in self.entities:
            en.tick()
        if self.player.god_mode:
            self.player.falling = False
        if self.player.falling:
            self.player.fall_delay += 1
        if self.player.jumping and self.player.falling:
            self.player.jumping = False

        checky = self.player.coords[0] + 1
        if checky <= level_y - 1 and self.level[self.player.coords[1]][checky] in block.BLOCK_NONSOLID:
            self.player.falling = True
        if self.player.fall_delay == 3:
            self.player.coords[0] += 1
            self.player.fall_delay = 0
            checky += 1
            if not (checky <= level_y - 1 and self.level[self.player.coords[1]][checky] in block.BLOCK_NONSOLID):
                self.player.falling = False
            self.player.jumping = False

        for x2 in range(level_x):
            for y2 in range(level_y):
                # Mechanics:
                # If the block is FLOWING, then put STATIONARY around it
                # Else if it's stationary, then do nothing, leaving it as-is.
                if self.level[x2][y2] == block.BLOCK_WATER_FLOWING:

                    if self.check_pos(x2 + 1, y2):
                        if self.get_block(x2 + 1, y2) == block.BLOCK_AIR:
                            self.set_block(x2 + 1, y2, block.BLOCK_WATER)

                    if self.check_pos(x2 - 1, y2):
                        if self.get_block(x2 - 1, y2) == block.BLOCK_AIR:
                            self.set_block(x2 - 1, y2, block.BLOCK_WATER)

                    if self.check_pos(x2, y2 + 1):
                        if self.get_block(x2, y2 + 1) == block.BLOCK_AIR:
                            self.set_block(x2, y2 + 1, block.BLOCK_WATER_FLOWING)

                if self.level[x2][y2] == block.BLOCK_LAVA_FLOWING:
                    if self.check_pos(x2 + 1, y2):
                        if self.get_block(x2 + 1, y2) == block.BLOCK_AIR:
                            self.set_block(x2 + 1, y2, block.BLOCK_LAVA)

                    if self.check_pos(x2 - 1, y2):
                        if self.get_block(x2 - 1, y2) == block.BLOCK_AIR:
                            self.set_block(x2 - 1, y2, block.BLOCK_LAVA)

                    if self.check_pos(x2, y2 + 1):
                        if self.get_block(x2, y2 + 1) == block.BLOCK_AIR:
                            self.set_block(x2, y2 + 1, block.BLOCK_LAVA_FLOWING)


    def destroy_block(self, blk_x, blk_y, add_inventory=True):
        blk = self.level[blk_x][blk_y]
        if (not blk in (block.BLOCK_INVENTORY + [block.BLOCK_WATER, block.BLOCK_LAVA])) and add_inventory:
            return

        self.level[blk_x][blk_y] = block.BLOCK_AIR
        if add_inventory:
            if blk == block.BLOCK_WATER:
                self.player.inventory[block.BLOCK_INVENTORY.index(block.BLOCK_WATER_FLOWING)] += 1
            elif blk == block.BLOCK_LAVA:
                self.player.inventory[block.BLOCK_INVENTORY.index(block.BLOCK_LAVA_FLOWING)] += 1
            else:
                self.player.inventory[block.BLOCK_INVENTORY.index(blk)] += 1

    def explode(self, exp_x, exp_y, exp_radius, add_inventory=False):
        import random

        for ex in range(exp_x - exp_radius, exp_x + exp_radius):
            for ey in range(exp_y - exp_radius, exp_y + exp_radius):
                if self.check_pos(ex, ey):
                    if (ey - exp_radius) > (exp_radius / 2):
                        if random.randint(0, 8) == 8:
                            self.destroy_block(ex, ey, add_inventory)
                    else:
                        self.destroy_block(ex, ey, add_inventory)


    def check_pos(self, pos_x, pos_y):
        levelx, levely = self.get_level_size()
        if 0 <= pos_x <= levelx - 1:
            if 0 <= pos_y <= levely - 1:
                # print "[DBG] check_pos(%d, %d) == True" % (pos_x, pos_y)
                return True
        # print "[DBG] check_pos(%d, %d) == False" % (pos_x, pos_y)
        return False


    def spawn_entity(self, ent):
        ent.spawn_hook()
        self.entities.append(ent)
        return self.entities.index(ent)


    def remove_entity(self, ent_id):
        self.entities[ent_id].removed_hook()
        self.entities.remove(self.entities[ent_id])

    def get_level_size(self):
        if not self.level:
            raise ValueError("Cannot get size of uninitialized level")
        return len(self.level), len(self.level[0])

    def set_block(self, x, y, blk):
        self.level[x][y] = blk

    def get_block(self, x, y):
        return self.level[x][y]
        

