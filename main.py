import os
import wave

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, \
    QMessageBox, QLabel, QSpinBox


class AudioSplitter(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle('Audio Splitter')

        self.btn_choose_file = QPushButton('Выбрать аудиофайл', self)
        self.btn_choose_file.move(50, 50)
        self.btn_choose_file.clicked.connect(self.choose_file)

        self.lbl_duration = QLabel('Длительность отрезков (мин):', self)
        self.lbl_duration.move(50, 90)

        self.spb_duration = QSpinBox(self)
        self.spb_duration.move(220, 90)
        self.spb_duration.setMinimum(10)
        self.spb_duration.setMaximum(80)
        self.spb_duration.setValue(30)

        self.btn_split_audio = QPushButton('Разбить на отрезки', self)
        self.btn_split_audio.move(50, 130)
        self.btn_split_audio.clicked.connect(self.split_audio)

        self.show()

    def choose_file(self):
        self.filename, _ = QFileDialog.getOpenFileName(self,
                                                       'Выбрать аудиофайл',
                                                       '.',
                                                       'Audio files (*.wav)')
        self.setWindowTitle(os.path.basename(self.filename))

    def split_audio(self):
        if not hasattr(self, 'filename'):
            QMessageBox.warning(self, 'Ошибка', 'Не выбран аудиофайл')
            return

        duration = self.spb_duration.value() * 60

        with wave.open(self.filename, 'rb') as wav_file:
            nframes = wav_file.getnframes()
            framerate = wav_file.getframerate()
            nchannels = wav_file.getnchannels()
            sampwidth = wav_file.getsampwidth()
            file_duration = nframes / float(framerate)

            if file_duration < duration:
                QMessageBox.warning(self, 'Ошибка',
                                    'Длительность аудиофайла меньше выбранной длительности отрезков')
                return

            basename = os.path.splitext(os.path.basename(self.filename))[0]
            dirname = os.path.dirname(self.filename)
            output_dir = os.path.join(dirname, f'{basename}_split')
            os.makedirs(output_dir, exist_ok=True)

            part_num = 1
            start_frame = 0

            while start_frame < nframes:
                end_frame = min(start_frame + duration * framerate, nframes)
                part_filename = os.path.join(output_dir,
                                             f'{basename}_{part_num}.wav')

                with wave.open(part_filename, 'wb') as part_file:
                    part_file.setnchannels(nchannels)
                    part_file.setsampwidth(sampwidth)
                    part_file.setframerate(framerate)
                    part_file.setnframes(end_frame - start_frame)
                    part_file.writeframes(
                        wav_file.readframes(end_frame - start_frame))

                part_num += 1
                start_frame = end_frame

            QMessageBox.information(self, 'Успех',
                                    'Аудиофайл успешно разбит на отрезки')


if __name__ == '__main__':
    app = QApplication([])
    splitter = AudioSplitter()
    app.exec_()
