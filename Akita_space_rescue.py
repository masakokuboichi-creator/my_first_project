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

        self.is_title=True
        self.reset_game()

        pyxel.run(self.update,self.draw)

    def reset_game(self):
        self.score=0

        self.timer=0

        self.explode_timer = 0
        
        self.life = 3

        self.ship_x=(pyxel.width-8)/2
        self.ship_y=pyxel.height/4
        self.ship_vx=0
        self.ship_vy=0
        self.ship_dir=1
        self.is_jetting=False
        self.is_exploding=False

        self.survivors=[]
        self.meteors=[]

        self.items = []
        self.invincible_timer = 0
        
    def add_item(self):
        x = pyxel.rndi(0, pyxel.width - 16)
        y = pyxel.rndi(0, pyxel.height - 16)
        self.items.append((x, y))

    def generate_distanced_pos(self,dist):
        while True:
            x=pyxel.rndi(0,pyxel.width-8)
            y=pyxel.rndi(0,pyxel.height-8)
            diff_x=x-self.ship_x
            diff_y=y-self.ship_y
            if diff_x**2+diff_y**2>dist**2:
                return(x,y)
            
    def add_survivor(self):
        survivor_pos=self.generate_distanced_pos(30)
        self.survivors.append(survivor_pos)

    def add_meteor(self):
        meteor_pos=self.generate_distanced_pos(60)
        self.meteors.append(meteor_pos)

    def update_ship(self):
        if pyxel.btn(pyxel.KEY_SPACE):
            self.is_jetting=True
            self.ship_vy=max(self.ship_vy-SHIP_ACCEL_UP,-MAX_SHIP_SPEED)
            self.ship_vx=max(
                min(self.ship_vx+self.ship_dir*SHIP_ACCEL_X,1),-MAX_SHIP_SPEED
            )
            self.play_jet_sound()
        else:
            self.is_jetting=False
            self.ship_vy=min(self.ship_vy+SHIP_ACCEL_DOWN,MAX_SHIP_SPEED)

        if pyxel.btnr(pyxel.KEY_SPACE):
            self.ship_dir=-self.ship_dir

        self.ship_x+=self.ship_vx
        self.ship_y+=self.ship_vy

        if self.ship_x<0:
            self.ship_x=0
            self.ship_vx=abs(self.ship_vx)
            self.play_bounce_sound()

        max_ship_x=pyxel.width-8
        if self.ship_x>max_ship_x:
            self.ship_x=max_ship_x
            self.ship_vx=-abs(self.ship_vx)
            self.play_bounce_sound()

        if self.ship_y<0:
            self.ship_y=0
            self.ship_vy=abs(self.ship_vy)
            self.play_bounce_sound()

        max_ship_y=pyxel.height-8
        if self.ship_y>max_ship_y:
            self.ship_y=max_ship_y
            self.ship_vy=-abs(self.ship_vy)
            self.play_bounce_sound()

    def add_objects(self):
        if self.timer==0:
            self.add_survivor()
            self.add_meteor()
            self.timer=OBJECT_SPAWN_INTERVAL
        else:
            self.timer-=1

    def check_ship_collisions(self,x,y):
        return abs(self.ship_x-x)<=5 and abs(self.ship_y-y)<=5
    
    def handle_survivor_collisions(self):
        new_survivors=[]
        for survivor_x,survivor_y in self.survivors:
            if self.check_ship_collisions(survivor_x,survivor_y):
                self.score+=1
                self.play_collect_survivor_sound()
            else:
                new_survivors.append((survivor_x,survivor_y))
        self.survivors=new_survivors

    def handle_meteor_collisions(self):
        if self.is_exploding:
            return
        if self.invincible_timer > 0:
            return

        new_meteors = []
        for meteor_x, meteor_y in self.meteors:
            if self.check_ship_collisions(meteor_x, meteor_y):
                self.is_exploding = True
                self.explode_timer = 60
                self.life -= 1
                self.play_explosion_sound()

                if self.life <= 0:
                    self.big_explosion = True
                    self.explode_timer = 90
                else:
                    self.big_explosion = False

                break
            else:
                new_meteors.append((meteor_x, meteor_y))

        self.meteors = new_meteors

    def handle_item_collisions(self):
        new_items = []
        for item_x, item_y in self.items:
            if abs(self.ship_x - item_x) < 8 and abs(self.ship_y - item_y) < 8:
                self.invincible_timer = 180
                self.play_invincible_item_sound()
                self.invincible_just_started = True
            else:
                new_items.append((item_x, item_y))
        self.items = new_items

    def update(self):
        if self.is_title:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.is_title=False
                self.reset_game()
                return
        
        if self.is_exploding:
            self.explode_timer -= 1
            if self.explode_timer <= 0:
                self.is_exploding = False
                if self.life <= 0:
                    self.is_title = True
            return

        self.update_ship()
        self.add_objects()
        self.handle_survivor_collisions()
        self.handle_item_collisions()
       
        if pyxel.frame_count % 600 == 0:
            self.add_item()

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        self.handle_meteor_collisions()

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
        offset_y=(pyxel.frame_count%3+2)if self.is_jetting else 0
        offset_x=offset_y*-self.ship_dir

        pyxel.blt(
            self.ship_x-self.ship_dir*3+offset_x,
            self.ship_y,
            0,
            0,
            0,
            8*self.ship_dir,
            8,
            0,
        )

        pyxel.blt(
            self.ship_x,
            self.ship_y+3+offset_y,
            0,
            8,
            8,
            8,
            8,
            0,
        )

        pyxel.blt(self.ship_x,self.ship_y,0,8,0,8,8,0)

        if self.is_exploding:
            num_particles = 30 if getattr(self, "big_explosion", False) else 10
            for _ in range(num_particles):
                blast_x = self.ship_x + pyxel.rndi(-10, 10)
                blast_y = self.ship_y + pyxel.rndi(-10, 10)
                blast_radius = pyxel.rndi(2, 6 if getattr(self, "big_explosion", False) else 4)
                blast_color = pyxel.rndi(7, 12)
                pyxel.circ(blast_x, blast_y, blast_radius, blast_color)

        if self.invincible_timer > 0:
            if pyxel.frame_count % 6 < 3:
                color = 7 if pyxel.frame_count % 12 < 6 else 10
                pyxel.circ(self.ship_x + 4, self.ship_y + 4, 8, color)
                pyxel.circ(self.ship_x + 4, self.ship_y + 4, 6, 0)
  
    def draw_items(self):
        for item_x, item_y in self.items:
            pyxel.blt(item_x, item_y, 0, 32, 0, 16, 16, 0)

    def draw_survivors(self):
        for survivor_x,survivor_y in self.survivors:
            pyxel.blt(survivor_x,survivor_y,0,16,0,8,8,0)

    def draw_meteors(self):
        for meteor_x,meteor_y in self.meteors:
            pyxel.blt(meteor_x,meteor_y,0,24,0,8,8,0)
    
    def draw_score(self):
        score=F"SCORE:{self.score}"
        for i in range(1,-1,-1):
            color=7 if i ==0 else 0
            pyxel.text(3+i,3,score,color)
    
    def draw_life(self):
        life_text = f"LIFE: {self.life}"
        pyxel.text(3, 12, life_text, 8)

    def draw_title(self):
        for i in range(1,-1,-1):
            color=10 if i ==0 else 8
            pyxel.text(57,50+i,GAME_TITLE,color)
            pyxel.text(42,70,"- Press Enter Key -",3)
   
        if self.life == 0:
            pyxel.text(60, 90, "GAME OVER", 8)

    def draw(self):
        self.draw_sky()
        self.draw_ship()
        self.draw_survivors()
        self.draw_items()
        self.draw_meteors()
        self.draw_score()
        self.draw_life()

        if self.is_title:
            self.draw_title()

    def play_jet_sound(self):
        if pyxel.frame_count % 5 == 0:
            pyxel.play(0, 0)

    def play_bounce_sound(self):
        pyxel.play(0, 1)

    def play_collect_survivor_sound(self):
        pyxel.play(1, 2)

    def play_explosion_sound(self):
        pyxel.play(1, 3)

    def play_invincible_item_sound(self):
        pyxel.play(1, 4)


OneKeyGame()