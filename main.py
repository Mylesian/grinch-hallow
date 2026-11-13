import pygut
import pygut.base
import entity
import ui

class Game(pygut.Application):
    def __init__(self):
        super().__init__((400, 400), maximize=True)
        w = self.win.get_surface().width
        h = self.win.get_surface().height
        
        self.hud = ui.HUD()
        self.platforms = [entity.Platform((w/4, h-25), w/2, 50), entity.Platform((3*w/4, h-25), w/2, 50)]
        self.player = entity.Player(self.platforms[0])
        self.enemies = [entity.Enemy(self.platforms[1])]
        
        game_screen = pygut.base.Screen((50,50,50), [self.player, self.hud])
        
        for p in self.platforms:
            game_screen.add(p)
        for e in self.enemies:
            game_screen.add(e)
        
        self.set_screen(game_screen)
        
game = Game()
game.run()