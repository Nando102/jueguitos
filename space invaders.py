import pygame
from personajes import Personaje
from personajes import Bala
from personajes import Enemigo
pygame.init()
pygame.font.init()

ancho = 800
largo = 550

ventana = pygame.display.set_mode((ancho, largo)) 
pygame.display.set_caption('space invaders')

jugador = Personaje(ancho // 2, largo - 50)
balas = []
reloj = pygame.time.Clock()

# --- CONFIGURACIÓN DE TEXTOS Y ESTADOS ---
fuente_puntaje = pygame.font.SysFont(None, 40)
fuente_grande = pygame.font.SysFont(None, 100)

puntaje = 0
game_over = False  
victoria = False   

filas = 4       
columnas = 10   
enemigos = []

# Función rápida para crear a los enemigos (así no repetimos código al reiniciar)
def crear_enemigos():
    lista = []
    for fila in range(filas):
        for col in range(columnas):
            x = 100 + (col * 60)
            y = 50 + (fila * 60)
            lista.append(Enemigo(x, y))
    return lista

enemigos = crear_enemigos()
direccion_enemigos = 1   
velocidad_enemigos = 2   
bajada_enemigos = 20     

# --- BUCLE PRINCIPAL ---
corriendo = True
while corriendo:
    # 1. Entrada de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            corriendo = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                corriendo = False
            
            # --- SISTEMA DE REINICIO ---
            # Si presionamos ESPACIO y el juego terminó (ya sea por ganar o perder)
            if event.key == pygame.K_SPACE:
                if game_over or victoria:
                    # Restauramos todas las variables a su estado original
                    jugador = Personaje(ancho // 2, largo - 50)
                    balas = []
                    enemigos = crear_enemigos()
                    puntaje = 0
                    direccion_enemigos = 1
                    game_over = False
                    victoria = False

    # Verificamos si ganamos (si la lista de enemigos está vacía)
    if len(enemigos) == 0 and not game_over:
        victoria = True

    # Solo permitimos jugar si NO hemos perdido y NO hemos ganado
    if not game_over and not victoria:
        # 2. Teclado
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            jugador.mover(-1, ancho)
        elif teclas[pygame.K_RIGHT]:
            jugador.mover(1, ancho)
        
        if teclas[pygame.K_SPACE]:
            if jugador.puede_disparar():
                centro_x, centro_y = jugador.forma.center
                nueva_bala = Bala(centro_x, centro_y - 20)
                balas.append(nueva_bala)

        # 3. Lógica física del juego
        tocar_borde = False
        for e in enemigos:
            e.mover(velocidad_enemigos, direccion_enemigos)
            
            if e.forma.bottom >= largo or e.forma.colliderect(jugador.forma):
                game_over = True
                
            if e.forma.right >= ancho or e.forma.left <= 0:
                tocar_borde = True

        if tocar_borde:
            direccion_enemigos *= -1
            for e in enemigos:
                e.forma.y += bajada_enemigos
                e.mover(velocidad_enemigos, direccion_enemigos)

        for b in balas[:]:  
            b.mover()
            if b.forma.bottom < 0:
                balas.remove(b)
                continue 
                
            bala_eliminada = False
            for e in enemigos[:]:
                if b.forma.colliderect(e.forma):
                    enemigos.remove(e)
                    bala_eliminada = True
                    puntaje += 10 
                    break 
                    
            if bala_eliminada:
                balas.remove(b)

    # 4. Renderizado (Dibujo)
    ventana.fill((0, 0, 0))
    
    for b in balas:
        b.dibujar(ventana)
        
    for e in enemigos:
        e.dibujar(ventana)
        
    jugador.dibujar(ventana)
    
    # Textos persistentes
    texto_puntaje = fuente_puntaje.render(f"Puntaje: {puntaje}", True, (255, 255, 255))
    ventana.blit(texto_puntaje, (ancho - 200, 20))
    
    # Mensajes de Fin de Juego
    if game_over:
        texto_go = fuente_grande.render("GAME OVER", True, (255, 0, 0))
        texto_reiniciar = fuente_puntaje.render("Presiona ESPACIO para reiniciar", True, (255, 255, 255))
        
        ventana.blit(texto_go, ((ancho - texto_go.get_width()) // 2, largo // 3))
        ventana.blit(texto_reiniciar, ((ancho - texto_reiniciar.get_width()) // 2, largo // 2))
        
    elif victoria:
        texto_vic = fuente_grande.render("¡GANASTE!", True, (0, 255, 0))
        texto_reiniciar = fuente_puntaje.render("Presiona ESPACIO para jugar de nuevo", True, (255, 255, 255))
        
        ventana.blit(texto_vic, ((ancho - texto_vic.get_width()) // 2, largo // 3))
        ventana.blit(texto_reiniciar, ((ancho - texto_reiniciar.get_width()) // 2, largo // 2))
    
    pygame.display.update()
    reloj.tick(60)

pygame.quit()
