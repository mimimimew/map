import pygame
import sys
import time
import os
import math
import json
from pygame.locals import *
from datetime import datetime


# ================= 公共字体配置 ================
if hasattr(sys, '_MEIPASS'):
    # Running from PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in normal Python environment
    base_path = os.path.dirname(__file__)

FONT_PATH = os.path.join(base_path, "simhei.ttf")
def get_font(size):
    return pygame.font.Font(FONT_PATH, size)

# ================= 第一部分（路径规划实验）的配置 =================
EXP_SCREEN_SIZE = (1920, 1080)  # 第一部分整体窗口尺寸
GRID_SIZE = 49
CELL_SIZE = 15
GAME_SIZE = GRID_SIZE * CELL_SIZE  # 735

EXP_COLORS = {
    'background': (255, 255, 255),
    'panel_bg': (245, 245, 245),
    'text': (51, 51, 51),
    'button': (79, 193, 233),
    'button_hover': (69, 183, 223),
    'grid': (211, 211, 211),
    'start': (0, 0, 255),
    'current': (255, 0, 0),
    'obstacle': (169, 169, 169)
}

MAP_CONFIGS = [
    {  # 练习地图
        'name': "练习地图",
        'start': (7, 42),
        'obstacles': []  # 无障碍物
    }
]

class ExperimentData:
    def __init__(self):
        self.reset()
    def reset(self):
        self.current_map = 0
        self.paths = [[] for _ in range(1)]
        self.start_times = [0] * 1
        self.end_times = [0] * 1
    def add_step(self, pos):
        pass
    def undo_step(self):
        pass

class ExperimentGame:
    def __init__(self, parent_screen, data_manager, map_config):
        self.parent_screen = parent_screen
        self.data = data_manager
        self.config = map_config
        self.game_surface = pygame.Surface((GAME_SIZE, GAME_SIZE))
        self.font = get_font(20)
        self.current_pos = list(self.config['start'])
        self.path = [tuple(self.current_pos)]
        self.active = False
        self.finished = False
    def convert_coords(self, x, y):
        return (x * CELL_SIZE, (GRID_SIZE - y) * CELL_SIZE)
    def draw_grid(self):
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(self.game_surface, EXP_COLORS['grid'],
                             (i * CELL_SIZE, 0), (i * CELL_SIZE, GAME_SIZE))
            pygame.draw.line(self.game_surface, EXP_COLORS['grid'],
                             (0, i * CELL_SIZE), (GAME_SIZE, i * CELL_SIZE))
    def draw_obstacles(self):
        for x, y, w, h in self.config['obstacles']:
            rect_x = x * CELL_SIZE
            rect_y = (GRID_SIZE - y - h) * CELL_SIZE
            pygame.draw.rect(self.game_surface, EXP_COLORS['obstacle'],
                             (rect_x, rect_y, w * CELL_SIZE, h * CELL_SIZE))
    def draw_points(self):
        start_pos = self.convert_coords(*self.config['start'])
        pygame.draw.circle(self.game_surface, EXP_COLORS['start'], start_pos, 8)
        current_pos = self.convert_coords(*self.current_pos)
        pygame.draw.circle(self.game_surface, EXP_COLORS['current'], current_pos, 8)
    def draw_path(self):
        if len(self.path) > 1:
            points = [self.convert_coords(x, y) for x, y in self.path]
            pygame.draw.lines(self.game_surface, (0, 0, 0), False, points, 3)
    def is_obstructed(self, x, y):
        for ox, oy, w, h in self.config['obstacles']:
            if ox <= x < ox + w and oy <= y < oy + h:
                return True
        return False
    def handle_input(self, events):
        if not self.active or self.finished:
            return
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    if len(self.path) > 1:
                        self.path.pop()
                        self.current_pos = list(self.path[-1])
                    return
                dx, dy = 0, 0
                if event.key == K_UP:
                    dy = 1
                elif event.key == K_DOWN:
                    dy = -1
                elif event.key == K_LEFT:
                    dx = -1
                elif event.key == K_RIGHT:
                    dx = 1
                elif event.key == K_ESCAPE:
                    self.finished = True
                    return
                else:
                    return
                new_x = self.current_pos[0] + dx
                new_y = self.current_pos[1] + dy
                if self.is_obstructed(new_x, new_y):
                    return
                if not (0 <= new_x <= GRID_SIZE and 0 <= new_y <= GRID_SIZE):
                    return
                self.current_pos = [new_x, new_y]
                self.path.append(tuple(self.current_pos))
    def update(self, events):
        self.handle_input(events)
        self.game_surface.fill(EXP_COLORS['background'])
        self.draw_grid()
        self.draw_obstacles()
        self.draw_points()
        self.draw_path()

class GamePage:
    def __init__(self, title, content, map_index=0, is_game=False):
        self.title = title
        self.content = content
        self.map_index = map_index
        self.is_game = is_game
        self.font = get_font(24)
        self.title_font = get_font(36)
        self.game_instance = None
    def draw_full_text_page(self, screen):
        screen.fill(EXP_COLORS['panel_bg'])
        title_surf = self.title_font.render(self.title, True, EXP_COLORS['text'])
        screen.blit(title_surf, (50, 50))
        y = 150
        for line in self.content.split('\n'):
            text_surf = self.font.render(line, True, EXP_COLORS['text'])
            screen.blit(text_surf, (50, y))
            y += 30
        btn_width = 180
        btn_rect = pygame.Rect(1000, 700, btn_width, 60)
        mouse_pos = pygame.mouse.get_pos()
        btn_color = EXP_COLORS['button_hover'] if btn_rect.collidepoint(mouse_pos) else EXP_COLORS['button']
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=8)
        text_surf = self.font.render("下一页", True, (255, 255, 255))
        screen.blit(text_surf, (btn_rect.x + 50, btn_rect.y + 15))
    def draw_panel(self, screen):
        if self.is_game:
            panel = pygame.Surface((400, 800))
            panel.fill(EXP_COLORS['panel_bg'])
            title_surf = self.title_font.render(self.title, True, EXP_COLORS['text'])
            panel.blit(title_surf, (20, 20))
            y = 100
            for line in self.content.split('\n'):
                text_surf = self.font.render(line, True, EXP_COLORS['text'])
                panel.blit(text_surf, (20, y))
                y += 30
            btn_width = 160
            btn_rect = pygame.Rect(220, 700, btn_width, 60)
            mouse_pos = pygame.mouse.get_pos()
            panel_mouse = (mouse_pos[0] - 800, mouse_pos[1])
            btn_color = EXP_COLORS['button_hover'] if btn_rect.collidepoint(panel_mouse) else EXP_COLORS['button']
            pygame.draw.rect(panel, btn_color, btn_rect, border_radius=8)
            btn_text = "开始规划" if self.map_index > 0 else "开始"
            text_surf = self.font.render(btn_text, True, (255, 255, 255))
            panel.blit(text_surf, (btn_rect.x + 40, btn_rect.y + 15))
            screen.blit(panel, (800, 0))
        else:
            self.draw_full_text_page(screen)
    def update(self, screen, data, events):
        if self.is_game:
            if not self.game_instance:
                self.game_instance = ExperimentGame(screen, data, MAP_CONFIGS[self.map_index])
            if self.game_instance and not self.game_instance.finished:
                self.game_instance.update(events)
                screen.blit(self.game_instance.game_surface, (0, 0))
                return False
        return True

