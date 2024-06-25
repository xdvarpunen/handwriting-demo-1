import hy
import pygame
from shapely.geometry import LineString

"""
install hy, pygame and shapely
"""


"""
Shapely Helper
"""


def do_shapely_lines_intersect(line1: LineString, line2: LineString):
    """Using shapely intersects"""
    return line1.intersects(line2)


def do_lines_intersect(line1, line2):
    line1_start = line1[0]
    line1_end = line1[-1]
    line2_start = line2[0]
    line2_end = line2[-1]
    line1_linestring = LineString([(line1_start[0], line1_start[1]), (line1_end[0], line1_end[1])])
    line2_linestring = LineString([(line2_start[0], line2_start[1]), (line2_end[0], line2_end[1])])
    return do_shapely_lines_intersect(line1_linestring, line2_linestring)


"""
Lisp
"""


class HyEval:
    @staticmethod
    def eval(code):
        # '(+ 1 1)' => 2
        if code == "(+11)":
            return str(hy.eval(hy.read_many('(+ 1 1)')))
        # hy.eval(hy.read_many(code))
        return code


"""
Recognition
"""


def point_in_area(area: pygame.Rect, point):
    is_point_in_area = area.collidepoint(point)
    return is_point_in_area


class Symbol:
    def __init__(self, list_of_line_drawn, symbol_represents):
        self.list_of_line_drawn = list_of_line_drawn
        self.symbol_represents = symbol_represents

    def area(self) -> pygame.Rect:
        if len(self.list_of_line_drawn) == 1:
            line1 = self.list_of_line_drawn[0]
            x = 0
            y = 1
            min_x1 = min(point[x] for point in line1)
            max_x1 = max(point[x] for point in line1)
            min_y1 = max(point[y] for point in line1)
            max_y1 = max(point[y] for point in line1)
            rect1 = pygame.Rect(min_x1, min_y1, (max_x1 - min_x1), (max_y1 - min_y1))
            return rect1
        if len(self.list_of_line_drawn) == 2:
            line1 = self.list_of_line_drawn[0] + self.list_of_line_drawn[1]
            x = 0
            y = 1
            min_x1 = min(point[x] for point in line1)
            max_x1 = max(point[x] for point in line1)
            min_y1 = min(point[y] for point in line1)
            max_y1 = max(point[y] for point in line1)
            rect1 = pygame.Rect(min_x1, min_y1, (max_x1 - min_x1), (max_y1 - min_y1))
            return rect1


def create_symbols_from_groups(lines, groups):
    symbols = []
    for key, value in groups.items():
        if len(value) == 0:
            symbol = Symbol([lines[key]], '')
            symbols.append(symbol)
        else:
            symbol = Symbol([lines[key], lines[value[0]]], '')
            symbols.append(symbol)
    return symbols


def create_groups_from_lines(lines):
    groups = {}
    index = -1
    skip_next = False
    len_of_lines = len(lines)
    for _ in lines:
        index = index + 1

        if skip_next:
            skip_next = False
            continue

        intersects = False
        if index is not len_of_lines - 1:
            intersects = do_lines_intersect(lines[index], lines[index + 1])

        if intersects:
            groups[index] = [index+1]
            skip_next = True
        else:
            groups[index] = []
            if index + 2 == len_of_lines:
                groups[index + 1] = []
                skip_next = True
    return groups


def group_by_intersecting(lines) -> list[Symbol]:
    if len(lines) == 0:
        return []

    groups = {}
    if len(lines) == 1:
        groups[0] = []
    else:
        groups = create_groups_from_lines(lines)

    symbols = create_symbols_from_groups(lines, groups)
    return symbols


def max_pointy(line):
    maxy = line[0][0]
    index = 0
    index_count = 0
    for point in line:
        if point[0] > maxy:
            maxy = point[0]
            index = index_count
        index_count = index_count + 1
    return maxy, index


def min_pointy(line):
    maxy = line[0][0]
    index = 0
    index_count = 0
    for point in line:
        if point[0] < maxy:
            maxy = point[0]
            index = index_count
        index_count = index_count + 1
    return maxy, index


