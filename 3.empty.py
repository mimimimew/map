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

POINTS = {  
    'start': (7, 42),  
    'close 1': (20, 18),  
    'close 2': (31, 29),  
    'far 1': (5, 1),  
    'far 2': (48, 44)  
}  

def get_font(size):  
    return pygame.font.Font(FONT_PATH, size)  

class PathGame:  
    def __init__(self):  
        pygame.init()  
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  
        pygame.display.set_caption("路径迷宫")  
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
        """坐标转换（逻辑坐标 → 屏幕坐标）"""  
        return (x * CELL_SIZE, (GRID_SIZE - y) * CELL_SIZE)  

    def draw_grid(self):  
        """绘制网格系统"""  
        for i in range(GRID_SIZE + 1):  
            pygame.draw.line(self.screen, COLORS['grid'],  
                            (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT))  
            pygame.draw.line(self.screen, COLORS['grid'],  
                            (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))  

    def draw_points(self):  
        """绘制所有关键点"""  
        for name, (x, y) in POINTS.items():  
            pos = self.convert_coords(x, y)  
            color = COLORS.get(name, (0,0,0))  
            pygame.draw.circle(self.screen, color, pos, 6)  
        
        # 绘制当前位置（红色点）  
        pygame.draw.circle(self.screen, COLORS['current'],  
                          self.convert_coords(*self.current_pos), 6)  

    def draw_path(self):  
        """绘制玩家路径"""  
        if len(self.path) > 1:  
            points = [self.convert_coords(x, y) for x, y in self.path]  
            pygame.draw.lines(self.screen, COLORS['path'], False, points, 2)  

    def calculate_angle(self, p1, p2, p3):  
        """计算路径夹角"""  
        v1 = (p1[0] - p2[0], p1[1] - p2[1])  
        v2 = (p3[0] - p2[0], p3[1] - p2[1])  
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]  
        magnitude_v1 = math.sqrt(v1[0]**2 + v1[1]**2)  
        magnitude_v2 = math.sqrt(v2[0]**2 + v2[1]**2)  
        cos_angle = dot_product / (magnitude_v1 * magnitude_v2)  
        return math.degrees(math.acos(cos_angle))  

    def handle_input(self):  
        """处理输入事件"""  
        for event in pygame.event.get():  
            if event.type == QUIT:  
                self.running = False  
            
            if event.type == MOUSEBUTTONDOWN and not self.game_started:  
                # 检测开始按钮点击  
                panel_x = GRID_SIZE * CELL_SIZE  
                if (panel_x + 50 < event.pos[0] < panel_x + 150 and  
                    HEIGHT//2 - 25 < event.pos[1] < HEIGHT//2 + 25):  
                    self.game_started = True  
                    self.start_time = time.time()  

            if event.type == KEYDOWN:  
                # 暂停逻辑（仅在游戏开始后生效）  
                if self.game_started and event.key == K_ESCAPE:  
                    if not self.paused:  
                        self.pause_start = time.time()  
                    else:  
                        self.start_time += time.time() - self.pause_start  
                    self.paused = not self.paused  
                
                # 游戏操作（仅在开始且非暂停状态）  
                if self.game_started and not self.paused and not self.finished:  
                    # 撤回逻辑  
                    if event.key == K_BACKSPACE:  
                        if len(self.path) > 1:  
                            self.path.pop()  
                            self.current_pos = list(self.path[-1])  
                    
                    # 移动控制  
                    dx, dy = 0, 0  
                    if event.key == K_UP: dy = 1  
                    elif event.key == K_DOWN: dy = -1  
                    elif event.key == K_LEFT: dx = -1  
                    elif event.key == K_RIGHT: dx = 1  
                    else: return  

                    # 计算新坐标  
                    new_x = self.current_pos[0] + dx  
                    new_y = self.current_pos[1] + dy  
                    
                    # 移动验证  
                    if not (0 <= new_x <= GRID_SIZE and 0 <= new_y <= GRID_SIZE):  
                        return  
                    # 移除之前的检查，允许重复走过的路径
                    if abs(new_x - self.current_pos[0]) + abs(new_y - self.current_pos[1]) != 1:  
                        return  
                    
                    # 转弯检测  
                    if len(self.path) > 1:  
                        angle = self.calculate_angle(self.path[-2], self.path[-1], (new_x, new_y))  
                        if angle >= 25 and self.previous_direction != (dx, dy):  
                            self.turn_count += 1  
                            elapsed_time = time.time() - self.start_time  
                            self.turn_times.append((self.turn_count, round(elapsed_time, 1)))  

                    # 更新状态  
                    self.current_pos = [new_x, new_y]  
                    self.path.append(tuple(self.current_pos))  
                    self.previous_direction = (dx, dy)  

    def check_finish(self):  
        """终点检测：如果玩家到达任何目标点，游戏结束"""  
        current = tuple(self.current_pos)  
        target_points = ['close 1', 'close 2', 'far 1', 'far 2']  
        
        for name in target_points:  
            if current == POINTS[name]:  
                self.finished = True  
                return True  
        return False  

    def generate_archive(self):  
        """生成存档数据"""  
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
        """保存存档文件为Excel文件"""  
        # 获取当前脚本目录路径
        current_directory = os.path.dirname(os.path.abspath(__file__))
        
        # 使用pandas保存为Excel文件
        df_path = pd.DataFrame(archive_data["path"], columns=["x", "y"])  
        df_turns = pd.DataFrame(archive_data["turn_events"])  

        # Create a DataFrame for summary data
        summary_data = {
            'Total Duration (Seconds)': [archive_data['meta']['duration']],
            'Total Steps': [archive_data['meta']['steps']],
            'Total Turns': [archive_data['meta']['turns']]
        }
        df_summary = pd.DataFrame(summary_data)

        # Save to Excel in the current directory
        excel_filename = os.path.join(current_directory, f"archive_{archive_data['meta']['timestamp']}.xlsx")
        with pd.ExcelWriter(excel_filename) as writer:
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
            df_path.to_excel(writer, sheet_name="Path", index=False)
            df_turns.to_excel(writer, sheet_name="Turns", index=False)  

        # 生成路径图片  
        self.save_path_image(archive_data['meta']['timestamp'])  

    def save_path_image(self, timestamp):  
        """生成带标记的路径图"""  
        surface = pygame.Surface((WIDTH, HEIGHT))  
        surface.fill(COLORS['background'])  
        
        # 绘制网格  
        for i in range(GRID_SIZE + 1):  
            pygame.draw.line(surface, COLORS['grid'],  
                            (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT))  
            pygame.draw.line(surface, COLORS['grid'],  
                            (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))  
        
        # 绘制路径  
        points = [self.convert_coords(x, y) for x, y in self.path]  
        if len(points) > 1:  
            pygame.draw.lines(surface, COLORS['path'], False, points, 2)  
            
            # 标记关键点（start, close1, close2, far1, far2）  
            for name, (x, y) in POINTS.items():  
                pos = self.convert_coords(x, y)  
                pygame.draw.circle(surface, COLORS[name], pos, 6)  # 用对应的颜色标记这些点
            
            # 标记路径的30%，50%，70%位置  
            for percent, color in [(0.3, (255, 255, 0)), (0.5, (0, 128, 0)), (0.7, (255, 0, 0))]:  
                idx = int((len(points) - 1) * percent)  
                if idx < len(points):  
                    pygame.draw.circle(surface, color, points[idx], 6)  # 黄色，蓝色，红色标记30%，50%，70%位置
        
        # 保存图片  
        path_image_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"path_{timestamp}.png")
        pygame.image.save(surface, path_image_filename)


    def draw_control_panel(self):  
        """绘制右侧控制面板"""  
        panel_x = GRID_SIZE * CELL_SIZE  
        # 绘制面板背景  
        pygame.draw.rect(self.screen, (240, 240, 240),   
                        (panel_x, 0, PANEL_WIDTH, HEIGHT))  

        # 绘制操作说明  
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

        # 绘制开始按钮  
        button_rect = pygame.Rect(panel_x + 50, HEIGHT//2 - 25, 100, 50)  
        mouse_pos = pygame.mouse.get_pos()  
        btn_color = COLORS['button_hover'] if button_rect.collidepoint(mouse_pos) else COLORS['button']  
        
        pygame.draw.rect(self.screen, btn_color, button_rect, border_radius=5)  
        btn_text = self.font.render("开始游戏" if not self.game_started else "进行中", True, (255,255,255))  
        self.screen.blit(btn_text, (panel_x + 65, HEIGHT//2 - 10))  

    def run(self):  
        """主游戏循环"""  
        while self.running:  
            self.screen.fill(COLORS['background'])  
            self.handle_input()  

            # 绘制游戏地图  
            self.draw_grid()  
            self.draw_points()  
            self.draw_path()  

            # 绘制右侧控制面板  
            self.draw_control_panel()  

            # 显示转弯次数和暂停状态  
            if self.game_started:  
                info_texts = [  
                    f"转弯次数: {self.turn_count}",  
                    "暂停中" if self.paused else ""  
                ]  
                for i, text in enumerate(info_texts):  
                    if text:  
                        text_surface = self.font.render(text, True, (0,0,0))  
                        self.screen.blit(text_surface, (10, 10 + i*25))  

            # 完成检测  
            if self.game_started and not self.paused and self.check_finish():  
                finish_text = self.font.render("任务完成！", True, (0,0,255))  
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
