import pygame
from entity import GenericEntity
from PIL import Image

__author__ = 'mark'
player = Image.open('textures/player.png')
player_flipped = Image.open('textures/player2.png')


class PlayerEntity(GenericEntity):
    _WALK_TEXTURES = [player_flipped, player]
    walk_dir = 0

    def __init__(self, texture=None, bounding_box=None, name=None):
        self.falling, self.fall_delay, self.jumping, self.god_mode = False, 0, False, False
        self.inventory = {}
        self.current_block = 0
        GenericEntity.__init__(self, player.tobytes() if not texture else texture,
                               bounding_box, name)

    def render(self, surface, tile_x, tile_y):
        nametag_font = pygame.font.SysFont("UbuntuMono", 13)
        if self.alive:
            if self.name:
                nametag = nametag_font.render(self.name, True, (255, 255, 255), (63, 63, 63))
                surface.blit(nametag, ((self.coords[1] * tile_x) - 32, (self.coords[0] * tile_y) - 16))
            surface.blit(pygame.image.fromstring(self._WALK_TEXTURES[self.walk_dir].tobytes(), (32, 32), "RGBA"),
                         (self.coords[1] * tile_x, self.coords[0] * tile_y))

    def removed_hook(self):
        GenericEntity.removed_hook(self)

    def spawn_hook(self):
        GenericEntity.spawn_hook(self)

    def tick(self):
        pass

    def set_inventory(self, inventory):
        self.inventory = inventory

    def get_inventory(self):
        return self.inventory

    def set_walk(self, walk_dir):
        self.walk_dir = walk_dir