def point_is_left(mid_x, line):
    count = 0
    for point in line:
        if point[0] < mid_x:
            count = count + 1
    return count


def point_is_right(mid_x, line):
    count = 0
    for point in line:
        if point[0] > mid_x:
            count = count + 1
    return count


def in_which_side_more_points(line):
    """if true then left else right"""
    min_y1, min_y1_index = min_pointy(line)
    max_y1, max_y1_index = max_pointy(line)
    delta_x = abs(line[min_y1_index][0] - line[max_y1_index][0]) / 2
    min_x_between_min_max_y = min(line[min_y1_index][0], line[max_y1_index][0])
    average_x = min_x_between_min_max_y + delta_x
    left_count = point_is_left(average_x, line)
    right_count = point_is_right(average_x, line)
    return left_count > right_count


def is_line_in_area(rect, line):
    for point in line:
        if rect.collidepoint((point[0], point[1])):
            return True
    return False


def recognize(lines, area: pygame.Rect, range_y0, range_y1, range_y2, range_y3, range_y4):
    """Convert lines into text"""
    text_to_return = ''
    groups = group_by_intersecting(lines)
    for single_group in groups:
        count_of_intersections = len(single_group.list_of_line_drawn)
        if count_of_intersections == 1:
            rect_range_y0_y1 = pygame.Rect(50, range_y0, area.width, range_y1 - range_y0)
            rect_range_y1_y2 = pygame.Rect(50, range_y1, area.width, range_y2 - range_y1)
            rect_range_y2_y3 = pygame.Rect(50, range_y2, area.width, range_y3 - range_y2)
            rect_range_y3_y4 = pygame.Rect(50, range_y3, area.width, range_y4 - range_y3)
            collides_range_y0_y1 = is_line_in_area(rect_range_y0_y1, single_group.list_of_line_drawn[0])
            collides_range_y1_y2 = is_line_in_area(rect_range_y1_y2, single_group.list_of_line_drawn[0])
            collides_range_y2_y3 = is_line_in_area(rect_range_y2_y3, single_group.list_of_line_drawn[0])
            collides_range_y3_y4 = is_line_in_area(rect_range_y3_y4, single_group.list_of_line_drawn[0])
            if collides_range_y0_y1 is False and collides_range_y1_y2 is True and collides_range_y2_y3 is True and collides_range_y3_y4 is False:
                text_to_return = text_to_return + "1"
                single_group.symbol_represents = "1"
            elif collides_range_y0_y1 is True and collides_range_y1_y2 is True and collides_range_y2_y3 is True and collides_range_y3_y4 is True:
                if in_which_side_more_points(single_group.list_of_line_drawn[0]):
                    text_to_return = text_to_return + "("
                    single_group.symbol_represents = "("
                else:
                    text_to_return = text_to_return + ")"
                    single_group.symbol_represents = ")"
        elif count_of_intersections == 2:
            rect_range_y0_y1 = pygame.Rect(50, range_y0, area.width, range_y1 - range_y0)
            rect_range_y1_y2 = pygame.Rect(50, range_y1, area.width, range_y2 - range_y1)
            rect_range_y2_y3 = pygame.Rect(50, range_y2, area.width, range_y3 - range_y2)
            rect_range_y3_y4 = pygame.Rect(50, range_y3, area.width, range_y4 - range_y3)
            single_group_area = single_group.area()
            collides_range_y0_y1 = rect_range_y0_y1.colliderect(single_group_area)
            collides_range_y1_y2 = rect_range_y1_y2.colliderect(single_group_area)
            collides_range_y2_y3 = rect_range_y2_y3.colliderect(single_group_area)
            collides_range_y3_y4 = rect_range_y3_y4.colliderect(single_group_area)
            if collides_range_y0_y1 is False and collides_range_y1_y2 is True and collides_range_y2_y3 is True and collides_range_y3_y4 is False:
                text_to_return = text_to_return + "+"
                single_group.symbol_represents = "+"
    result = HyEval.eval(text_to_return)
    return result


"""
Widgets
"""