class ExperimentScene:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.data = ExperimentData()
        self.pages = [
            GamePage("欢迎页", "欢迎参与路径规划实验！"),
            GamePage("任务说明",
                     "您的任务是规划网格地图中，绘制一条从起点到目标点的路径。\n\n"
                     "本次实验一共会有四组网格地图需要完成。在实验过程中，我们将指定一个目标点，\n"
                     "您需要根据该目标点设计路径，并通过路径的设计来尽可能让对手猜不出您的真实目标。\n\n"),
            GamePage("练习阶段",
                     "操作说明：\n"
                     "1. 点击右侧开始按钮激活游戏\n"
                     "2. 使用方向键控制移动\n"
                     "3. 熟悉操作后，可以按Esc键结束游戏\n",
                     map_index=0, is_game=True),
            GamePage("准备开始", "现在你已经了解了该游戏的过程，点击下一页进入区域选择游戏！")
        ]
        self.current_page = 0
        self.running = True
    def process_input(self, events):
        for event in events:
            if event.type == QUIT:
                self.running = False
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                # 统一处理右下角“下一页”按钮区域
                if 1000 <= x <= 1180 and 700 <= y <= 760:
                    if self.current_page == len(self.pages) - 1:
                        self.running = False
                    elif self.current_page == 1:
                        self.current_page += 1
                    elif self.current_page < len(self.pages) - 1:
                        if self.pages[self.current_page].is_game:
                            if self.pages[self.current_page].game_instance and self.pages[self.current_page].game_instance.finished:
                                self.current_page += 1
                        else:
                            self.current_page += 1
                if self.pages[self.current_page].is_game and 1020 <= x <= 1180 and 700 <= y <= 760:
                    if not self.pages[self.current_page].game_instance:
                        self.pages[self.current_page].game_instance = ExperimentGame(self.screen, self.data, MAP_CONFIGS[self.pages[self.current_page].map_index])
                    if not self.pages[self.current_page].game_instance.active:
                        self.pages[self.current_page].game_instance.active = True
                        if not self.data.start_times[self.pages[self.current_page].map_index]:
                            self.data.start_times[self.pages[self.current_page].map_index] = time.time()
    def update(self, events):
        self.screen.fill(EXP_COLORS['background'])
        if self.current_page == 1:
            self.pages[self.current_page].draw_full_text_page(self.screen)
        else:
            self.pages[self.current_page].draw_panel(self.screen)
        if self.pages[self.current_page].is_game and self.current_page not in [1]:
            if self.pages[self.current_page].update(self.screen, self.data, events):
                if self.current_page < len(self.pages) - 1:
                    self.current_page += 1
                else:
                    self.running = False
        pygame.display.flip()
    def run(self):
        while self.running:
            events = pygame.event.get()
            self.process_input(events)
            self.update(events)
            self.clock.tick(30)

# ================= 第二部分（区域选择游戏）的配置 =================
RS_SCREEN_SIZE = (1920, 1080)
RS_GRID_WIDTH = GRID_SIZE * CELL_SIZE  # 735
REGION_SIZE = 7  # 同前

RS_COLORS = {
    'background': (255, 255, 255),
    'grid': (211, 211, 211),
    'path': (0, 0, 0),
    'highlight': (255, 0, 0),
    'current': (255, 0, 0),
    'button': (100, 200, 100),
    'button_hover': (50, 150, 50),
    'start': (0, 255, 0),
    'close 1': (0, 0, 0),
    'close 2': (0, 0, 0),
    'far 1': (0, 0, 0),
    'far 2': (0, 0, 0),
    'selected': (169, 169, 169)
}

RS_POINTS = {
    'start': (7, 42),
    'close 1': (20, 18),
    'close 2': (31, 29),
    'far 1': (5, 1),
    'far 2': (48, 44)
}

