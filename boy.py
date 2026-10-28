import time

from pico2d import (
    load_image,
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDLK_LEFT,
    SDLK_RIGHT,
    SDLK_a,
)
from transitions import Machine

class AutoRun:
    AUTO_RUN_SPEED = 10
    AUTO_RUN_SIZE = 150
    CANVAS_WIDTH = 800
    DURATION = 5

    def __init__(self, boy):
        self.boy = boy
        self.started_at = None

    def enter(self):
        self.started_at = time.monotonic()
        self.boy.frame = 0

    def update(self):
        boy = self.boy
        if time.monotonic() - self.started_at >= self.DURATION:
            boy.stop_auto_running()
            return

        boy.frame = (boy.frame + 1) % 8
        next_x = boy.x + boy.face_dir * self.AUTO_RUN_SPEED
        if next_x <= 0:
            boy.x = 0
            boy.face_dir = 1
        elif next_x >= self.CANVAS_WIDTH:
            boy.x = self.CANVAS_WIDTH
            boy.face_dir = -1
        else:
            boy.x = next_x

    def draw(self):
        boy = self.boy
        source_y = 100 if boy.face_dir == 1 else 0
        boy.image.clip_composite_draw(
            boy.frame * 100,
            source_y,
            100,
            100,
            0,
            '',
            boy.x,
            boy.y + (self.AUTO_RUN_SIZE - 100) / 2 - 5,
            self.AUTO_RUN_SIZE,
            self.AUTO_RUN_SIZE,
        )


class Boy:

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.auto_run = AutoRun(self)
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'AUTO_RUN'],
            initial='IDLE',
            auto_transitions=False,
        )
        self.machine.add_transition('start_running', 'IDLE', 'RUN')
        self.machine.add_transition('start_running', 'AUTO_RUN', 'RUN')
        self.machine.add_transition(
            'start_auto_running', 'IDLE', 'AUTO_RUN', after='start_auto_run'
        )
        self.machine.add_transition(
            'stop_auto_running', 'AUTO_RUN', 'IDLE', after='reset_idle_animation'
        )
        self.machine.add_transition(
            'stop_running', 'RUN', 'IDLE', after='reset_idle_animation'
        )

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if self.state == 'IDLE' and event.key == SDLK_a:
                self.start_auto_running()
            elif event.key in (SDLK_LEFT, SDLK_RIGHT):
                self.face_dir = -1 if event.key == SDLK_LEFT else 1
                if self.state in ('IDLE', 'AUTO_RUN'):
                    self.start_running()
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            if self.state == 'RUN':
                self.stop_running()

    def start_auto_run(self):
        self.auto_run.enter()

    def reset_idle_animation(self):
        self.frame = 0

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8
        elif self.state == 'RUN':
            self.frame = (self.frame + 1) % 8
            self.x = min(max(self.x + self.face_dir * 5, 50), 750)
        elif self.state == 'AUTO_RUN':
            self.auto_run.update()

    def draw(self):
        if self.state == 'IDLE':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
        elif self.state == 'RUN':
            source_y = 100 if self.face_dir == 1 else 0
            self.image.clip_draw(self.frame * 100, source_y, 100, 100, self.x, self.y)
        elif self.state == 'AUTO_RUN':
            self.auto_run.draw()