class Text:
    def __init__(self, scene_screen_area: pygame.Rect, text, font_name='Comic Sans MS', font_size=30,
                 color=(0, 0, 0)):
        self.scene_screen_area = scene_screen_area
        self.text = text
        self.font = pygame.font.SysFont(font_name, font_size)
        self.color = color
        self.text_surface = self.font.render(self.text, False, color)

    def render(self, screen):
        screen.blit(self.text_surface, (self.scene_screen_area.x, self.scene_screen_area.y))
        pygame.draw.rect(screen, (255, 0, 0), self.scene_screen_area, 3)

    def set_text(self, text):
        self.text = text
        self.text_surface = self.font.render(self.text, False, self.color)


class Button:
    def __init__(self, scene_screen_area: pygame.Rect, text, font_name='Comic Sans MS', font_size=30,
                 color=(0, 0, 0), action=lambda: None):
        self.scene_screen_area = scene_screen_area
        self.text = text
        self.font = pygame.font.SysFont(font_name, font_size)
        self.text_surface = self.font.render(self.text, False, color)
        self.action = action

    def render(self, screen):
        screen.blit(self.text_surface, (self.scene_screen_area.x, self.scene_screen_area.y))
        pygame.draw.rect(screen, (255, 0, 0), self.scene_screen_area, 3)

    def process_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if self.scene_screen_area.collidepoint((mouse_x, mouse_y)):
                    self.action()


class Row:
    def __init__(self, scene_screen_area: pygame.Rect, line_number, font_name='Comic Sans MS', font_size=30,
                 color=(0, 0, 0)):
        self.scene_screen_area = scene_screen_area
        self.text = line_number
        self.font = pygame.font.SysFont(font_name, font_size)
        self.text_surface = self.font.render(self.text, True, color)
        self.lines = []
        self.current_line = []
        self.is_drawing = False
        self.previous_position = (0, 0)

    def render(self, screen):
        # draw four lines
        pygame.draw.line(screen, (255, 255, 255), (50, self.scene_screen_area.y),
                         (self.scene_screen_area.width, self.scene_screen_area.y), 3)
        pygame.draw.line(screen, (255, 255, 255), (50, self.scene_screen_area.y+50),
                         (self.scene_screen_area.width, self.scene_screen_area.y+50), 3)
        pygame.draw.line(screen, (255, 255, 255), (50, self.scene_screen_area.y+100),
                         (self.scene_screen_area.width, self.scene_screen_area.y+100), 3)
        pygame.draw.line(screen, (255, 255, 255), (50, self.scene_screen_area.y+150),
                         (self.scene_screen_area.width, self.scene_screen_area.y+150), 3)
        pygame.draw.line(screen, (255, 255, 255), (50, self.scene_screen_area.y+200),
                         (self.scene_screen_area.width, self.scene_screen_area.y+200), 3)

        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(50,
                                                          self.scene_screen_area.y,
                                                          self.scene_screen_area.width - 50,
                                                          self.scene_screen_area.height), 3)
        screen.blit(self.text_surface, (self.scene_screen_area.x, self.scene_screen_area.y))
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(self.scene_screen_area.x,
                                                          self.scene_screen_area.y,
                                                          50,
                                                          50), 3)
        for line in self.lines:
            if len(line) > 2:
                pygame.draw.lines(screen, (0, 0, 0), False, line, 3)

        if len(self.current_line) > 2:
            pygame.draw.lines(screen, (0, 0, 0), False, self.current_line, 3)

    def process_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                rect = pygame.Rect(50,
                                   self.scene_screen_area.y,
                                   self.scene_screen_area.width,
                                   self.scene_screen_area.height)
                if rect.collidepoint((mouse_x, mouse_y)):
                    self.is_drawing = True
                    self.current_line.append((mouse_x, mouse_y))
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                rect = pygame.Rect(50,
                                   self.scene_screen_area.y,
                                   self.scene_screen_area.width,
                                   self.scene_screen_area.height)
                if rect.collidepoint((mouse_x, mouse_y)):
                    self.is_drawing = False
                    self.lines.append(self.current_line)
                    self.current_line = []
                    self.previous_position = None
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                rect = pygame.Rect(50,
                                   self.scene_screen_area.y,
                                   self.scene_screen_area.width,
                                   self.scene_screen_area.height)
                if rect.collidepoint((mouse_x, mouse_y)):
                    if self.is_drawing:
                        self.current_line.append((mouse_x, mouse_y))


