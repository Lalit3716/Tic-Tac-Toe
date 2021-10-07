import pygame


class Button:
    def __init__(self, surface, pos, config):
        if config["text"]:
            self.font = pygame.font.Font(None, config["text_size"])
        self.config = config
        self.color = config["color"]
        if config["hover"]:
            self.hover = config["hover"]
        self.display_surface = surface
        self.button = pygame.Surface(config["size"])
        self.button.set_colorkey((0, 0, 0))
        self.rect = self.button.get_rect(center=pos)
        self.clicked = False

    def check_click(self, onClick):
        left_click = pygame.mouse.get_pressed()[0]
        if self.config["hover"]:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.config["color"] = self.hover
            else:
                self.config["color"] = self.color

        if left_click and not self.clicked:
            self.clicked = True
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                onClick()
        elif not left_click and self.clicked:
            self.clicked = False

    def draw(self):
        btn = self.config
        pygame.draw.rect(
            self.display_surface,
            btn["color"],
            self.rect,
            border_radius=btn["border_radius"])
        if btn["outline"]:
            pygame.draw.rect(
                self.display_surface,
                (0,
                 0,
                 0),
                self.rect,
                border_radius=btn["border_radius"],
                width=btn["outline"])
        if btn["text"]:
            text_surface = self.font.render(
                btn["text"], True, btn["text_color"])
            pos = text_surface.get_rect(center=self.rect.center)
            self.display_surface.blit(text_surface, pos)

    def active(self, onClick):
        self.check_click(onClick)
        self.draw()


class Input:
    def __init__(self, x, y, size, text_size=32, width=1, border_radius=0):
        self.display_surface = pygame.display.get_surface()
        self.x = x
        self.y = y
        self.size = size
        self.width = width
        self.border_radius = border_radius
        self.rect_color = "black"
        self.font_obj = pygame.font.Font(None, text_size)
        self.rect = pygame.Rect((x, y), size)
        self.input = ""
        self.focused = False
        self.key_pressed = False

    def focus(self):
        left_click = pygame.mouse.get_pressed()[0]

        if left_click:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.focused = True
                self.width = 2
                self.rect_color = "#FF5C58"
            else:
                self.focused = False
                self.width = 1
                self.rect_color = "black"

    def display_text(self):
        text = self.font_obj.render(self.input, True, "#000000")
        pos = self.x + 10, self.y + 5
        self.display_surface.blit(text, pos)

    def take_input(self, event):
        if self.focused:
            if event.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]
            else:
                self.input += event.unicode

    def active(self):
        pygame.draw.rect(
            self.display_surface,
            self.rect_color,
            self.rect,
            width=self.width,
            border_radius=self.border_radius)
        self.display_text()
        self.focus()
