import pyxel

GAME_TITLE="Space Resceu"

SHIP_ACCEL_X=0.06
SHIP_ACCEL_UP=0.04
SHIP_ACCEL_DOWN=0.02
MAX_SHIP_SPEED=0.8
OBJECT_SPAWN_INTERVAL=150


class OneKeyGame:
    def __init__(self):
        pyxel.init(160,120,title=GAME_TITLE)

        pyxel.load("my_first_game.pyxres")

        self.is_titile=True
        self.reset_game()

        pyxel.run(self.update,self.draw)

    def reset_game(self):
        self.score=0

        self.timer=0

        self.ship_x=(pyxel.width-8)/2
        self.ship_y=pyxel.height/4
        self.ship_vx=0
        self.ship_vy=0
        self.ship_dir=1
        self.is_jetting=False
        self.is_exploding=False

        self.survivors=[]
        self.meteors=[]

    def update(self):
        pass

    def draw_sky(self):
        num_grads=4
        grad_height=6
        grad_start_y=pyxel.height-grad_height*num_grads

        pyxel.cls(0)
        for i in range(num_grads):
            pyxel.dither((i+1)/num_grads)
            pyxel.rect(
                0,
                grad_start_y+i*grad_height,
                pyxel.width,
                grad_height,
                1,
            )
        pyxel.dither(1)


    def draw_ship(self):
        pyxel.blt(
            self.ship_x,
            self.ship_y,
            0,
            8,
            0,
            8,
            8,
            0,
        )

    def draw(self):
        self.draw_sky()
        self.draw_ship()


OneKeyGame()