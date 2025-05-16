import time
from pygame.locals import *
import pygame
import random

zona = 0

BLANCO = (255, 255, 255)
ROJO = (200, 0, 0)
VERDE = (0, 200, 0)
NEGRO = (0, 0, 0)

# Tamaño ventana
VIEW_WIDTH = 640
VIEW_HEIGHT = 360

# Iniciamos pygame
pygame.init()
pantalla = pygame.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT))
pygame.display.set_caption("FIGHT CLUB DEMO")

# Cargamos imagen de fondo
background_image = 'assets/fons.jpeg'
background = pygame.image.load(background_image).convert()
background_width = background.get_width()
background_height = background.get_height()

# Límites para mover el fondo en lugar del personaje
MARGIN_X, MARGIN_Y = VIEW_WIDTH // 2, VIEW_HEIGHT // 2

# Cargamos imagen inicial del personaje
player_image = pygame.image.load('assets/sprites/down0.png')
protagonist_speed = 8

# Posiciones iniciales del personaje y del fondo
player_rect = player_image.get_rect(midbottom=(VIEW_WIDTH // 2, VIEW_HEIGHT // 2))
bg_x, bg_y = 0, 0

# Control de FPS
clock = pygame.time.Clock()
fps = 30

# Control de la animación del personaje
sprite_direction = "down"
sprite_index = 0
animation_protagonist_speed = 200
sprite_frame_number = 7
last_change_frame_time = 0
idle = False

def combate():
    global zona  # Para poder salir del combate y regresar
    pantalla = pygame.display.set_mode((640, 360))
    fuente = pygame.font.SysFont(None, 24)

    fondo = pygame.image.load("assets/fight1.jpeg")
    fondo = pygame.transform.scale(fondo, (640, 360))

    jugador_vida = 100
    enemigo_vida = 100
    jugador_resistencia = 100
    jugador_turno = True
    fase = "menu"

    ataques = {
        "Jab": {"dano": (5, 10), "coste": 10},
        "Gancho": {"dano": (8, 15), "coste": 15},
        "Uppercut": {"dano": (10, 20), "coste": 20},
        "Llave": {"coste": 25}
    }
    ataque_seleccionado = None
    mensaje = "¡Tu turno! Elige un ataque."
    opciones = list(ataques.keys())
    menu_rects = [pygame.Rect(20, 250 + i * 25, 180, 20) for i in range(len(opciones))]

    barra_rect = pygame.Rect(200, 150, 240, 20)
    zona_perfecta = pygame.Rect(barra_rect.centerx - 10, barra_rect.y, 20, barra_rect.height)
    cursor_rect = pygame.Rect(barra_rect.left, barra_rect.y, 5, barra_rect.height)
    cursor_vel = 5
    cursor_moving = False

    toques = 0
    llave_tiempo = 2000
    llave_timer_start = 0

    def dibujar_texto(texto, x, y, color=(255, 255, 255)):
        pantalla.blit(fuente.render(texto, True, color), (x, y))

    def dibujar_barra(x, y, valor_actual, valor_max, ancho=150, alto=15, color_fondo=(200, 0, 0), color_llenado=(0, 200, 0)):
        pygame.draw.rect(pantalla, color_fondo, (x, y, ancho, alto))
        ancho_llenado = max(0, int(ancho * (valor_actual / valor_max)))
        pygame.draw.rect(pantalla, color_llenado, (x, y, ancho_llenado, alto))

    clock = pygame.time.Clock()
    en_combate = True

    while en_combate:
        tiempo_actual = pygame.time.get_ticks()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

            if fase == "menu" and jugador_turno and evento.type == KEYDOWN:
                if evento.key in [K_1, K_2, K_3, K_4]:
                    indice = [K_1, K_2, K_3, K_4].index(evento.key)
                    if indice < len(opciones):
                        nombre = opciones[indice]
                        ataque = ataques[nombre]
                        if jugador_resistencia >= ataque["coste"]:
                            ataque_seleccionado = nombre
                            jugador_resistencia -= ataque["coste"]

                            if nombre == "Llave":
                                toques = 0
                                llave_timer_start = tiempo_actual
                                fase = "llave_ataque"
                                mensaje = "¡Pulsa ESPACIO rápido para hacer más daño!"
                            else:
                                fase = "precision"
                                cursor_rect.left = barra_rect.left
                                cursor_moving = True
                                mensaje = "¡Presiona ESPACIO en el centro!"

                        else:
                            mensaje = "¡No tienes suficiente resistencia!"

            elif fase == "precision" and evento.type == KEYDOWN and evento.key == K_SPACE:
                cursor_moving = False
                pygame.mixer.music.load('assets/punetazo.mp3')
                pygame.mixer.music.play()
                datos = ataques[ataque_seleccionado]
                base_dano = random.randint(*datos["dano"])
                if zona_perfecta.colliderect(cursor_rect):
                    dano = int(base_dano * 1.5)
                    mensaje = f"¡Golpe perfecto! {dano} daño."
                else:
                    dano = int(base_dano * 0.5)
                    mensaje = f"¡Golpe débil! {dano} daño."
                enemigo_vida -= dano
                fase = "espera"
                espera_inicio = tiempo_actual

            elif fase in ["llave_ataque", "llave_defensa"] and evento.type == KEYDOWN and evento.key == K_SPACE:
                toques += 1

            elif evento.type == USEREVENT + 1 and fase == "enemigo":
                jugador_resistencia = min(100, jugador_resistencia + 10)
                jugador_turno = True
                fase = "menu"
                mensaje = "¡Tu turno! Elige un ataque."
                pygame.time.set_timer(USEREVENT + 1, 0)

        if fase == "precision" and cursor_moving:
            cursor_rect.x += cursor_vel
            if cursor_rect.right > barra_rect.right or cursor_rect.left < barra_rect.left:
                cursor_vel *= -1

        if fase == "llave_ataque" and tiempo_actual - llave_timer_start > llave_tiempo:
            dano = min(30, int(toques * 1.5))
            mensaje = f"¡Llave exitosa! {dano} daño."
            enemigo_vida -= dano
            fase = "espera"
            espera_inicio = tiempo_actual

        if fase == "llave_defensa" and tiempo_actual - llave_timer_start > llave_tiempo:
            dano_base = random.randint(15, 30)
            reduccion = min(toques * 1, dano_base)
            dano_final = dano_base - reduccion
            mensaje = f"¡Resistes la llave! Recibes {dano_final} daño."
            jugador_vida -= dano_final
            pygame.time.set_timer(USEREVENT + 1, 1000)
            fase = "enemigo"

        if fase == "espera" and tiempo_actual - espera_inicio > 1000:
            if enemigo_vida > 0:
                if random.random() < 0.3:
                    ataque_seleccionado = "Llave"
                    toques = 0
                    llave_timer_start = tiempo_actual
                    mensaje = "¡El enemigo te hace una llave! ¡Pulsa ESPACIO para defenderte!"
                    fase = "llave_defensa"
                else:
                    ataque = random.choice(["Jab", "Gancho", "Uppercut"])
                    base_dano = random.randint(*ataques[ataque]["dano"])
                    jugador_vida -= base_dano
                    mensaje = f"El enemigo usa {ataque}: {base_dano} daño."
                    pygame.time.set_timer(USEREVENT + 1, 1000)
                    fase = "enemigo"
            else:
                jugador_turno = True
                fase = "menu"

        pantalla.blit(fondo, (0, 0))
        dibujar_texto("Tú", 20, 20)
        dibujar_barra(60, 20, jugador_vida, 100)
        dibujar_texto(f"RES: {jugador_resistencia}", 60, 45, (0, 100, 255))
        dibujar_texto("Enemigo", 350, 20)
        dibujar_barra(430, 20, enemigo_vida, 100)
        dibujar_texto(mensaje, 20, 90, (180, 180, 180))

        if fase == "menu":
            for i, rect in enumerate(menu_rects):
                pygame.draw.rect(pantalla, (180, 180, 180), rect)
                nombre = opciones[i]
                coste = ataques[nombre]["coste"]
                texto = f"{i + 1}. {nombre} ({coste})"
                dibujar_texto(texto, rect.x + 5, rect.y + 2, (0, 0, 0))

        elif fase == "precision":
            pygame.draw.rect(pantalla, (255, 255, 255), barra_rect, 2)
            pygame.draw.rect(pantalla, (0, 200, 0), zona_perfecta)
            pygame.draw.rect(pantalla, (0, 100, 255), cursor_rect)

        elif fase in ["llave_ataque", "llave_defensa"]:
            tiempo_restante = max(0, llave_tiempo - (tiempo_actual - llave_timer_start))
            dibujar_texto(f"Pulsa ESPACIO rápido ({int(tiempo_restante / 1000)}s)", 200, 130)
            dibujar_texto(f"Toques: {toques}", 260, 160)

        if jugador_vida <= 0:
            mensaje = "¡Has perdido!"
            en_combate = False
            ganar = pygame.image.load('assets/GAME OVER.png')
            imprimir_pantalla_fons(ganar, 0, 0)
            zona = 2
            pygame.mixer.music.load('assets/aplausos.mp3')
            pygame.mixer.music.play()
        elif enemigo_vida <= 0:
            mensaje = "¡Has ganado!"
            en_combate = False
            ganar = pygame.image.load('assets/win .jpeg')
            imprimir_pantalla_fons(ganar, 0, 0)
            zona = 2
            pygame.mixer.music.load('assets/aplausos.mp3')
            pygame.mixer.music.play()
        pygame.display.update()
        clock.tick(60)

    pygame.time.delay(2000)


def imprimir_pantalla_fons(image, x, y):
    # Imprime imagen de fondo:

    pantalla.blit(image, (x, y))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    if zona == 0:
        keys = pygame.key.get_pressed()
        # Imprimimos la pantalla de inicio
        logo_image = pygame.image.load('assets/logojoc.png')
        imprimir_pantalla_fons(logo_image, 0, 0)
        pygame.mixer.music.load('assets/50cent.mp3')
        pygame.mixer.music.play()

        if keys[K_SPACE]:  # Cambiar al menú al presionar espacio
            zona = 1  # Ir al menú
            pygame.display.update()
    if zona == 3:
        keys = pygame.key.get_pressed()
        CREDITS = pygame.image.load('assets/CREDITS.jpeg')
        imprimir_pantalla_fons(CREDITS, 0, 0)
        if keys[K_SPACE]:  # Cambiar zona al presionar 1
            zona = 1

    elif zona == 1:
        keys = pygame.key.get_pressed()
        # Imprimimos el menú
        menu_image = pygame.image.load('assets/menu.png')
        imprimir_pantalla_fons(menu_image, 0, 0)
        if keys[K_1]:  # Cambiar zona al presionar 1
            zona = 2
            pygame.mixer.music.load('assets/chillmusic.wav')
            pygame.mixer.music.play()
        if keys[K_2]:  # Cambiar zona al presionar 2
            zona = 3
        if keys[K_3]:  # Salir al presionar 3
            pygame.quit()

    elif zona == 2:


        # Movimiento del jugador
        idle = True
        keys = pygame.key.get_pressed()

        if keys[K_UP]:
            idle = False
            sprite_direction = "up"
            if player_rect.y > MARGIN_Y or bg_y >= 0:
                player_rect.y = max(player_rect.y - protagonist_speed, player_rect.height // 2)
            else:
                bg_y = min(bg_y + protagonist_speed, 0)

        if keys[K_DOWN]:
            idle = False
            sprite_direction = "down"
            if player_rect.y < VIEW_HEIGHT - MARGIN_Y or bg_y <= VIEW_HEIGHT - background_height:
                player_rect.y = min(player_rect.y + protagonist_speed, VIEW_HEIGHT - player_rect.height // 2)
            else:
                bg_y = max(bg_y - protagonist_speed, VIEW_HEIGHT - background_height)

        if keys[K_RIGHT]:
            idle = False
            sprite_direction = "right"
            if player_rect.x < VIEW_WIDTH - MARGIN_X or bg_x <= VIEW_WIDTH - background_width:
                player_rect.x = min(player_rect.x + protagonist_speed, VIEW_WIDTH - player_rect.width // 2)
            else:
                bg_x = max(bg_x - protagonist_speed, VIEW_WIDTH - background_width)

        if keys[K_LEFT]:
            idle = False
            sprite_direction = "left"
            if player_rect.x > MARGIN_X or bg_x >= 0:
                player_rect.x = max(player_rect.x - protagonist_speed, player_rect.width // 2)
            else:
                bg_x = min(bg_x + protagonist_speed, 0)

        # Dibuja el fondo
        imprimir_pantalla_fons(background, bg_x, bg_y)

        # Animación del personaje
        current_time = pygame.time.get_ticks()

        if not idle:
            if current_time - last_change_frame_time >= animation_protagonist_speed:
                last_change_frame_time = current_time
                sprite_index = (sprite_index + 1) % sprite_frame_number
        else:
            sprite_index = 0

        # Cargar la imagen del personaje según la dirección y el índice del sprite
        player_image = pygame.image.load(f'assets/sprites/{sprite_direction}{sprite_index}.png')
        pantalla.blit(player_image, player_rect)

        # Mantener el jugador dentro de la ventana
        player_rect.clamp_ip(pantalla.get_rect())

        # Áreas de colisión
        area1_rect = pygame.Rect(bg_x + 750, bg_y + 150, 200, 80)
        area2_rect = pygame.Rect(bg_x + 750, bg_y + 450, 200, 80)
        area3_rect = pygame.Rect(bg_x + 750, bg_y + 780, 100, 80)


        # pygame.draw.rect(pantalla, (255, 255, 0), area1_rect)
        # pygame.draw.rect(pantalla, (0, 255, 255), area2_rect)
        # pygame.draw.rect(pantalla, (255, 0, 255), area3_rect)


        # Comprobación de colisiones
        if player_rect.colliderect(area1_rect):
            combate()
            zona = 4
            bg_x = max(bg_x + protagonist_speed, 0)

        elif player_rect.colliderect(area2_rect):
            combate()
            zona = 4
        elif player_rect.colliderect(area3_rect):
            combate()
            zona = 4


    pygame.display.update()
    clock.tick(fps)
