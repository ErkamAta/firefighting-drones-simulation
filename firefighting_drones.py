import pygame
import random
import math

pygame.init()
WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Yangın Söndürme Droneleri Sürüsü")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
AGENT_COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (0, 255, 255), (255, 0, 255),
    (100, 100, 255), (255, 100, 100), (100, 255, 100), (200, 200, 0),
    (150, 50, 200), (50, 200, 150), (200, 150, 50)
]
WATER_COLOR = (0, 120, 255)

MIN_AGENT_DIST = 35
MAX_YANGIN = 5
YANGIN_ARALIK = 300

hizli_yanginlar = random.sample(range(MAX_YANGIN), 2)

class Ajan:
    def __init__(self, color):
        self.radius = 15
        self.isi_radius = 80
        self.cevre_radius = 40
        placed = False
        while not placed:
            self.x = random.randint(self.radius+40, WIDTH - self.radius-40)
            self.y = random.randint(self.radius+40, HEIGHT - self.radius-40)
            placed = True
            for a in ajanlar:
                if math.hypot(self.x - a.x, self.y - a.y) < MIN_AGENT_DIST*2:
                    placed = False
                    break
        self.color = color
        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])

    def move(self, ajanlar, yangin_list, ayrilma_modu):
        for diger in ajanlar:
            if diger is not self:
                mesafe = math.hypot(self.x - diger.x, self.y - diger.y)
                if ayrilma_modu:
                    if mesafe < MIN_AGENT_DIST * 3:
                        self.dx -= (diger.x - self.x) * 0.01
                        self.dy -= (diger.y - self.y) * 0.01
                else:
                    if mesafe < MIN_AGENT_DIST:
                        self.dx -= (diger.x - self.x) * 0.01
                        self.dy -= (diger.y - self.y) * 0.01
                    elif mesafe < self.cevre_radius:
                        self.dx += (diger.x - self.x) * 0.005
                        self.dy += (diger.y - self.y) * 0.005

        for yangin in yangin_list:
            if yangin["aktif"]:
                yangin_cx = yangin["x"] + yangin["w"] // 2
                yangin_cy = yangin["y"] + yangin["h"] // 2
                mesafe = math.hypot(self.x - yangin_cx, self.y - yangin_cy)
                if mesafe < 250:
                    self.dx += (yangin_cx - self.x) * 0.01
                    self.dy += (yangin_cy - self.y) * 0.01

        self.dx = max(-2, min(2, self.dx))
        self.dy = max(-2, min(2, self.dy))
        self.x += int(self.dx)
        self.y += int(self.dy)

        if self.x < self.radius+40 or self.x > WIDTH - self.radius-40:
            self.dx *= -1
            self.x = max(self.radius+40, min(WIDTH - self.radius-40, self.x))
        if self.y < self.radius+40 or self.y > HEIGHT - self.radius-40:
            self.dy *= -1
            self.y = max(self.radius+40, min(HEIGHT - self.radius-40, self.y))

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 200, 200), (self.x, self.y), self.isi_radius, 1)
        pygame.draw.circle(surface, (200, 220, 220), (self.x, self.y), self.cevre_radius, 1)
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)

def su_fiskirtma_animasyonu(surface, drone_x, drone_y, yangin_x, yangin_y):
    # Başlangıç noktası: ajan ısı çemberinin dışı
    baslangic_x = drone_x + (yangin_x - drone_x) * 80 / math.hypot(yangin_x - drone_x, yangin_y - drone_y)
    baslangic_y = drone_y + (yangin_y - drone_y) * 80 / math.hypot(yangin_x - drone_x, yangin_y - drone_y)
    damla_sayisi = 8
    for i in range(1, damla_sayisi + 1):
        t = i / damla_sayisi
        x = int(baslangic_x + t * (yangin_x - baslangic_x) + math.sin(i * 2) * 10)
        y = int(baslangic_y + t * (yangin_y - baslangic_y) + math.cos(i * 2) * 10)
        pygame.draw.circle(surface, WATER_COLOR, (x, y), 6)

ajanlar = []
for color in AGENT_COLORS:
    ajanlar.append(Ajan(color))

def yeni_yangin(index):
    hizli = index in hizli_yanginlar
    return {
        "x": random.randint(300, WIDTH-300),
        "y": random.randint(200, HEIGHT-200),
        "w": 80,
        "h": 60,
        "aktif": True,
        "sundurme": False,
        "renk": [255, 180, 120],
        "yayilma_hizi": 2.0 if hizli else 0.7,
        "index": index
    }

