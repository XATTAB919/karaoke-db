import os


BASE_DIR = os.path.dirname(__file__)
from kivy.app import App
# Импортируем основной класс приложения Kivy. От него наследуемся, чтобы создать наше приложение.
from kivy.uix.boxlayout import BoxLayout
# BoxLayout — это контейнер, который располагает элементы по горизонтали или вертикали. Мы используем его для компоновки кнопок и текста.

from kivy.uix.label import Label
# Label — это виджет, который показывает текст. Мы используем его, чтобы показать лицензионное соглашение.

from kivy.uix.button import Button
# Button — это кнопка. Мы используем её, чтобы пользователь мог нажать "Я принимаю".
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation  # Для анимации
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import RoundedRectangle
from kivy.uix.screenmanager import ScreenManager, NoTransition, Screen
from utils.font_size import *
from utils.size_image import *
import json


class MyApp(App):  # Создаём главный класс приложения, наследуемый от App
    def __init__(self, **kwargs):
        super().__init__(**kwargs)        # Вызываем конструктор родительского класса App (важно для правильной инициализации Kivy)
        self.language = 'ru'              # self.language — переменная, в которой будем хранить выбранный язык.
                                          # По умолчанию ставим 'ru' — русский язык.
                                          # Теперь во всём приложении мы можем узнать, какой язык выбран, обратившись к self.language

    def set_language(self, lang_code):
        # Этот метод вызывается, когда пользователь выбирает язык на экране выбора языка.
        # lang_code — строка с кодом языка, например, 'ru' или 'en'.
        self.language = lang_code         # Присваиваем self.language новое значение — выбранный пользователем язык.
                                          # Например: если пользователь нажал на английский флаг, вызывается set_language('en'), и self.language теперь равен 'en'.

    def get_language(self):
        # Этот метод нужен, чтобы в любом месте приложения узнать, какой язык сейчас выбран.
        return self.language              # Просто возвращаем значение self.language.
                                          # Например, если нужно подгрузить перевод — вызываем app.get_language(), получаем 'ru' или 'en'.
class LoadScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.208, 0.573, 0.988, 1)  # RGB (0-1), альфа=1 — это синий оттенок
            self.rect = Rectangle(size=self.size, pos=self.pos)

        # Обновляем размер и позицию прямоугольника при изменениях
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Главный контейнер
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.add_widget(self.layout)

        # Анимация GIF
        self.spinner = Image(
            source="Pictures/cargando-loading.gif",
            anim_delay=0.023
        )

        self.layout.add_widget(self.spinner)

        Clock.schedule_once(self.switch_to_language_screen, 2)  # вызываем переход через 2 сек

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def switch_to_language_screen(self, dt):  # метод, вызываемый после 2 секунд
        self.manager.current = 'Language'
