import random
import pygame
import sys


class BirdBrain:
    def __init__(self, maingame):
        self.dist_x = 0
        self.dist_y = 0
        self.game = maingame
        self.i = 0

    def update_info(self):
        bird_x = self.game.player.pos.x
        bird_y = self.game.player.pos.y
        closest_wall = 1000
        closest_wall_y = 0
        for i in self.game.walls:
            closest_wall_y = max(i.pos.y, closest_wall_y)
            closest_wall = min(i.pos.x, closest_wall)
        self.dist_x = closest_wall - bird_x
        self.dist_y = closest_wall_y - bird_y

    def do_jump(self):
        self.update_info()
        if self.dist_y < 0:
            return True
        return False

class Game:
    def __init__(self):
        self.fps = 60
        self.vec = pygame.math.Vector2
        pygame.init()
        pygame.display.init()
        pygame.mixer.init()
        self.width, self.height = 144 * 3, 206 * 3
        self.playSurface = pygame.display.set_mode([self.width, self.height])
        pygame.display.set_caption('Flappy AI')
        self.SpriteSheeet = pygame.image.load('Flappy_Bird_Spritesheet.png').convert()
        self.Green = [0, 255, 0]
        self.Red = [255, 0, 0]
        self.Black = [0, 0, 0]
        self.White = [255, 255, 255]

    def new(self):
        self.walls = pygame.sprite.Group()
        self.Clock = pygame.time.Clock()
        self.fpsController = pygame.time.Clock()
        self.stop = False
        self.score = 0
        self.all_sprites = pygame.sprite.Group()
        self.player = Bird(self)
        self.all_sprites.add(self.player)
        self.walls_upper = walls_upper(self)
        self.walls.add(self.walls_upper)
        self.walls_lower = walls_lower(self, self.walls_upper.y_level)
        self.walls.add(self.walls_lower)
        self.ground = Floor(self)
        self.all_sprites.add(self.ground)
        self.image = pygame.Surface([self.width, self.height])
        self.update_count = 0
        self.run()

    def run(self):
        self.stop = False
        self.update()

    def update(self):
        self.playSurface.fill(self.Black)
        while not self.stop:
            self.Clock.tick(self.fps)
            if pygame.sprite.collide_mask(self.player, self.walls_lower) or pygame.sprite.collide_mask(self.player,
                                                                                                       self.walls_upper):
                self.player.death()
            if self.player.brain.do_jump():
                self.player.jump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop = True
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    if event.key == pygame.K_EQUALS:
                        self.fps += 10
                    if event.key == pygame.K_MINUS:
                        self.fps -= 10
            self.all_sprites.update()
            if self.update_count != 280:
                self.update_count += 1
            else:
                self.update_count = 0
                self.walls_upper = walls_upper(self)
                self.walls.add(self.walls_upper)
                self.walls_lower = walls_lower(self, self.walls_upper.y_level)
                self.walls.add(self.walls_lower)
            self.walls.update()
            self.draw()

    def draw(self):
        self.image.blit(self.SpriteSheeet, (0, 0), (0, 50, 144, 600))
        self.playSurface.blit(pygame.transform.scale(self.image, (144 * 9, 206 * 9)), (0, 0))
        self.walls.draw(self.playSurface)
        self.all_sprites.draw(self.playSurface)
        pygame.display.update()


class Floor(pygame.sprite.Sprite):
    def __init__(self, game):
        self.vec = pygame.Vector2
        pygame.sprite.Sprite.__init__(self)
        self.x = 108
        self.game = game
        self.image = pygame.Surface([self.game.width * 2, 56 * 2])
        self.rect = self.image.get_rect()
        self.rect.center = (self.game.width, 56)
        self.ground = pygame.Surface([168, 56])
        self.ground.set_colorkey((255, 255, 255))
        self.ground.blit(self.game.SpriteSheeet, (0, 0), (292, 0, 168, 56))

    def update(self):
        self.rel_x = self.x % self.game.width
        self.image.blit(pygame.transform.scale(self.ground, (self.game.width * 2, 56 * 2)), (0, 0))
        self.pos = self.vec(self.rel_x, self.game.height)
        self.rect.midbottom = self.pos
        self.x -= 1.5