yangin_list = []
yangin_sayisi = 0
ayrilma_modu = False
frame_count = 0

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (30, 30, WIDTH-60, HEIGHT-60), 5)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    frame_count += 1
    if yangin_sayisi < MAX_YANGIN:
        if frame_count % YANGIN_ARALIK == 0 or (frame_count % (YANGIN_ARALIK//2) == 0 and random.random() < 0.3):
            if random.random() < 0.5 and yangin_sayisi < MAX_YANGIN-1:
                yangin_list.append(yeni_yangin(yangin_sayisi))
                yangin_sayisi += 1
                yangin_list.append(yeni_yangin(yangin_sayisi))
                yangin_sayisi += 1
            else:
                yangin_list.append(yeni_yangin(yangin_sayisi))
                yangin_sayisi += 1

    aktif_yanginler = [y for y in yangin_list if y["aktif"]]
    yangin_kontrol_edilemez = False

    for yangin in aktif_yanginler:
        mudahale_sayisi = 0
        gereken_drone = 3
        mudahale_ajanlar = []
        yangin_cx = yangin["x"] + yangin["w"] // 2
        yangin_cy = yangin["y"] + yangin["h"] // 2
        yangin_alan = yangin["w"] * yangin["h"]
        cerceve_alan = (WIDTH-60) * (HEIGHT-60)
        oran = yangin_alan / cerceve_alan

        if oran < 0.10:
            gereken_drone = 3
            drone_etkisi = 0.07
        elif oran < 0.20:
            gereken_drone = 5
            drone_etkisi = 0.05
        elif oran < 0.30:
            gereken_drone = 7
            drone_etkisi = 0.03
        elif oran < 0.40:
            gereken_drone = 10
            drone_etkisi = 0.02
        else:
            yangin_kontrol_edilemez = True

        for ajan in ajanlar:
            mesafe = math.hypot(ajan.x - yangin_cx, ajan.y - yangin_cy)
            if mesafe < yangin["w"]//2 + ajan.radius + 10:
                mudahale_sayisi += 1
                mudahale_ajanlar.append(ajan)
                su_fiskirtma_animasyonu(screen, ajan.x, ajan.y, yangin_cx, yangin_cy)

        yayilma = max(0.1, yangin["yayilma_hizi"] - mudahale_sayisi * drone_etkisi)
        yangin["w"] += yayilma
        yangin["h"] += yayilma
        yangin["x"] -= yayilma/2
        yangin["y"] -= yayilma/2

        if mudahale_sayisi >= gereken_drone and not yangin_kontrol_edilemez:
            yangin["sundurme"] = True

        if yangin["sundurme"]:
            yangin["renk"][0] = max(100, yangin["renk"][0] - 2)
            yangin["renk"][1] = max(150, yangin["renk"][1] - 2)
            yangin["renk"][2] = max(100, yangin["renk"][2] - 2)
            if yangin["renk"][0] == 100 and yangin["renk"][1] == 150 and yangin["renk"][2] == 100:
                yangin["aktif"] = False
                # Müdahale eden droneler ayrılma moduna geçsin
                for ajan in mudahale_ajanlar:
                    ajan.dx = random.choice([-2, 2])
                    ajan.dy = random.choice([-2, 2])

        pygame.draw.rect(screen, tuple(yangin["renk"]), (yangin["x"], yangin["y"], yangin["w"], yangin["h"]))

        font = pygame.font.SysFont(None, 32)
        if yangin_kontrol_edilemez:
            text = font.render(f"Yangın {yangin['index']+1}: Kontrol edilemiyor!", True, (200, 0, 0))
            screen.blit(text, (40, 40 + yangin['index']*60))
            info = font.render(f"Oran: %{int(oran*100)} | Müdahale: {mudahale_sayisi}", True, (0, 0, 0))
            screen.blit(info, (40, 70 + yangin['index']*60))
        elif yangin["aktif"]:
            text = font.render(f"Yangın {yangin['index']+1}: Müdahale: {mudahale_sayisi} | Gereken: {gereken_drone} | Oran: %{int(oran*100)}", True, (0, 0, 0))
            screen.blit(text, (40, 40 + yangin['index']*60))
        else:
            text = font.render(f"Yangın {yangin['index']+1}: SÖNDÜRÜLDÜ", True, (0, 0, 0))
            screen.blit(text, (40, 40 + yangin['index']*60))

    if yangin_sayisi >= MAX_YANGIN and not any([y["aktif"] for y in yangin_list]):
        ayrilma_modu = True

    for ajan in ajanlar:
        ajan.move(ajanlar, aktif_yanginler, ayrilma_modu)
        ajan.draw(screen)

    pygame.display.flip()
    clock.tick(60)

# Simülasyon Sonlandırıldı yazısı
screen.fill(WHITE)
font = pygame.font.SysFont(None, 64)
msg = font.render("Simülasyon Sonlandırıldı", True, BLACK)
screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
pygame.display.flip()

# Bekleme
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            waiting = False

pygame.quit()
exit()