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

    def build(self):
        # initialize logger
        KL.start([DataMode.file, DataMode.communication, DataMode.ros], self.user_data_dir)
        # KL.start([DataMode.file], "/sdcard/curiosity/")#self.user_data_dir)
        TTS.start()

        self.sm = ScreenManager()

        screen = ZeroScreen()
        screen.ids['subject_id'].bind(text=screen.ids['subject_id'].on_text_change)

        self.sm.add_widget(screen)

        screen = GameScreen(name='thegame')
        screen.start(self)
        screen.add_widget(screen.curiosity_game.the_widget)
        self.sm.add_widget(screen)

        self.sm.current = 'zero_screen'
        return self.sm

if __name__ == '__main__':
    FreeExplorationApp().run()
