# Hack-Elite-AI-Powered-Food-Spoilage-Detection

## Overview
This project aims to develop an AI-powered food spoilage detection model using transfer learning with the Image captioning and ResNet50 architecture. The model classifies images of food as either fresh or spoiled/ healty or unhealthy, providing a valuable tool for reducing food waste and enhancing food safety.
Integration of Raspberry pi pico W with sensors like DHT-11, MQ135 can also be seen. 

## Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/food-spoilage-detection.git
   cd food-spoilage-detection
   ```

2. Install the required packages in each folder:
   ```bash
   pip install -r requirements.txt
   ```

3. For ResNet50, download the dataset and place it in the `data/train` directory.

## Project Structure
```
Image-Captioning/
│
├── food_classification.ipynb
├── requirements.txt

ResNet50/
│
├── data/
│   └── train/
│       ├── fresh/
│       └── spoiled/
│
├── app.py
├── requirements.txt

WebServer-and-IOT/
│
├── Circuit Diagram.png
├── Description of Components Used
├── List of Components Required.png
├── Web Server Page.png
├── finWeb.py
├── final1.py

── README.md

```

Drive link for Video/Presentation: [Click Here!!]("https://drive.google.com/drive/folders/1wlCWJa5w4xO2fOP7bD_pMEmbu4OIJsyT")
