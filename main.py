#!/usr/bin/python
# -*- coding: utf-8 -*-
from kivy.app import App
from free_exploration import *
from kivy_communication import *
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from text_handling import *
from os.path import join, dirname
try:
    from jnius import autoclass
    from android.runnable import run_on_ui_thread

    android_api_version = autoclass('android.os.Build$VERSION')
    AndroidView = autoclass('android.view.View')
    # AndroidPythonActivity = autoclass('org.renpy.android.PythonActivity')
    AndroidPythonActivity = autoclass('org.kivy.android.PythonActivity')

    Logger.debug(
        'Application runs on Android, API level {0}'.format(
            android_api_version.SDK_INT
        )
    )
except ImportError:
    def run_on_ui_thread(func):
        def wrapper(*args):
            Logger.debug('{0} called on non android platform'.format(
                func.__name__
            ))
        return wrapper


session_types = ['pre', 'post', 'after', 'delay', 'file']

class SetupScreenRoom(Screen):
    ip = ''

class ZeroScreen(Screen):
    pass


class FreeExplorationApp(App):
    game_screen = None

    def build(self):

        TTS.start()

        self.sm = ScreenManager()
        self.sm.add_widget(SetupScreenRoom(name='setup_screen_room'))
        self.sm.current = 'setup_screen_room'
        return self.sm

    def on_start(self):
        self.android_set_hide_menu()

    def init_communication(self, ip_addr):
        self.local_ip = ip_addr
        KC.start(the_ip=self.local_ip, the_parents=[self])  # 127.0.0.1

        if ip_addr == "":
            self.on_connection()

    def on_connection(self):
        self.zero_screen = ZeroScreen(name='zero_screen')
        self.sm.add_widget(self.zero_screen)

        try:
            with open(join(dirname(self.user_data_dir),"pid_initial.txt"), 'r') as id_f:
                print "hi"
                line = id_f.readlines()
                line = line[0].split(";")
                print line[0], line[1]
                #print self.zero_screen.subject_id.text, self.zero_screen.subject_initial.text
                self.zero_screen.subject_initial.text = line[1]
                self.zero_screen.subject_id.text = line[0]

                id_f.close()
        except Exception as e:
            print e

        self.android_set_hide_menu()
        self.sm.current = 'zero_screen'

    def press_connect_button(self, ip_addr):
        # To-Do: save previous ip input
        print ip_addr
        self.init_communication(ip_addr)

    def start_assessment(self, pre_post_flag, subject_id, subject_initial):
        self.subject_id = subject_id
        self.subject_initial = subject_initial

        self.session = session_types[pre_post_flag - 1]

        if self.subject_id == "" or self.subject_initial == "":
            return

        KL.start(mode=[DataMode.file, DataMode.communication, DataMode.ros], pathname=self.user_data_dir,
                 file_prefix=self.session + "_" + self.subject_id + "_" + self.subject_initial + "_", the_ip=self.local_ip)

        KL.log.insert(action=LogAction.data, obj='FreeExplorationApp', comment='start')

        with open(join(dirname(self.user_data_dir),"pid_initial.txt"), 'w') as id_f:
            id_f.write(self.subject_id+";"+self.subject_initial)
            id_f.close()

        self.game_screen = GameScreen(name='the_game')
        self.game_screen.start(self)
        self.game_screen.add_widget(self.game_screen.curiosity_game.the_widget)
        self.sm.add_widget(self.game_screen)

        if self.session == 'file':
            self.game_screen.curiosity_game.filename = dirname(self.user_data_dir) + '/freeexploration/'
        else:
            self.game_screen.curiosity_game.filename = 'items/'

        self.game_screen.curiosity_game.filename += 'items_' + self.session + '.json'
        self.sm.current = 'the_game'
        self.android_set_hide_menu()
        return

    @run_on_ui_thread
    def android_set_hide_menu(self):
        if android_api_version.SDK_INT >= 19:
            Logger.debug('API >= 19. Set hide menu')
            view = AndroidPythonActivity.mActivity.getWindow().getDecorView()
            view.setSystemUiVisibility(
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            )

if __name__ == '__main__':
    FreeExplorationApp().run()
