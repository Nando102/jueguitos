import pygame
# --- CLASE PERSONAJE ---
class Personaje():
    def __init__(self, x, y):
        # Creamos la forma base del personaje (un rectángulo de 40x40)
        self.forma = pygame.Rect(0, 0, 40, 40)
        self.forma.center = (x, y)
        self.velocidad = 5
        # Tiempo de espera entre disparos (300 milisegundos)
        self.cooldown = 300 
        self.ultimo_disparo = 0 # Empezamos en 0 para poder disparar de inmediato

    def mover(self, direccion, ancho_pantalla):
        nueva_x = self.forma.x + (direccion * self.velocidad)
        if nueva_x >= 0 and nueva_x <= (ancho_pantalla - self.forma.width):
            self.forma.x = nueva_x     

    def dibujar(self, interfaz):
        # Obtenemos el centro usando self.forma.center de manera segura
        x, y = self.forma.center
        punto1 = (x, y - 20)      # Punta superior
        punto2 = (x - 20, y + 20)  # Ala izquierda
        punto3 = (x + 20, y + 20)  # Ala derecha
        pygame.draw.polygon(interfaz, (255, 255, 0), [punto1, punto2, punto3])

    def puede_disparar(self):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_disparo > self.cooldown:
            self.ultimo_disparo = tiempo_actual
            return True
        return False


# --- CLASE BALA ---
class Bala():
    def __init__(self, x, y):
        # Creamos un rectángulo pequeño para el proyectil
        self.forma = pygame.Rect(x - 2, y, 4, 15)
        self.velocidad = 8

    def mover(self):
        self.forma.y -= self.velocidad

    def dibujar(self, interfaz):
        pygame.draw.rect(interfaz, (255, 50, 50), self.forma)
        
        #--- CLASE ENEMIGO ---#
class Enemigo():
    def __init__(self, x, y):
        self.forma = pygame.Rect(x, y, 30, 30)

    def dibujar(self, interfaz):
        pygame.draw.rect(interfaz, (0, 255, 0), self.forma)

    # Añadimos un método para mover al enemigo
    def mover(self, velocidad, direccion):
        self.forma.x += (velocidad * direccion)
