#!/usr/bin/python
# -*- coding: utf-8 -*-
from kivy.app import App
from curiosity_assessment import *
from kivy_communication import *
from kivy.uix.screenmanager import ScreenManager, Screen
from text_handling import *


class ZeroScreen(Screen):
    pass


class CuriosityAssessmentApp(App):

    def build(self):
        # initialize logger
        KL.start([DataMode.file, DataMode.communication, DataMode.ros], self.user_data_dir)
        # KL.start([DataMode.file], "/sdcard/curiosity/")#self.user_data_dir)
        TTS.start()

        self.sm = ScreenManager()

        screen = ZeroScreen(name='zero')
        self.sm.add_widget(screen)

        screen = GameScreen(name='thegame')
        screen.start(self)
        screen.add_widget(screen.curiosity_game.the_widget)
        self.sm.add_widget(screen)

        self.sm.current = 'zero'
        return self.sm

if __name__ == '__main__':
    CuriosityAssessmentApp().run()
