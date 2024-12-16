# Motion Detection Application (AXON)

This project is a multiprocessing application for processing video files. It includes functionality to stream video, detect objects, and present the results with options for blurring detected objects.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Example](#example)

## Features
- Stream video from a file.
- Detect objects in the video frames using a specified detection method (provided).
- Present detected objects with optional blurring.
- Multi-process architecture for efficient video processing.

## Requirements
- All the necessary modules for the project are provided in the requirements file.

## Getting Started
To run the application locally, follow these steps:

1. Clone the repository
2. Install the required packages (if any)

```bash
git clone git@github.com:pvgraf/axon.git
cd axon
pip install -r requirements
```

## Usage
To run the application, use the following command in your terminal:
```bash
python app.py -h

usage: app.py [-h] -v VIDEO [-b]

Motion Detection Application (AXON)

options:
  -h, --help            show this help message and exit
  -v VIDEO, --video VIDEO
                        Path to the input video file
  -b, --blurring        Enable blurring of detected objects
```

## Example
To process a video without blurring:
```bash
python your_script.py -v input_video.mp4
```

To process a video with blurring:
```bash
python your_script.py -v input_video.mp4 -b
```

* The code adheres to Python standards (PEP 8) and has been verified using flake8 to ensure quality and consistency.
