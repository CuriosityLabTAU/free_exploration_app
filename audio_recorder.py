from kivy.clock import Clock
from jnius import autoclass
from audiostream import get_input
import wave


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
        self.outstream = self.FileOutputStream(self.filename)
        self.sData = []
        self.mic = get_input(callback=self.mic_callback, source='mic', buffersize=self.BufferSize)

    def mic_callback(self, buf):
        self.sData.append(buf)
        print ('got : ' + str(len(buf)))

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
