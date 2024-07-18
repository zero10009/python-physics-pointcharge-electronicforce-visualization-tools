import pygame
import math
from fractions import Fraction

# 초기화 및 설정
pygame.init()

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# 화면 크기 (확대)
WIDTH, HEIGHT = 1800, 1200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("점전하 전기력 시각화")

# 폰트 설정
def get_font(size):
    return pygame.font.Font('소야논8.ttf', size)

font_size = 30
small_font_size = 24
font = get_font(font_size)
global small_font
small_font = get_font(small_font_size)
global info_font
info_font = get_font(20)
global i_button_font_size
i_button_font_size = 24

class PointCharge:
    def __init__(self, x, q):
        self.x = x
        self.q = q
        self.show_force = True # 전기력 표시 여부 상태

    def toggle_force_display(self):
        self.show_force = not self.show_force

    def render_charge(self, screen, scale, offset):
        charge_pos = ((self.x * 60 * scale) + WIDTH // 2 + offset, HEIGHT // 2)
        color = GRAY if not self.show_force else BLACK # 전기력 표시 여부에 따라 색상 변경
        pygame.draw.circle(screen, color, charge_pos, int(10 * scale))
        # 전하량 텍스트 폰트 크기 조정
        current_font = get_font(int(small_font_size * scale))
        text = current_font.render(f"{self.q}Q", True, BLACK) # 전하량은 항상 표시
        # 텍스트 위치 계산
        text_rect = text.get_rect(center=(charge_pos[0], charge_pos[1] + 20 * scale))
        # 텍스트 그리기
        screen.blit(text, text_rect)

class ElectricFieldCalculator:
    def __init__(self, x_min, x_max):
        self.charges = []
        self.x_min = x_min
        self.x_max = x_max
        self.show_fraction = False
        self.show_negative_force = False  # 음의 부호 표시 여부 상태 추가

    def toggle_force_sign(self):
        self.show_negative_force = not self.show_negative_force

    def add_charge(self, x, q):
        if x < self.x_min or x > self.x_max:
            return
        for charge in self.charges:
            if charge.x == x:
                return
        self.charges.append(PointCharge(x, q))

    def remove_charge(self, x):
        self.charges = [charge for charge in self.charges if charge.x != x]

    def toggle_force_display(self, x):
        for charge in self.charges:
            if charge.x == x:
                charge.toggle_force_display()

    def toggle_fraction(self):
        self.show_fraction = not self.show_fraction

    def calculate_forces(self):
        forces = {charge: 0 for charge in self.charges}
        for i, charge1 in enumerate(self.charges):
            for j, charge2 in enumerate(self.charges):
                if i != j:
                    r = charge1.x - charge2.x
                    if r != 0:
                        F = charge1.q * charge2.q / (r ** 2)
                        direction = 1 if r > 0 else -1
                        forces[charge1] += F * direction
        return forces

    def draw_forces(self, screen, scale, offset):
        forces = self.calculate_forces()
        num_charges = len(self.charges)

        # Check if there are charges to avoid division by zero
        if num_charges > 0:
            font_scale = max(0.5, min(1.0, 10 / num_charges))  # 최소 0.5, 최대 1.0으로 제한
        else:
            font_scale = 1.0  # Default font scale if there are no charges

        for charge, force in forces.items():
            if not charge.show_force:
                continue  # 전기력 표시가 꺼져 있으면 표시하지 않음

            charge_pos = (charge.x * 60 * scale + WIDTH // 2 + offset, HEIGHT // 2)
            force_pos = (charge.x * 60 * scale + WIDTH // 2 + offset + int(30 * scale * (1 if force > 0 else -1)), HEIGHT // 2)

            if force > 0:
                text_pos = (force_pos[0] + 15 * scale, force_pos[1] - 30 * scale)
            else:
                text_pos = (force_pos[0] - 20 * scale, force_pos[1] - 30 * scale)

            if force != 0:
                color = RED if force > 0 else BLUE
                pygame.draw.line(screen, color, charge_pos, force_pos, int(2 * scale))
                self.draw_arrowhead(screen, color, force_pos, force > 0, scale)

                current_font = get_font(int(font_size * scale * font_scale))

                if self.show_fraction:
                    fraction = Fraction(force).limit_denominator()
                    numerator = abs(fraction.numerator)
                    denominator = abs(fraction.denominator)

                    # 정수 형태로 표현 가능한 경우
                    if denominator == 1:
                        text = current_font.render(f"{'-' if force < 0 and self.show_negative_force else ''}{numerator}F", True, BLACK)
                        text_rect = text.get_rect(center=text_pos)
                        screen.blit(text, text_rect)
                    else:
                        negative_sign = "-" if force < 0 and self.show_negative_force else ""
                        negative_sign_rendered = current_font.render(negative_sign, True, BLACK)
                        numerator_rendered = current_font.render(f"{numerator}", True, BLACK)
                        denominator_rendered = current_font.render(f"{denominator}", True, BLACK)

                        # 분자 및 분모의 너비 계산
                        num_width = numerator_rendered.get_width()
                        den_width = denominator_rendered.get_width()

                        # 분자와 분모의 높이 계산
                        num_height = numerator_rendered.get_height()
                        den_height = denominator_rendered.get_height()

                        # 분자와 분모 중 더 긴 쪽을 기준으로 막대기 기호의 길이 계산
                        bar_length = max(num_width, den_width)

                        # 막대기 기호 렌더링 위치 계산
                        bar_pos = (text_pos[0], text_pos[1] - num_height // 2)

                        # 분자 위치 계산
                        num_pos = (bar_pos[0] + (bar_length - num_width) // 2, bar_pos[1] - num_height - 5 * scale)

                        # 분모 위치 계산
                        den_pos = (bar_pos[0] + (bar_length - den_width) // 2, bar_pos[1] + 5 * scale)

                        # 분자 및 분모 렌더링
                        screen.blit(numerator_rendered, num_pos)
                        screen.blit(denominator_rendered, den_pos)

                        # 막대기 기호 렌더링
                        pygame.draw.line(screen, BLACK, bar_pos, (bar_pos[0] + bar_length, bar_pos[1]), int(2 * scale))

                        # F(비례기호) 텍스트 렌더링
                        f_text = current_font.render("F", True, BLACK)
                        f_text_pos = (bar_pos[0] + bar_length + 5 * scale, bar_pos[1] - num_height // 2)
                        screen.blit(f_text, f_text_pos)

                        # 음의 부호 렌더링
                        neg_sign_pos = (bar_pos[0] - negative_sign_rendered.get_width() - 5 * scale, bar_pos[1] - num_height // 2)
                        screen.blit(negative_sign_rendered, neg_sign_pos)
                else:
                    text = current_font.render(f"{'-' if force < 0 and self.show_negative_force else ''}{abs(force):.2f}F", True, BLACK)
                    text_rect = text.get_rect(center=text_pos)
                    screen.blit(text, text_rect)

    def draw_arrowhead(self, screen, color, position, right, scale):
        if right:
            points = [(position[0] + 15 * scale, position[1]), (position[0], position[1] - 5 * scale), (position[0], position[1] + 5 * scale)]
        else:
            points = [(position[0] - 15 * scale, position[1]), (position[0], position[1] - 5 * scale), (position[0], position[1] + 5 * scale)]
        pygame.draw.polygon(screen, color, points)

# X축 그리기 함수
def draw_x_axis(screen, scale, offset):
    current_font = get_font(int(small_font_size * scale))
    for x in range(-10, 11):
        x_center = x * 60 * scale + WIDTH // 2 + offset
        pygame.draw.line(screen, BLACK, (x_center, HEIGHT // 2 - 10 * scale), (x_center, HEIGHT // 2 + 10 * scale), 1)
        label = current_font.render(str(x), True, BLACK)
        label_rect = label.get_rect(center=(x_center, HEIGHT // 2 + 60 * scale))
        screen.blit(label, label_rect)
    pygame.draw.line(screen, BLACK, (WIDTH // 2 - 600 * scale + offset, HEIGHT // 2), (WIDTH // 2 + 600 * scale + offset, HEIGHT // 2), 1)

class InputBox:
    def __init__(self, x, y, w, h, text='', label=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLACK
        self.text = text
        self.font_size = h - 20 # 입력 상자의 높이에 맞게 폰트 크기를 조정
        self.font = get_font(self.font_size)
        self.label_font = get_font(int(small_font_size * 1.5)) # 폰트 크기를 1.5배로 설정
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False
        self.initial_text = text # 초기 입력값을 저장해둠
        self.label = label

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 입력 상자를 클릭하면 초기화하고 활성화 상태로 변경
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.text = '' # 입력 초기화
            else:
                self.active = False
            self.color = RED if self.active else BLACK
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = BLACK
                elif event.key == pygame.K_BACKSPACE:
                    # 백스페이스 키를 연속적으로 처리
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)

    def draw(self, screen):
        # 사각형 테두리를 둥글게 그리기
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=5)
        # 입력 박스 내의 텍스트가 넘칠 경우, 줄이는 처리
        visible_text = self.text
        while self.font.render(visible_text, True, self.color).get_width() > self.rect.width - 10:
            visible_text = visible_text[1:]
        # 텍스트 그리기
        self.txt_surface = self.font.render(visible_text, True, self.color)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # 레이블 그리기
        if self.label:
            label = self.label_font.render(self.label, True, BLACK)
            screen.blit(label, (self.rect.x - label.get_width() - 20, self.rect.y + (self.rect.height - label.get_height()) // 2))

    def get_text(self):
        return self.text if self.text else self.initial_text

def render_text_file(screen, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    y = HEIGHT // 4 # 시작 y 좌표
    for line in lines:
        rendered_line = info_font.render(line.strip(), True, BLACK)
        screen.blit(rendered_line, (50, y))
        y += 25 # 줄 간격

def main():
    running = True
    efc = ElectricFieldCalculator(-10, 10)
    input_box = InputBox(WIDTH // 1.9, 100, 100, 50, label="전하량 설정 :")
    info_button_rect = pygame.Rect(WIDTH // 1.9 + 120, 100, 50, 50) # i 버튼 위치와 크기 설정
    display_readme = False
    scale = 1
    original_scale = 1
    ctrl_pressed = False
    grab_mode = False
    grab_start_pos = None
    view_offset = 0
    global i_button_font_size
    global i_button_font  # 전역 변수로 선언

    # i_button_font 초기화
    i_button_font = get_font(i_button_font_size)

    while running:
        screen.fill(WHITE)
        draw_x_axis(screen, scale, view_offset)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if info_button_rect.collidepoint(event.pos):
                    display_readme = not display_readme
                elif grab_mode:
                    grab_start_pos = event.pos
                if abs(y - HEIGHT // 2) < 40 * scale:
                    charge_x = round((x - WIDTH // 2 - view_offset) / (60 * scale))
                    if -10 <= charge_x <= 10:
                        if event.button == 1:
                            matching_charge = next((c for c in efc.charges if c.x == charge_x), None)
                            if matching_charge:
                                efc.toggle_force_display(charge_x)
                            else:
                                try:
                                    q = float(input_box.get_text())
                                except ValueError:
                                    q = 1
                                efc.add_charge(charge_x, q)
                        elif event.button == 3:
                            efc.remove_charge(charge_x)
            elif event.type == pygame.MOUSEBUTTONUP:
                if grab_mode:
                    grab_start_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if grab_mode and grab_start_pos:
                    dx = event.pos[0] - grab_start_pos[0]
                    view_offset += dx
                    grab_start_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_n:
                    efc.toggle_force_sign()
                elif event.key == pygame.K_f:
                    efc.toggle_fraction()
                elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    ctrl_pressed = True
                elif event.key == pygame.K_i:
                    display_readme = not display_readme
                elif event.key == pygame.K_o:
                    scale = original_scale
                    view_offset = 0
                elif event.key == pygame.K_g:
                    grab_mode = not grab_mode
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    ctrl_pressed = False
            elif event.type == pygame.MOUSEWHEEL:
                if ctrl_pressed:
                    if event.y > 0:
                        scale *= 1.1
                    elif event.y < 0:
                        scale /= 1.1
                    scale = max(1, scale) # 최소 scale을 1(기본값)로 제한
                    scale = min(10, scale) # 최대 scale을 10으로 제한
                    global font
                    font = get_font(int(font_size * scale))
                    global small_font
                    small_font = get_font(int(small_font_size * scale))
                    # 'i' 버튼의 글자 크기를 고정하기 위해 별도의 font 유지
                    i_button_font = get_font(i_button_font_size)
            input_box.handle_event(event)
        efc.draw_forces(screen, scale, view_offset)
        for charge in efc.charges:
            charge.render_charge(screen, scale, view_offset)
        input_box.draw(screen)
        # i 버튼 그리기
        pygame.draw.rect(screen, BLACK, info_button_rect, 2, border_radius=5)
        i_text = i_button_font.render("i", True, BLACK) # i 버튼의 글자 크기 설정
        screen.blit(i_text, (info_button_rect.x + (info_button_rect.width - i_text.get_width()) // 2, info_button_rect.y + (info_button_rect.height - i_text.get_height()) // 2))
        if display_readme:
            render_text_file(screen, 'readme.txt')
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
