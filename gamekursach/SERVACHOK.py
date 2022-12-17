import socket
import pygame
import random

WIDTH_ROOM, HEIGHT_ROOM = 800, 600
WITHH_SERV_ROOM, HEIGHT_SERV_ROOM = 800, 600
FPS = 60
TILE = 32

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('localhost', 10000))
main_socket.setblocking(0)
main_socket.listen(5)
pygame.display.set_caption('server window')
print('сокет создан')

pygame.init()
screen = pygame.display.set_mode((WITHH_SERV_ROOM, HEIGHT_SERV_ROOM))
clock = pygame.time.Clock()
server_works = True
chage_speed = True
colours = {'0': (255, 0, 0), '1': (255, 20, 147), '2': (255, 69, 0), '3': (255, 255, 0), '4': (255, 0, 125),
           '5': (218, 112, 214), '6': (128, 0, 128), '7': (128, 0, 0), '8': (0, 255, 0), '9': (0, 0, 139),
           '10': (123, 104, 238)}
bullets = []
players = []


def find(s):
    begin = None
    for i in range(len(s)):
        if s[i] == '[':
            begin = i
        if s[i] == '>':
            end = i
            res = s[begin+1:end]
            res = list(map(int, res.split(',')))
            return res
    return ''


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


class Bullet():
    def __init__(self, player, x, y, dx, dy, damage):
        bullets.append(self)
        self.player = player
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.x < 0 or self.x > WIDTH_ROOM or self.y > HEIGHT_ROOM:
            bullets.remove(self)
        else:
            for player in players:
                if player.number != self.player or player.rect.collidepoint(self.x, self.y):
                    player.damage(self.damage)
                    bullets.remove(self)
                    break

    def draw(self):
        pygame.draw.circle(screen, 'red', (self.x, self.y), 2)


class Player():
    def __init__(self, conn, addr, colour, x, y, a, number):
        self.conn = conn
        self.addr = addr
        self.type = 'tank'
        self.colour = colour
        self.x = x
        self.y = y
        self.a = a
        self.errors = 0
        self.mvs = 5
        self.speed_x = 0
        self.speed_y = 0
        self.w_vision = 5000
        self.h_vision = 5000
        self.bulletDamage = 1
        self.bulletSpeed = 1
        self.hp = 1
        self.rect = pygame.Rect(x, y, a//2, a//2)
        self.directs = 0
        self.number = number

    def change_speed(self, data):
        if data == [0, -1]:
                self.speed_x -= self.mvs
                self.speed_y = 0
                self.directs = 4
        elif data == [1, 0]:
                self.speed_x += self.mvs
                self.speed_y = 0
                self.directs = 3
        elif data == [0, 1]:
                self.speed_y -= self.mvs
                self.speed_x = 0
                self.directs = 1
        elif data == [-1, 0]:
                self.speed_y += self.mvs
                self.speed_x = 0
                self.directs = 2
        elif data == [1, 1]:
            dx = dirrects(self.directs) * self.bulletSpeed
            dy = directs(self.directs) * self.bulletSpeed
            Bullet(self.number, self.x + 16, self.y + 16, dx, dy, self.bulletDamage)
        elif data == [0, 0]:
            self.speed_x = 0
            self.speed_y = 0

    def update(self):
        if self.x + TILE < WIDTH_ROOM:
            self.x += self.speed_x
        if self.y + TILE < HEIGHT_ROOM:
            self.y += self.speed_y
        if self.x + TILE >= WIDTH_ROOM:
            self.x -= 20
        if self.x + TILE <= 16:
            self.x += 20
        if self.y + TILE >= HEIGHT_ROOM:
            self.y -= 20
        if self.y + TILE <= 16:
            self.y += 20
    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            players.remove(self)
            print(self.colour, 'dead')
while server_works:
    clock.tick(FPS)
    for bullet in bullets:
        bullet.update()
    try:
        new_socket, addr = main_socket.accept()
        print('Игрок', addr)
        new_socket.setblocking(0)
        new_player = Player(new_socket, addr, str(random.randint(0, 10)),
                            random.randint(0, WIDTH_ROOM),
                            random.randint(0, HEIGHT_ROOM),  TILE, random.randint(0, 100000))
        new_player.conn.send(new_player.colour.encode())
        x_ = str(new_player.x)
        y_ = str(new_player.y)
        new_player.conn.send(x_.encode())
        new_player.conn.send(y_.encode())
        players.append(new_player)
        print(new_player.number)


    except:
        pass

    for player in players:
        try:
            data = player.conn.recv(2**30)
            data = data.decode()
            print(data)
            data = find(data)
            player.change_speed(data)
            pygame.display.update()

        except:
            player.update()



    visible_tanks = [[] for i in range(len(players))]


    for i in range(len(players)):
        for j in range(i+1, len(players)):
            dist_x = players[j].x - players[i].x
            dist_y = players[j].y - players[i].y
            if ((abs(dist_x) <= (players[i].w_vision)*2 + players[j].a) and
                    (abs(dist_y) <= (players[i].h_vision)*2 + players[j].a)):
                x_ = str(round(dist_x))
                y_ = str(round(dist_y))
                a_ = str(round(players[j].a))
                c_ = players[j].colour
                d_ = str(players[j].directs)
                visible_tanks[i].append(x_+' '+y_+' '+a_+' '+c_+' '+d_)
                if ((abs(dist_x) <= (players[j].w_vision)*2 + players[i].a) and
                        (abs(dist_y) <= (players[j].h_vision)*2 + players[i].a)):
                    x_ = str(round(-dist_x))
                    y_ = str(round(-dist_y))
                    a_ = str(round(players[i].a))
                    c_ = players[i].colour
                    d_ = str(players[i].directs)
                    visible_tanks[j].append(x_+' '+y_+' '+a_+' '+c_+' '+d_)

    otvets = ['' for i in range(len(players))]
    for i in range(len(players)):
        otvets[i] = '['+(','.join(visible_tanks[i])) + ']'

    for i in range(len(players)):
        try:
            players[i].conn.send(otvets[i].encode())
            players[i].errors = 0
        except:
            players[i].errors += 1
    for player in players:
        if player.errors == 100:
            player.conn.close()
            players.remove(player)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server_works = False
    screen.fill('black')
    for player in players:
        x = player.x
        y = player.y
        a = player.a
        c = colours[player.colour]
        pygame.draw.rect(screen, c, (x, y, TILE, TILE))
        if player.directs == 0:
            pygame.draw.line(screen, 'white', (player.x + 16, player.y - 10), (player.x + 16, player.y + 20), 4)
        if player.directs == 1:
            pygame.draw.line(screen, 'white', (player.x + 16, player.y - 10), (player.x + 16, player.y + 20), 4)
        elif player.directs == 2:
            pygame.draw.line(screen, 'white', (player.x + 16, player.y + 50), (player.x + 16, player.y + 20), 4)
        elif player.directs == 3:
            pygame.draw.line(screen, 'white', (player.x + 48, player.y+16), (player.x+16, player.y+16), 4)
        elif player.directs == 4:
            pygame.draw.line(screen, 'white', (player.x - 16, player.y+16), (player.x+16, player.y+16), 4)
    for bullet in bullets:
        bullet.draw()
    pygame.display.update()


pygame.quit()
main_socket.close()
