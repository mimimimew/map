import pygame
import sys
import time
import os
from pygame.locals import *
from datetime import datetime

# ================= 字体配置 =================  
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"  
def get_font(size):  
    return pygame.font.Font(FONT_PATH, size)  

# ================= 全局配置 =================  

SCREEN_SIZE = (1200, 800)  # Define the screen size here
GRID_SIZE = 49  
CELL_SIZE = 15  
REGION_SIZE = 7  # Each region is 7x7
REGION_GRID_SIZE = GRID_SIZE // REGION_SIZE  # 7x7 regions in the 49x49 grid

# Window dimensions
WIDTH = GRID_SIZE * CELL_SIZE + 200  
HEIGHT = GRID_SIZE * CELL_SIZE

COLORS = {  
    'background': (255, 255, 255),  
    'grid': (211, 211, 211),  
    'path': (0, 0, 0),  
    'highlight': (255, 0, 0),  
    'start': (0, 0, 255),  # Color for the start point
    'current': (255, 0, 0),  
    'button': (100, 200, 100),  
    'button_hover': (50, 150, 50),
    'close 1': (0, 255, 0),  # Color for close 1 point
    'close 2': (0, 255, 0),  # Color for close 2 point
    'far 1': (255, 0, 255),  # Color for far 1 point
    'far 2': (255, 0, 255),  # Color for far 2 point   
    'selected': (169, 169, 169)  # Color for the selected regions
}  

POINTS = {  
    'start': (7, 42),  
    'close 1': (20, 18),  
    'close 2': (31, 29),  
    'far 1': (5, 1),  
    'far 2': (48, 44)  
}  

# ================= 游戏核心类 =================  
class PathGame:
    def __init__(self, parent_screen):
        pygame.init()
        self.screen = parent_screen
        self.clock = pygame.time.Clock()
        self.font = get_font(20)

        self.selected_regions = []  # To store selected regions
        self.reset_game()

    def reset_game(self):
        self.selected_regions = []  # Reset the selection

    def convert_coords(self, x, y):
        """坐标转换（逻辑坐标 → 屏幕坐标）"""
        return (x * CELL_SIZE, (GRID_SIZE - y) * CELL_SIZE)

    def draw_grid(self):
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, COLORS['grid'], (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT))
            pygame.draw.line(self.screen, COLORS['grid'], (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))

    def draw_selected_regions(self):
        """Draw the selected regions in gray."""
        for region in self.selected_regions:
            x, y = region
            rect_x, rect_y = self.convert_coords(x, y)
            pygame.draw.rect(self.screen, COLORS['selected'], 
                             (rect_x, rect_y, REGION_SIZE * CELL_SIZE, REGION_SIZE * CELL_SIZE))

    def draw_control_panel(self):
        panel_x = GRID_SIZE * CELL_SIZE
        pygame.draw.rect(self.screen, (240, 240, 240), (panel_x, 0, 200, HEIGHT))

        text_y = 50
        controls = [
            "操作说明：",
            "点击区域选中",
            "点击确认保存选择"
        ]
        for line in controls:
            text = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text, (panel_x + 20, text_y))
            text_y += 30

        # Confirm button
        button_rect = pygame.Rect(panel_x + 50, HEIGHT // 2 - 25, 100, 50)
        mouse_pos = pygame.mouse.get_pos()
        btn_color = COLORS['button_hover'] if button_rect.collidepoint(mouse_pos) else COLORS['button']

        pygame.draw.rect(self.screen, btn_color, button_rect, border_radius=5)
        btn_text = self.font.render("确认", True, (255, 255, 255))
        self.screen.blit(btn_text, (panel_x + 65, HEIGHT // 2 - 10))

    def draw_points(self):
        """Draw points on the grid."""
        for point, (x, y) in POINTS.items():
            pygame.draw.circle(self.screen, COLORS[point], 
                               (x * CELL_SIZE + CELL_SIZE // 2, (GRID_SIZE - y) * CELL_SIZE + CELL_SIZE // 2), 5)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < GRID_SIZE * CELL_SIZE and y < GRID_SIZE * CELL_SIZE:
                    # Convert to grid coordinates
                    region_x = x // (REGION_SIZE * CELL_SIZE)
                    region_y = (GRID_SIZE - y) // (REGION_SIZE * CELL_SIZE)

                    # Toggle the selection of the region
                    if (region_x, region_y) in self.selected_regions:
                        self.selected_regions.remove((region_x, region_y))
                    else:
                        self.selected_regions.append((region_x, region_y))

            if event.type == MOUSEBUTTONDOWN and 200 <= event.pos[0] <= 300 and HEIGHT // 2 - 25 <= event.pos[1] <= HEIGHT // 2 + 25:
                # When clicking on the confirm button, save the selected regions as an image
                self.save_selected_regions()
                pygame.quit()  # Exit the game after saving
                sys.exit()  # Ensure the program exits

    def save_selected_regions(self):
        folder = "selected_regions"  # Folder to save images
        if not os.path.exists(folder):
            os.makedirs(folder)

        surface = pygame.Surface((WIDTH, HEIGHT))
        surface.fill(COLORS['background'])

        self.draw_grid()
        self.draw_selected_regions()
        self.draw_points()  # Draw the points when saving the image

        # Save the image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(folder, f"selected_regions_{timestamp}.png")
        pygame.image.save(surface, image_path)
        print(f"保存成功: {image_path}")

    def update(self):
        self.screen.fill(COLORS['background'])

        # Draw grid, selected regions, points and control panel
        self.draw_grid()
        self.draw_selected_regions()
        self.draw_points()  # Draw the points every frame
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
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("区域选择游戏")

    game = PathGame(screen)
    game.run()

if __name__ == "__main__":
    main()
