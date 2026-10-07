import math
import random
from array import array

import pygame
from game.color_button import ColorButton

# Playback timing (milliseconds)
BASE_FLASH_DURATION = 450
BASE_PAUSE_DURATION = 200
MIN_FLASH_DURATION = 150
MIN_PAUSE_DURATION = 80

# How much faster playback gets for each successful round
FLASH_SPEEDUP_PER_ROUND = 25
PAUSE_SPEEDUP_PER_ROUND = 10

# Player turn timer (milliseconds)
# Time limit = BASE + PER_STEP * (number of steps in the sequence)
TURN_TIME_BASE_MS = 2000
TURN_TIME_PER_STEP_MS = 800

# Timer bar appearance
TIMER_BAR_WIDTH = 300
TIMER_BAR_HEIGHT = 16
TIMER_BAR_Y = 460
TIMER_COLOR_OK = (50, 255, 90)
TIMER_COLOR_WARN = (255, 235, 40)
TIMER_COLOR_DANGER = (255, 50, 50)
TIMER_WARN_FRACTION = 0.5     # below this fraction of time left, bar turns yellow
TIMER_DANGER_FRACTION = 0.25  # below this fraction of time left, bar turns red

# Reasons the game can end
REASON_WRONG = "WRONG"
REASON_TIMEOUT = "TIMEOUT"

# Audio settings
SAMPLE_RATE = 44100
TONE_VOLUME = 0.3            # 0.0 - 1.0 of full scale
TONE_LOOP_SECONDS = 0.5      # approximate length of the looped tone buffer
TONE_FADE_IN_MS = 10         # softens the start of a tone to avoid clicks
TONE_FADE_OUT_MS = 40        # softens the end of a tone to avoid clicks

