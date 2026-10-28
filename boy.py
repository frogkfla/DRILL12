import math
import time

from pico2d import (
    load_image,
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDLK_LEFT,
    SDLK_RIGHT,
    SDLK_SPACE,
)
from transitions import Machine

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'SLEEP'],
            initial='IDLE',
            auto_transitions=False,
        )
        self.machine.add_transition('start_running', 'IDLE', 'RUN')
        self.machine.add_transition('start_running', 'SLEEP', 'RUN')
        self.machine.add_transition('stop_running', 'RUN', 'IDLE', after='reset_idle_timer')
        self.machine.add_transition('go_to_sleep', 'IDLE', 'SLEEP')
        self.machine.add_transition('wake_up', 'SLEEP', 'IDLE', after='reset_idle_timer')
        self.idle_started_at = time.monotonic()

    def handle_event(self, event):
        if self.state == 'SLEEP':
            if event.type == SDL_KEYDOWN:
                if event.key == SDLK_SPACE:
                    self.wake_up()
                elif event.key in (SDLK_LEFT, SDLK_RIGHT):
                    self.face_dir = -1 if event.key == SDLK_LEFT else 1
                    self.start_running()
            return

        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.face_dir = -1 if event.key == SDLK_LEFT else 1
            if self.state == 'IDLE':
                self.start_running()
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            if self.state == 'RUN':
                self.stop_running()

    def reset_idle_timer(self):
        self.idle_started_at = time.monotonic()
        self.frame = 0

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8
            if time.monotonic() - self.idle_started_at >= 5:
                self.go_to_sleep()
        elif self.state == 'RUN':
            self.frame = (self.frame + 1) % 8
            self.x = min(max(self.x + self.face_dir * 5, 50), 750)

    def draw(self):
        if self.state == 'IDLE':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
        elif self.state == 'RUN':
            source_y = 100 if self.face_dir == 1 else 0
            self.image.clip_draw(self.frame * 100, source_y, 100, 100, self.x, self.y)
        elif self.state == 'SLEEP':
            angle = math.pi / 2 if self.face_dir == 1 else -math.pi / 2
            source_y = 300 if self.face_dir == 1 else 200
            self.image.clip_composite_draw(
                0, source_y, 100, 100, angle, '', self.x, self.y - 30, 100, 100
            )