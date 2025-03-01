import os  
import sys  
from datetime import datetime  

import pygame  
from pygame.locals import *  


# ================= 字体配置 =================  
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"  
def get_font(size):  
    return pygame.font.Font(FONT_PATH, size)  

# ================= 全局配置 =================  
GRID_SIZE = 49  
CELL_SIZE = 15  
PANEL_WIDTH = 200  # 右侧面板宽度  
WIDTH = GRID_SIZE * CELL_SIZE + PANEL_WIDTH  
HEIGHT = GRID_SIZE * CELL_SIZE  

COLORS = {  
    'background': (255, 255, 255),  
    'grid': (211, 211, 211),  
    'highlight': (211, 211, 211),  # 选中区域颜色  
    'button': (100, 200, 100),  
    'button_hover': (50, 150, 50)  
}  

# ================= 游戏核心类 =================  
class PathGame:  
    def __init__(self, parent_screen):  
        pygame.init()  
        self.screen = parent_screen  
        self.clock = pygame.time.Clock()  
        self.font = get_font(20)  

        self.selected_regions = []  # 存储选中的区域  
        self.reset_game()  

    def reset_game(self):  
        self.selected_regions = []  # 重置选中区域  

    def draw_grid(self):  
        """绘制基础网格和7x7分区边框"""  
        for i in range(GRID_SIZE + 1):  
            pygame.draw.line(self.screen, COLORS['grid'],  
                            (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT))  
            pygame.draw.line(self.screen, COLORS['grid'],  
                            (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))  

        # 绘制7x7分区边框  
        for i in range(0, GRID_SIZE, 7):  
            for j in range(0, GRID_SIZE, 7):  
                pygame.draw.rect(self.screen, COLORS['grid'],   
                                (j * CELL_SIZE, i * CELL_SIZE, 7 * CELL_SIZE, 7 * CELL_SIZE),   
                                width=3)  

    def draw_selected_regions(self):  
        """绘制选中的区域"""  
        for region in self.selected_regions:  
            x, y = region  
            rect_x = x * 7 * CELL_SIZE  
            rect_y = (GRID_SIZE - y - 1) * 7 * CELL_SIZE  # Y轴反转  
            pygame.draw.rect(self.screen, COLORS['highlight'],   
                            (rect_x, rect_y, 7 * CELL_SIZE, 7 * CELL_SIZE))  

    def draw_control_panel(self):  
        """绘制右侧控制面板"""  
        panel_x = GRID_SIZE * CELL_SIZE  
        pygame.draw.rect(self.screen, (240, 240, 240), (panel_x, 0, PANEL_WIDTH, HEIGHT))  

        text_y = 50  
        controls = [  
            "操作说明：",  
            "点击区域选中",  
            "再次点击取消选择",  
            "点击确认保存选择"  
        ]  
        for line in controls:  
            text = self.font.render(line, True, (0, 0, 0))  
            self.screen.blit(text, (panel_x + 20, text_y))  
            text_y += 30  

        # 确认按钮  
        button_rect = pygame.Rect(panel_x + 50, HEIGHT // 2 - 25, 100, 50)  
        mouse_pos = pygame.mouse.get_pos()  
        btn_color = COLORS['button_hover'] if button_rect.collidepoint(mouse_pos) else COLORS['button']  

        pygame.draw.rect(self.screen, btn_color, button_rect, border_radius=5)  
        btn_text = self.font.render("确认", True, (255, 255, 255))  
        self.screen.blit(btn_text, (panel_x + 65, HEIGHT // 2 - 10))  

    def handle_input(self):  
        for event in pygame.event.get():  
            if event.type == QUIT:  
                pygame.quit()  
                sys.exit()  

            if event.type == MOUSEBUTTONDOWN:  
                x, y = event.pos  
                if x < GRID_SIZE * CELL_SIZE and y < GRID_SIZE * CELL_SIZE:  
                    # 计算点击的区域坐标  
                    region_x = x // (7 * CELL_SIZE)  
                    region_y = (GRID_SIZE * CELL_SIZE - y) // (7 * CELL_SIZE)  

                    # 切换选中状态  
                    if (region_x, region_y) in self.selected_regions:  
                        self.selected_regions.remove((region_x, region_y))  
                    else:  
                        self.selected_regions.append((region_x, region_y))  

                # 检查是否点击了确认按钮  
                panel_x = GRID_SIZE * CELL_SIZE  
                button_rect = pygame.Rect(panel_x + 50, HEIGHT // 2 - 25, 100, 50)  
                if button_rect.collidepoint(event.pos):  
                    self.save_selected_regions()  

    def save_selected_regions(self):  
        folder = "selected_regions"  # 保存图片的文件夹  
        if not os.path.exists(folder):  
            os.makedirs(folder)  

        surface = pygame.Surface((WIDTH, HEIGHT))  
        surface.fill(COLORS['background'])  

        self.draw_grid()  
        self.draw_selected_regions()  

        # 保存图片  
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  
        image_path = os.path.join(folder, f"selected_regions_{timestamp}.png")  
        pygame.image.save(surface, image_path)  
        print(f"保存成功: {image_path}")  

    def update(self):  
        self.screen.fill(COLORS['background'])  

        # 绘制网格、选中区域和控制面板  
        self.draw_grid()  
        self.draw_selected_regions()  
        self.draw_control_panel()  

        pygame.display.flip()  

    def run(self):  
        while True:  
            self.handle_input()  
            self.update()  
            self.clock.tick(30)  


# ================= 主程序 =================  
def main():  
    pygame.init()  
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  
    pygame.display.set_caption("区域选择游戏")  

    game = PathGame(screen)  
    game.run()  

if __name__ == "__main__":  
    main()  