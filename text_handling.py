import json
from random import choice
import time
from kivy.clock import Clock

the_tts = None
try:
    from plyer import tts
    tts.speak('')
    the_tts = 'plyer'
except:
    pass

try:
    import pyttsx
    the_tts = 'pyttsx'
except:
    pass


class TTS:
    engine = None
    what = ''
    current_text = None

    @staticmethod
    def start():
        TTS.engine =  None
        if the_tts is 'pyttsx':
            TTS.engine = pyttsx.init()
            TTS.engine.setProperty('voice', 'HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Speech/Voices/Tokens/TTS_MS_EN-US_ZIRA_11.0')
            TTS.engine.connect(topic='finished-utterance', cb=TTS.finished)

    @staticmethod
    def finished():
        print('finished', TTS.what)
        return True

    @staticmethod
    def speak(the_text, finished=None):
        if the_tts is 'pyttsx':
            for txt in the_text:
                TTS.engine.say(txt)
            TTS.engine.runAndWait()
            time.sleep(1)
            if finished:
                finished(0.0)

        elif the_tts is 'plyer':
            if the_text:
                print('the_text', the_text)
                TTS.current_text = the_text[0]
                Clock.schedule_once(TTS.speak_tts,
                                    float(len(TTS.current_text)) * 0.05)
                the_text.remove(TTS.current_text)
                TTS.speak(the_text, finished=finished)
            elif finished:
                Clock.schedule_once(finished, 0.05)

    @staticmethod
    def speak_tts(dt):
        print('speaking ... ', TTS.current_text)
        tts.speak(TTS.current_text)



class TextHandler:

    def __init__(self, condition='growth'):
        self.data = None
        self.condition = condition
        self.what = None
        TTS.start()

    def load_text(self, filename='./tablet_app/robot_text.json'):
        with open(filename) as data_file:
            self.data = json.load(data_file)

    def say(self, what):
        self.what = what
        if what in self.data:
            the_options = self.data[what]
            the_text = []
            if isinstance(the_options, list):
                the_text.append(choice(the_options))
            elif isinstance(the_options, dict):
                if 'all' in the_options:
                    the_text.append(choice(the_options['all']))
                if self.condition in the_options:
                    the_text.append(choice(the_options[self.condition]))

            print('speak: ', the_text)
            TTS.speak(the_text)
            return True
        else:
            return False