def update_background(instance):
    # instance — это объект экрана, переданный при вызове
    instance.rect.size = instance.size  # обновляем размер фона
    instance.rect.pos = instance.pos    # обновляем позицию фона


def update_overlay(instance):
    # Эта функция будет вызываться при изменении размера или позиции контейнера layout.
    # Она подгоняет прямоугольник overlay_rect по размеру и позиции под layout.

    instance.overlay_rect.size = instance.screen_box.size
    # Устанавливаем размер прямоугольника = размеру layout
    # Например, если layout.size == (800, 600), то overlay_rect будет тоже (800, 600)

    instance.overlay_rect.pos = instance.screen_box.pos
    # Устанавливаем позицию прямоугольника = позиции layout
    # Например, если layout.pos == (100, 50), то и overlay_rect будет в этой точке
