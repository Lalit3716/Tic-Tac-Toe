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

	def check_click(self, onClick):
		left_click = pygame.mouse.get_pressed()[0]
		if self.config["hover"]:
			if self.rect.collidepoint(pygame.mouse.get_pos()):
				self.config["color"] = self.hover
			else:
				self.config["color"] = self.color

		if left_click:
			if self.rect.collidepoint(pygame.mouse.get_pos()):
				onClick()

	def draw(self):
		btn = self.config
		pygame.draw.rect(self.display_surface, btn["color"], self.rect, border_radius=btn["border_radius"])
		if btn["outline"]:
			pygame.draw.rect(self.display_surface, (0, 0, 0), self.rect, border_radius=btn["border_radius"], width=btn["outline"])
		if btn["text"]:
			text_surface = self.font.render(btn["text"], True, btn["text_color"])
			pos = text_surface.get_rect(center = self.rect.center)
			self.display_surface.blit(text_surface, pos)

	def active(self, onClick):
		self.check_click(onClick)
		self.draw()
