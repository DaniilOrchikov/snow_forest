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

    def get_day_phase(self):
        return ((time.time() - self.start_time) % DAY_CYCLE_SECONDS) / DAY_CYCLE_SECONDS

    def get_ambient(self):
        phase = self.get_day_phase()
        # 0 and 1 -> sunrise, 0.5 -> sunset, middle near 0.25 daytime
        sun_wave = (math.sin(phase * math.tau - math.pi / 2) + 1) / 2
        daylight = 0.12 + sun_wave * 0.88
        day_color = (94, 84, 64)
        night_color = (46, 68, 112)
        tint = _lerp_color(night_color, day_color, daylight)
        alpha = int(210 - daylight * 150)
        return daylight, tint, alpha

    def get_global_light_source(self, scroll):
        phase = self.get_day_phase()
        angle = phase * math.tau
        distance = max(WIDTH, HEIGHT) * 1.7
        center_x = scroll[0] + WIDTH // 2
        center_y = scroll[1] + HEIGHT // 2
        return (
            center_x + math.cos(angle) * distance,
            center_y + math.sin(angle) * distance,
        )

    def _light_gradient(self, radius, strength):
        key = (int(radius), int(strength * 100))
        if key in self.light_cache:
            return self.light_cache[key]

        size = int(radius * 2)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = radius
        # stepped circles keep pixel-art look
        rings = max(6, int(radius // 10))
        for i in range(rings, 0, -1):
            k = i / rings
            ring_radius = int(radius * k)
            val = int(strength * (k ** 2))
            color = (val, val, val, val)
            pygame.draw.circle(surf, color, (center, center), ring_radius)
        self.light_cache[key] = surf
        return surf

    def _blit_light(self, target, world_pos, scroll, radius, strength):
        gradient = self._light_gradient(radius, strength)
        screen_pos = (int(world_pos[0] - scroll[0] - radius), int(world_pos[1] - scroll[1] - radius))
        target.blit(gradient, screen_pos, special_flags=pygame.BLEND_RGBA_SUB)

    def _visible_trees(self, trees, scroll):
        result = []
        x0, y0 = scroll[0] - 80, scroll[1] - 80
        x1, y1 = scroll[0] + WIDTH + 80, scroll[1] + HEIGHT + 80
        for tree in trees:
            if tree.hp <= 0:
                continue
            if x0 <= tree.x <= x1 and y0 <= tree.y <= y1:
                result.append(tree)
        return result

    def _draw_tree_shadow(self, tree, light_pos, scroll, alpha_scale):
        root_x = tree.rect.centerx
        root_y = tree.rect.bottom
        vx = root_x - light_pos[0]
        vy = root_y - light_pos[1]
        dist = max(1.0, math.hypot(vx, vy))
        dx, dy = vx / dist, vy / dist

        base = tree.shadow_sprite
        elongation = min(3.2, 1.1 + dist / 240)
        sh_w = max(6, int(base.get_width() * 0.72))
        sh_h = max(10, int(base.get_height() * 0.28 * elongation))
        shadow = pygame.transform.scale(base, (sh_w, sh_h))

        angle = -math.degrees(math.atan2(dy, dx)) + 90
        shadow = pygame.transform.rotate(shadow, angle)
        shadow.set_alpha(max(20, min(170, int(alpha_scale))))

        draw_x = int(root_x - scroll[0] + dx * 6 - shadow.get_width() // 2)
        draw_y = int(root_y - scroll[1] + dy * 6 - shadow.get_height() // 2)
        self.shadow_surface.blit(shadow, (draw_x, draw_y))

    def paint(self, screen, scroll, trees, fire, player_rect, player_light_until):
        daylight, ambient_tint, ambient_alpha = self.get_ambient()

        # Ambient global tint/darkness.
        self.ambient_surface.fill((ambient_tint[0], ambient_tint[1], ambient_tint[2], ambient_alpha))

        # Local lights subtract darkness from the ambient overlay.
        fire_boost = 1.0 + min(1.0, fire.hp / max(1.0, fire.HP))
        self._blit_light(self.ambient_surface, fire.rect.center, scroll, FIRE_LIGHT_RADIUS, 95 * fire_boost)

        if player_light_until > time.time():
            self._blit_light(self.ambient_surface, player_rect.center, scroll, PLAYER_LIGHT_RADIUS, 120)

        # Sun/moon global direction for dynamic shadows.
        self.shadow_surface.fill((0, 0, 0, 0))
        sun_pos = self.get_global_light_source(scroll)
        visible_trees = self._visible_trees(trees, scroll)

        global_shadow_alpha = 70 * (1 - daylight) + 24
        for tree in visible_trees:
            self._draw_tree_shadow(tree, sun_pos, scroll, global_shadow_alpha)
            self._draw_tree_shadow(tree, fire.rect.center, scroll, 52 + (1 - daylight) * 16)
            if player_light_until > time.time():
                self._draw_tree_shadow(tree, player_rect.center, scroll, 44)

        # pixelate shadows for retro look
        mini = pygame.transform.scale(self.shadow_surface, (WIDTH // 2, HEIGHT // 2))
        pixel_shadow = pygame.transform.scale(mini, (WIDTH, HEIGHT))
        screen.blit(pixel_shadow, (0, 0))
        screen.blit(self.ambient_surface, (0, 0))
