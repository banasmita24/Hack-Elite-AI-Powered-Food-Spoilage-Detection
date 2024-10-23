import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
import cv2
import os
import numpy as np

# Image data augmentation and loading dataset
train_datagen = ImageDataGenerator(rescale=1./255,
                                   shear_range=0.2,
                                   zoom_range=0.2,
                                   horizontal_flip=True,
                                   validation_split=0.2)  # Splitting data into training and validation sets

# Load training data from the directory
train_generator = train_datagen.flow_from_directory(
    'data/train',  # Path to the dataset
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary',
    subset='training'  # Use the training subset
)

# Load validation data from the directory
validation_generator = train_datagen.flow_from_directory(
    'data/train',  # Path to the dataset
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary',
    subset='validation'  # Use the validation subset
)

# Print class information and sample counts
print(f'Training classes: {train_generator.class_indices}')
print(f'Number of training images: {train_generator.samples}')
print(f'Number of validation images: {validation_generator.samples}')

# Load pre-trained ResNet50 model without the top layer (for feature extraction)
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Build the complete model by adding custom layers on top of the base model
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dense(128, activation='relu'),
    Dense(1, activation='sigmoid')  # Sigmoid for binary classification
])

# Freeze the base model layers (to train only the top layers initially)
for layer in base_model.layers:
    layer.trainable = False

# Compile the model with Adam optimizer and binary cross-entropy loss
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(train_generator,
                    epochs=10,
                    validation_data=validation_generator)

# Evaluate the model on the validation set
loss, accuracy = model.evaluate(validation_generator)
print(f'Validation Accuracy: {accuracy}')

# Function to preprocess and predict a single image
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))
    image = image / 255.0  # Normalize the pixel values
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

# Example: Path to a test image (Update with the actual test image path)
test_image_path = 'data/train/spoiled/rottenapples/rotated_by_15_Screen Shot 2018-06-07 at 2.16.18 PM.png'  # Use an actual image path from your dataset
test_image = preprocess_image(test_image_path)

# Predict whether the test image is fresh or spoiled
prediction = model.predict(test_image)
print('Spoiled' if prediction > 0.5 else 'Fresh')

# Fine-tuning: Unfreeze the last 10 layers of the base model for fine-tuning
for layer in base_model.layers[-10:]:
    layer.trainable = True

# Recompile the model with a lower learning rate for fine-tuning
model.compile(optimizer=tf.keras.optimizers.Adam(1e-5), loss='binary_crossentropy', metrics=['accuracy'])

# Fine-tune the model on the training set
history_fine = model.fit(train_generator, epochs=5, validation_data=validation_generator)

# Save the final model
model.save('food_spoilage_detection_model.h5')
