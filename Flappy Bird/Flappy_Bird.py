import pygame
import random
import os

pygame.init()
pygame.mixer.init()

# --- RESOLUCIÓN VIRTUAL ---
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Flappy Bird Definitivo")
clock = pygame.time.Clock()

# --- CONFIGURACIONES ---
BIRD_WIDTH, BIRD_HEIGHT = 110, 80    
PIPE_WIDTH = 220                     
PIPE_GAP = 210                       
GRAVITY = 0.95                       
BIRD_JUMP = -13.5                    
PIPE_VELOCITY = 4.0                  

# --- GESTIÓN DE RÉCORD (ARCHIVOS) ---
RECORD_FILE = "record.txt"

def load_high_score():
    if os.path.exists(RECORD_FILE):
        try:
            with open(RECORD_FILE, "r") as f:
                return int(f.read().strip())
        except ValueError:
            return 0
    return 0

def save_high_score(new_score):
    current_high = load_high_score()
    if new_score > current_high:
        with open(RECORD_FILE, "w") as f:
            f.write(str(new_score))

# --- CARGA DE RECURSOS ---
try:
    RAW_BIRD_IMG = pygame.image.load("pajaro.png").convert_alpha()
    BIRD_IMG = pygame.transform.scale(RAW_BIRD_IMG, (BIRD_WIDTH, BIRD_HEIGHT))

    RAW_PIPE_IMG = pygame.image.load("tuberia.png").convert_alpha()
    
    BG_IMG = pygame.image.load("fondo.jpg").convert()
    BG_IMG = pygame.transform.scale(BG_IMG, (WIDTH, HEIGHT))

except FileNotFoundError as e:
    print(f"ADVERTENCIA: No se pudo cargar algún archivo multimedia. Detalles: {e}")

class Bird:
    def __init__(self):
        self.x = 200
        self.y = HEIGHT // 2
        self.velocity = 0
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.img = BIRD_IMG
        self.mask = pygame.mask.from_surface(self.img)

    def jump(self):
        self.velocity = BIRD_JUMP

    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self):
        rot_angle = -self.velocity * 2.0
        rot_angle = max(min(rot_angle, 25), -90) 
        rotated_bird = pygame.transform.rotate(self.img, rot_angle)
        self.mask = pygame.mask.from_surface(rotated_bird)
        WIN.blit(rotated_bird, (self.x, self.y))

    def get_mask(self):
        return self.mask

class Pipe:
    def __init__(self, score):
        self.x = WIDTH
        
        dynamic_margin = max(20, 100 - (score * 5))
        
        # Margen de seguridad para que la boquilla no quede cortada ni flotando fuera de la pantalla
        boquilla_alto = 70 
        
        min_top = dynamic_margin + boquilla_alto
        max_top = HEIGHT - PIPE_GAP - dynamic_margin - boquilla_alto
        
        if min_top >= max_top:
            min_top = 20
            max_top = HEIGHT - PIPE_GAP - 20

        self.gap_y = random.randint(min_top, max_top)
        
        self.top_height = self.gap_y
        self.bottom_y = self.gap_y + PIPE_GAP
        self.bottom_height = HEIGHT - self.bottom_y
        
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.top_height)
        self.bottom_rect = pygame.Rect(self.x, self.bottom_y, PIPE_WIDTH, self.bottom_height)
        
        self.passed = False
        self.spawned_next = False

        self.top_img, self.top_mask = self.create_pipe_texture(self.top_rect.height, inverted=True)
        self.bottom_img, self.bottom_mask = self.create_pipe_texture(self.bottom_rect.height, inverted=False)

    def create_pipe_texture(self, target_height, inverted=False):
        surface = pygame.Surface((PIPE_WIDTH, target_height), pygame.SRCALPHA)
        
        base_w = PIPE_WIDTH
        raw_h = RAW_PIPE_IMG.get_height()
        raw_w = RAW_PIPE_IMG.get_width()
        
        base_h = int(raw_h * (PIPE_WIDTH / raw_w))
        scaled_base = pygame.transform.scale(RAW_PIPE_IMG, (base_w, base_h))
        
        current_y = 0
        while current_y < target_height:
            surface.blit(scaled_base, (0, current_y))
            current_y += base_h
            
        if inverted:
            surface = pygame.transform.flip(surface, False, True)
                
        mask = pygame.mask.from_surface(surface)
        return surface, mask

    def move(self):
        self.x -= PIPE_VELOCITY
        self.top_rect.x = int(self.x)
        self.bottom_rect.x = int(self.x)

    def draw(self):
        WIN.blit(self.top_img, (self.x, self.top_rect.y))
        WIN.blit(self.bottom_img, (self.x, self.bottom_rect.y))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        
        top_offset = (int(self.x) - int(bird.x), int(self.top_rect.y) - int(bird.y))
        bottom_offset = (int(self.x) - int(bird.x), int(self.bottom_rect.y) - int(bird.y))

        top_collision = bird_mask.overlap(self.top_mask, top_offset)
        bottom_collision = bird_mask.overlap(self.bottom_mask, bottom_offset)

        if top_collision or bottom_collision:
            return True
        return False

