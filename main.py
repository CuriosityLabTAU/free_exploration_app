#!/usr/bin/python
# -*- coding: utf-8 -*-
from kivy.app import App
from free_exploration import *
from kivy_communication import *
from kivy.uix.screenmanager import ScreenManager, Screen
from text_handling import *


class ZeroScreen(Screen):

    def on_enter(self, *args):
        KL.restart()


class FreeExplorationApp(App):
    game_screen = None

    def build(self):
        self.init_communication()

        TTS.start()

        self.sm = ScreenManager()

        screen = ZeroScreen()
        screen.ids['subject_id'].bind(text=screen.ids['subject_id'].on_text_change)

        self.sm.add_widget(screen)

        self.game_screen = GameScreen(name='the_game')
        self.game_screen.start(self)
        self.game_screen.add_widget(self.game_screen.curiosity_game.the_widget)
        self.sm.add_widget(self.game_screen)

        self.sm.current = 'zero_screen'
        return self.sm

    def init_communication(self):
        KC.start(the_ip='192.168.1.254', the_parents=[self])  # 127.0.0.1
        KL.start(mode=[DataMode.file, DataMode.communication, DataMode.ros], pathname=self.user_data_dir,
                 the_ip='192.168.1.254')

    def on_connection(self):
        KL.log.insert(action=LogAction.data, obj='FreeExplorationApp', comment='start')

    def press_start(self, pre_post):
        self.game_screen.curiosity_game.filename = 'items_' + pre_post + '.json'
        self.sm.current = 'the_game'

if __name__ == '__main__':
    FreeExplorationApp().run()
