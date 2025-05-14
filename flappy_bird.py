import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.25
BIRD_JUMP = -5
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # мс

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
SKY_BLUE = (135, 206, 235)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Шрифты
font_small = pygame.font.SysFont('Arial', 20)
font_large = pygame.font.SysFont('Arial', 40)


class Bird:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.velocity = 0
        self.radius = 15

    def jump(self):
        self.velocity = BIRD_JUMP

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

        if self.y < 0:
            self.y = 0
            self.velocity = 0
        if self.y > HEIGHT:
            self.y = HEIGHT
            self.velocity = 0

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 0), (self.x, int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (self.x + 5, int(self.y) - 5), 3)
        pygame.draw.polygon(screen, (255, 165, 0), [
            (self.x + self.radius, int(self.y)),
            (self.x + self.radius + 10, int(self.y)),
            (self.x + self.radius, int(self.y) + 5)
        ])

    def get_mask(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)


class Pipe:
    def __init__(self, speed):
        self.x = WIDTH
        self.speed = speed
        self.height = random.randint(100, HEIGHT - 100 - PIPE_GAP)
        self.top_pipe = pygame.Rect(self.x, 0, 50, self.height)
        self.bottom_pipe = pygame.Rect(self.x, self.height + PIPE_GAP, 50, HEIGHT - self.height - PIPE_GAP)
        self.passed = False

    def update(self):
        self.x -= self.speed
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.top_pipe)
        pygame.draw.rect(screen, GREEN, self.bottom_pipe)

    def collide(self, bird):
        bird_rect = bird.get_mask()
        return bird_rect.colliderect(self.top_pipe) or bird_rect.colliderect(self.bottom_pipe)


def draw_menu():
    screen.fill(SKY_BLUE)

    title = font_large.render("FLAPPY BIRD", True, WHITE)
    start_text = font_small.render("Нажмите ПРОБЕЛ чтобы начать", True, WHITE)
    exit_text = font_small.render("Нажмите ESC чтобы выйти", True, WHITE)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
    screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.update()


def draw_game_over(score):
    screen.fill(SKY_BLUE)

    game_over = font_large.render("ИГРА ОКОНЧЕНА", True, RED)
    score_text = font_small.render(f"Счет: {score}", True, BLACK)
    restart_text = font_small.render("Нажмите ПРОБЕЛ чтобы играть снова", True, WHITE)
    exit_text = font_small.render("Нажмите ESC чтобы выйти", True, WHITE)

    screen.blit(game_over, (WIDTH // 2 - game_over.get_width() // 2, HEIGHT // 3))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))
    screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 100))

    pygame.display.update()


def main():
    # Игровые объекты
    bird = Bird()
    pipes = []
    score = 0
    last_pipe = pygame.time.get_ticks()
    pipe_speed = 3  # Начальная скорость труб
    last_speed_increase = 0  # Последнее увеличение скорости

    # Состояния игры
    game_active = False
    running = True

    # Главный игровой цикл
    while running:
        clock.tick(FPS)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_active:
                        # Начало новой игры
                        game_active = True
                        bird = Bird()
                        pipes = []
                        score = 0
                        pipe_speed = 3
                        last_speed_increase = 0
                        last_pipe = pygame.time.get_ticks()
                    else:
                        bird.jump()

                if event.key == pygame.K_ESCAPE:
                    if not game_active:
                        running = False
                    else:
                        game_active = False

        if game_active:
            # Обновление птицы
            bird.update()

            # Генерация труб
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe(pipe_speed))
                last_pipe = time_now

            # Обновление труб
            for pipe in pipes[:]:
                pipe.update()

                # Проверка столкновений
                if pipe.collide(bird):
                    game_active = False

                # Проверка прохождения трубы
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    score += 1

                # Удаление труб за экраном
                if pipe.x < -50:
                    pipes.remove(pipe)

            # Увеличение скорости каждые 5 очков
            if score - last_speed_increase >= 5:
                pipe_speed += 1
                last_speed_increase = score

            # Проверка выхода за границы
            if bird.y >= HEIGHT or bird.y <= 0:
                game_active = False

            # Отрисовка
            screen.fill(SKY_BLUE)

            for pipe in pipes:
                pipe.draw()

            bird.draw()

            # Отрисовка счета
            score_text = font_small.render(f"Счет: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

            pygame.display.update()
        else:
            if score > 0:
                draw_game_over(score)
            else:
                draw_menu()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()