#!/usr/bin/kivy
# -*- coding: utf-8 -*-
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty, ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.uix.floatlayout import FloatLayout
from functools import partial
from kivy.graphics import Rectangle
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy_communication import *
from hebrew_management import HebrewManagement
from text_handling import *
from kivy.uix.screenmanager import Screen
LANGUAGE = 'English'  # 'Hebrew'


class Item(Scatter, WidgetLogger):
    SOMEONE_MOVED = False

    item_lbl = ObjectProperty(None)
    source = StringProperty()
    img = {}
    info = {}
    current = 1
    cg = None
    base_pos = None
    question = {}
    i_moved = False

    def change_img(self, im = '1'):
        if im in self.img:
            self.source = self.img[im]

    def on_transform_with_touch(self, touch):
        pass
        # if self.collide_point(*touch.pos):
        #     self.play()

    def on_touch_down(self, touch):
        super(Item, self).on_touch_down(touch)
        if self.collide_point(*touch.pos):
            if Item.SOMEONE_MOVED:
                self.i_moved = False
                self._set_do_translation(False)
                return
            Item.SOMEONE_MOVED = True
            self.i_moved = True
            self._set_do_translation(True)
            self.force_on_touch_down(touch)
            Clock.schedule_once(self.play, 0.5)

    def on_touch_up(self, touch):
        super(Item, self).on_touch_up(touch)
        if self.collide_point(*touch.pos):
            self.force_on_touch_up(touch)
        Item.SOMEONE_MOVED = False
        self.i_moved = False
        self._set_do_translation(True)

    def play(self, dt):
        # if still has something to play
        if self.current in self.info:
            if 'audio' in self.info[self.current]:
                # if not playing
                if not self.cg.is_playing:
                    self.info[self.current]['audio'].play()
            elif 'text' in self.info[self.current]:
                self.on_play()
                TTS.speak([self.info[self.current]['text']], self.on_stop)

    def on_play(self):
        if self.current in self.info:
            if 'audio' in self.info[self.current]:
                super(Item, self).on_play_wl(self.info[self.current]['audio'].source)
            elif 'text' in self.info[self.current]:
                super(Item, self).on_play_wl(self.info[self.current]['text'])
            self.cg.is_playing = True
            self.change_img('2')

    def on_stop(self, dt):
        if self.current in self.info:
            if 'audio' in self.info[self.current]:
                super(Item, self).on_stop_wl(self.info[self.current]['audio'].source)
            elif 'text' in self.info[self.current]:
                super(Item, self).on_stop_wl(self.info[self.current]['text'])
            self.cg.is_playing = False
            self.current += 1
            CuriosityGame.current += 1
            self.change_img('1')

    def get_text(self):
        # if still has text
        if self.current in self.info:
            if 'text' in self.info[self.current]:
                return self.info[self.current]['text'][::-1]
        return None


class GameScreen(Screen):
    the_app = None
    curiosity_game = None

    def start(self, the_app):
        self.the_app = the_app
        self.curiosity_game = CuriosityGame()

    def on_enter(self, *args):
        self.curiosity_game.load(self.the_app.root.size)
        Clock.schedule_once(self.end_game, self.curiosity_game.game_duration)
        self.curiosity_game.start()

    def end_game(self, dt):
        self.the_app.sm.current = 'zero_screen'


class CuriosityGame:
    items = {}
    current = 0
    the_widget = None
    is_playing = False
    the_end = False
    game_duration = 120
    filename = 'items.json'

    def __init__(self):
        self.the_widget = CuriosityWidget()

    def load(self, size=[100,100]):
        # initialize items
        items_path = 'items/'

        items_json = JsonStore(items_path + self.filename)
        self.the_widget.update_background(items_path + items_json.get('background'))
        items_list = items_json.get('list')

        for name, value in items_list.items():
            self.items[name] = Item(do_rotation=False, do_scale=False)
            self.items[name].name = name
            self.items[name].cg = self

            if 'label' in value:
                if LANGUAGE == 'Hebrew':
                    self.items[name].item_lbl.text = value['label'][::-1]
                elif LANGUAGE == 'English':
                    self.items[name].item_lbl.text = value['label']

            if 'pos' in value:
                self.items[name].base_pos = (int(float(value['pos']['x']) * size[1]), int(float(value['pos']['y']) * size[0]))

            self.items[name].img = {}
            if 'img' in value:
                for ki, i in value['img'].items():
                    self.items[name].img[ki] = items_path + i
                self.items[name].change_img('1')

            self.items[name].info = {}
            self.items[name].question = {}
            if 'text' in value:
                for kt, t in value['text'].items():
                    self.items[name].info[int(kt)] = {'text': t['text']}
                    try:
                        self.items[name].info[int(kt)]['audio'] = SoundLoader.load(items_path + t['audio'])
                        self.items[name].info[int(kt)]['audio'].bind(
                                on_play=partial(self.on_play, name))
                        self.items[name].info[int(kt)]['audio'].bind(
                                on_stop=partial(self.on_stop, name))
                    except:
                        if 'audio' in t:
                            Logger.info('audio: cant find ' + items_path + t['audio'])
                    if 'question' in t:
                        self.items[name].question[int(kt)] = {}
                        self.items[name].question[int(kt)] = t['question']

        # set widgets
        self.the_widget.clear_widgets()
        for key, value in self.items.items():
            self.the_widget.add_widget(value)

    def start(self):
        # set the timer of the game
        print('Starting clock...')
        for k,v in self.items.items():
            v.current = 1
            v.pos = v.base_pos
        self.the_end = False
        self.is_playing = False


    def on_play(self, name, par):
        self.items[name].on_play()
        text = self.items[name].get_text()
        if text:
            self.show_text(text)

    def on_stop(self, name, par):
        self.items[name].on_stop()
        self.show_text("")
        if self.the_end:
            self.end_game(0.5)

    def show_text(self, text):
        if len(text) > 0:
            new_lines = None
            if LANGUAGE == 'Hebrew':
                new_lines = HebrewManagement.multiline(text, 45)
            if new_lines:
                for nl in range(0, len(new_lines)):
                    self.the_widget.cg_lbl[nl].text = new_lines[nl]
        else:
            for l in self.the_widget.cg_lbl:
                l.text = ''


class CuriosityWidget(FloatLayout):
    cg_lbl = None

    def __init__(self):
        super(CuriosityWidget, self).__init__()
        with self.canvas.before:
            self.rect = Rectangle(source='')
            self.bind(size=self._update_rect, pos=self._update_rect)
        self.cg_lbl = []
        for k in range(0,3):
            self.cg_lbl.append(Label(font_name='fonts/the_font.ttf', halign='right', text='',
                            pos=(10, 10 + 75 * k), font_size='48sp', size_hint_y=0.1, color=[0,0.1,0.5,1.0]))
            self.add_widget(self.cg_lbl[-1])

    def update_background(self, filename):
        with self.canvas.before:
            self.rect = Rectangle(source=filename, size=self.size)

            self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
