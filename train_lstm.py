import numpy
import argparse
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils

parser = argparse.ArgumentParser()
parser.add_argument("--data", help="The training data")
parser.add_argument("--epochs" help="Number of epochs to train for")
args = parser.parse_args()

filename = args.data
if args.epochs:
    epochs = args.epochs
else:
    epochs = 30
raw_text = ""
with open(filename, mode='r', encoding='utf8') as file:
    for line in file:
        raw_text += line
raw_text = raw_text.lower()

chars = sorted(list(set(raw_text)))
char_to_int = dict((c, i) for i, c in enumerate(chars))

n_chars = len(raw_text)
n_vocab = len(chars)

print("Total chars: " + str(n_chars))
print("Total vocab: " + str(n_vocab))

seq_length = 100
dataX = []
dataY = []

for i in range(0, n_chars - seq_length, 1):
    seq_in = raw_text[i:i + seq_length]
    seq_out = raw_text[i + seq_length]
    dataX.append([char_to_int[char] for char in seq_in])
    dataY.append(char_to_int[seq_out])
n_patterns = len(dataX)

print("Total patterns: " + str(n_patterns))

X = numpy.reshape(dataX, (n_patterns, seq_length, 1))
X = X / float(n_vocab)

y = np_utils.to_categorical(dataY)

model = Sequential()
model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(256))
model.add(Dropout(0.2))
model.add(Dense(y.shape[1], activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam')

filepath = "weights-improvement-" + str(filename) + "-{epoch:02d}-{loss:.4f}-bigger.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
callbacks_list = [checkpoint]

try:
    model.fit(X, y, epochs=epochs, batch_size=64, callbacks=callbacks_list, verbose=1)
except MemoryError as err:
    print(str(err))

