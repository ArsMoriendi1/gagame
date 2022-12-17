import pygame
import sys
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(('localhost', 10000))
my_colour = sock.recv(16).decode()
my_x = int(sock.recv(16).decode())
my_y = int(sock.recv(16).decode())
X_CORD = my_x
Y_CORD = my_y


run = True

pygame.init()
WIDTH, HEIGHT = 800, 600
FPS = 60
TILE = 32
colours = {'0': (255, 0, 0), '1': (255, 20, 147), '2': (255, 69, 0), '3': (255, 255, 0), '4': (255, 0, 125),
           '5': (218, 112, 214), '6': (128, 0, 128), '7': (128, 0, 0), '8': (0, 255, 0), '9': (0, 0, 139),
           '10': (123, 104, 238)}
pygame.display.set_caption('ТАHЧИКИ 1944')
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
DIR = 0
bullets = []


def dirrects(i):
    if i == 0 or i == 1:
        dx = 0
    elif i == 4:
        dx = -16
    elif i == 3:
        dx = 16
    elif i == 2:
        dx = 0
    return dx


def directs(i):
    if i == 0 or i == 1:
        dy = -16
    elif i == 4:
        dy = 0
    elif i == 3:
        dy = 0
    elif i == 2:
        dy = 16
    return dy


def draw_opponents(data):
    for i in range(len(data)):
        j = data[i].split(' ')
        x = my_x + int(j[0])
        y = my_y + int(j[1])
        a = int(j[2])
        c = colours[j[3]]
        d = int(j[4])
        pygame.draw.rect(screen, c, (x, y, a, a))
        if d == 0:
            pygame.draw.line(screen, 'white', (x + 16, y - 10), (x + 16, y + 20), 4)
        if d == 1:
            pygame.draw.line(screen, 'white', (x + 16, y - 10), (x + 16, y + 20), 4)
        elif d == 2:
            pygame.draw.line(screen, 'white', (x + 16, y + 50), (x + 16, y + 20), 4)
        elif d == 3:
            pygame.draw.line(screen, 'white', (x + 48, y + 16), (x + 16, y + 16), 4)
        elif d == 4:
            pygame.draw.line(screen, 'white', (x - 16, y + 16), (x + 16, y + 16), 4)


def find(s):
    begin = None
    for i in range(len(s)):
        if s[i] == '[':
            begin = i
        if s[i] == ']':
            end = i
            res = s[begin + 1:end]
            return res
    return ''
class Bullet():
    def __init__(self, x, y, dx, dy):
        bullets.append(self)
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.x < 0 or self.x > WIDTH or self.y > HEIGHT:
            bullets.remove(self)
    def draw(self):
        pygame.draw.circle(screen, 'red', (self.x, self.y), 2)
x_speed = 0
y_speed = 0

while run:

    clock.tick(FPS)
    for bullet in bullets:
        bullet.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            data = '[0, -1>'
            sock.send(data.encode())
            x_speed -= 5
            y_speed = 0
            DIR = 4
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            data = '[1, 0>'
            sock.send(data.encode())
            x_speed += 5
            y_speed = 0
            DIR = 3
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            data = '[0, 1>'
            sock.send(data.encode())
            x_speed = 0
            y_speed -= 5
            DIR = 1
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            data = '[-1, 0>'
            sock.send(data.encode())
            x_speed = 0
            y_speed += 5
            DIR = 2
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            data = '[1, 1>'
            sock.send(data.encode())
            dx = dirrects(DIR) * 2
            dy = directs(DIR) * 2
            Bullet(my_x + 16, my_y + 16, dx, dy)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_a and event.key == pygame.K_d:
            x_speed = 0
            y_speed = 0
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w and event.key == pygame.K_s:
            x_speed = 0
            y_speed = 0
        elif event.type == pygame.KEYUP and event.key == pygame.K_a:
            sock.send('[0, 0>'.encode())
            x_speed = 0
            y_speed = 0
        elif event.type == pygame.KEYUP and event.key == pygame.K_d:
            sock.send('[0, 0>'.encode())
            x_speed = 0
            y_speed = 0
        elif event.type == pygame.KEYUP and event.key == pygame.K_w:
            sock.send('[0, 0>'.encode())
            x_speed = 0
            y_speed = 0
        elif event.type == pygame.KEYUP and event.key == pygame.K_s:
            sock.send('[0, 0>'.encode())
            x_speed = 0
            y_speed = 0
    if my_x + TILE < WIDTH:
        my_x += x_speed
    if my_y + TILE < HEIGHT:
        my_y += y_speed
    if my_x + TILE >= WIDTH:
        my_x -= 20
    if my_x + TILE <= 33:
        my_x += 20
    if my_y + TILE >= HEIGHT:
        my_y -= 20
    if my_y + TILE <= 33:
        my_y += 20

    data = sock.recv(2**20)
    data = data.decode()
    data = find(data)
    data = data.split(',')


    screen.fill((102, 204, 0))
    pygame.draw.rect(screen, colours[my_colour], (my_x,my_y,TILE,TILE))
    if DIR == 0:
        pygame.draw.line(screen, 'white', (my_x+16, my_y-10), (my_x+16, my_y+20), 4)
    if DIR == 1:
        pygame.draw.line(screen, 'white', (my_x+16, my_y-10), (my_x+16, my_y+20), 4)
    if DIR == 2:
        pygame.draw.line(screen, 'white', (my_x+16, my_y+50), (my_x+16, my_y+20), 4)
    if DIR == 3:
        pygame.draw.line(screen, 'white', (my_x+48, my_y+16), (my_x+16, my_y+16), 4)
    if DIR == 4:
        pygame.draw.line(screen, 'white', (my_x-16, my_y+16), (my_x+16, my_y+16), 4)

    if data != ['']:
        draw_opponents(data)
    for bullet in bullets:
        bullet.draw()
    pygame.display.update()
pygame.quit()
sys.exit()

