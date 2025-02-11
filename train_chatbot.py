#import libraries and components for project
# chatbot will be trained on the dataset which contains categories (intents), pattern and responses
#usng neural network (LSTM) to classify which category the user’s message belongs
#give back random response depending on category

#NEEDS TO BE RUN IN PYTHON 3.6.X FOR LIBRARIES TO WORK


import nltk
nltk.download('punkt')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import json
import pickle
import matplotlib.pyplot as plt

import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import random


#store words cand categories
#4 parsing JSON into python

words=[]
classes = []
pairs = []
#ignore punctuation
ignore_words = ['?', '!']
#get intents file for training with predefined patterns and responses.
data_file = open('intents.json').read()
intents = json.loads(data_file)


for intent in intents['intents']:
    for pattern in intent['patterns']:
        # tokenize each word
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        # adding pairs of words and tags
        pairs.append((w, intent['tag']))

        # adding classes to our class array
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

#clean up words and print
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

classes = sorted(list(set(classes)))

print (len(pairs), "pairs")
print (len(classes), "classes", classes)
print (len(words), "words", words)

pickle.dump(words,open('words.pkl','wb'))
pickle.dump(classes,open('classes.pkl','wb'))

# initializing training data
training = []
outputZeroes = [0] * len(classes)
# pairs is the petterns and the tags
# each doc has a bag of words
for p in pairs:
    bag = []
    # list of tokenized words for the pattern
    pattern_words = p[0]
    # lemmatize each word create base word, in attempt to represent related words
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    # if a word match is found, set the bag at that word to 1, otherwise, set to 0
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    # output is a '0' for each tag and set to 1 if it is the current tag
    output = list(outputZeroes)
    output[classes.index(p[1])] = 1
    training.append([bag, output])
# shuffle our features and turn into np.array
random.shuffle(training)
training = np.array(training)
# create train and test lists. X - words, Y - class
x = list(training[:,0])
y = list(training[:,1])
print("Training data created")

#Use Keras sequential API to create model
# Create model - 3 layers. First layer 128 neurons, second layer 64 neurons and 3rd output layer contains number of neurons
# equal to number of intents to predict output intent with softmax
model = Sequential()
model.add(Dense(128, input_shape=(len(x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(y[0]), activation='softmax'))

# Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy', 'mse'])

#fitting and saving the model
history = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)

plt.figure(0)
plt.plot(history.history['accuracy'])
plt.ylabel("Accuracy")
plt.xlabel("Epochs")
plt.savefig("accuracy.png")
plt.figure(1)
plt.plot(history.history['mse'])
plt.ylabel("MSE")
plt.xlabel("Epochs")
plt.savefig("MSE.png")

model.save('chatbot_model.h5', history)

print("model created")
