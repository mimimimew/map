import pygame  
import sys  
import time  
from pygame.locals import *  
from datetime import datetime  

# ================= 字体配置 =================  
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"  
def get_font(size):  
    return pygame.font.Font(FONT_PATH, size)  

# ================= 全局配置 =================  
SCREEN_SIZE = (1200, 800)  
GRID_SIZE = 49  
CELL_SIZE = 15  
GAME_SIZE = GRID_SIZE * CELL_SIZE  

COLORS = {  
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

# ================= 地图配置 =================  
MAP_CONFIGS = [  
    {  # 练习地图  
        'name': "练习地图",  
        'start': (7, 42),  
        'obstacles': []  # 去掉目标点
    }  
]  

# ================= 数据管理系统 =================  
class ExperimentData:  
    def __init__(self):  
        self.reset()  
        
    def reset(self):  
        self.current_map = 0  
        self.paths = [[] for _ in range(1)]  # 只保留练习地图  
        self.start_times = [0]*1  
        self.end_times = [0]*1  
    
    def add_step(self, pos):  
        pass  # 不需要保存路径数据  
    
    def undo_step(self):  
        pass  # 不需要撤销路径数据  

# ================= 游戏核心类 =================  
class PathGame:  
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
            pygame.draw.line(self.game_surface, COLORS['grid'],  
                             (i * CELL_SIZE, 0), (i * CELL_SIZE, GAME_SIZE))  
            pygame.draw.line(self.game_surface, COLORS['grid'],  
                             (0, i * CELL_SIZE), (GAME_SIZE, i * CELL_SIZE))  
    
    def draw_obstacles(self):  
        for x, y, w, h in self.config['obstacles']:  
            rect_x = x * CELL_SIZE  
            rect_y = (GRID_SIZE - y - h) * CELL_SIZE  
            pygame.draw.rect(self.game_surface, COLORS['obstacle'],  
                             (rect_x, rect_y, w*CELL_SIZE, h*CELL_SIZE))  
    
    def draw_points(self):  
        start_pos = self.convert_coords(*self.config['start'])  
        pygame.draw.circle(self.game_surface, COLORS['start'], start_pos, 8)  
        
        current_pos = self.convert_coords(*self.current_pos)  
        pygame.draw.circle(self.game_surface, COLORS['current'], current_pos, 8)  # 移除目标点的绘制
    
    def draw_path(self):  
        if len(self.path) > 1:  
            points = [self.convert_coords(x, y) for x, y in self.path]  
            pygame.draw.lines(self.game_surface, (0,0,0), False, points, 3)  
    
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
                if event.key == K_UP: dy = 1  
                elif event.key == K_DOWN: dy = -1  
                elif event.key == K_LEFT: dx = -1  
                elif event.key == K_RIGHT: dx = 1  
                elif event.key == K_ESCAPE:  # ESC key pressed, end game
                    self.finished = True
                    return  
                else: return  
                
                new_x = self.current_pos[0] + dx  
                new_y = self.current_pos[1] + dy  
                
                if self.is_obstructed(new_x, new_y):  
                    return  
                if not (0 <= new_x <= GRID_SIZE and 0 <= new_y <= GRID_SIZE):  
                    return  
                
                self.current_pos = [new_x, new_y]  
                self.path.append(tuple(self.current_pos))  
    
    def check_finish(self):  
        # Removed the target check, as there is no target now
        return False  
    
    def update(self, events):  
        self.handle_input(events)  
        self.game_surface.fill(COLORS['background'])  
        self.draw_grid()  
        self.draw_obstacles()  
        self.draw_points()  
        self.draw_path()  

# ================= 页面系统 =================  
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
        screen.fill(COLORS['panel_bg'])        
        title_surf = self.title_font.render(self.title, True, COLORS['text'])  
        screen.blit(title_surf, (50, 50))  
        
        y = 150  
        for line in self.content.split('\n'):  
            text_surf = self.font.render(line, True, COLORS['text'])  
            screen.blit(text_surf, (50, y))  
            y += 30  
        
        # 右下角按钮配置  
        btn_width = 180  
        btn_rect = pygame.Rect(1000, 700, btn_width, 60)  
        mouse_pos = pygame.mouse.get_pos()  
        btn_color = COLORS['button_hover'] if btn_rect.collidepoint(mouse_pos) else COLORS['button']  
        
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=8)  
        text_surf = self.font.render("下一页", True, (255,255,255))  
        screen.blit(text_surf, (btn_rect.x+50, btn_rect.y+15))  
    
    def draw_panel(self, screen):  
        if self.is_game:  
            panel = pygame.Surface((400, 800))  
            panel.fill(COLORS['panel_bg'])  
            
            title_surf = self.title_font.render(self.title, True, COLORS['text'])  
            panel.blit(title_surf, (20, 20))  
            
            y = 100  
            for line in self.content.split('\n'):  
                text_surf = self.font.render(line, True, COLORS['text'])  
                panel.blit(text_surf, (20, y))  
                y += 30  
            
            # 右侧面板按钮配置  
            btn_width = 160  
            btn_rect = pygame.Rect(220, 700, btn_width, 60)  
            mouse_pos = pygame.mouse.get_pos()  
            panel_mouse = (mouse_pos[0]-800, mouse_pos[1])  
            
            btn_color = COLORS['button_hover'] if btn_rect.collidepoint(panel_mouse) else COLORS['button']  
            pygame.draw.rect(panel, btn_color, btn_rect, border_radius=8)  
            
            btn_text = "开始规划" if self.map_index > 0 else "开始"  
            text_surf = self.font.render(btn_text, True, (255,255,255))  
            panel.blit(text_surf, (btn_rect.x+40, btn_rect.y+15))  
            
            screen.blit(panel, (800, 0))  
        else:  
            self.draw_full_text_page(screen)  
    
    def update(self, screen, data, events):  
        if self.is_game:  
            if not self.game_instance:  
                self.game_instance = PathGame(screen, data, MAP_CONFIGS[self.map_index])  
            
            if self.game_instance and not self.game_instance.finished:  
                self.game_instance.update(events)  
                screen.blit(self.game_instance.game_surface, (0, 0))  
                
                # Removed the finish check
                return False  
        return True  

