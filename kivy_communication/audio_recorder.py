from kivy.clock import Clock
from os.path import join
import wave
from kivy_communication.kivy_logger import *
try:
    from jnius import autoclass
except:
    pass

class AR:
    rec = None
    filename = None
    finished = None

    @staticmethod
    def start(file_name, record_time=10, finished=None):
        AR.filename = file_name
        AR.finished = finished
        t0 = datetime.now()
        # full_filename = KL.log.pathname + '/' + t0.strftime('%Y_%m_%d_%H_%M_%S_%f') + AR.filename + '.wav'
        full_filename = join(KL.log.pathname,
                             KL.log.file_prefix + t0.strftime('%Y-%m-%d-%H-%M-%S-%f') + AR.filename + '.wav')
        print "audio fn: ", full_filename
        AR.rec = Recorder(full_filename)
        KL.log.insert(action=LogAction.audio, obj=full_filename, comment='audio recording start')
        AR.rec.start()
        Clock.schedule_once(AR.finish_recording, record_time)


    @staticmethod
    def finish_recording(self):
        KL.log.insert(action=LogAction.audio, obj='', comment='audio recording stop')
        AR.rec.stop()
        AR.finished()


class Recorder(object):

    def __init__(self, filename):
        MediaRecorder = autoclass('android.media.MediaRecorder')
        AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
        AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

        # create out recorder
        self.mRecorder = MediaRecorder()
        self.mRecorder.setAudioSource(AudioSource.MIC)
        self.mRecorder.setOutputFormat(OutputFormat.THREE_GPP)
        self.mRecorder.setOutputFile(filename)
        self.mRecorder.setAudioEncoder(AudioEncoder.AMR_NB)
        self.mRecorder.prepare()

    def start(self):
        self.mRecorder.start()

    def stop(self):
        self.mRecorder.stop()
        self.mRecorder.release()

