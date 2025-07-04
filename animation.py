def animation_generator(arr, step):
    v = 0
    ln = len(arr) * step
    while True:
        yield arr[v // step]
        v += 1
        v %= ln


class Animation:
    def __init__(self, frames, frame_duration=10, loop=True):
        """
        Улучшенная система анимации
        :param frames: список кадров анимации
        :param frame_duration: длительность кадра в циклах
        :param loop: зациклить анимацию
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.frame_counter = 0
        self.finished = False
        self.width, self.height = frames[0].get_size()
        
        # Для обратной совместимости
        self.generator = animation_generator(frames, frame_duration)

    def update(self):
        """Обновляет анимацию на один шаг"""
        if not self.finished:
            self.frame_counter += 1
            if self.frame_counter >= self.frame_duration:
                self.frame_counter = 0
                self.current_frame += 1
                if self.current_frame >= len(self.frames):
                    if self.loop:
                        self.current_frame = 0
                    else:
                        self.current_frame = len(self.frames) - 1
                        self.finished = True

    def get_current_frame(self):
        """Возвращает текущий кадр анимации"""
        return self.frames[self.current_frame]

    def next(self):
        """Обратная совместимость - возвращает следующий кадр"""
        return next(self.generator)

    def reset(self):
        """Сбрасывает анимацию в начальное состояние"""
        self.current_frame = 0
        self.frame_counter = 0
        self.finished = False

    def is_finished(self):
        """Проверяет, завершена ли анимация"""
        return self.finished
