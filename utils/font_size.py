def update_font_size_title(instance, size, base_width=600, base_height = 80, base_font_size=35, min_size=5, max_size=70):
    """
    Автоматически масштабирует шрифт в зависимости от ширины виджета.

    :param instance: объект Label, у которого нужно изменить размер шрифта
    :param size: кортеж (width, height) — текущие размеры label
    :param base_width: ширина, при которой font_size будет стандартным
    :param base_font_size: стандартный размер шрифта при base_width
    :param min_size: минимально допустимый размер шрифта
    :param max_size: максимально допустимый размер шрифта
    """
    width, height = size  # получаем текущую ширину и высоту
    width_scale = width / base_width  # вычисляем масштаб (во сколько раз больше или меньше стандартной ширины)
    height_scale = height / base_height
    scale = min(width_scale, height_scale)
    new_font_size = base_font_size * scale  # масштабируем шрифт
    instance.font_size = max(min_size, min(new_font_size, max_size))  # ограничиваем размер по min/max
    instance.text_size = (width, None)  # задаём ширину области текста

def update_font_size_checkbox(instance, size, base_width=900, base_height=100, base_font_size=50, min_size=5,
                           max_size=100):
    """
    Автоматически масштабирует шрифт в зависимости от ширины виджета.

    :param instance: объект Label, у которого нужно изменить размер шрифта
    :param size: кортеж (width, height) — текущие размеры label
    :param base_width: ширина, при которой font_size будет стандартным
    :param base_font_size: стандартный размер шрифта при base_width
    :param min_size: минимально допустимый размер шрифта
    :param max_size: максимально допустимый размер шрифта
    """
    width, height = size  # получаем текущую ширину и высоту
    width_scale = width / base_width  # вычисляем масштаб (во сколько раз больше или меньше стандартной ширины)
    height_scale = height / base_height
    scale = min(width_scale, height_scale)
    new_font_size = base_font_size * scale  # масштабируем шрифт
    instance.font_size = max(min_size, min(new_font_size, max_size))  # ограничиваем размер по min/max
    instance.text_size = (instance.width, None)  # задаём ширину области текста

def update_font_size_agreement(self, instance, size):
    width, height = size
    base_width = 400
    base_font_size = 16        # Базовый размер шрифта при ширине 400
    scale = width / base_width
    new_font_size = base_font_size * scale      # Масштабируем базовый размер шрифт
    instance.font_size = max(5, min(new_font_size, 22))
    instance.text_size = (width, None)
    # Устанавливаем ширину области отрисовки текста, чтобы строки переносились