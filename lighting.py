from settings import *


def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(c1, c2, t):
    return tuple(int(_lerp(c1[i], c2[i], t)) for i in range(3))


class LightingSystem:
    def __init__(self):
        self.start_time = time.time()
        self.shadow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.ambient_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.light_cache = {}

    def day_phase(self):
        return ((time.time() - self.start_time) % DAY_CYCLE_SECONDS) / DAY_CYCLE_SECONDS

    def sun_level(self):
        # 0 at night, 1 at noon
        return max(0.0, math.sin(self.day_phase() * math.tau - math.pi / 2))

    def ambient_params(self):
        sun = self.sun_level()
        day_color = (95, 86, 64)
        night_color = (46, 69, 116)
        tint = _lerp_color(night_color, day_color, sun)
        alpha = int(205 - 145 * sun)
        return sun, tint, alpha

    def global_light_position(self, scroll):
        phase = self.day_phase()
        angle = phase * math.tau
        distance = max(WIDTH, HEIGHT) * 2.0
        cx = scroll[0] + WIDTH // 2
        cy = scroll[1] + HEIGHT // 2
        return cx + math.cos(angle) * distance, cy + math.sin(angle) * distance

    def _light_gradient(self, radius, max_alpha):
        key = (int(radius), int(max_alpha))
        if key in self.light_cache:
            return self.light_cache[key]

        size = int(radius * 2)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = int(radius)
        rings = max(8, int(radius // 8))

        for i in range(rings, 0, -1):
            k = i / rings
            ring_radius = int(radius * k)
            # stronger in center, softer on edge
            alpha = int(max_alpha * ((1 - k) ** 0.85))
            pygame.draw.circle(surf, (0, 0, 0, alpha), (center, center), ring_radius)

        self.light_cache[key] = surf
        return surf

    def _cut_light(self, world_pos, scroll, radius, strength):
        spot = self._light_gradient(radius, strength)
        x = int(world_pos[0] - scroll[0] - radius)
        y = int(world_pos[1] - scroll[1] - radius)
        self.ambient_surface.blit(spot, (x, y), special_flags=pygame.BLEND_RGBA_SUB)

    def _visible_objects(self, trees, scroll):
        x0, y0 = scroll[0] - 120, scroll[1] - 120
        x1, y1 = scroll[0] + WIDTH + 120, scroll[1] + HEIGHT + 120
        result = []
        for tree in trees:
            if x0 <= tree.x <= x1 and y0 <= tree.y <= y1:
                result.append(tree)
        return result

    @staticmethod
    def _tree_base(tree):
        if tree.hp > 0:
            return tree.shadow_sprite, tree.rect.centerx, tree.rect.bottom
        return tree.stump_shadow_sprite, tree.rect_for_interaction.centerx, tree.rect_for_interaction.bottom

    def _draw_shadow_chain(self, tree, light_pos, scroll, alpha, length, thickness=0.5):
        base, root_x, root_y = self._tree_base(tree)

        vx = root_x - light_pos[0]
        vy = root_y - light_pos[1]
        dist = max(1.0, math.hypot(vx, vy))
        dir_x, dir_y = vx / dist, vy / dist

        h = max(6, int(base.get_height() * thickness))
        w = max(6, int(base.get_width() * 0.72))
        proj = pygame.transform.scale(base, (w, h)).convert_alpha()

        angle = -math.degrees(math.atan2(dir_y, dir_x))
        proj = pygame.transform.rotate(proj, angle)

        steps = max(1, int(length // 8))
        for s in range(steps):
            t = s / max(1, steps - 1)
            a = int(alpha * (1 - t * 0.7))
            proj.set_alpha(max(10, a))
            # first segment starts at trunk base and then extends away
            off = s * 8
            x = int(root_x - scroll[0] + dir_x * off - proj.get_width() // 2)
            y = int(root_y - scroll[1] + dir_y * off - proj.get_height() // 2)
            self.shadow_surface.blit(proj, (x, y))

    def paint(self, screen, scroll, trees, fire, player_rect, player_light_until):
        sun, tint, ambient_alpha = self.ambient_params()

        # Base tinted darkness overlay (full-screen sprite).
        self.ambient_surface.fill((tint[0], tint[1], tint[2], ambient_alpha))

        # Cut transparent zones where local light exists.
        fire_strength = int(145 + 60 * min(1.0, fire.hp / max(1, fire.HP)))
        self._cut_light(fire.rect.center, scroll, FIRE_LIGHT_RADIUS, fire_strength)

        has_player_light = player_light_until > time.time()
        if has_player_light:
            self._cut_light(player_rect.center, scroll, PLAYER_LIGHT_RADIUS, 165)

        # Dynamic shadows.
        self.shadow_surface.fill((0, 0, 0, 0))
        visible = self._visible_objects(trees, scroll)

        # Global shadows: long at dawn/sunset, tiny at noon, absent at night.
        if sun > 0:
            sun_pos = self.global_light_position(scroll)
            global_len = 12 + (1 - sun) * 62
            global_alpha = 18 + (1 - sun) * 62
            global_thickness = 0.30 + (1 - sun) * 0.26
            for tree in visible:
                self._draw_shadow_chain(tree, sun_pos, scroll, global_alpha, global_len, global_thickness)

        # Fire shadows.
        for tree in visible:
            self._draw_shadow_chain(tree, fire.rect.center, scroll, 58, 28, 0.38)

        # Player shadows (while player emits light).
        if has_player_light:
            for tree in visible:
                self._draw_shadow_chain(tree, player_rect.center, scroll, 46, 22, 0.35)

        # Pixel-art postprocess for shadows.
        mini = pygame.transform.scale(self.shadow_surface, (WIDTH // 2, HEIGHT // 2))
        pixel_shadow = pygame.transform.scale(mini, (WIDTH, HEIGHT))

        screen.blit(pixel_shadow, (0, 0))
        screen.blit(self.ambient_surface, (0, 0))
