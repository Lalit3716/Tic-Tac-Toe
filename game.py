import pygame
import numpy as np
from random import choice
from utils import Button
from _global import Global

pygame.init()

SCREEN_W = 800
SCREEN_H = 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Tic Tac Toe")
clock = pygame.time.Clock()

class Controller:
	def __init__(self):
		# Game
		self.game = Game()

		# Title
		self.title = self.game.font_obj.render("Tic Tac Toe", True, "#86340A")
		self.title_rect = self.title.get_rect(center=(SCREEN_W//2, 50))

		# Select Buttons
		self.btn_config = {
			"size": (150, 60),
			"color": "#57CC99",
			"border_radius": 20,
			"text": "AI Mode",
			"text_size": 30,
			"text_color": (0, 0, 0),
			"outline": 1,
			"hover": "#FF5C58"
		}
		self.choose_ai_btn = Button(screen, (SCREEN_W//2-100, SCREEN_H//2), self.btn_config)
		self.choose_two_player_btn = Button(screen, (SCREEN_W//2+100, SCREEN_H//2), {**self.btn_config, "text": "Two Player Mode", "size":(200, 60)})

	def on_choose_ai_clk(self):
		self.game.set_mode("AI")
		Global.state = "playing"

	def on_choose_two_player_clk(self):
		self.game.set_mode("Two Player")
		Global.state = "playing"

	def run(self):
		state = Global.state

		# Background
		screen.fill("grey")
		
		# Title
		screen.blit(self.title, self.title_rect)

		# Game
		if state == "main_menu":
			self.choose_ai_btn.active(self.on_choose_ai_clk)
			self.choose_two_player_btn.active(self.on_choose_two_player_clk)

		elif state == "playing":
			self.game.run()

class Game:
	def __init__(self):

		# General Setup
		self.grid_surface = pygame.Surface((300, 300), pygame.SRCALPHA)
		self.grid_rect = self.grid_surface.get_rect(center=(SCREEN_W//2, SCREEN_H//2))
		self.boxes = np.zeros((3, 3), dtype=object)
		self.create_boxes()
		self.player_turn = True
		self.opponent_turn = False
		self.move_number = 0
		self.won = False
		self.loose = False
		self.draw = False
		self.player = "X"
		self.opponent = "O"

		# Cross/Circles
		self.text_surfaces = []
		self.font_obj = pygame.font.Font(None, 60)	

		# Restart Button
		self.restart_btn_pos = (SCREEN_W//2-100, SCREEN_H-80)
		self.restart_btn_config = {
			"size": (130, 40),
			"color": "#57CC99",
			"border_radius": 10,
			"text": "Restart",
			"text_size": 30,
			"text_color": (0, 0, 0),
			"outline": 1,
			"hover": "#FF5C58"
		}
		self.restart_btn = Button(screen, self.restart_btn_pos, self.restart_btn_config)
		self.main_menu_config = {**self.restart_btn_config, "text": "Select Mode", "size":(150, 40)}
		self.main_menu_btn = Button(screen, (SCREEN_W//2+100, SCREEN_H-80), self.main_menu_config)

	def set_mode(self, mode):
		self.mode = mode

	def on_restart_btn_clk(self):
		self.__init__()

	def on_select_mode_btn_clk(self):
		self.__init__()
		Global.state = "main_menu"

	def draw_grid(self):
		grid_w, grid_h = self.grid_rect.size
		w = grid_w//3
		h = grid_h//3
		pygame.draw.line(self.grid_surface, (0, 0, 0), (w, 0), (w, grid_h), 2)
		pygame.draw.line(self.grid_surface, (0, 0, 0), (2*w, 0), (2*w, grid_h), 2)
		pygame.draw.line(self.grid_surface, (0, 0, 0), (0, h), (grid_w, h), 2)
		pygame.draw.line(self.grid_surface, (0, 0, 0), (0, 2*h), (grid_w, 2*h), 2)
		screen.blit(self.grid_surface, self.grid_rect)		

	def ai_move(self, player_move):
		choosed_box = self.ai_choice(player_move)
		choosed_box[1] = self.opponent                                 # To be extra safe
		text_surface = self.font_obj.render(self.opponent, True, (255, 0, 0))
		text_rect = text_surface.get_rect(center=choosed_box[0].center)
		self.player_turn = True
		self.opponent_turn = False
		return text_surface, text_rect

	def ai_choice(self, player_box):
		# First Move after Player
		if self.move_number == 1:
			position = player_box[2]
			if position == "center":
				x, y = choice([(0, 0), (0, 2), (2, 0), (2, 2)])

			elif position == "corner":
				x, y = 1, 1

			elif position == "edge":
				x, y = 1, 1

		else:
			changed = False
			res = self.ai_logic(self.player)		# Defeats Player
			if res != None:
				x, y = res
				changed = True
			res = self.ai_logic(self.opponent)		# Favours itself over Defeating Player
			if res != None:
				x, y = res
				changed = True

			if not changed:
				corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
				edges = [(0, 1), (1, 0), (1, 2), (2, 1)]
				x, y = choice(corners)
				while not self.boxes[x, y][1] == "":
					if corners:
						corners.remove((x, y))
					else:
						edges.remove((x, y))
					if len(corners) == 0:						
						x, y = choice(edges)
					else:
						x, y = choice(corners)

		return self.boxes[x, y]

	def ai_logic(self, player):
		# Checks Diagonal For 2 X's or O's

		d1 = list(map(lambda x: x[1]==player , np.diag(self.boxes)))
		player_count = d1.count(True)
		if player_count == 2:
			x1 = d1.index(False)
			y1 = d1.index(False)
			if self.boxes[x1, y1][1] == "":
				self.boxes[x1, y1][1] == self.opponent
				return x1, y1

		d2 = list(map(lambda x: x[1]==player, np.diag(self.boxes[::-1])[::-1]))
		player_count = d2.count(True)
		
		if player_count == 2:
			x1 = d2.index(False)
			y1 = 2 - d2.index(False)
			if self.boxes[x1, y1][1] == "":
				self.boxes[x1, y1][1] == self.opponent
				return x1, y1

		# Checks Rows and Coloumns for 2 X's or 2 O's
		for i in range(3):
			# Row
			row = list(map(lambda x: x[1]==player, self.boxes[i, :]))
			player_count = row.count(True)
			if player_count == 2:
				x1 = i
				y1 = row.index(False)
				if self.boxes[x1, y1][1] == "":
					self.boxes[x1, y1][1] == self.opponent
					return x1, y1

			# Col
			col = list(map(lambda x: x[1]==player, self.boxes[:, i]))
			player_count = col.count(True)
			if player_count == 2:
				x1 = col.index(False)
				y1 = i
				if self.boxes[x1, y1][1] == "":
					self.boxes[x1, y1][1] == self.opponent
					return x1, y1

	def handle_input(self, event):
		if event.button == 1 and not (self.won or self.loose or self.draw):
			for ix, iy in np.ndindex(self.boxes.shape):
				box = self.boxes[ix, iy]
				if box[1] == "" and box[0].collidepoint(event.pos):
					if self.player_turn:
						player_move = self.font_obj.render(self.player, True, (0, 0, 255))
						box[1] = self.player
						self.move_number += 1
						self.player_turn = False
						self.opponent_turn = True
						self.check_draw()

						if self.mode == "AI":
							if not self.draw:
								ai_move, ai_move_rect = self.ai_move(box)
								self.text_surfaces.append((ai_move, ai_move_rect))
								self.check_draw()

					elif self.opponent_turn and not self.mode == "AI":
						player_move = self.font_obj.render(self.opponent, True, (255, 0, 0))
						box[1] = self.opponent
						self.move_number += 1
						self.player_turn = True
						self.opponent_turn = False
						self.check_draw()

					player_move_rect = player_move.get_rect(center=box[0].center)
					self.text_surfaces.append((player_move, player_move_rect))
					self.check_win()

	def draw_crosses_and_circles(self):
	 	for surface, rect in self.text_surfaces:
	 		screen.blit(surface, rect)

	def create_boxes(self):
		grid_w, grid_h = self.grid_rect.size
		w = grid_w//3
		h = grid_h//3
		points = np.array([
			[(0, 0), (w, 0), (2*w, 0)],
			[(0, h), (w, h), (2*w, h)],
			[(0, 2*h), (w, 2*h), (2*w, 2*h)],
		])
		
		offset = pygame.math.Vector2(self.grid_rect.topleft)

		for row_index, row in enumerate(points):
			for col_index, point in enumerate(row):
				point = point + offset
				rect = pygame.Rect(point, (w, h))
				item = [rect, ""]
				if (row_index, col_index) in [(0, 0), (0, 2), (2, 0), (2, 2)]:
					item.append("corner")
				elif (row_index, col_index) == (1, 1):
					item.append("center")
				else:
					item.append("edge")
				self.boxes[row_index, col_index] = item
	
	def debug(self):
		for ix, iy in np.ndindex(self.boxes.shape):
			pygame.draw.rect(screen, "#00A19D", self.boxes[ix, iy][0], 2)

	def check_win(self):
		for i in range(3):
			if all(map(lambda x: x[1]==self.player, self.boxes[i, :])):
				self.won = True

			elif all(map(lambda x: x[1]==self.opponent, self.boxes[i, :])):
				self.loose = True
			
			elif all(map(lambda x: x[1]==self.player, self.boxes[:, i])):
				self.won = True

			elif all(map(lambda x: x[1]==self.opponent, self.boxes[:, i])):
				self.loose = True
			
		if all(map(lambda x: x[1]==self.player ,np.diag(self.boxes))):
			self.won = True

		elif all(map(lambda x: x[1]==self.player ,np.diag(self.boxes[::-1])[::-1])):
			self.won = True

		elif all(map(lambda x: x[1]==self.opponent ,np.diag(self.boxes))):
			self.loose = True

		elif all(map(lambda x: x[1]==self.opponent ,np.diag(self.boxes[::-1])[::-1])):
			self.loose = True

	def check_draw(self):
		filled_boxes = np.zeros((3, 3), dtype=object)
		for ix, iy in np.ndindex(self.boxes.shape):
			if self.boxes[ix, iy][1] == "":
				filled_boxes[ix, iy] = False
			else:
				filled_boxes[ix, iy] = True

		filled_boxes = filled_boxes.flat
		if all(filled_boxes):
			self.draw = True

	def display_text(self, text):
		if text == "won":
			if self.mode == "AI":
				won_text = self.font_obj.render("Player Won", True, (0, 0, 255))
			else:
				won_text = self.font_obj.render("Player-1 Won", True, (0, 0, 255))
			won_text_rect = won_text.get_rect(center=(SCREEN_W//2, 100))
			screen.blit(won_text, won_text_rect)

		elif text == "loose":
			if self.mode == "AI":
				loose_text = self.font_obj.render("AI Won", True, (0, 0, 255))
			else:
				loose_text = self.font_obj.render("Player-2 Won", True, (255, 0, 0))
			loose_text_rect = loose_text.get_rect(center=(SCREEN_W//2, 100))
			screen.blit(loose_text, loose_text_rect)

		elif text == "draw":
			draw_text = self.font_obj.render("Draw", True, "#7027A0")
			draw_text_rect = draw_text.get_rect(center=(SCREEN_W//2, 100))
			screen.blit(draw_text, draw_text_rect)

	def draw_hud(self):
		font_obj = pygame.font.Font(None, 40)
		if self.mode == "AI":
			player = font_obj.render(self.player + " - Player", True, (0, 0, 255))
			opponent = font_obj.render(self.opponent + " - AI", True, (255, 0, 0))
		else:
			player = font_obj.render(self.player + " - Player 1", True, (0, 0, 255))
			opponent = font_obj.render(self.opponent + " - Player 2", True, (255, 0, 0))

		font_obj = pygame.font.Font(None, 35)
		if self.player_turn:
			turn = font_obj.render("Waiting for - " + self.player, True, (0, 0, 255))
		elif self.opponent_turn:
			turn = font_obj.render("Waiting for - " + self.opponent, True, (255, 0, 0))

		screen.blit(player, (50, 35))
		screen.blit(opponent, (50, 85))

		if not (self.draw or self.won or self.loose):
			screen.blit(turn, (SCREEN_W-200, SCREEN_H-550))

	def run(self):
		self.draw_grid()
		self.draw_crosses_and_circles()
		self.draw_hud()
		# self.debug()

		if self.won:
			self.display_text("won")
		elif self.loose:
			self.display_text("loose")
		elif self.draw:
			self.display_text("draw")
		
		self.restart_btn.active(self.on_restart_btn_clk)
		self.main_menu_btn.active(self.on_select_mode_btn_clk)

controller = Controller()

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()
		if event.type == pygame.MOUSEBUTTONDOWN and Global.state=="playing":
			controller.game.handle_input(event)
	
	controller.run()	

	clock.tick(60)	
	pygame.display.update()