import pygame
import sys
import numpy as np
from src.interface.grid.manifold_mapping import Tile, ManifoldMap
from src.interface.controller import ObserverController

def generate_tone(frequency, duration=0.05):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    # Sine wave for the Harmonic Lead
    tone = np.sin(frequency * t * 2 * np.pi)
    audio = (tone * 32767).astype(np.int16)
    # Duplicate for stereo
    stereo_audio = np.stack((audio, audio), axis=-1)
    return pygame.sndarray.make_sound(stereo_audio)

def run_manifold_view():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((512, 512))
    pygame.display.set_caption("MLAOS Sovereign Interface - Phase 11 (Audio)")
    clock = pygame.time.Clock()
    
    # Pre-generate the Spherical Tones
    move_sound = generate_tone(440) # A4 - Consistency
    fail_sound = generate_tone(220) # A3 - Constraint
    
    manifold = ManifoldMap(32)
    observer = ObserverController(16, 16)
    
    # Re-manifest the Sanctuary
    for y in range(14, 19):
        for x in range(14, 19): manifold.grid[y][x] = Tile.FLOOR
    for i in range(10, 22): manifold.grid[13][i] = Tile.WALL; manifold.grid[19][i] = Tile.WALL

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_UP:    dy = -1
                if event.key == pygame.K_DOWN:  dy = 1
                if event.key == pygame.K_LEFT:  dx = -1
                if event.key == pygame.K_RIGHT: dx = 1
                
                if dx != 0 or dy != 0:
                    if observer.move(dx, dy, manifold):
                        move_sound.play()
                    else:
                        fail_sound.play()

        screen.fill((0, 0, 0))
        for y in range(32):
            for x in range(32):
                tile = manifold.grid[y][x]
                rect = (x * 16, y * 16, 15, 15)
                if x == observer.x and y == observer.y: color = (0, 255, 255)
                elif tile == Tile.WALL: color = (80, 0, 0)
                elif tile == Tile.FLOOR: color = (40, 40, 40)
                else: continue
                pygame.draw.rect(screen, color, rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    run_manifold_view()
