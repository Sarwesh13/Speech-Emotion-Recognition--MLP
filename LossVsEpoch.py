import os
Root = "C:/Users/Sarwe/OneDrive/Desktop/SER/Ravdess"
os.chdir(Root)


import librosa
import soundfile
import os, glob, pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import validation_curve
from sklearn.metrics import log_loss
import matplotlib.pyplot as plt
import itertools

# Define the scaler object
scaler = StandardScaler()

# Extract features (mfcc, chroma, mel) from a sound file
def extract_feature(file_name, mfcc, chroma, mel):
    with soundfile.SoundFile(file_name) as sound_file:
        X = sound_file.read(dtype="float32")
        sample_rate=sound_file.samplerate
        if chroma:
            stft = np.abs(librosa.stft(X))
        result=np.array([])
        if mfcc:
            mfccs=np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
            result=np.hstack((result, mfccs))
        if chroma:
            chroma=np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
            result=np.hstack((result, chroma))
        if mel:
            mel=np.mean(librosa.feature.melspectrogram(y=X, sr=sample_rate).T,axis=0)
            result=np.hstack((result, mel))
    return result

# Emotions in the RAVDESS dataset
emotions={
  '01':'neutral',
  '02':'calm',
  '03':'happy',
  '04':'sad',
  '05':'angry',
  '06':'fearful',
  '07':'disgust',
  '08':'surprised'
}

# Emotions in the TESS dataset
tess_emotions = {
    'angry': 'angry',
    'disgust': 'disgust',
    'fear': 'fearful',
    'happy': 'happy',
    'neutral': 'neutral',
    'ps': 'surprised',
    'sad': 'sad'
}



# Observed emotions in both datasets
observed_emotions = set(list(emotions.values()) + list(tess_emotions.values()))

# Load the data and extract features for each sound file
def load_data(test_size=0.2):
    x, y = [], []
    
    # Load RAVDESS dataset
    for file in glob.glob("C:/Users/Sarwe/OneDrive/Desktop/SER/Ravdess/Actor_*/*.wav"):
        file_name = os.path.basename(file)
        emotion = emotions[file_name.split("-")[2]]
        if emotion not in observed_emotions:
            continue
        feature = extract_feature(file, mfcc=True, chroma=True, mel=True)
        x.append(feature)
        y.append(emotion)
    
    # Load TESS dataset
    for file in glob.glob("C:/Users/Sarwe/OneDrive/Desktop/SER/Tess/*/*.wav"):
        file_name = os.path.basename(file)
        emotion = tess_emotions[file_name.split("_")[2].split(".")[0]]
        if emotion not in observed_emotions:
            continue
        feature = extract_feature(file, mfcc=True, chroma=True, mel=True)
        x.append(feature)
        y.append(emotion)
        

    # Split the dataset
    x_train, x_test, y_train, y_test = train_test_split(np.array(x), y, test_size=test_size, random_state=9)

    # Normalize the features using StandardScaler
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    return x_train, x_test, y_train, y_test


# Split the dataset
x_train, x_test, y_train, y_test = load_data(test_size=0.25)

# Get the shape of the training and testing datasets
print((x_train.shape[0], x_test.shape[0]))

# Get the number of features extracted
print(f'Features extracted: {x_train.shape[1]}')


# Initialize the Multi Layer Perceptron Classifier with modified parameters
model = MLPClassifier(alpha=0.01, batch_size=16, hidden_layer_sizes=(512,), learning_rate='constant', max_iter=1, warm_start=True)

num_epochs = 100
train_losses = []
val_losses = []

# Train the model
for epoch in range(num_epochs):
    model.fit(x_train, y_train)
    train_loss = model.loss_
    train_losses.append(train_loss)
    
    y_pred_proba = model.predict_proba(x_test)
    val_loss = log_loss(y_test, y_pred_proba)
    val_losses.append(val_loss)
    
    print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")


# Plot the training and validation loss versus epoch
plt.plot(range(1, num_epochs+1), train_losses, label='Training Loss')
plt.plot(range(1, num_epochs+1), val_losses, label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()