"""
Scenes
"""


class SceneBase:
    # widget aware
    def __init__(self):
        self.next = self
        self.widgets = []

    def process_input(self, events):
        pass

    def update(self):
        pass

    def render(self, screen):
        for widget in self.widgets:
            widget.render(screen)

    def switch_to_scene(self, next_scene):
        self.next = next_scene

    def terminate(self):
        self.switch_to_scene(None)


class AboutScene(SceneBase):
    def __init__(self):
        super().__init__()
        self.text = Text(pygame.Rect(0, 0, 640, 50),
                         'About Scene')
        self.text2 = Text(pygame.Rect(0, 50, 640, 50),
                          'Hi, This is handwriting editor.')
        self.buttonAbout = Button(pygame.Rect(0, 100, 640, 50),
                                  'Go to about scene', action=lambda: self.switch_to_scene(AboutScene()))
        self.buttonWriting = Button(pygame.Rect(0, 150, 640, 50),
                                    'Go to writing scene', action=lambda: self.switch_to_scene(WritingScene()))

    def render(self, screen):
        screen.fill((128, 128, 128))
        self.text.render(screen)
        self.text2.render(screen)
        self.buttonAbout.render(screen)
        self.buttonWriting.render(screen)

    def process_input(self, events):
        self.buttonAbout.process_input(events)
        self.buttonWriting.process_input(events)


class WritingScene(SceneBase):
    def __init__(self):
        super().__init__()
        self.textTitle = Text(pygame.Rect(0, 0, 640, 50),
                              'Writing Scene')
        self.textDescription = Text(pygame.Rect(0, 50, 640, 50),
                                    'Here we write hy lang code.')
        self.buttonAbout = Button(pygame.Rect(0, 100, 640, 50),
                                  'Go to about scene', action=lambda: self.switch_to_scene(AboutScene()))
        self.buttonWriting = Button(pygame.Rect(0, 150, 640, 50),
                                    'Go to writing scene', action=lambda: self.switch_to_scene(WritingScene()))
        self.rowOne = Row(pygame.Rect(0, 200, 640, 200),
                          '1')
        self.rowTwo = Row(pygame.Rect(0, 400, 640, 50),
                          '2')
        self.rowThree = Row(pygame.Rect(0, 450, 640, 50),
                            '3')
        self.textConsole = Text(pygame.Rect(0, 550, 640, 50), 'No output yet.')
        self.buttonEval = Button(pygame.Rect(0, 500, 640, 50), 'Eval Hy Code',
                                 action=lambda: (self.textConsole.set_text("OUTPUT> " + recognize(self.rowOne.lines, pygame.Rect(0, 200, 640, 200), 200, 250, 300, 350, 400))))

    def render(self, screen):
        screen.fill((128, 128, 128))
        self.textTitle.render(screen)
        self.textDescription.render(screen)
        self.buttonAbout.render(screen)
        self.buttonWriting.render(screen)
        self.rowOne.render(screen)
        self.rowTwo.render(screen)
        self.rowThree.render(screen)
        self.buttonEval.render(screen)
        self.textConsole.render(screen)

    def process_input(self, events):
        self.buttonAbout.process_input(events)
        self.buttonWriting.process_input(events)
        self.rowOne.process_input(events)
        self.buttonEval.process_input(events)


class SceneManager:
    """Dependent on SceneBase"""
    def __init__(self, screen, scenes, start_scene: SceneBase):
        self.screen = screen
        self.scenes = scenes
        self.current_scene = start_scene

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.current_scene.terminate()
                    return
            self.current_scene.process_input(events)
            self.current_scene.update()
            self.current_scene.render(self.screen)

            self.current_scene = self.current_scene.next

            pygame.display.flip()


"""
App
"""


class App:
    """Application entrance point."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Handwriting Code Editor")
        self.screen = pygame.display.set_mode((640, 600))
        self.scene_manager = SceneManager(self.screen, [AboutScene()], AboutScene())

    def run(self):
        self.scene_manager.run()


"""
Main
"""

if __name__ == '__main__':
    App().run()
