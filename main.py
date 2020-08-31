import pygame
import os
import random

pygame.font.init()

chiều_rộng, chiều_dài = 750, 750
cửa_sổ = pygame.display.set_mode((chiều_rộng, chiều_dài))
pygame.display.set_caption("Space Shooter")

# Load images
thuyền_đỏ = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
thuyền_xanh_lá_cây = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
thuyền_xanh_da_trời = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

  # Player
thuyền_người_chơi = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
laser_đỏ = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
laser_xanh_lá_cây = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
laser_xanh_da_trời = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
laser_vàng = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
Background = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (chiều_rộng, chiều_dài))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(height >= self.y >= -40)

    def collision(self, obj):
        return va_chạm(self, obj)

class Thuyền:
    COOLDOWN = 30

    def __init__(self, x, y, máu=100):
        self.x = x
        self.y = y
        self.máu = máu
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, vật):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(chiều_dài):
                self.lasers.remove(laser)
            elif laser.collision(vật):
                vật.máu -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def bắn(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Người_Chơi(Thuyền):
    def __init__(self, x, y, máu=100):
        super().__init__(x, y, máu)
        self.ship_img = thuyền_người_chơi
        self.laser_img = laser_vàng
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.nhiều_máu = máu

    def move_lasers(self, vel, nhiều_vật):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(chiều_dài):
                self.lasers.remove(laser)
            else:
                for vật in nhiều_vật:
                    if laser.collision(vật):
                        nhiều_vật.remove(vật)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.thanh_máu(window)

    def thanh_máu(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,  255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.máu/self.nhiều_máu), 10))


class Kẻ_thù(Thuyền):
    COLOR_MAP = {
                "red": (thuyền_đỏ, laser_đỏ),
                "green": (thuyền_xanh_lá_cây, laser_xanh_lá_cây),
                "blue": (thuyền_xanh_da_trời, laser_xanh_da_trời)
                }

    def __init__(self, x, y, color, máu=100):
        super().__init__(x, y, máu)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def di_chuyển(self, vel):
        self.y += vel

    def bắn(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def va_chạm(vật1, vật2):
    offset_x = vật2.x - vật1.x
    offset_y = vật2.y - vật1.y
    return vật1.mask.overlap(vật2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    FPS = 120
    level = 0
    mạng = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    kẻ_thù_liên_tiếp = []
    wave_length = 5
    tốc_độ_kẻ_thù = 1

    tốc_độ_người_chơi = 5
    tốc_độ_laser = 5

    người_chơi = Người_Chơi(300, 630)

    clock = pygame.time.Clock()

    Thua = False
    lost_count = 0

    def redraw_window():
        cửa_sổ.blit(Background, (0, 0))
        # draw text
        mạng_label = main_font.render(f"Lives: {mạng}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        cửa_sổ.blit(mạng_label, (10, 10))
        cửa_sổ.blit(level_label, (chiều_rộng - level_label.get_width() - 10, 10))

        for kẻ_thù in kẻ_thù_liên_tiếp:
            kẻ_thù.draw(cửa_sổ)

        người_chơi.draw(cửa_sổ)

        if Thua:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            cửa_sổ.blit(lost_label, (chiều_rộng/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if mạng <= 0 or người_chơi.máu <= 0:
            Thua = True
            lost_count += 1

        if Thua:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(kẻ_thù_liên_tiếp) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                kẻ_thù = Kẻ_thù(random.randrange(50, chiều_rộng-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                kẻ_thù_liên_tiếp.append(kẻ_thù)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        # Di chuyển
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and người_chơi.x - tốc_độ_người_chơi > 0:
            người_chơi.x -= tốc_độ_người_chơi
        if keys[pygame.K_d] and người_chơi.x + tốc_độ_người_chơi + người_chơi.get_width() < chiều_rộng:
            người_chơi.x += tốc_độ_người_chơi
        if keys[pygame.K_w] and người_chơi.y - tốc_độ_người_chơi > 0:
            người_chơi.y -= tốc_độ_người_chơi
        if keys[pygame.K_s] and người_chơi.y + tốc_độ_người_chơi + người_chơi.get_height() + 15 < chiều_dài:
            người_chơi.y += tốc_độ_người_chơi
        if keys[pygame.K_SPACE]:
            người_chơi.bắn()

        for kẻ_thù in kẻ_thù_liên_tiếp[:]:
            kẻ_thù.di_chuyển(tốc_độ_kẻ_thù)
            kẻ_thù.move_lasers(tốc_độ_laser, người_chơi)

            if random.randrange(0, 2*60) == 1:
                kẻ_thù.bắn()

            if va_chạm(kẻ_thù, người_chơi):
                người_chơi.máu -= 10
                kẻ_thù_liên_tiếp.remove(kẻ_thù)
            elif kẻ_thù.y + kẻ_thù.get_height() > chiều_dài:
                mạng -= 1
                kẻ_thù_liên_tiếp.remove(kẻ_thù)

        người_chơi.move_lasers(-tốc_độ_laser, kẻ_thù_liên_tiếp)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        cửa_sổ.blit(Background, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        cửa_sổ.blit(title_label, (chiều_rộng/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
