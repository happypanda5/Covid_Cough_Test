from tensorflow.keras.models import load_model
from clean import downsample_mono, envelope
from kapre.time_frequency import Melspectrogram
from kapre.utils import Normalization2D
import numpy as np
from glob import glob
import argparse
import os


def make_prediction(args):

    model = load_model(args.model_fn,
        custom_objects={'Melspectrogram':Melspectrogram,
                        'Normalization2D':Normalization2D})

    wav_paths = glob('{}/**'.format('testop'), recursive=True)
    print(wav_paths)
    wav_paths = sorted([x for x in wav_paths if '.wav' in x])
    classes = sorted(os.listdir('wavfiles'))

    for wav_fn in wav_paths:
        rate, wav = downsample_mono(wav_fn, args.sr)
        mask, env = envelope(wav, rate, threshold=args.threshold)
        clean_wav = wav[mask]
        step = int(args.sr*args.dt)
        batch = []

        for i in range(0, clean_wav.shape[0], step):
            sample = clean_wav[i:i+step]
            sample = sample.reshape(1,-1)
            if sample.shape[0] < step:
                tmp = np.zeros(shape=(1,step), dtype=np.int16)
                tmp[:,:sample.shape[1]] = sample.flatten()
                sample = tmp
            batch.append(sample)
        X_batch = np.array(batch)
        y_pred = model.predict(X_batch)
        y_mean = np.mean(y_pred, axis=0)
        y_pred = np.argmax(y_mean)
        print(wav_fn, classes[y_pred])


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Audio Classification Training')
    parser.add_argument('--model_fn', type=str, default='models/lstm.h5',
                        help='model file to make predictions')
    parser.add_argument('--dt', type=float, default=1.0,
                        help='time in seconds to sample audio')
    parser.add_argument('--sr', type=int, default=16000,
                        help='sample rate of clean audio')
    parser.add_argument('--threshold', type=str, default=20,
                        help='threshold magnitude for np.int16 dtype')
    args, _ = parser.parse_known_args()

    make_prediction(args)