class Bird(pygame.sprite.Sprite):
    def __init__(self, game):
        self.mainstuff = game
        self.vec = pygame.Vector2
        self.all_sprite = self.mainstuff.all_sprites
        self.bird = pygame.Surface((20, 15))
        self.image = pygame.Surface((20 * 3, 15 * 3))
        self.rect = self.image.get_rect()
        pygame.sprite.Sprite.__init__(self)
        self.rect.center = (self.mainstuff.width / 4, self.mainstuff.height / 2)
        self.pos = self.vec(self.mainstuff.width / 4, self.mainstuff.height / 2)
        self.vel = self.vec(0, 0)
        self.bird_image = [(0, 490, 20, 15), (28, 490, 20, 15), (56, 490, 20, 25)]
        self.foo = 1
        self.foo2 = 0
        self.angle = 0
        self.brain = BirdBrain(game)

    def jump(self):
        self.vel.y = -5

    def update(self):
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        self.bird.blit(self.mainstuff.SpriteSheeet, (0, 0), (self.bird_image[self.foo]))
        self.bird.set_colorkey((255, 255, 255))
        self.acc = self.vec(0, 0.2)
        if self.rect.midtop[1] <= 0:
            self.vel.y = 0
            self.pos.y = 48
        elif not self.pos.y > 512:
            self.vel.y += self.acc.y
            self.pos.y += self.vel.y + 0.2 * self.acc.y
        else:
            self.death()

        self.rect.midbottom = self.pos
        self.image.blit(pygame.transform.scale(self.bird, (20 * 3, 15 * 3)), (0, 0))
        pygame.mask.from_surface(self.image)
        if self.foo2 != 15:
            self.foo2 += 1
        else:
            self.foo = self.foo + 1 if self.foo < 2 else 0
            self.foo2 = 0

    def death(self):
        maingame.stop = True





class WallsBasic(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.y_level = random.randint(50, 350)
        self.vec = pygame.Vector2
        self.pipe = pygame.Surface((26, 160))
        self.image = pygame.Surface((26 * 3, 160 * 3))
        self.game = game
        self.all_sprites = game.all_sprites
        self.rect = self.image.get_rect()

    def update_walls(self):
        self.image.set_colorkey((0, 0, 0))

        self.pipe.blit(self.game.SpriteSheeet, (0, 0), self.area)
        self.pipe.set_colorkey((255, 255, 255))
        self.image.blit(pygame.transform.scale(self.pipe, (26 * 3, 160 * 3)), (0, 0))
        self.pos.x -= 1.5

class walls_lower(WallsBasic):
    def __init__(self, game, y_level):
        level = 110
        super(walls_lower, self).__init__(game)
        self.rect.midtop = self.vec(game.width + 50, y_level + level)
        self.pos = self.vec(game.width + 50, y_level + level)
        self.area =(84, 323, 26, 160)

    def update(self):
        self.update_walls()
        self.rect.midtop = self.pos
        pygame.mask.from_surface(self.image)
        if self.pos.x < -40:
            pygame.sprite.Sprite.kill(self)

class walls_upper(WallsBasic):

    def __init__(self, game):
        super(walls_upper, self).__init__(game)
        self.rect.midbottom = self.vec(game.width + 50, self.y_level)
        self.pos = self.vec(game.width + 50, self.y_level)
        self.area = (56, 323, 26, 160)

    def update(self):
        self.update_walls()
        self.rect.midbottom = self.pos
        pygame.mask.from_surface(self.image)
        if self.pos.x < -40:
            pygame.sprite.Sprite.kill(self)
        elif self.pos.x == 9.5:
            self.game.score += 1
            print(self.game.score)


if __name__ == '__main__':
    oof = False
    maingame = Game()
    while not oof:
        maingame.new()
