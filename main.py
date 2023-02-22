import kivy
from kivy.app import App
from kivy.uix.image import Image
import sqlite3 as sl
import random
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import Clock
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager,Screen,WipeTransition
from kivy.properties import NumericProperty,StringProperty
from kivy.config import Config
Config.set('graphics', 'width', '2400')
Config.set('graphics', 'height', '1080')


class GameManager(ScreenManager):
    pass

class Pipe(Image):
     
    def __init__(self, **kwargs):
        super(Pipe, self).__init__(**kwargs)
        self.flag=0    #decide the pipeup or pipedown
        
    def on_pos(self,*args):
       
       if self.flag==0:
           #    pipe down
           self.ids.cap.pos= (self.x+self.width/2-self.ids.cap.width/2,self.y)
       else:
           self.ids.cap.pos= (self.x+self.width/2-self.ids.cap.width/2,self.y+self.height)
           #    pipe up 


class Bird(Image):
    
    def __init__(self, **kwargs):
        super(Bird, self).__init__(**kwargs)
        self.velocity = 630
        self.gravity = 1200#1200#820
        self.alive=True
        self.update_event=None
        self.flag=0

    def update_delay(self):
        self.update_event = Clock.schedule_interval(self.update,1/60)
        
    def  is_collide_pipe(self,pipe):
        if self.collide_widget(pipe):
            return False
            
    def is_collide_magic_bottle(self,bottle):
        if self.collide_widget(bottle):
            return True
    
    def update(self,dt):
        self.y += self.velocity *dt
        self.velocity -= self.gravity*dt
                    
    def on_touch_down(self,touch):
       
        if self.alive:
            if self.flag == 0:
                self.flag = 1
                self.update_delay()
                Clock.schedule_once(lambda dt:self.parent.manager.get_screen('screen2').start_move(),1)
            self.source = self.source.split('_')[0]+'_up.png'
            self.velocity = 630
            wing = SoundLoader.load('Audio/wing.wav')
            wing.volume = .1
            wing.play()
                    
    def on_touch_up(self,touch):
        if self.alive:
            self.source = self.source.split('_')[0]+'_down.png'
            #SoundLoader.load('Audio/swoosh.wav').play()
          
class magic(Image):
    pass

class Screen1(Screen):
    pass
    
class Coin(Widget):
    def __init__(self, **kwargs):
        super(Coin, self).__init__(**kwargs)
        anim = None
        
    def animate_coin(self):
        self.anim = Animation(pos=self.pos,d=.1)
        self.anim += Animation(pos=(self.x,self.y+500),opacity=1,d=.5)
        self.anim.start(self)
        self.anim.bind(on_complete=lambda x,y:self.remove())
        
    def remove(self):
        if self.parent:
            self.parent.remove_widget(self)
    
