import pygame  
import time  
import math  
import json  
import os  # To get the current directory for saving files
from datetime import datetime  
import pandas as pd  # Import pandas for DataFrame and Excel functionality
from pygame.locals import *  

# ================= 配置参数 =================  
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"  
GRID_SIZE = 49  
CELL_SIZE = 15  
PANEL_WIDTH = 200  # 右侧面板宽度  
WIDTH = GRID_SIZE * CELL_SIZE + PANEL_WIDTH  
HEIGHT = GRID_SIZE * CELL_SIZE  

COLORS = {  
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

POINTS = {  
    'start': (7, 42),  
    'close1': (20, 18),  
    'close2': (31, 29),  
    'far1': (5, 1),  
    'far2': (48, 44)  
}  

# 障碍物定义
ORIGINAL_OBSTACLES = [  
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

MIRRORED_OBSTACLES = [  
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

ALL_OBSTACLES = ORIGINAL_OBSTACLES + MIRRORED_OBSTACLES  

def get_font(size):  
    return pygame.font.Font(FONT_PATH, size)    

class PathGame:  
    def __init__(self):  
        pygame.init()  
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  
        pygame.display.set_caption("迷宫路径-完整障碍物版")  
        self.clock = pygame.time.Clock()  
        self.font = get_font(20)  
        self.reset_game()  

    def reset_game(self):  
        """初始化游戏状态"""  
        self.current_pos = list(POINTS['start'])  
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
            pygame.draw.line(self.screen, COLORS['grid'],  
                             (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT))  
            pygame.draw.line(self.screen, COLORS['grid'],  
                             (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))  

    def draw_obstacles(self):  
        for obstacle in ALL_OBSTACLES:  
            ox, oy, ow, oh = obstacle  
            screen_x = ox * CELL_SIZE  
            screen_y = (GRID_SIZE - oy - oh) * CELL_SIZE  
            width = ow * CELL_SIZE  
            height = oh * CELL_SIZE  
            pygame.draw.rect(self.screen, COLORS['obstacle'],   
                             (screen_x, screen_y, width, height))  

    def draw_points(self):  
        self.draw_obstacles()  
        
        for name, (x, y) in POINTS.items():  
            pos = self.convert_coords(x, y)  
            color = COLORS.get(name, (0,0,0))  
            pygame.draw.circle(self.screen, color, pos, 8)  
            
        pygame.draw.circle(self.screen, COLORS['current'],  
                           self.convert_coords(*self.current_pos), 8)  

    def draw_path(self):  
        if len(self.path) > 1:  
            points = [self.convert_coords(x, y) for x, y in self.path]  
            pygame.draw.lines(self.screen, (0,0,0), False, points, 3)  

    def is_in_obstacle(self, x, y):  
        """允许穿过障碍物"""  
        return False  # Always return False to allow movement through obstacles.

    def is_valid_move(self, new_x, new_y):  
        # Check bounds
        if not (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE):  
            return False  

        # Path can move freely through obstacles now.
        # We don't block the movement based on whether it's a visited path or obstacle.

        # Must move to an adjacent cell
        if abs(new_x - self.current_pos[0]) + abs(new_y - self.current_pos[1]) != 1:  
            return False  

        # If none of the above conditions block us, it's valid
        return True  

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
                    HEIGHT//2 - 25 < event.pos[1] < HEIGHT//2 + 25):  
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
                    else: return  

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
        for name, pos in POINTS.items():  
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
        filename = f"archive_{archive_data['meta']['timestamp']}.json"  
        with open(filename, "w", encoding='utf-8') as f:  
            json.dump(archive_data, f, indent=4, ensure_ascii=False)  
        self.save_path_image(archive_data['meta']['timestamp'])  

    def save_path_image(self, timestamp):  
        surface = pygame.Surface((WIDTH, HEIGHT))  
        surface.fill(COLORS['background'])  

        for i in range(GRID_SIZE + 1):  
            pygame.draw.line(surface, COLORS['grid'],  
                             (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT))  
            pygame.draw.line(surface, COLORS['grid'],  
                             (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))  

        for obstacle in ALL_OBSTACLES:  
            ox, oy, ow, oh = obstacle  
            screen_x = ox * CELL_SIZE  
            screen_y = (GRID_SIZE - oy - oh) * CELL_SIZE  
            width = ow * CELL_SIZE  
            height = oh * CELL_SIZE  
            pygame.draw.rect(surface, COLORS['obstacle'],   
                             (screen_x, screen_y, width, height))  

        points = [self.convert_coords(x, y) for x, y in self.path]  
        if len(points) > 1:  
            pygame.draw.lines(surface, (0,0,0), False, points, 3)  

        # Mark 30%, 50%, and 70% points on the path with yellow, blue, and red respectively
        for percent, color in [(0.3, (255, 255, 0)), (0.5, (0, 0, 255)), (0.7, (255, 0, 0))]:  
            idx = int((len(points) - 1) * percent)  
            if idx < len(points):  
                pygame.draw.circle(surface, color, points[idx], 6)  # Yellow, Blue, and Red for 30%, 50%, and 70%

        pygame.image.save(surface, f"path_{timestamp}.png")  

    def draw_control_panel(self):  
        panel_x = GRID_SIZE * CELL_SIZE  
        pygame.draw.rect(self.screen, (240, 240, 240),   
                         (panel_x, 0, PANEL_WIDTH, HEIGHT))  

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

        button_rect = pygame.Rect(panel_x + 50, HEIGHT//2 - 25, 100, 50)  
        mouse_pos = pygame.mouse.get_pos()  
        btn_color = COLORS['button_hover'] if button_rect.collidepoint(mouse_pos) else COLORS['button']  
        
        pygame.draw.rect(self.screen, btn_color, button_rect, border_radius=5)  
        btn_text = self.font.render("开始游戏" if not self.game_started else "进行中", True, (255,255,255))  
        self.screen.blit(btn_text, (panel_x + 65, HEIGHT//2 - 10))  

    def run(self):  
        while self.running:  
            self.screen.fill(COLORS['background'])  
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
                self.screen.blit(finish_text, (WIDTH//2-50, HEIGHT//2))  
                
                archive_data = self.generate_archive()  
                self.save_archive(archive_data)  
                pygame.time.wait(2000)  
                self.running = False  

            pygame.display.flip()  
            self.clock.tick(30)  

        pygame.quit()  

if __name__ == "__main__":  
    game = PathGame()  
    game.run()