# ================= 主程序 =================  
def main():  
    pygame.init()  
    screen = pygame.display.set_mode(SCREEN_SIZE)  
    pygame.display.set_caption("路径规划实验")  
    clock = pygame.time.Clock()  
    
    data = ExperimentData()  
    
    pages = [  
        GamePage("欢迎页", "欢迎参与路径规划实验！"),  
        GamePage("任务说明",   
            "您的任务是规划网格地图地图中，绘制一条从起点到目标点的路径。\n\n"  
            "本次实验一共会有四组网格地图需要完成。在实验过程中，我们将指定一个目标点，\n您需要根据该目标点设计路径，并通过路径的设计来尽可能让对手猜不出您的真实目标。\n\n"  
            ),  
        GamePage("练习阶段",   
            "操作说明：\n"  
            "1. 点击右侧开始按钮激活游戏\n"  
            "2. 使用方向键控制移动\n"  
            "3. 熟悉操作后，可以按Esc键结束游戏\n",
            map_index=0, is_game=True),  
        GamePage("准备开始", "现在你已经了解了该游戏的过程，点击确认键正式开始游戏！")  
    ]  
    
    current_page = 0  
    running = True    
    
    while running: 
        screen.fill(COLORS['background'])  
        events = pygame.event.get()  
        page = pages[current_page]  
        
        # ========== 事件处理核心逻辑 ==========  
        for event in events:  
            if event.type == QUIT:  
                running = False  
                
            if event.type == MOUSEBUTTONDOWN:  
                x, y = event.pos  
                
                # 统一处理右下角按钮区域 (1000-1180, 700-760)  
                if 1000 <= x <= 1180 and 700 <= y <= 760:  
                    # 处理说明页翻页  
                    if current_page == 1:  
                        current_page += 1  
                    # 处理常规
                    elif current_page < len(pages)-1:  
                        # 游戏页需完成才能翻页  
                        if page.is_game:  
                            if page.game_instance and page.game_instance.finished:  
                                current_page += 1  
                        else:  
                            current_page += 1  
                    # 退出程序  
                    else:  
                        running = False  
                
                # 处理游戏页开始按钮（同一区域）  
                if page.is_game and 1020 <= x <= 1180 and 700 <= y <= 760:  
                    if not page.game_instance.active:  
                        page.game_instance.active = True  
                        # 记录开始时间  
                        if not data.start_times[page.map_index]:  
                            data.start_times[page.map_index] = time.time()  
        
        # ========== 页面渲染逻辑 ==========  
        if current_page == 1:  # 全屏文字页特殊处理  
            page.draw_full_text_page(screen)  
        else:  
            page.draw_panel(screen)  
        
        # ========== 游戏逻辑更新 ==========  
        if page.is_game and current_page not in [1]:  
            if page.update(screen, data, events):  
                # 游戏完成时自动翻页  
                if current_page < len(pages)-1:  
                    current_page += 1  
                else:  
                    # 退出游戏或结束实验
                    running = False
        
        pygame.display.flip()  
        clock.tick(30)  
    
    pygame.quit()  
    sys.exit()  

if __name__ == "__main__":  
    main()  