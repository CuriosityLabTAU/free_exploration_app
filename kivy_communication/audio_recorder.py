from kivy.clock import Clock
from jnius import autoclass
from audiostream import get_input
import wave
from kivy_communication.kivy_logger import *


class AR:
    rec = None
    filename = None
    finished = None

    @staticmethod
    def start(file_name, record_time=10, finished=None):
        AR.filename = file_name
        AR.finished = finished
        t0 = datetime.now()
        full_filename = KL.log.pathname + '/' + t0.strftime('%Y_%m_%d_%H_%M_%S_%f') + AR.filename + '.wav'
        AR.rec = Recorder(full_filename)
        AR.rec.start()
        Clock.schedule_once(AR.finish_recording, record_time)


    @staticmethod
    def finish_recording(self):
        AR.rec.stop()
        KL.log.insert(action=LogAction.audio, obj=str(AR.rec.sData), comment='audio recording')
        AR.finished()


class Recorder(object):
    filename = None
    samples_per_second = 60

    def __init__(self, filename):
        self.filename = filename
        # get the needed Java classes
        self.MediaRecorder = autoclass('android.media.MediaRecorder')
        self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        self.AudioFormat = autoclass('android.media.AudioFormat')
        self.AudioRecord = autoclass('android.media.AudioRecord')
        # define our system
        self.SampleRate = 44100
        self.ChannelConfig = self.AudioFormat.CHANNEL_IN_MONO
        self.AudioEncoding = self.AudioFormat.ENCODING_PCM_16BIT
        self.BufferSize = self.AudioRecord.getMinBufferSize(self.SampleRate, self.ChannelConfig, self.AudioEncoding)
        self.sData = []
        self.mic = get_input(callback=self.mic_callback, source='mic', buffersize=self.BufferSize)

    def mic_callback(self, buf):
        self.sData.append(buf)
        # print ('got : ' + str(len(buf)))

    def start(self, recordtime=1):
        self.mic.start()
        Clock.schedule_interval(self.readbuffer, 1/self.samples_per_second)

    def readbuffer(self, dt):
        self.mic.poll()

    def stop(self):
        Clock.unschedule(self.readbuffer)
        self.mic.stop()
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.mic.channels)
        wf.setsampwidth(2)
        wf.setframerate(self.mic.rate)
        wf.writeframes(b''.join(self.sData))
        wf.close()
