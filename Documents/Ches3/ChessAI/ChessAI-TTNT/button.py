import pygame

class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

class RadioButton():
    def __init__(self, pos, text_input, font, base_color, hovering_color, selected_color, radius=15):
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.selected_color = selected_color
        self.text_input = text_input
        self.radius = radius
        self.selected = False  # Trạng thái được chọn

        # Tạo text
        self.text = self.font.render(self.text_input, True, self.base_color)
        self.text_rect = self.text.get_rect(midleft=(self.x_pos + self.radius * 2 + 10, self.y_pos))

        # Tạo hình tròn (radio button)
        self.circle_rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.circle_rect.center = (self.x_pos, self.y_pos)

    def update(self, screen):
        # Vẽ hình tròn
        pygame.draw.circle(screen, self.selected_color if self.selected else self.base_color, self.circle_rect.center, self.radius)
        pygame.draw.circle(screen, self.hovering_color, self.circle_rect.center, self.radius, 2)  # Viền ngoài
        # Vẽ text
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        # Kiểm tra nếu click vào hình tròn
        if self.circle_rect.collidepoint(position):
            return True
        return False