def start_menu_music():
    try:
        pygame.mixer.music.load("menu.mp3")
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

def start_game_music():
    try:
        pygame.mixer.music.load("theme.mp3")
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

def stop_music():
    pygame.mixer.music.stop()

def play_game_over_sound():
    try:
        pygame.mixer.music.load("Game Over.mp3")
        pygame.mixer.music.set_volume(2.0)
        pygame.mixer.music.play(0)
    except Exception:
        pass

def main_menu():
    title_font = pygame.font.SysFont("arial", 70, bold=True)
    instruction_font = pygame.font.SysFont("arial", 40, bold=True)
    
    start_menu_music() 
    high_score = load_high_score()

    while True:
        clock.tick(60)
        WIN.blit(BG_IMG, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start_game_music() 
                    return 
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        title_shadow = title_font.render("FLAPPY BIRD", True, (0, 0, 0))
        title_text = title_font.render("FLAPPY BIRD", True, (255, 255, 255))
        
        record_shadow = instruction_font.render(f"Récord: {high_score}", True, (0, 0, 0))
        record_text = instruction_font.render(f"Récord: {high_score}", True, (255, 215, 0))

        play_shadow = instruction_font.render("Presiona ESPACIO para Jugar", True, (0, 0, 0))
        play_text = instruction_font.render("Presiona ESPACIO para Jugar", True, (255, 255, 255))

        WIN.blit(title_shadow, (WIDTH // 2 - title_shadow.get_width() // 2 + 3, 183))
        WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 180))

        WIN.blit(record_shadow, (WIDTH // 2 - record_shadow.get_width() // 2 + 2, 303))
        WIN.blit(record_text, (WIDTH // 2 - record_shadow.get_width() // 2, 300))

        WIN.blit(play_shadow, (WIDTH // 2 - play_shadow.get_width() // 2 + 2, 423))
        WIN.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, 420))

        pygame.display.update()

def game_over_screen(score):
    title_font = pygame.font.SysFont("arial", 70, bold=True)
    instruction_font = pygame.font.SysFont("arial", 40, bold=True)
    
    stop_music() 
    play_game_over_sound() 
    high_score = load_high_score()

    timer = 360

    while timer > 0:
        clock.tick(60)
        timer -= 1
        WIN.blit(BG_IMG, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        go_shadow = title_font.render("¡FIN DEL JUEGO!", True, (0, 0, 0))
        go_text = title_font.render("¡FIN DEL JUEGO!", True, (255, 69, 69))

        score_shadow = instruction_font.render(f"Puntaje obtenido: {score}", True, (0, 0, 0))
        score_text = instruction_font.render(f"Puntaje obtenido: {score}", True, (255, 255, 255))

        record_shadow = instruction_font.render(f"Récord actual: {high_score}", True, (0, 0, 0))
        record_text = instruction_font.render(f"Récord actual: {high_score}", True, (255, 215, 0))

        WIN.blit(go_shadow, (WIDTH // 2 - go_shadow.get_width() // 2 + 3, 183))
        WIN.blit(go_text, (WIDTH // 2 - go_shadow.get_width() // 2, 180))

        WIN.blit(score_shadow, (WIDTH // 2 - score_shadow.get_width() // 2 + 2, 303))
        WIN.blit(score_text, (WIDTH // 2 - score_shadow.get_width() // 2, 300))

        WIN.blit(record_shadow, (WIDTH // 2 - record_shadow.get_width() // 2 + 2, 383))
        WIN.blit(record_text, (WIDTH // 2 - record_shadow.get_width() // 2, 380))

        pygame.display.update()

def main():
    while True:
        main_menu()
        
        bird = Bird()
        score = 0
        pipes = [Pipe(score)]
        
        font = pygame.font.SysFont("arial", 60, bold=True)
        run = True

        while run:
            clock.tick(60)
            WIN.blit(BG_IMG, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird.jump()
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

            bird.move()

            pipes_to_remove = []
            add_pipe = False
            
            for pipe in pipes:
                pipe.move()
                
                if pipe.collide(bird):
                    run = False
                
                if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                    pipe.passed = True
                    score += 1

                if not pipe.spawned_next and pipe.x < WIDTH - 450:
                    pipe.spawned_next = True
                    add_pipe = True
                
                if pipe.x + PIPE_WIDTH < 0:
                    pipes_to_remove.append(pipe)
                
                pipe.draw()

            if add_pipe:
                pipes.append(Pipe(score))

            for p in pipes_to_remove:
                pipes.remove(p)

            if bird.y + bird.height > HEIGHT or bird.y < 0:
                run = False

            bird.draw()
            
            score_shadow = font.render(f"{score}", True, (0, 0, 0))
            score_text = font.render(f"{score}", True, (255, 255, 255))
            WIN.blit(score_shadow, (WIDTH // 2 - score_shadow.get_width() // 2 + 3, 53))
            WIN.blit(score_text, (WIDTH // 2 - score_shadow.get_width() // 2, 50))

            pygame.display.update()

        save_high_score(score)
        game_over_screen(score)

if __name__ == "__main__":
    main()