# One pitch per pad, in Hz: a C major arpeggio (C4, E4, G4, C5)
PAD_FREQUENCIES = [
    261.63,  # Red
    329.63,  # Blue
    392.00,  # Green
    523.25,  # Yellow
]


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        pad_size = 130
        gap = 24
        start_x = width // 2 - pad_size - (gap // 2)
        start_y = 150

        self.buttons = [
            ColorButton(0, pygame.Rect(start_x, start_y, pad_size, pad_size), (110, 20, 20), (255, 50, 50)),                      # Red
            ColorButton(1, pygame.Rect(start_x + pad_size + gap, start_y, pad_size, pad_size), (15, 60, 150), (40, 170, 255)),   # Blue
            ColorButton(2, pygame.Rect(start_x, start_y + pad_size + gap, pad_size, pad_size), (15, 100, 30), (50, 255, 90)),    # Green
            ColorButton(3, pygame.Rect(start_x + pad_size + gap, start_y + pad_size + gap, pad_size, pad_size), (140, 110, 10), (255, 235, 40)), # Yellow
        ]

        self.sequence = []
        self.player_input = []
        self.score = 0

        self.state = "WATCH"
        self.showing_step = 0
        self.step_start_time = 0
        self.flash_duration = BASE_FLASH_DURATION
        self.pause_duration = BASE_PAUSE_DURATION
        self.is_flashing = False

        self.player_lit_button = None
        self.player_lit_start = 0
        self.player_flash_duration = 150

        # Player turn timer
        self.turn_start_time = 0
        self.turn_time_limit = TURN_TIME_BASE_MS
        self.game_over_reason = REASON_WRONG

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_medium = pygame.font.SysFont(None, 28)

        self.sound_enabled = False
        self.tones = []
        self.init_audio()

        self.start_next_round()

    # ------------------------------------------------------------------
    # Audio
    # ------------------------------------------------------------------
    def init_audio(self):
        """Set up the mixer and build one tone per pad. Fails silently."""
        try:
            # pygame.init() may have already opened the mixer with other
            # settings (or failed to open it), so (re)open it ourselves.
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)

            settings = pygame.mixer.get_init()
            if settings is None:
                return
            rate, fmt, channels = settings

            # The tone generator writes signed 16-bit samples only.
            if fmt != -16:
                pygame.mixer.quit()
                return

            self.tones = [self.build_tone(freq, rate, channels) for freq in PAD_FREQUENCIES]
            self.sound_enabled = True
        except (pygame.error, NotImplementedError, OSError):
            # No audio device or driver: run the game without sound.
            self.sound_enabled = False
            self.tones = []

    def build_tone(self, frequency, rate, channels):
        """Create a loopable sine-wave Sound for the given frequency."""
        # Use a whole number of cycles so the loop point is seamless.
        cycles = max(1, round(frequency * TONE_LOOP_SECONDS))
        num_samples = round(cycles * rate / frequency)
        amplitude = int(32767 * TONE_VOLUME)

        samples = array("h")
        for i in range(num_samples):
            value = int(amplitude * math.sin(2 * math.pi * cycles * i / num_samples))
            for _ in range(channels):
                samples.append(value)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def start_tone(self, color_id):
        if not self.sound_enabled:
            return
        try:
            self.tones[color_id].play(loops=-1, fade_ms=TONE_FADE_IN_MS)
        except pygame.error:
            self.sound_enabled = False

    def stop_tone(self, color_id):
        if not self.sound_enabled:
            return
        try:
            self.tones[color_id].fadeout(TONE_FADE_OUT_MS)
        except pygame.error:
            self.sound_enabled = False

    def stop_all_tones(self):
        for color_id in range(len(self.tones)):
            self.stop_tone(color_id)

    # ------------------------------------------------------------------
    # Game logic
    # ------------------------------------------------------------------
    def update_playback_speed(self):
        """Shorten flash and pause durations as the score grows, down to a floor."""
        self.flash_duration = max(
            MIN_FLASH_DURATION,
            BASE_FLASH_DURATION - self.score * FLASH_SPEEDUP_PER_ROUND,
        )
        self.pause_duration = max(
            MIN_PAUSE_DURATION,
            BASE_PAUSE_DURATION - self.score * PAUSE_SPEEDUP_PER_ROUND,
        )

    def start_player_turn(self, now):
        """Switch to the player's turn and start the countdown."""
        self.state = "PLAYER_TURN"
        self.turn_start_time = now
        self.turn_time_limit = TURN_TIME_BASE_MS + TURN_TIME_PER_STEP_MS * len(self.sequence)

    def get_time_left_fraction(self):
        """Fraction of the turn time still remaining, from 1.0 down to 0.0."""
        elapsed = pygame.time.get_ticks() - self.turn_start_time
        remaining = self.turn_time_limit - elapsed
        return max(0.0, min(1.0, remaining / self.turn_time_limit))

    def start_next_round(self):
        new_color = random.randint(0, 3)

        # Append exactly one new step to the existing sequence
        self.sequence.append(new_color)

        self.update_playback_speed()

        self.player_input.clear()
        self.state = "WATCH"
        self.showing_step = 0
        self.step_start_time = pygame.time.get_ticks()
        self.is_flashing = True
        self.buttons[self.sequence[0]].is_lit = True
        self.start_tone(self.sequence[0])

    def update(self):
        now = pygame.time.get_ticks()

        if self.player_lit_button is not None:
            if now - self.player_lit_start >= self.player_flash_duration:
                self.player_lit_button.is_lit = False
                self.stop_tone(self.player_lit_button.color_id)
                self.player_lit_button = None

        if self.state == "WATCH":
            current_btn_id = self.sequence[self.showing_step]

            if self.is_flashing:
                if now - self.step_start_time >= self.flash_duration:
                    self.buttons[current_btn_id].is_lit = False
                    self.stop_tone(current_btn_id)
                    self.is_flashing = False
                    self.step_start_time = now
            else:
                if now - self.step_start_time >= self.pause_duration:
                    self.showing_step += 1
                    if self.showing_step < len(self.sequence):
                        next_id = self.sequence[self.showing_step]
                        self.buttons[next_id].is_lit = True
                        self.start_tone(next_id)
                        self.is_flashing = True
                        self.step_start_time = now
                    else:
                        self.start_player_turn(now)

        elif self.state == "PLAYER_TURN":
            if now - self.turn_start_time >= self.turn_time_limit:
                self.game_over_reason = REASON_TIMEOUT
                self.state = "GAME_OVER"

    def handle_event(self, event):
        if self.state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if self.state == "PLAYER_TURN" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.contains(event.pos):
                    btn.is_lit = True
                    self.start_tone(btn.color_id)
                    self.player_lit_button = btn
                    self.player_lit_start = pygame.time.get_ticks()

                    self.register_player_click(btn.color_id)
                    break

    def register_player_click(self, color_id):
        self.player_input.append(color_id)
        current_idx = len(self.player_input) - 1

        if self.player_input[current_idx] != self.sequence[current_idx]:
            self.game_over_reason = REASON_WRONG
            self.state = "GAME_OVER"
            return

        if len(self.player_input) == len(self.sequence):
            self.score += 1
            self.start_next_round()

    def reset(self):
        self.stop_all_tones()
        self.sequence.clear()
        self.player_input.clear()
        self.score = 0
        self.game_over_reason = REASON_WRONG
        for btn in self.buttons:
            btn.is_lit = False
        self.player_lit_button = None
        self.start_next_round()

    def render_timer_bar(self, screen):
        """Draw the countdown bar under the pads during the player's turn."""
        fraction = self.get_time_left_fraction()

        if fraction > TIMER_WARN_FRACTION:
            color = TIMER_COLOR_OK
        elif fraction > TIMER_DANGER_FRACTION:
            color = TIMER_COLOR_WARN
        else:
            color = TIMER_COLOR_DANGER

        bar_x = self.width // 2 - TIMER_BAR_WIDTH // 2
        track_rect = pygame.Rect(bar_x, TIMER_BAR_Y, TIMER_BAR_WIDTH, TIMER_BAR_HEIGHT)
        pygame.draw.rect(screen, (45, 48, 58), track_rect, border_radius=8)

        fill_width = int(TIMER_BAR_WIDTH * fraction)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, TIMER_BAR_Y, fill_width, TIMER_BAR_HEIGHT)
            pygame.draw.rect(screen, color, fill_rect, border_radius=8)

        pygame.draw.rect(screen, (70, 75, 85), track_rect, width=2, border_radius=8)

    def render(self, screen):
        screen.fill((22, 24, 30))

        title_surf = self.font_title.render("Memory Pattern Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 20))

        score_surf = self.font_medium.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 60))

        status_text = "Watch the pattern..." if self.state == "WATCH" else "Your turn: Click the pattern!"
        status_color = (190, 195, 205) if self.state == "WATCH" else (80, 240, 130)
        status_surf = self.font_medium.render(status_text, True, status_color)
        screen.blit(status_surf, (self.width // 2 - status_surf.get_width() // 2, 95))

        for btn in self.buttons:
            btn.render(screen)

        if self.state == "PLAYER_TURN":
            self.render_timer_bar(screen)

        if self.state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            if self.game_over_reason == REASON_TIMEOUT:
                over_text = "TIME'S UP!"
            else:
                over_text = "WRONG PATTERN! GAME OVER"

            over_surf = self.font_title.render(over_text, True, (240, 70, 70))
            screen.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 40))

            final_score_surf = self.font_medium.render(f"Final Score: {self.score}", True, (255, 255, 255))
            screen.blit(final_score_surf, (self.width // 2 - final_score_surf.get_width() // 2, self.height // 2 + 10))

            restart_surf = self.font_medium.render("Press [R] to Play Again", True, (200, 200, 200))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 50))