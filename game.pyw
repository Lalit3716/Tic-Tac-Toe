import pygame
import socket
import threading
import numpy as np
import pickle
from string import ascii_letters
from random import choice, sample
from utils import Button, Input

# Initialize Pygame
pygame.init()


# Global Variables
SCREEN_W = 800
SCREEN_H = 600
STATE = "main_menu"
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Tic Tac Toe")
clock = pygame.time.Clock()


# Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = socket.gethostbyname("localhost")
PORT = 5556

# Controller Class TO Control The states of game
class Controller:
	def __init__(self):
		# Game
		self.game = Game(self.error_contoller)

		# Title
		self.title = self.game.font_obj.render("Tic Tac Toe", True, "#86340A")
		self.title_rect = self.title.get_rect(center=(SCREEN_W // 2, 50))

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
		self.choose_ai_btn = Button(
			screen, (SCREEN_W // 2 - 100, SCREEN_H // 2 - 50), self.btn_config)

		self.choose_two_player_btn = Button(screen,
											(SCREEN_W // 2 + 100,
											 SCREEN_H // 2 - 50),
											{**self.btn_config,
											 "text": "Two Player Mode",
											 "size": (200,
													  60)})

		self.choose_multiplayer_btn = Button(
			screen,
			(SCREEN_W // 2,
			 SCREEN_H // 2 + 50),
			{
				**self.btn_config,
				"text": "Multiplayer",
				"size": (
					200,
					60)})

		# Input Fields
		self.name_field_font = self.game.font_obj.render(
			"Name", True, "#000000")
		self.name_field_pos = self.name_field_font.get_rect(center=(250, 250))
		self.name_field = Input(150, 300, size=(200, 25))

		self.room_field_font = self.game.font_obj.render(
			"Room ID", True, "#000000")
		self.room_field_pos = self.room_field_font.get_rect(center=(550, 250))
		self.room_field = Input(450, 300, size=(200, 25))

		self.all_inputs = [self.name_field, self.room_field]

		self.join_btn = Button(screen,
							   (SCREEN_W // 2 - 70,
								SCREEN_H // 2 + 150),
							   {**self.btn_config,
								"text": "Join",
								"size": (100,
										 40)})
		self.create_btn = Button(screen,
								 (SCREEN_W // 2 + 70,
								  SCREEN_H // 2 + 150),
								 {**self.btn_config,
								  "text": "Create",
								  "size": (100,
										   40)})

		self.info_font = pygame.font.Font(None, 16)
		self.error_font = pygame.font.Font(None, 32)
		self.err_msg = ""

		self.info1_font = self.info_font.render(
			"Leave Blank For Creating Room", True, "#000000")
		
		self.info2_font = self.info_font.render(
			"Name Field Must Not Be Empty", True, "#000000")

		self.error_surf = self.error_font.render(self.err_msg, True, "#FF0000")

	def error_contoller(self, msg=""):
		self.err_msg = msg
		
	def on_choose_ai_clk(self):
		global STATE
		self.game.set_mode("AI")
		STATE = "playing"

	def on_choose_two_player_clk(self):
		global STATE
		self.game.set_mode("Two Player")
		STATE = "playing"

	def on_choose_multiplayer_clk(self):
		global STATE
		STATE = "room"

	def on_join_btn_clk(self):
		if self.name_field.input.strip() != "" and self.room_field.input.strip() != "" and len(self.room_field.input.strip()) == 6:
			try:
				server.connect((IP, PORT))
				client = pickle.dumps(
					{"name": self.name_field.input, "room_id": self.room_field.input, "req": "join"})
				self.game.set_mode("Multiplayer")
				server.send(client)

			except:
				self.err_msg = "Server Down Sorry!"

		else:
			if self.name_field.input.strip() == "":
				self.err_msg = "Name Empty"
			elif self.room_field.input.strip() == "":
				self.err_msg = "Room ID Empty"
			elif len(self.room_field.input) != 6:
				self.err_msg = "Room ID Must Be Six Letters Long"

	def on_create_btn_clk(self):
		if self.name_field.input.strip() != "":
			try:
				server.connect((IP, PORT))
				room_id = "".join(sample(ascii_letters, 6))
				client = pickle.dumps(
					{"name": self.name_field.input, "room_id": room_id, "req": "create"})
				self.game.set_mode("Multiplayer")
				server.send(client)

			except:
				self.err_msg = "Server Down, Sorry!"

	def run(self):
		global STATE

		# Background
		screen.fill("grey")

		# Title
		screen.blit(self.title, self.title_rect)

		# Game
		if STATE == "main_menu":
			self.choose_ai_btn.active(self.on_choose_ai_clk)
			self.choose_two_player_btn.active(self.on_choose_two_player_clk)
			self.choose_multiplayer_btn.active(self.on_choose_multiplayer_clk)

		elif STATE == "room":
			screen.blit(self.name_field_font, self.name_field_pos)
			self.name_field.active()
			screen.blit(self.info2_font, (150, 330))

			screen.blit(self.room_field_font, self.room_field_pos)
			self.room_field.active()
			screen.blit(self.info1_font, (450, 330))

			self.join_btn.active(self.on_join_btn_clk)
			self.create_btn.active(self.on_create_btn_clk)

			# Show Errors
			self.error_surf = self.error_font.render(self.err_msg, True, "#FF0000")
			self.err_rect = self.error_surf.get_rect(center=(SCREEN_W//2, 150))
			screen.blit(self.error_surf, self.err_rect)

		elif STATE == "playing":
			self.game.run()


# Main Game Class
class Game:
	def __init__(self, error_contoller=None):

		# General Setup
		self.mode = None
		self.grid_surface = pygame.Surface((300, 300), pygame.SRCALPHA)
		self.grid_rect = self.grid_surface.get_rect(
			center=(SCREEN_W // 2, SCREEN_H // 2))
		self.boxes = np.zeros((3, 3), dtype=object)
		self.create_boxes()
		self.player_turn = True
		self.opponent_turn = False
		self.opponent_left = False
		self.move_number = 0
		self.won = False
		self.winner_boxes = None
		self.win_type = None
		self.loose = False
		self.draw = False
		self.player = "X"
		self.opponent = "O"
		self.p1 = "X"
		self.p2 = "O"
		self.room_id = "None"
		self.ai_timer = False
		self.ai_timeout = 30

		# Cross/Circles
		self.font_obj = pygame.font.Font(None, 60)

		# Restart Button
		self.restart_btn_pos = (SCREEN_W // 2 - 80, SCREEN_H - 80)
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
		self.restart_btn = Button(
			screen, self.restart_btn_pos, self.restart_btn_config)
		
		self.main_menu_config = {**self.restart_btn_config,
								 "text": "Select Mode", "size": (150, 40)}
		self.main_menu_btn = Button(
			screen, (SCREEN_W // 2 + 80, SCREEN_H - 80), self.main_menu_config)

		# Multiplayer Error Controller
		self.error_contoller = error_contoller

	def set_mode(self, mode):
		self.mode = mode
		if self.mode == "Multiplayer":
			self.opponent_left = False
			self.thread = threading.Thread(target=self.recv_server)
			self.thread.start()

	def on_restart_btn_clk(self):
		if self.mode == "Multiplayer":
			self.send_server("Restart Button Clicked")
		
		else:
			err_contol = self.error_contoller
			mode = self.mode
			self.__init__()
			self.mode = mode # Preserve Last Mode
			self.error_contoller = err_contol # Preserve Error Control Method

	def on_select_mode_btn_clk(self):
		global STATE, server
	
		if self.mode == "Multiplayer":
			self.send_server("Select Button Clicked")
			server.close()
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		err_contol = self.error_contoller
		self.__init__()
		self.error_contoller = err_contol # Preserve Error Control
		STATE = "main_menu"

	def draw_grid(self):
		grid_w, grid_h = self.grid_rect.size
		w = grid_w // 3
		h = grid_h // 3
		pygame.draw.line(self.grid_surface, (0, 0, 0), (w, 0), (w, grid_h), 2)
		pygame.draw.line(self.grid_surface, (0, 0, 0),
						 (2 * w, 0), (2 * w, grid_h), 2)
		pygame.draw.line(self.grid_surface, (0, 0, 0), (0, h), (grid_w, h), 2)
		pygame.draw.line(self.grid_surface, (0, 0, 0),
						 (0, 2 * h), (grid_w, 2 * h), 2)
		screen.blit(self.grid_surface, self.grid_rect)

	def ai_choice(self):
		
		# First Move after Player
		if self.move_number == 1:
			position = self.player_box[2]
			if position == "center":
				x, y = choice([(0, 0), (0, 2), (2, 0), (2, 2)])

			elif position == "corner":
				x, y = 1, 1

			elif position == "edge":
				x, y = 1, 1

		else:
			changed = False
			res = self.ai_logic(self.player)		# Defeats Player
			if res is not None:
				x, y = res
				changed = True

			# Favours itself over Defeating Player
			res = self.ai_logic(self.opponent)
			if res is not None:
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

		choosed_box = self.boxes[x, y]
		choosed_box[1] = self.opponent  # To be extra safe
		self.player_turn = True
		self.opponent_turn = False

	def ai_logic(self, player):
		# Checks Diagonal For 2 X's or O's

		d1 = list(map(lambda x: x[1] == player, np.diag(self.boxes)))
		player_count = d1.count(True)
		if player_count == 2:
			x1 = d1.index(False)
			y1 = d1.index(False)
			if self.boxes[x1, y1][1] == "":
				self.boxes[x1, y1][1] == self.opponent
				return x1, y1

		d2 = list(map(lambda x: x[1] == player,
					  np.diag(self.boxes[::-1])[::-1]))
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
			row = list(map(lambda x: x[1] == player, self.boxes[i, :]))
			player_count = row.count(True)
			if player_count == 2:
				x1 = i
				y1 = row.index(False)
				if self.boxes[x1, y1][1] == "":
					self.boxes[x1, y1][1] == self.opponent
					return x1, y1

			# Col
			col = list(map(lambda x: x[1] == player, self.boxes[:, i]))
			player_count = col.count(True)
			if player_count == 2:
				x1 = col.index(False)
				y1 = i
				if self.boxes[x1, y1][1] == "":
					self.boxes[x1, y1][1] == self.opponent
					return x1, y1

	def handle_normal_input(self, event):
		if event.button == 1 and not (self.won or self.loose or self.draw):
			for ix, iy in np.ndindex(self.boxes.shape):
				self.player_box = self.boxes[ix, iy]
				if self.player_box[1] == "" and self.player_box[0].collidepoint(
						event.pos):
					if self.player_turn and not self.draw:
						self.player_box[1] = self.player
						self.move_number += 1
						self.player_turn = False
						self.opponent_turn = True
						self.check_draw()
						self.check_win()

						if self.mode == "AI":
							if not (self.draw or self.loose or self.won):
								self.ai_timer = True

					elif self.opponent_turn and not self.mode == "AI" and not (self.draw or self.won or self.loose):
						self.player_box[1] = self.opponent
						self.move_number += 1
						self.player_turn = True
						self.opponent_turn = False
						self.check_draw()
						self.check_win()

					break

	def handle_multiplayer_input(self, event):
		if event.button == 1 and not (
				self.won or self.loose or self.draw) and self.player_turn:
			for ix, iy in np.ndindex(self.boxes.shape):
				self.player_box = self.boxes[ix, iy]
				if self.player_box[1] == "" and self.player_box[0].collidepoint(
						event.pos):
					self.player_box[1] = self.player
					self.player_turn = False
					self.opponent_turn = True
					self.check_draw()
					self.check_win()
					self.send_server({"ix": ix, "iy": iy})
					break

	def recv_server(self):
		global server, STATE
		while True:
			try:
				response = server.recv(5000)
				if response:
					response = pickle.loads(response)
					event = response["event"]
					
					if event == "room_created":
						self.p1 = response["name"]
						self.p2 = "Waiting"
						self.room_id = response["room_id"]
						self.player_turn = False
						self.opponent_turn = True
						STATE = "playing"
						self.error_contoller()

					elif event == "p2_joined":
						STATE = "playing"
						self.p1 = response["p1"]
						self.p2 = response["p2"]
						self.room_id = response["room_id"]
						self.create_boxes()
						self.draw = False
						self.won = False
						self.loose = False
						self.oppponent_left = False
						self.player_turn = response["player_turn"]
						self.opponent_turn = not self.player_turn
						self.error_contoller()

					elif event == "player_move":
						x = response["ix"]
						y = response["iy"]
						self.boxes[x, y][1] = self.opponent
						self.player_turn = True
						self.opponent_turn = False
						self.check_win()
						self.check_draw()

					elif event == "restart":
						self.create_boxes()
						self.won = False
						self.loose = False
						self.draw = False
						self.player_turn = response["player_turn"]
						self.opponent_turn = not self.player_turn

					elif event == "Opponent Left":
						self.p2 = f"{self.p2} Left"
						self.player_turn = False
						self.opponent_turn = True
						self.opponent_left = True

					elif event == "error":
						self.error_contoller(response["message"])
						server.close()
						server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			except:
				break

	def send_server(self, obj):
		obj = pickle.dumps(obj)
		server.send(obj)

	def draw_crosses_and_circles(self):
		for ix, iy in np.ndindex(self.boxes.shape):
			color = (255, 0, 0) if self.boxes[ix,
											  iy][1] == "O" else (0, 0, 255)
			text_surface = self.font_obj.render(
				self.boxes[ix, iy][1], True, color)
			rect = text_surface.get_rect(center=self.boxes[ix, iy][0].center)
			screen.blit(text_surface, rect)

	def create_boxes(self):
		grid_w, grid_h = self.grid_rect.size
		w = grid_w // 3
		h = grid_h // 3
		points = np.array([
			[(0, 0), (w, 0), (2 * w, 0)],
			[(0, h), (w, h), (2 * w, h)],
			[(0, 2 * h), (w, 2 * h), (2 * w, 2 * h)],
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

	def check_win(self):
		# Rows and Coloumns
		for i in range(3):
			if all(map(lambda x: x[1] == self.player,
				   row := self.boxes[i, :])):
				self.won = True
				self.winner_boxes = row
				self.win_type = "row"

			elif all(map(lambda x: x[1] == self.opponent, row := self.boxes[i, :])):
				self.loose = True
				self.winner_boxes = row
				self.win_type = "row"

			elif all(map(lambda x: x[1] == self.player, col := self.boxes[:, i])):
				self.won = True
				self.winner_boxes = col
				self.win_type = "col"

			elif all(map(lambda x: x[1] == self.opponent, col := self.boxes[:, i])):
				self.loose = True
				self.winner_boxes = col
				self.win_type = "col"

		# Checking Diagonals
		if all(map(lambda x: x[1] == self.player,
			   main_diag := np.diag(self.boxes))):
			self.won = True
			self.winner_boxes = main_diag
			self.win_type = "main_diag"

		elif all(map(lambda x: x[1] == self.player, diag := np.diag(self.boxes[::-1])[::-1])):
			self.won = True
			self.winner_boxes = diag
			self.win_type = "diag"

		elif all(map(lambda x: x[1] == self.opponent, main_diag := np.diag(self.boxes))):
			self.loose = True
			self.winner_boxes = main_diag
			self.win_type = "main_diag"

		elif all(map(lambda x: x[1] == self.opponent, diag := np.diag(self.boxes[::-1])[::-1])):
			self.loose = True
			self.winner_boxes = diag
			self.win_type = "diag"

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

	def show_winner(self, boxes, type):
		color = "#170055"
		for box in boxes:
			if type == "row":
				pygame.draw.line(
					screen, color, box[0].midleft, box[0].midright, 2)
			elif type == "col":
				pygame.draw.line(
					screen, color, box[0].midtop, box[0].midbottom, 2)
			elif type == "main_diag":
				pygame.draw.line(
					screen,
					color,
					box[0].topleft,
					box[0].bottomright,
					2)
			elif type == "diag":
				pygame.draw.line(
					screen,
					color,
					box[0].topright,
					box[0].bottomleft,
					2)

	def display_text(self, text):
		if text == "won":
			if self.mode == "AI":
				won_text = self.font_obj.render(
					"Player Won", True, (0, 0, 255))

			elif self.mode == "Multiplayer":
				won_text = self.font_obj.render(
					f"{self.p1} Won", True, (0, 0, 255))

			else:
				won_text = self.font_obj.render(
					"Player-1 Won", True, (0, 0, 255))

			won_text_rect = won_text.get_rect(center=(SCREEN_W // 2, 100))
			screen.blit(won_text, won_text_rect)

		elif text == "loose":
			if self.mode == "AI":
				loose_text = self.font_obj.render("AI Won", True, (255, 0, 0))

			elif self.mode == "Multiplayer":
				loose_text = self.font_obj.render(
					f"{self.p2} Won", True, (255, 0, 0))

			else:
				loose_text = self.font_obj.render(
					"Player-2 Won", True, (255, 0, 0))

			loose_text_rect = loose_text.get_rect(center=(SCREEN_W // 2, 100))
			screen.blit(loose_text, loose_text_rect)

		elif text == "draw":
			draw_text = self.font_obj.render("Draw", True, "#7027A0")
			draw_text_rect = draw_text.get_rect(center=(SCREEN_W // 2, 100))
			screen.blit(draw_text, draw_text_rect)

	def draw_hud(self):
		font_obj = pygame.font.Font(None, 40)
		if self.mode == "AI":
			player = font_obj.render(
				self.player + " - Player", True, (0, 0, 255))
			opponent = font_obj.render(
				self.opponent + " - AI", True, (255, 0, 0))

		elif self.mode == "Multiplayer":
			player = font_obj.render(
				f"{self.p1} - {self.player}", True, (0, 0, 255))
			opponent = font_obj.render(
				f"{self.p2} - {self.opponent}", True, (255, 0, 0))
			room_id = font_obj.render(
				f"Room - {self.room_id}", True, "#000000")
			screen.blit(room_id, (50, 150))

		else:
			player = font_obj.render(
				self.player + " - Player 1", True, (0, 0, 255))
			opponent = font_obj.render(
				self.opponent + " - Player 2", True, (255, 0, 0))

		font_obj = pygame.font.Font(None, 35)

		if self.player_turn:
			turn = font_obj.render(
				"Waiting for - " + self.player, True, (0, 0, 255))

		elif self.opponent_turn:
			turn = font_obj.render(
				"Waiting for - " + self.opponent, True, (255, 0, 0))

		screen.blit(player, (50, 35))
		screen.blit(opponent, (50, 85))

		if not (self.draw or self.won or self.loose):
			if not self.mode == "Multiplayer" or (self.mode == "Multiplayer" and self.p2 != "Waiting"):
				screen.blit(turn, (SCREEN_W - 260, SCREEN_H - 565))

	def run(self):
		# Graphics
		self.draw_grid()
		self.draw_crosses_and_circles()
		self.draw_hud()

		# AI
		if self.mode == "AI":
			if self.ai_timer:
				self.ai_timeout -= 1

			if self.ai_timeout <= 0:
				self.ai_choice()
				self.check_draw()
				self.check_win()
				self.ai_timer = False
				self.ai_timeout = 30

		# Texts
		if self.won:
			self.display_text("won")
			self.show_winner(self.winner_boxes, self.win_type)
		elif self.loose:
			self.display_text("loose")
			self.show_winner(self.winner_boxes, self.win_type)
		elif self.draw:
			self.display_text("draw")

		# Buttons
		if self.mode == "Multiplayer":
			if not self.opponent_left and (self.won or self.draw or self.loose):
				self.restart_btn.active(self.on_restart_btn_clk)
		else:
			self.restart_btn.active(self.on_restart_btn_clk)

		self.main_menu_btn.active(self.on_select_mode_btn_clk)


# Contoller Instance
controller = Controller()


while True:
	# Event Loop
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
		
			if controller.game.mode == "Multiplayer" and STATE == "playing":
				controller.game.send_server("Select Button Clicked")
				server.close()

			pygame.quit()
			exit()

		if event.type == pygame.MOUSEBUTTONDOWN and STATE == "playing":
			if controller.game.mode == "Multiplayer":
				controller.game.handle_multiplayer_input(event)
			else:
				controller.game.handle_normal_input(event)

		if event.type == pygame.KEYDOWN:
			if STATE == "room":
				for _input in controller.all_inputs:
					_input.take_input(event)


	# Run The Game In MainLoop
	controller.run()

	clock.tick(60)
	pygame.display.update()