class Screen2(Screen):
    
    pipes =[]  
    move_pipe = None
    magic = ''
    bottle = None
    pipe_gap = 1000
    
    def on_enter(self,*args):        
        self.start1 = Clock.schedule_once(lambda x:self.start(),0)
        self.manager.get_screen('screen3').flag = 0
             
    def game_event(self):
        self.move_pipe =Clock.schedule_interval(self.move_pipes,1/60)
        
    def start(self):
        
        self.bird = Bird()
        self.bird.pos=0,self.center[1]  
        self.add_widget(self.bird)                  
        self.add_pipes(3)
   
    def   start_move(self):    
         self.game_event()
         
    def change_theme(self):
        color = self.bottle.source.split('/')[-1].split('.')[0] 
        self.pipe_theme = color
        anim = Animation(source='Images/bg/'+self.pipe_theme)
                
    def move_pipes(self,dt):
        self.p = None
        def sound():
            self.p=SoundLoader.load('Audio/points.wav')
            self.p.play()
        
        game_speed = 900#550 
        
        for pipe in self.pipes:
            pipe.x -= dt*game_speed
            
            if self.bird.is_collide_pipe(pipe):
                self.bird.update_event.cancel()
                self.game_over()
        
            if self.bottle:                 
                if  self.bird.is_collide_magic_bottle(self.bottle):
                    #SoundLoader.load('Audio/win.mp3').play()
                    self.bottle.opacity = 0
                    self.remove_widget(self.bottle)
                    self.change_theme()
                    self.move_pipe.cancel()
                    self.move_pipe = None
                    self.bottle = None                 
            
                    if self.move_pipe == None:
                        Clock.schedule_once(lambda x:self.game_event(),0)  
                                    
     
        if self.bird.y < 0 or self.bird.y > self.height:
            self.game_over()
            
        self.distance += dt*game_speed
      
        if self.distance >= self.v:
            self.v += self.pipe_gap
            self.points += 1
            coin = Coin()
            coin.pos= (self.parent.x+self.parent.width,self.parent.y+self.parent.height) 
            self.bird.add_widget(coin)
            coin.animate_coin()
            
            if self.points % 4==0 and self.points != 0:
               self.magic = 'magic_bottle'
             
            #Clock.schedule_once(lambda dt: sound(), .1)
                         
        if self.distance>=(self.pipe_gap*self.c):
           self.add_pipes(3,self.magic)
           self.magic =''
           self.flag = 0
           self.c +=3
           
        if self.distance>=(self.pipe_gap*self.c)+100: 
            for pipe in self.pipes:  
               self.remove_widget(pipe)

            
    def add_pipes(self,n,power=''):          

        for i in range(1,n+1):          
         
            pipeup= Pipe()
            pipeup.flag=1
            
            pipeup.height = self.ids.window.height/random.choice([2,2.5,3,3.5,4,4.5])       
             
            pipeup.pos= self.ids.window.pos[0]+i*self.pipe_gap,self.ids.window.pos[1]
            
            if power == 'magic_bottle':
                self.bottle = magic()
                if 0<self.points <=10:
                    self.bottle.source = 'Images/portions/pink.png'
                elif 10< self.points <20:
                     self.bottle.source = 'Images/portions/orange.png'
                elif 20 <= self.points <= 30:
                     self.bottle.source = 'Images/portions/brown.png'
                else: 
                     self.bottle.source = 'Images/portions/%s.png'%random.choice(['pink','orange','brown'])                      
                self.bottle.size=self.bird.width+100,self.bird.height+100
                pipeup.add_widget(self.bottle)
                power = ''              
            
            pipedown = Pipe()           
            pipeup.flag=1
             
            pipedown.height = self.ids.window.height-(self.bird.height*3)-pipeup.height
            
            pipedown.ids.cap.pos=(self.x-30,self.y+self.height)
            pipedown.pos= self.ids.window.pos[0]+i*self.pipe_gap,self.ids.window.pos[1]+self.ids.window.height-pipedown.height
            
            self.pipes.append(pipeup)
            self.pipes.append(pipedown)
            
            self.add_widget(pipeup)                
            self.add_widget(pipedown)
            
    def game_over(self):
        
        SoundLoader.load('Audio/hit.wav').play()
        SoundLoader.load('Audio/die.ogg').play()
        
        if self.move_pipe:
            self.move_pipe.cancel()
            
        self.bird.update_event.cancel()      
        
        self.bird.alive = False  
        self.bird.source = self.bird.source.split('_')[0]+'_dead.png'
        
        self.govr = Image(source='Images/gameover.png',size_hint=(.7,.7),pos_hint={'center_x':.5,'center_y':.5})
        
        self.add_widget(self.govr)
        
        Clock.schedule_once(lambda dt:self.score_board(),1)
    
    def reset(self):
        
        for pipe in self.pipes:  
            self.remove_widget(pipe)
            
        self.pipes = []    
        self.distance =0
        self.remove_widget(self.govr)
        self.remove_widget(self.bird)
        self.pipe_theme = 'brown'
        self.c =3
        self.v =self.pipe_gap
        
        self.manager.get_screen('screen3').score = self.points
        
        con = sl.connect('main.db')
        cur = con.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS INFO(id char(5),
        points int
        );
    """)
    
        if self.points >= cur.execute("Select * from INFO").fetchone()[-1] :
            con.execute(""" UPDATE  INFO SET points = %d WHERE id='best_score' """%self.points)
            self.manager.get_screen('screen3').best_score = self.points
        else:
           self.manager.get_screen('screen3').best_score = int(cur.execute('''select points from INFO where id = 'best_score' ''').fetchone()[-1])
                     
        self.points = 0
        con.commit()  
        con.close()  
        
    def score_board(self):
        
        self.manager.transition = WipeTransition(duration=.8)
        self.manager.transition.direction = 'left'
        self.manager.current = 'screen3'
        self.reset()
        
class Screen3(Screen):
         
        flag =0
        def on_touch_down(self,touch):
            if self.flag == 0:
                Clock.schedule_once(lambda dt:self.go_home(),.5)
                self.flag = 1
     
        def go_home(self):        
            self.manager.transition = WipeTransition(duration=.5)
            self.manager.transition.direction = 'left'
            self.manager.current = 'screen1'
                                
class main(App):
    
    def build(self):
        return GameManager()
         
if __name__=='__main__':
    main().run()