class RegionSelectionGame:
    def __init__(self, parent_surface):
        self.screen = parent_surface
        self.clock = pygame.time.Clock()
        self.font = get_font(20)
        self.selected_regions = []
        self.finished = False  # 修改：通过 finished 标志退出循环
        self.reset_game()
    def reset_game(self):
        self.selected_regions = []
    def convert_coords(self, x, y):
        return (x * CELL_SIZE, (GRID_SIZE - y) * CELL_SIZE)
    def convert_region_coords(self, region_x, region_y):
        pixel_x = region_x * REGION_SIZE * CELL_SIZE
        pixel_y = (GRID_SIZE - (region_y + 1) * REGION_SIZE) * CELL_SIZE
        return (pixel_x, pixel_y)
    def draw_grid(self):
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, RS_COLORS['grid'], (i * CELL_SIZE, 0), (i * CELL_SIZE, RS_GRID_WIDTH))
            pygame.draw.line(self.screen, RS_COLORS['grid'], (0, i * CELL_SIZE), (RS_GRID_WIDTH, i * CELL_SIZE))
    def draw_selected_regions(self):
        for region in self.selected_regions:
            region_x, region_y = region
            rect_x, rect_y = self.convert_region_coords(region_x, region_y)
            temp_surface = pygame.Surface((REGION_SIZE * CELL_SIZE, REGION_SIZE * CELL_SIZE), pygame.SRCALPHA)
            temp_surface.fill((RS_COLORS['selected'][0], RS_COLORS['selected'][1], RS_COLORS['selected'][2], 128))
            self.screen.blit(temp_surface, (rect_x, rect_y))
    def draw_control_panel(self):
        panel_x = RS_GRID_WIDTH
        pygame.draw.rect(self.screen, (240, 240, 240), (panel_x, 0, RS_SCREEN_SIZE[0] - RS_GRID_WIDTH, RS_SCREEN_SIZE[1]))
        text_y = 50
        controls = [
            "操作说明：",
            "点击区域选中/取消",
            "点击确认保存选择"
        ]
        for line in controls:
            text = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text, (panel_x + 20, text_y))
            text_y += 30
        button_rect = pygame.Rect(panel_x + 50, RS_SCREEN_SIZE[1] // 2 - 25, 100, 50)
        mouse_pos = pygame.mouse.get_pos()
        btn_color = RS_COLORS['button_hover'] if button_rect.collidepoint(mouse_pos) else RS_COLORS['button']
        pygame.draw.rect(self.screen, btn_color, button_rect, border_radius=5)
        btn_text = self.font.render("确认", True, (255, 255, 255))
        text_rect = btn_text.get_rect(center=button_rect.center)
        self.screen.blit(btn_text, text_rect)
    def draw_points(self):
        for point, (x, y) in RS_POINTS.items():
            pygame.draw.circle(self.screen, RS_COLORS[point],
                               (x * CELL_SIZE + CELL_SIZE // 2, (GRID_SIZE - y) * CELL_SIZE + CELL_SIZE // 2), 5)
    def handle_input(self, events):
        for event in events:
            if event.type == QUIT:
                self.finished = True
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                panel_x = RS_GRID_WIDTH
                button_rect = pygame.Rect(panel_x + 50, RS_SCREEN_SIZE[1] // 2 - 25, 100, 50)
                if button_rect.collidepoint(x, y):
                    self.save_selected_regions()
                    self.finished = True  # 修改：点击确认后退出循环
                elif x < RS_GRID_WIDTH and y < RS_GRID_WIDTH:
                    region_x = x // (REGION_SIZE * CELL_SIZE)
                    region_y = (RS_GRID_WIDTH - y - 1) // (REGION_SIZE * CELL_SIZE)
                    if (region_x, region_y) in self.selected_regions:
                        self.selected_regions.remove((region_x, region_y))
                    else:
                        self.selected_regions.append((region_x, region_y))
    def save_selected_regions(self):
        folder = "selected_regions"
        if not os.path.exists(folder):
            os.makedirs(folder)
        surface = pygame.Surface((RS_GRID_WIDTH, RS_GRID_WIDTH))
        surface.fill(RS_COLORS['background'])
        self.draw_grid_on_surface(surface)
        self.draw_selected_regions_on_surface(surface)
        self.draw_points_on_surface(surface)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(folder, f"selected_regions_{timestamp}.png")
        pygame.image.save(surface, image_path)
        print(f"保存成功: {image_path}")
    def draw_grid_on_surface(self, surface):
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(surface, RS_COLORS['grid'], (i * CELL_SIZE, 0), (i * CELL_SIZE, RS_GRID_WIDTH))
            pygame.draw.line(surface, RS_COLORS['grid'], (0, i * CELL_SIZE), (RS_GRID_WIDTH, i * CELL_SIZE))
    def draw_selected_regions_on_surface(self, surface):
        for region in self.selected_regions:
            region_x, region_y = region
            rect_x, rect_y = self.convert_region_coords(region_x, region_y)
            temp_surface = pygame.Surface((REGION_SIZE * CELL_SIZE, REGION_SIZE * CELL_SIZE), pygame.SRCALPHA)
            temp_surface.fill((RS_COLORS['selected'][0], RS_COLORS['selected'][1], RS_COLORS['selected'][2], 128))
            surface.blit(temp_surface, (rect_x, rect_y))
    def draw_points_on_surface(self, surface):
        for point, (x, y) in RS_POINTS.items():
            pygame.draw.circle(surface, RS_COLORS[point],
                               (x * CELL_SIZE + CELL_SIZE // 2, (GRID_SIZE - y) * CELL_SIZE + CELL_SIZE // 2), 5)
    def update(self):
        self.screen.fill(RS_COLORS['background'])
        self.draw_grid()
        self.draw_selected_regions()
        self.draw_points()
        self.draw_control_panel()
        pygame.display.flip()
        self.clock.tick(30)

class RegionSelectionScene:
    def __init__(self, main_screen):
        self.main_screen = main_screen
        self.region_surface = pygame.Surface(RS_SCREEN_SIZE)
        self.game = RegionSelectionGame(self.region_surface)
    def run(self):
        finished = False
        while not finished:
            events = pygame.event.get()
            self.game.handle_input(events)
            self.game.update()
            self.main_screen.fill(RS_COLORS['background'])
            self.main_screen.blit(self.region_surface, (0, 0))
            for event in events:
                if event.type == QUIT:
                    finished = True
            pygame.display.flip()
            self.game.clock.tick(30)
            if self.game.finished:
                finished = True

# ================= 第三部分（路径迷宫游戏）的配置 =================
PANEL_WIDTH = 500
MAZE_WIDTH = GRID_SIZE * CELL_SIZE + PANEL_WIDTH  
MAZE_HEIGHT = GRID_SIZE * CELL_SIZE  

MAZE_COLORS = {
    'background': (255, 255, 255),
    'grid': (211, 211, 211),
    'path': (0, 0, 0),
    'highlight': (255, 0, 0),
    'start': (0, 0, 255),
    'current': (255, 0, 0),
    'button': (100, 200, 100),
    'button_hover': (50, 150, 50),
    'close 1': (0, 0, 0),
    'close 2': (0, 0, 0),
    'far 1': (0, 0, 0),
    'far 2': (0, 0, 0)
}

MAZE_POINTS = {
    'start': (7, 42),
    'close 1': (20, 18),
    'close 2': (31, 29),
    'far 1': (5, 1),
    'far 2': (48, 44)
}

class MazeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((MAZE_WIDTH, MAZE_HEIGHT))
        pygame.display.set_caption("路径迷宫")
        self.clock = pygame.time.Clock()
        self.font = get_font(20)
        self.reset_game()
    def reset_game(self):
        self.current_pos = list(MAZE_POINTS['start'])
        self.path = [tuple(self.current_pos)]
        self.turn_count = 0
        self.start_time = 0
        self.paused = False
        self.running = True
        self.finished = False
        self.game_started = False
        self.previous_direction = None
        self.turn_times = []
        self.pause_start = 0
    def convert_coords(self, x, y):
        return (x * CELL_SIZE, (GRID_SIZE - y) * CELL_SIZE)
    def draw_grid(self):
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, MAZE_COLORS['grid'],
                             (i * CELL_SIZE, 0), (i * CELL_SIZE, MAZE_HEIGHT))
            pygame.draw.line(self.screen, MAZE_COLORS['grid'],
                             (0, i * CELL_SIZE), (MAZE_WIDTH, i * CELL_SIZE))
    def draw_points(self):
        for name, (x, y) in MAZE_POINTS.items():
            pos = self.convert_coords(x, y)
            color = MAZE_COLORS.get(name, (0, 0, 0))
            pygame.draw.circle(self.screen, color, pos, 6)
        pygame.draw.circle(self.screen, MAZE_COLORS['current'],
                           self.convert_coords(*self.current_pos), 6)
    def draw_path(self):
        if len(self.path) > 1:
            points = [self.convert_coords(x, y) for x, y in self.path]
            pygame.draw.lines(self.screen, MAZE_COLORS['path'], False, points, 2)
    def calculate_angle(self, p1, p2, p3):
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        magnitude_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
        magnitude_v2 = math.sqrt(v2[0]**2 + v2[1]**2)
        cos_angle = dot_product / (magnitude_v1 * magnitude_v2)
        return math.degrees(math.acos(cos_angle))
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == MOUSEBUTTONDOWN and not self.game_started:
                panel_x = GRID_SIZE * CELL_SIZE
                if (panel_x + 50 < event.pos[0] < panel_x + 150 and
                    MAZE_HEIGHT//2 - 25 < event.pos[1] < MAZE_HEIGHT//2 + 25):
                    self.game_started = True
                    self.start_time = time.time()
            if event.type == KEYDOWN:
                if self.game_started and event.key == K_ESCAPE:
                    if not self.paused:
                        self.pause_start = time.time()
                    else:
                        self.start_time += time.time() - self.pause_start
                    self.paused = not self.paused
                if self.game_started and not self.paused and not self.finished:
                    if event.key == K_BACKSPACE:
                        if len(self.path) > 1:
                            self.path.pop()
                            self.current_pos = list(self.path[-1])
                    dx, dy = 0, 0
                    if event.key == K_UP: dy = 1
                    elif event.key == K_DOWN: dy = -1
                    elif event.key == K_LEFT: dx = -1
                    elif event.key == K_RIGHT: dx = 1
                    else:
                        return
                    new_x = self.current_pos[0] + dx
                    new_y = self.current_pos[1] + dy
                    if not (0 <= new_x <= GRID_SIZE and 0 <= new_y <= GRID_SIZE):
                        return
                    if abs(new_x - self.current_pos[0]) + abs(new_y - self.current_pos[1]) != 1:
                        return
                    if len(self.path) > 1:
                        angle = self.calculate_angle(self.path[-2], self.path[-1], (new_x, new_y))
                        if angle >= 25 and self.previous_direction != (dx, dy):
                            self.turn_count += 1
                            elapsed_time = time.time() - self.start_time
                            self.turn_times.append((self.turn_count, round(elapsed_time, 1)))
                    self.current_pos = [new_x, new_y]
                    self.path.append(tuple(self.current_pos))
                    self.previous_direction = (dx, dy)
    def check_finish(self):
        current = tuple(self.current_pos)
        target_points = ['close 1', 'close 2', 'far 1', 'far 2']
        for name in target_points:
            if current == MAZE_POINTS[name]:
                self.finished = True
                return name
        return None
    def generate_archive(self):
        return {
            "meta": {
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "duration": round(time.time() - self.start_time, 1),
                "steps": len(self.path) - 1,
                "turns": self.turn_count
            },
            "path": self.path,
            "turn_events": [{"turn": t[0], "time": t[1]} for t in self.turn_times]
        }
    def save_archive(self, archive_data):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        import pandas as pd
        df_path = pd.DataFrame(archive_data["path"], columns=["x", "y"])
        df_turns = pd.DataFrame(archive_data["turn_events"])
        summary_data = {
            'Total Duration (Seconds)': [archive_data['meta']['duration']],
            'Total Steps': [archive_data['meta']['steps']],
            'Total Turns': [archive_data['meta']['turns']]
        }
        df_summary = pd.DataFrame(summary_data)
        excel_filename = os.path.join(current_directory, f"archive_{archive_data['meta']['timestamp']}.xlsx")
        with pd.ExcelWriter(excel_filename) as writer:
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
            df_path.to_excel(writer, sheet_name="Path", index=False)
            df_turns.to_excel(writer, sheet_name="Turns", index=False)
        self.save_path_image(archive_data['meta']['timestamp'])
    def save_path_image(self, timestamp):
        surface = pygame.Surface((MAZE_WIDTH, MAZE_HEIGHT))
        surface.fill(MAZE_COLORS['background'])
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(surface, MAZE_COLORS['grid'],
                             (i * CELL_SIZE, 0), (i * CELL_SIZE, MAZE_HEIGHT))
            pygame.draw.line(surface, MAZE_COLORS['grid'],
                             (0, i * CELL_SIZE), (MAZE_WIDTH, i * CELL_SIZE))
        points = [self.convert_coords(x, y) for x, y in self.path]
        if len(points) > 1:
            pygame.draw.lines(surface, MAZE_COLORS['path'], False, points, 2)
            for name, (x, y) in MAZE_POINTS.items():
                pos = self.convert_coords(x, y)
                pygame.draw.circle(surface, MAZE_COLORS[name], pos, 6)
            for percent, color in [(0.3, (255, 255, 0)), (0.5, (0, 128, 0)), (0.7, (255, 0, 0))]:
                idx = int((len(points) - 1) * percent)
                if idx < len(points):
                    pygame.draw.circle(surface, color, points[idx], 6)

        path_image_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"path_{timestamp}.png")
        pygame.image.save(surface, path_image_filename)
    def draw_control_panel(self):
        panel_x = GRID_SIZE * CELL_SIZE
        pygame.draw.rect(self.screen, (240, 240, 240), (panel_x, 0, PANEL_WIDTH, MAZE_HEIGHT))
        text_y = 50
        controls = [
            "操作说明：",
            "↑ 上移",
            "↓ 下移",
            "← 左移",
            "→ 右移",
        ]
        for line in controls:
            text = self.font.render(line, True, (0,0,0))
            self.screen.blit(text, (panel_x + 20, text_y))
            text_y += 30
        button_rect = pygame.Rect(panel_x + 50, MAZE_HEIGHT//2 - 25, 100, 50)
        mouse_pos = pygame.mouse.get_pos()
        btn_color = MAZE_COLORS['button_hover'] if button_rect.collidepoint(mouse_pos) else MAZE_COLORS['button']
        pygame.draw.rect(self.screen, btn_color, button_rect, border_radius=5)
        btn_text = self.font.render("开始游戏" if not self.game_started else "进行中", True, (255,255,255))
        self.screen.blit(btn_text, (panel_x + 65, MAZE_HEIGHT//2 - 10))
    def run(self):
        while self.running:
            self.screen.fill(MAZE_COLORS['background'])
            self.handle_input()
            self.draw_grid()
            self.draw_points()
            self.draw_path()
            self.draw_control_panel()
            if self.game_started:
                info_texts = [
                    f"转弯次数: {self.turn_count}",
                    "暂停中" if self.paused else ""
                ]
                for i, text in enumerate(info_texts):
                    if text:
                        text_surface = self.font.render(text, True, (0,0,0))
                        self.screen.blit(text_surface, (10, 10 + i*25))
            if self.game_started and not self.paused and (result := self.check_finish()):
                finish_text = self.font.render(f"到达 {result}！", True, (0,0,255))
                self.screen.blit(finish_text, (MAZE_WIDTH//2 - 50, MAZE_HEIGHT//2))
                archive_data = self.generate_archive()
                self.save_archive(archive_data)
                pygame.time.wait(2000)
                self.running = False
            pygame.display.flip()
            self.clock.tick(30)
        # 退出当前部分，返回主程序

# ================= 第四部分（迷宫路径-完整障碍物版）的配置 =================
F4_GRID_SIZE = 49
F4_CELL_SIZE = 15
F4_PANEL_WIDTH = 500
F4_WIDTH = F4_GRID_SIZE * F4_CELL_SIZE + F4_PANEL_WIDTH  # 935
F4_HEIGHT = F4_GRID_SIZE * F4_CELL_SIZE  # 735
F4_REGION_SIZE = 7

F4_COLORS = {
    'background': (255, 255, 255),
    'grid': (200, 200, 200),
    'start': (0, 255, 0),
    'close 1': (0, 0, 0),
    'close 2': (0, 0, 0),
    'far 1': (0, 0, 0),
    'far 2': (0, 0, 0),
    'obstacle': (100, 100, 100),
    'button': (100, 200, 100),
    'button_hover': (50, 150, 50),
    'current': (255, 0, 0),
    'selected': (169, 169, 169)
}

F4_POINTS = {
    'start': (7, 42),
    'close1': (20, 18),
    'close2': (31, 29),
    'far1': (5, 1),
    'far2': (48, 44)
}

F4_ORIGINAL_OBSTACLES = [
    (9, 9, 8, 1),
    (8, 8, 12, 1),
    (10, 10, 6, 1),
    (11, 7, 4, 1),
    (14, 25, 6, 1),
    (13, 24, 5, 1),
    (15, 26, 3, 1),
    (10, 23, 7, 1),
    (24, 15, 5, 1),
    (27, 14, 2, 1),
    (23, 16, 6, 1),
    (3, 31, 6, 1),
    (4, 32, 4, 1),
    (5, 30, 3, 1),
    (44, 9, 5, 1),
    (43, 10, 3, 1),
    (45, 8, 4, 1),
]

F4_MIRRORED_OBSTACLES = [
    (39, 32, 1, 8),
    (40, 29, 1, 12),
    (38, 33, 1, 6),
    (41, 34, 1, 4),
    (23, 29, 1, 6),
    (24, 31, 1, 5),
    (22, 31, 1, 3),
    (25, 32, 1, 7),
    (33, 20, 1, 5),
    (34, 20, 1, 2),
    (32, 20, 1, 6),
    (17, 40, 1, 6),
    (16, 41, 1, 4),
    (18, 41, 1, 3),
    (39, 0, 1, 5),
    (38, 3, 1, 3),
    (40, 0, 1, 4),
]

F4_ALL_OBSTACLES = F4_ORIGINAL_OBSTACLES + F4_MIRRORED_OBSTACLES

class FullMazeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((F4_WIDTH, F4_HEIGHT))
        pygame.display.set_caption("迷宫路径-完整障碍物版")
        self.clock = pygame.time.Clock()
        self.font = get_font(20)
        self.reset_game()
    def reset_game(self):
        self.current_pos = list(F4_POINTS['start'])
        self.path = [tuple(self.current_pos)]
        self.turn_count = 0
        self.start_time = 0
        self.paused = False
        self.running = True
        self.finished = False
        self.game_started = False
        self.previous_direction = None
        self.turn_times = []
        self.pause_start = 0
        self.selected_regions = []
    def convert_coords(self, x, y):
        return (x * F4_CELL_SIZE, (F4_GRID_SIZE - y) * F4_CELL_SIZE)
    def convert_region_coords(self, region_x, region_y):
        pixel_x = region_x * F4_REGION_SIZE * F4_CELL_SIZE
        pixel_y = (F4_GRID_SIZE - (region_y + 1) * F4_REGION_SIZE) * F4_CELL_SIZE
        return (pixel_x, pixel_y)
    def draw_grid(self):
        for i in range(F4_GRID_SIZE + 1):
            pygame.draw.line(self.screen, F4_COLORS['grid'],
                             (i * F4_CELL_SIZE, 0), (i * F4_CELL_SIZE, F4_HEIGHT))
            pygame.draw.line(self.screen, F4_COLORS['grid'],
                             (0, i * F4_CELL_SIZE), (F4_WIDTH, i * F4_CELL_SIZE))
    def draw_obstacles(self):
        for obstacle in F4_ALL_OBSTACLES:
            ox, oy, ow, oh = obstacle
            screen_x = ox * F4_CELL_SIZE
            screen_y = (F4_GRID_SIZE - oy - oh) * F4_CELL_SIZE
            width = ow * F4_CELL_SIZE
            height = oh * F4_CELL_SIZE
            pygame.draw.rect(self.screen, F4_COLORS['obstacle'],
                             (screen_x, screen_y, width, height))
    def draw_selected_regions(self):
        for region in self.selected_regions:
            region_x, region_y = region
            rect_x, rect_y = self.convert_region_coords(region_x, region_y)
            temp_surface = pygame.Surface((F4_REGION_SIZE * F4_CELL_SIZE, F4_REGION_SIZE * F4_CELL_SIZE), pygame.SRCALPHA)
            temp_surface.fill((F4_COLORS['selected'][0], F4_COLORS['selected'][1], F4_COLORS['selected'][2], 128))
            self.screen.blit(temp_surface, (rect_x, rect_y))
    def draw_points(self):
        self.draw_obstacles()
        self.draw_selected_regions()
        for name, (x, y) in F4_POINTS.items():
            pos = self.convert_coords(x, y)
            color = F4_COLORS.get(name, (0, 0, 0))
            pygame.draw.circle(self.screen, color, pos, 8)
        pygame.draw.circle(self.screen, F4_COLORS['current'],
                           self.convert_coords(*self.current_pos), 8)
    def draw_path(self):
        if len(self.path) > 1:
            points = [self.convert_coords(x, y) for x, y in self.path]
            pygame.draw.lines(self.screen, (0, 0, 0), False, points, 3)
    def draw_control_panel(self):
        panel_x = F4_GRID_SIZE * F4_CELL_SIZE
        pygame.draw.rect(self.screen, (240, 240, 240), (panel_x, 0, F4_PANEL_WIDTH, F4_HEIGHT))
        text_y = 50
        controls = [
            "操作说明：",
            "点击区域选中/取消",
            "点击确认退出游戏"
        ]
        for line in controls:
            text = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text, (panel_x + 20, text_y))
            text_y += 30
        button_rect = pygame.Rect(panel_x + 50, F4_HEIGHT // 2 - 25, 100, 50)
        mouse_pos = pygame.mouse.get_pos()
        btn_color = F4_COLORS['button_hover'] if button_rect.collidepoint(mouse_pos) else F4_COLORS['button']
        pygame.draw.rect(self.screen, btn_color, button_rect, border_radius=5)
        btn_text = self.font.render("确认", True, (255, 255, 255))
        text_rect = btn_text.get_rect(center=button_rect.center)
        self.screen.blit(btn_text, text_rect)
    def draw_grid_on_surface(self, surface):
        for i in range(F4_GRID_SIZE + 1):
            pygame.draw.line(surface, F4_COLORS['grid'], (i * F4_CELL_SIZE, 0), (i * F4_CELL_SIZE, F4_HEIGHT))
            pygame.draw.line(surface, F4_COLORS['grid'], (0, i * F4_CELL_SIZE), (F4_GRID_SIZE * F4_CELL_SIZE, i * F4_CELL_SIZE))
    def draw_obstacles_on_surface(self, surface):
        for obstacle in F4_ALL_OBSTACLES:
            ox, oy, ow, oh = obstacle
            screen_x = ox * F4_CELL_SIZE
            screen_y = (F4_GRID_SIZE - oy - oh) * F4_CELL_SIZE
            width = ow * F4_CELL_SIZE
            height = oh * F4_CELL_SIZE
            pygame.draw.rect(surface, F4_COLORS['obstacle'], (screen_x, screen_y, width, height))
    def draw_selected_regions_on_surface(self, surface):
        for region in self.selected_regions:
            region_x, region_y = region
            rect_x, rect_y = self.convert_region_coords(region_x, region_y)
            temp_surface = pygame.Surface((F4_REGION_SIZE * F4_CELL_SIZE, F4_REGION_SIZE * F4_CELL_SIZE), pygame.SRCALPHA)
            temp_surface.fill((F4_COLORS['selected'][0], F4_COLORS['selected'][1], F4_COLORS['selected'][2], 128))
            surface.blit(temp_surface, (rect_x, rect_y))
    def draw_path_on_surface(self, surface):
        if len(self.path) > 1:
            points = [self.convert_coords(x, y) for x, y in self.path]
            pygame.draw.lines(surface, (0, 0, 0), False, points, 3)
    def draw_points_on_surface(self, surface):
        self.draw_obstacles_on_surface(surface)
        self.draw_selected_regions_on_surface(surface)
        for name, (x, y) in F4_POINTS.items():
            pos = self.convert_coords(x, y)
            color = F4_COLORS.get(name, (0, 0, 0))
            pygame.draw.circle(surface, color, pos, 8)
        pygame.draw.circle(surface, F4_COLORS['current'], self.convert_coords(*self.current_pos), 8)
    def save_selected_regions(self):
        folder = "selected_regions"
        if not os.path.exists(folder):
            os.makedirs(folder)
        surface = pygame.Surface((F4_GRID_SIZE * F4_CELL_SIZE, F4_HEIGHT))
        surface.fill(F4_COLORS['background'])
        self.draw_grid_on_surface(surface)
        self.draw_obstacles_on_surface(surface)
        self.draw_selected_regions_on_surface(surface)
        self.draw_path_on_surface(surface)
        self.draw_points_on_surface(surface)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(folder, f"selected_regions_{timestamp}.png")
        pygame.image.save(surface, image_path)
        print(f"保存成功: {image_path}")
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                panel_x = F4_GRID_SIZE * F4_CELL_SIZE
                button_rect = pygame.Rect(panel_x + 50, F4_HEIGHT // 2 - 25, 100, 50)
                if button_rect.collidepoint(x, y):
                    self.save_selected_regions()
                    self.running = False  # 修改：点击确认后退出当前部分
                elif x < F4_GRID_SIZE * F4_CELL_SIZE and y < F4_HEIGHT:
                    region_x = x // (F4_REGION_SIZE * F4_CELL_SIZE)
                    region_y = (F4_HEIGHT - y - 1) // (F4_REGION_SIZE * F4_CELL_SIZE)
                    if (region_x, region_y) in self.selected_regions:
                        self.selected_regions.remove((region_x, region_y))
                    else:
                        self.selected_regions.append((region_x, region_y))
    def update(self):
        self.screen.fill(F4_COLORS['background'])
        self.draw_grid()
        self.draw_selected_regions()
        self.draw_path()
        self.draw_points()
        self.draw_control_panel()
        pygame.display.flip()
        self.clock.tick(30)
    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.clock.tick(30)
        # 退出当前部分后返回主程序

# ================= 第五部分（迷宫路径-完整障碍物版）的配置 =================
F5_GRID_SIZE = 49
F5_CELL_SIZE = 15
F5_PANEL_WIDTH = 500
F5_WIDTH = F5_GRID_SIZE * F5_CELL_SIZE + F5_PANEL_WIDTH  # 935
F5_HEIGHT = F5_GRID_SIZE * F5_CELL_SIZE  # 735

F5_COLORS = {
    'background': (255, 255, 255),
    'grid': (200, 200, 200),
    'start': (0, 255, 0),
    'close 1': (0, 0, 0),
    'close 2': (0, 0, 0),
    'far 1': (0, 0, 0),
    'far 2': (0, 0, 0),
    'obstacle': (100, 100, 100),
    'button': (100, 200, 100),
    'button_hover': (50, 150, 50),
    'current': (255, 0, 0)
}

F5_POINTS = {
    'start': (7, 42),
    'close1': (20, 18),
    'close2': (31, 29),
    'far1': (5, 1),
    'far2': (48, 44)
}

F5_ORIGINAL_OBSTACLES = [
    (9, 9, 8, 1),
    (8, 8, 12, 1),
    (10, 10, 6, 1),
    (11, 7, 4, 1),
    (14, 25, 6, 1),
    (13, 24, 5, 1),
    (15, 26, 3, 1),
    (10, 23, 7, 1),
    (24, 15, 5, 1),
    (27, 14, 2, 1),
    (23, 16, 6, 1),
    (3, 31, 6, 1),
    (4, 32, 4, 1), 
    (5, 30, 3, 1),
    (44, 9, 5, 1),
    (43, 10, 3, 1),
    (45, 8, 4, 1),
]

F5_MIRRORED_OBSTACLES = [
    (39, 32, 1, 8),
    (40, 29, 1, 12),
    (38, 33, 1, 6),
    (41, 34, 1, 4),
    (23, 29, 1, 6),
    (24, 31, 1, 5),
    (22, 31, 1, 3),
    (25, 32, 1, 7),
    (33, 20, 1, 5),
    (34, 20, 1, 2),
    (32, 20, 1, 6),
    (17, 40, 1, 6),
    (16, 41, 1, 4),
    (18, 41, 1, 3),
    (39, 0, 1, 5),
    (38, 3, 1, 3),
    (40, 0, 1, 4),
]

F5_ALL_OBSTACLES = F5_ORIGINAL_OBSTACLES + F5_MIRRORED_OBSTACLES

class FifthGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((F5_WIDTH, F5_HEIGHT))
        pygame.display.set_caption("迷宫路径-完整障碍物版 (第五部分)")
        self.clock = pygame.time.Clock()
        self.font = get_font(20)
        self.reset_game()
    def reset_game(self):
        self.current_pos = list(F5_POINTS['start'])
        self.path = [tuple(self.current_pos)]
        self.turn_count = 0
        self.start_time = 0
        self.paused = False
        self.running = True
        self.finished = False
        self.game_started = False
        self.previous_direction = None
        self.turn_times = []
        self.pause_start = 0
    def convert_coords(self, x, y):
        return (x * F5_CELL_SIZE, (F5_GRID_SIZE - y) * F5_CELL_SIZE)
    def draw_grid(self):
        for i in range(F5_GRID_SIZE + 1):
            pygame.draw.line(self.screen, F5_COLORS['grid'],
                             (i * F5_CELL_SIZE, 0), (i * F5_CELL_SIZE, F5_HEIGHT))
            pygame.draw.line(self.screen, F5_COLORS['grid'],
                             (0, i * F5_CELL_SIZE), (F5_WIDTH, i * F5_CELL_SIZE))
    def draw_obstacles(self):
        for obstacle in F5_ALL_OBSTACLES:
            ox, oy, ow, oh = obstacle
            screen_x = ox * F5_CELL_SIZE
            screen_y = (F5_GRID_SIZE - oy - oh) * F5_CELL_SIZE
            width = ow * F5_CELL_SIZE
            height = oh * F5_CELL_SIZE
            pygame.draw.rect(self.screen, F5_COLORS['obstacle'],
                             (screen_x, screen_y, width, height))
    def draw_points(self):
        self.draw_obstacles()
        for name, (x, y) in F5_POINTS.items():
            pos = self.convert_coords(x, y)
            color = F5_COLORS.get(name, (0, 0, 0))
            pygame.draw.circle(self.screen, color, pos, 8)
        pygame.draw.circle(self.screen, F5_COLORS['current'],
                           self.convert_coords(*self.current_pos), 8)
    def draw_path(self):
        if len(self.path) > 1:
            points = [self.convert_coords(x, y) for x, y in self.path]
            pygame.draw.lines(self.screen, (0, 0, 0), False, points, 3)
    def is_valid_move(self, new_x, new_y):
        if not (0 <= new_x < F5_GRID_SIZE and 0 <= new_y < F5_GRID_SIZE):
            return False
        if abs(new_x - self.current_pos[0]) + abs(new_y - self.current_pos[1]) != 1:
            return False
        return True
    def calculate_angle(self, p1, p2, p3):
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        dot_product = v1[0]*v2[0] + v1[1]*v2[1]
        magnitude_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
        magnitude_v2 = math.sqrt(v2[0]**2 + v2[1]**2)
        cos_angle = dot_product / (magnitude_v1 * magnitude_v2)
        return math.degrees(math.acos(cos_angle))
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == MOUSEBUTTONDOWN and not self.game_started:
                panel_x = F5_GRID_SIZE * F5_CELL_SIZE
                if (panel_x + 50 < event.pos[0] < panel_x + 150 and
                    F5_HEIGHT//2 - 25 < event.pos[1] < F5_HEIGHT//2 + 25):
                    self.game_started = True
                    self.start_time = time.time()
            if event.type == KEYDOWN:
                if self.game_started and event.key == K_ESCAPE:
                    if not self.paused:
                        self.pause_start = time.time()
                    else:
                        self.start_time += time.time() - self.pause_start
                    self.paused = not self.paused
                if self.game_started and not self.paused and not self.finished:
                    if event.key == K_BACKSPACE:
                        if len(self.path) > 1:
                            self.path.pop()
                            self.current_pos = list(self.path[-1])
                    dx, dy = 0, 0
                    if event.key == K_UP: dy = 1
                    elif event.key == K_DOWN: dy = -1
                    elif event.key == K_LEFT: dx = -1
                    elif event.key == K_RIGHT: dx = 1
                    else:
                        return
                    new_x = self.current_pos[0] + dx
                    new_y = self.current_pos[1] + dy
                    if not self.is_valid_move(new_x, new_y):
                        return
                    if len(self.path) > 1:
                        angle = self.calculate_angle(self.path[-2], self.path[-1], (new_x, new_y))
                        if angle >= 25 and self.previous_direction != (dx, dy):
                            self.turn_count += 1
                            elapsed_time = time.time() - self.start_time
                            self.turn_times.append((self.turn_count, round(elapsed_time, 1)))
                    self.current_pos = [new_x, new_y]
                    self.path.append(tuple(self.current_pos))
                    self.previous_direction = (dx, dy)
    def check_finish(self):
        current = tuple(self.current_pos)
        for name, pos in F5_POINTS.items():
            if name != 'start' and current == pos:
                self.finished = True
                return name
        return None
    def generate_archive(self):
        return {
            "meta": {
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "duration": round(time.time() - self.start_time, 1),
                "steps": len(self.path) - 1,
                "turns": self.turn_count
            },
            "path": self.path,
            "turn_events": [{"turn": t[0], "time": t[1]} for t in self.turn_times]
        }
    def save_archive(self, archive_data):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        import pandas as pd
        df_path = pd.DataFrame(archive_data["path"], columns=["x", "y"])
        df_turns = pd.DataFrame(archive_data["turn_events"])
        summary_data = {
            'Total Duration (Seconds)': [archive_data['meta']['duration']],
            'Total Steps': [archive_data['meta']['steps']],
            'Total Turns': [archive_data['meta']['turns']]
        }
        df_summary = pd.DataFrame(summary_data)
        excel_filename = os.path.join(current_directory, f"archive_{archive_data['meta']['timestamp']}.xlsx")
        with pd.ExcelWriter(excel_filename) as writer:
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
            df_path.to_excel(writer, sheet_name="Path", index=False)
            df_turns.to_excel(writer, sheet_name="Turns", index=False)
        self.save_path_image(archive_data['meta']['timestamp'])

    def save_path_image(self, timestamp):
        surface = pygame.Surface((F5_WIDTH, F5_HEIGHT))
        surface.fill(F5_COLORS['background'])
        for i in range(F5_GRID_SIZE + 1):
            pygame.draw.line(surface, F5_COLORS['grid'],
                             (i * F5_CELL_SIZE, 0), (i * F5_CELL_SIZE, F5_HEIGHT))
            pygame.draw.line(surface, F5_COLORS['grid'],
                             (0, i * F5_CELL_SIZE), (F5_WIDTH, i * F5_CELL_SIZE))
        for obstacle in F5_ALL_OBSTACLES:
            ox, oy, ow, oh = obstacle
            screen_x = ox * F5_CELL_SIZE
            screen_y = (F5_GRID_SIZE - oy - oh) * F5_CELL_SIZE
            width = ow * F5_CELL_SIZE
            height = oh * F5_CELL_SIZE
            pygame.draw.rect(surface, F5_COLORS['obstacle'],
                             (screen_x, screen_y, width, height))
        points = [self.convert_coords(x, y) for x, y in self.path]
        if len(points) > 1:
            pygame.draw.lines(surface, (0,0,0), False, points, 3)
            for percent, color in [(0.3, (255, 255, 0)), (0.5, (0, 0, 255)), (0.7, (255, 0, 0))]:
                idx = int((len(points) - 1) * percent)
                if idx < len(points):
                    pygame.draw.circle(surface, color, points[idx], 6)
        pygame.image.save(surface, f"path_{timestamp}.png")
    def draw_control_panel(self):
        panel_x = F5_GRID_SIZE * F5_CELL_SIZE
        pygame.draw.rect(self.screen, (240, 240, 240), (panel_x, 0, F5_PANEL_WIDTH, F5_HEIGHT))
        text_y = 50
        controls = [
            "操作说明：",
            "↑ 上移",
            "↓ 下移",
            "← 左移",
            "→ 右移",
            "请勿穿过灰色障碍",
        ]
        for line in controls:
            text = self.font.render(line, True, (0,0,0))
            self.screen.blit(text, (panel_x + 20, text_y))
            text_y += 30
        button_rect = pygame.Rect(panel_x + 50, F5_HEIGHT//2 - 25, 100, 50)
        mouse_pos = pygame.mouse.get_pos()
        btn_color = F5_COLORS['button_hover'] if button_rect.collidepoint(mouse_pos) else F5_COLORS['button']
        pygame.draw.rect(self.screen, btn_color, button_rect, border_radius=5)
        btn_text = self.font.render("开始游戏" if not self.game_started else "进行中", True, (255,255,255))
        self.screen.blit(btn_text, (panel_x + 65, F5_HEIGHT//2 - 10))
    def run(self):
        while self.running:
            self.screen.fill(F5_COLORS['background'])
            self.handle_input()
            self.draw_grid()
            self.draw_points()
            self.draw_path()
            self.draw_control_panel()
            if self.game_started:
                info_texts = [
                    f"转弯次数: {self.turn_count}",
                    "暂停中" if self.paused else ""
                ]
                for i, text in enumerate(info_texts):
                    if text:
                        text_surface = self.font.render(text, True, (0,0,0))
                        self.screen.blit(text_surface, (10, 10 + i*25))
            if self.game_started and not self.paused and (result := self.check_finish()):
                finish_text = self.font.render(f"到达 {result}！", True, (0,0,255))
                self.screen.blit(finish_text, (F5_WIDTH//2-50, F5_HEIGHT//2))
                archive_data = self.generate_archive()
                self.save_archive(archive_data)
                pygame.time.wait(2000)
                self.running = False
            pygame.display.flip()
            self.clock.tick(30)
        # 结束后返回主程序

# ================= 主程序 =================
def main():
    pygame.init()
    # 第一部分：路径规划实验（1920×1080）
    exp_screen = pygame.display.set_mode(EXP_SCREEN_SIZE)
    pygame.display.set_caption("整合版游戏 - 路径规划实验")
    exp_scene = ExperimentScene(exp_screen)
    exp_scene.run()
    
    # 第二部分：区域选择游戏（1200×800），点击“确认”后退出该部分进入第三部分
    pygame.display.quit()
    pygame.display.init()
    rs_screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("区域选择游戏")
    region_scene = RegionSelectionScene(rs_screen)
    region_scene.run()
    
    # 第三部分：路径迷宫游戏（935×735），游戏结束后自动退出该部分进入第四部分
    pygame.display.quit()
    pygame.display.init()
    maze_screen = pygame.display.set_mode((MAZE_WIDTH, MAZE_HEIGHT))
    pygame.display.set_caption("路径迷宫")
    maze_game = MazeGame()
    maze_game.run()
    
    # 第四部分：迷宫路径-完整障碍物版（935×735），点击“确认”后退出该部分进入第五部分
    pygame.display.quit()
    pygame.display.init()
    f4_screen = pygame.display.set_mode((F4_WIDTH, F4_HEIGHT))
    pygame.display.set_caption("迷宫路径-完整障碍物版")
    full_maze_game = FullMazeGame()
    full_maze_game.run()
    
    # 第五部分：迷宫路径-完整障碍物版（第五部分），游戏结束后退出整个程序
    pygame.display.quit()
    pygame.display.init()
    f5_screen = pygame.display.set_mode((F5_WIDTH, F5_HEIGHT))
    pygame.display.set_caption("迷宫路径-完整障碍物版 (第五部分)")
    fifth_game = FifthGame()
    fifth_game.run()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