class TouchImage(Image):  # создаём класс TouchImage — это кастомное изображение, реагирующее на касание, наследуется от стандартного Image
    is_busy = False  # класс-переменная: общий флаг, указывающий, занят ли сейчас какой-то флаг (True = другой уже увеличен, нельзя трогать этот)

    def __init__(self, lang_code, select_callback, **kwargs):  # инициализатор объекта: принимает lang_code (например, 'ru'), функцию select_callback, и другие параметры
        super().__init__(**kwargs)  # передаёт все остальные параметры (например, source='флаг.png', size_hint и т.д.) в стандартный Image

        self.lang_code = lang_code  # сохраняем код языка в экземпляре, чтобы потом передать его при выборе (например: self.lang_code = 'ru')
        self.select_callback = select_callback  # сохраняем переданную функцию (например: self.select_callback = self.select_language), которая будет вызвана при выборе флага
        self.enlarged = False  # флаг, увеличено ли текущее изображение (чтобы не реагировать повторно во время анимации)
        self.original_size_hint = kwargs.get('size_hint', (1, 1))
        # сохраняем оригинальный размер size_hint, переданный в конструктор (например: (0.8, 0.8)); если не был передан — по умолчанию (1, 1)

    def on_touch_down(self, touch):  # вызывается автоматически при касании к экрану
        if self.collide_point(*touch.pos):  # проверяем: находится ли точка касания внутри границ изображения
            if not self.enlarged and not TouchImage.is_busy:  # если изображение ещё не увеличено и сейчас ни одно изображение не занято
                TouchImage.is_busy = True  # устанавливаем общий флаг: сейчас одно изображение в анимации
                self.enlarged = True  # устанавливаем флаг: это изображение увеличено

                anim = Animation(size_hint=(1.0, 1.0), duration=0.3)  # создаём анимацию: увеличить size_hint до (1.0, 1.0) за 0.3 секунды
                anim.start(self)  # запускаем анимацию на текущем изображении

                Clock.schedule_once(self._delayed_select, 1.5)  # через 1.5 секунды вызываем метод _delayed_select (например, для перехода на другой экран)
                Clock.schedule_once(self._restore_size, 1.0)  # через 1.0 секунду начинаем обратную анимацию (уменьшение обратно)

            return True  # возвращаем True — сигнализируем, что касание обработано

        return super().on_touch_down(touch)  # если касание не по изображению — передаём обработку дальше родительскому классу

    def _delayed_select(self, dt):  # вызывается через 1.5 секунды после касания
        self.select_callback(self.lang_code)
        # вызываем сохранённую функцию выбора языка (например: self.select_language('ru'))

    def _restore_size(self, dt):  # вызывается через 1 секунду после касания (для уменьшения обратно)
        anim = Animation(size_hint=self.original_size_hint, duration=0.3)
        # создаём анимацию: уменьшить обратно до исходного размера (например: (0.8, 0.8)) за 0.3 секунды
        anim.bind(on_complete=self._on_restore_complete)
        # привязываем метод: когда анимация завершится — вызвать _on_restore_complete
        anim.start(self)  # запускаем анимацию на текущем изображении

    def _on_restore_complete(self, animation, widget):  # вызывается после завершения анимации уменьшения
        self.enlarged = False  # сбрасываем флаг: изображение больше не увеличено
        TouchImage.is_busy = False  # разрешаем другим изображениям обрабатываться — сбрасываем общий флаг


class LanguageScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # Инициализируем базовый Screen, чтобы получить все возможности экрана

        # 🎨 Рисуем фон экрана — делаем это в canvas.before,
        # чтобы фон рисовался перед всеми виджетами (был позади)
        with self.canvas.before:
            # Загружаем изображение фона как текстуру для быстрого рендеринга
            self.bg_texture = CoreImage('Pictures/background.jpeg').texture

            # Создаем Rectangle с этой текстурой,
            # который будет размером и позицией совпадать с размером экрана
            self.rect = Rectangle(texture=self.bg_texture, size=self.size, pos=self.pos)
            # 🖼 Привязываемся к изменению размеров экрана — для background
            self.bind(
                size=lambda *args: update_background(self),
                pos=lambda *args: update_background(self)
            )

        # 🎨 Рисуем полупрозрачный черный overlay (прямоугольник),
        # чтобы затемнить фон, но поверх него уже пойдут виджеты.
        # Для этого используем canvas (обычный, он рисует после canvas.before)
        self.screen_box = BoxLayout(orientation='vertical',size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5},)
        with self.screen_box.canvas.before:
            # Цвет с альфа-каналом 0.5 (полупрозрачный черный)
            Color(0.87, 0.87, 0.87, 0.7)
            # Создаём закруглённый прямоугольник
            self.overlay_rect = RoundedRectangle(
                size=(0, 0),  # зададим позже
                pos=(0, 0),  # зададим позже
                radius=[30]  # скругление всех углов (в пикселях)
            )

        self.add_widget(self.screen_box)

        # ⛳ Привязываемся к изменениям размеров и позиции именно контейнера, не всего экрана
        self.screen_box.bind(size= lambda *args: update_overlay(self), pos= lambda *args: update_overlay(self))



        # --------------------------------------------
        # Создаем заголовок с текстом — будет сверху экрана
        # BoxLayout с вертикальной ориентацией для размещения внутри Label
        header = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.25),  # Занимает всю ширину экрана и 20% по высоте
        )

        # Добавляем текст с большим шрифтом в header
        # создаём метку
        label = Label(
            text='[b]SELECT LANGUAGE[/b]',
            font_size=100,
            color=(0, 0, 0, 1),
            halign='center',
            valign='middle',
            markup=True  # включаем поддержку разметки
        )
        # Привязываем функцию масштабирования
        label.bind(size=lambda instance, size: update_font_size_title(instance, size))
        header.add_widget(label)
        self.screen_box.add_widget(header)

        # --------------------------------------------
        # Горизонтальный контейнер для размещения флагов

        baton = BoxLayout(
            orientation='horizontal',  # Расположим виджеты слева направо
            size_hint=(1, 0.6),  # Занимает всю ширину и 20% высоты экрана
            pos_hint={'center_x': 0.5, 'center_y': 0.5}, padding=25,  # Центрируем батон по обеим осям
        )

        # --------------------------------------------
        # Чтобы выровнять флаги аккуратно, создаем 3 вертикальных контейнера (box1, box2, box3)
        # В них помещаем AnchorLayout, которые сами выравнивают содержимое по краям или центру
        # Это более гибко, чем просто BoxLayout, когда нужно точное позиционирование

        # Первый box для флага России — выравнивание по правому краю
        box1 = BoxLayout(orientation='vertical', size_hint=(0.45, 1))  # 30% ширины батона
        anchor_box1 = AnchorLayout(size_hint=(1, 1), anchor_x='center', anchor_y='center')
        box1.add_widget(anchor_box1)  # Добавляем якорь в box1

        # Второй box для флага Англии — выравнивание по центру
        box2 = BoxLayout(orientation='vertical',
                         size_hint=(0.1, 1))  # 20% ширины батона (больше, чтобы флаг был в центре)
        anchor_box2 = AnchorLayout(size_hint=(1, 1), anchor_x='center', anchor_y='top')
        box2.add_widget(anchor_box2)

        # Третий box — пустой, для отступа справа (оставляем 30%)
        box3 = BoxLayout(orientation='vertical', size_hint=(0.45, 1))
        anchor_box3 = AnchorLayout(size_hint=(1, 1), anchor_x='center', anchor_y='center')
        box3.add_widget(anchor_box3)

        # Добавляем все три бокса в горизонтальный контейнер baton
        baton.add_widget(box1)  # Слева — русский флаг
        baton.add_widget(box2)  # По центру — пустой отступ
        baton.add_widget(box3)  # Справа — английский флаг

        # --------------------------------------------
        # Создаем сами флаги — картинки с возможностью обрабатывать касания
        flag_ru = TouchImage(
            lang_code='ru',  # Код языка, который передается в функцию обратного вызова при выборе флага
            select_callback=self.select_language,
            # Функция, которая вызывается при нажатии на флаг — для обработки выбора языка
            source='Pictures/russian_flag.png',  # Путь к изображению флага России — загружается и отображается картинка
            allow_stretch=True,
            # Разрешаем растягивание изображения, чтобы оно могло подстроиться под размер контейнера
            keep_ratio=True,  # Сохраняем пропорции картинки, чтобы флаг не исказился при масштабировании
            size_hint=(0.85, 0.85),  # Размер относительно родительского контейнера:
            # 0.5 — ширина занимает 50% от ширины родителя,
            # 1 — высота равна 100% высоты родителя
            # size не задаем явно, чтобы не фиксировать размеры, а позволить size_hint управлять размером
        )

        flag_en = TouchImage(
            lang_code='en',
            select_callback=self.select_language,
            source='Pictures/english_flag.png',
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.85, 0.85),
        )

        # --------------------------------------------
        # Добавляем флаги в соответствующие AnchorLayout,
        # чтобы они были выровнены по нужной стороне внутри своих box

        anchor_box1.add_widget(flag_ru)  # Русский флаг справа (в box1)
        anchor_box3.add_widget(flag_en)  # Английский флаг по центру (в box3)
        # anchor_box3 остается пустым — отступ справа

        # Добавляем батон с флагами на экран
        self.screen_box.add_widget(baton)
        self.screen_box.add_widget(Widget(size_hint=(1, 0.25)))

    def select_language(self, lang_code):
        app = App.get_running_app()  # Получаем экземпляр приложения
        app.set_language(lang_code)  # Сохраняем выбранный язык ('ru' или 'en')
        self.manager.current = 'license'  # Переходим к экрану лицензии (или 'welcome', если так называется)


class LicenseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            self.bg_texture = CoreImage('Pictures/background.jpeg').texture
            self.rect = Rectangle(texture=self.bg_texture, size=self.size, pos=self.pos)
        self.bind(
            size=lambda *args: update_background(self),
            pos=lambda *args: update_background(self)
        )

        # Главный контейнер? нужен чтобы кнопка была снаружи
        self.layout = BoxLayout(orientation='vertical')
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        # ⛳ Привязываемся к изменениям размеров и позиции именно контейнера, не всего экрана

        self.screen_box = BoxLayout(orientation='vertical',size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.55},padding=10, spacing=35)
        with self.screen_box.canvas.before:
            # Цвет с альфа-каналом 0.5 (полупрозрачный черный)
            Color(0.87, 0.87, 0.87, 0.7)
            # Создаём закруглённый прямоугольник
            self.overlay_rect = RoundedRectangle(
                size=(0, 0),  # зададим позже
                pos=(0, 0),  # зададим позже
                radius=[30]  # скругление всех углов (в пикселях)
            )

        # 📌 Когда меняется размер или позиция экрана, надо обновлять фон и overlay,
        # поэтому привязываемся к этим событиям и вызываем update_canvas
        self.add_widget(self.screen_box)
        self.screen_box.bind(size= lambda *args: update_overlay(self), pos= lambda *args: update_overlay(self))

    def on_enter(self):
        self.show_license_text(0)

    def show_license_text(self, dt):

        base_path = os.path.dirname(os.path.abspath(__file__))  # Папка с текущим скриптом
        json_path = os.path.join(base_path, 'lang', 'ru.json')  # lang/ru.json в папке с кодом
        with open(json_path, encoding='utf-8') as f:
            # Открываем файл 'ru.json' в режиме чтения ('r' по умолчанию)
            # encoding='utf-8' — чтобы правильно читать кириллические символы из файла.
            # Оператор with гарантирует, что файл будет автоматически закрыт после блока.

            self.lang_data = json.load(f)
            # json.load(f) читает содержимое файла 'ru.json' и преобразует JSON-строку в словарь Python.
            # В переменную self.lang_data сохраняем этот словарь.
            # Теперь в self.lang_data — все ключи и значения из JSON-файла доступны как обычный словарь.
            # Например, self.lang_data['welcome_text'] будет содержать строку с приветствием на русском.


        # --- Приветственный текст ---
        self.greetings_text = Label(
            text='[b]' + self.lang_data['welcome_text1'] + '[/b]',
            font_size=22,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle",
            markup=True,  # включаем поддержку разметки
            size_hint=(1, 0.2),
            )
        self.greetings_text2 = Label(
            text='[b]' + self.lang_data['welcome_text2'] + '[/b]',
            font_size=22,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle",
            markup=True,  # включаем поддержку разметки
            size_hint=(1, 0.2),
        )

        self.greetings_text.bind(size=lambda instance, size: update_font_size_title(instance, size))
        self.greetings_text2.bind(size=lambda instance, size: update_font_size_title(instance, size))
        self.title_box = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        self.screen_box.add_widget(self.title_box)
        self.title_box.add_widget(self.greetings_text)
        self.title_box.add_widget(self.greetings_text2)

        # --- Прямоугольник с прокручиваемым соглашением ---
        scroll_view = ScrollView(size_hint=(1, 0.5))  # Прокручиваемая область


        # Контейнер для текста внутри ScrollView
        agreement_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=10, spacing=10)
        agreement_box.bind(minimum_height=agreement_box.setter('height'))  # Автовысота от содержимого
        # Многострочный текст

        agreement_text_content = self.lang_data.get('license_text', '[Ошибка] Ключ license_text не найден в JSON.')

        self.agreement_text = Label(
            text=agreement_text_content,
            font_size=16,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=1500,  # Обязательно фиксированная высота
            halign='left',
            valign='top',
            markup=True,
            text_size=(self.width - 40, 1500)
        )
        self.agreement_text.bind(
            size=lambda instance, size: update_font_size_agreement(self, instance, size),
            pos=lambda instance, pos: update_font_size_agreement(self, instance, instance.size)
        )
        # agreement_text.bind(size=self.update_font_size_agreement)
        agreement_box.add_widget(self.agreement_text)  # Вставляем текст в контейнер
        scroll_view.add_widget(agreement_box)  # Вставляем контейнер в прокрутку
        self.screen_box.add_widget(scroll_view)

        # --- Чекбокс и подпись ---
        checkbox_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=20)
        # └ горизонтальный контейнер, занимает всю ширину родителя (self.layout), высота 10% от родителя
        # spacing=10 — расстояние 10 пикселей между дочерними виджетами
        self.screen_box.add_widget(checkbox_layout)


        # empty_space = Widget(size_hint_x=0.73)  # пустой невидимый виджет, занимает 73% ширины

        checkbox_and_label = BoxLayout(orientation='horizontal')
        left_empty_box = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        middle_box_check = BoxLayout(orientation='vertical', size_hint=(0.15, 1))
        right_checkbox_label = BoxLayout(orientation='vertical', size_hint=(0.35, 1))
        checkbox_and_label.add_widget(left_empty_box)
        checkbox_and_label.add_widget(middle_box_check)
        checkbox_and_label.add_widget(right_checkbox_label)



        self.checkbox = CheckBox(
            size_hint=(None, 1),
            width=40,
            background_checkbox_normal='Pictures/checkbox/box_empty.png',  # твоя иконка для обычного состояния
            background_checkbox_down='Pictures/checkbox/checkbox_active.png',  # твоя иконка для активного состояния
        )
        # └ чекбокс с фиксированной шириной 40px, высотой 100% от родителя (checkbox_layout)
        # self.checkbox — сохраняем в поле класса, чтобы иметь к нему доступ в других методах
        checkbox_label = Label(
            text="Я прочитал и принимаю условия",
            halign="right",
            valign="middle",
        )


        # └ при изменении ширины label вызываем функцию update_text_size,
        #   чтобы text_size (область отрисовки текста) подстраивалась под размер label
        checkbox_label.bind(size=lambda instance, size: update_font_size_text(instance, size))


        middle_box_check.add_widget(self.checkbox)
        right_checkbox_label.add_widget(checkbox_label)

        # checkbox_layout.add_widget(empty_space)  # добавляем пустое пространство слева
        checkbox_layout.add_widget(checkbox_and_label)  # Добавляем чекбокс в горизонтальный контейнер

        # Контейнер для кнопки
        self.button_box = BoxLayout(orientation='vertical',pos_hint={'center_x': 0.5, 'center_y': 0.08}, size_hint=(0.8, 0.1), spacing=10, padding=10)
        self.layout.add_widget(self.button_box)

        # --- Кнопка принятия ---
        self.accept_button = Button(
            text="Я принимаю условия",
            size_hint=(1, 0.15),
            disabled=True
        )
        self.accept_button.bind(on_press=self.accept_license)

        # --- Проверка прокрутки вниз и активной галочки---
        def check_scroll_position(instance, value):

            if scroll_view.scroll_y <= 0.3 and self.checkbox.active:
                self.accept_button.disabled = False
            else:
                self.accept_button.disabled = True

        scroll_view.bind(scroll_y=check_scroll_position)

        self.checkbox.bind(
            active=lambda instance, value: check_scroll_position(None, None))  # повторная проверка при отметке

        self.button_box.add_widget(self.accept_button)


    def accept_license(self, instance):
        self.manager.current = 'main'


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout()
        layout.add_widget(Label(text="Главный экран. Здесь будет список песен."))
        self.add_widget(layout)


class KaraokeApp(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(LoadScreen(name="load"))
        sm.add_widget(LanguageScreen(name='Language'))
        sm.add_widget(LicenseScreen(name='license'))
        sm.add_widget(MainScreen(name='main'))
        return sm

    def set_language(self, lang_code):
        print(f"Язык выбран: {lang_code}")

if __name__ == '__main__':
    KaraokeApp().run()