# MRC to TIFF Converter

This Python script provides a comprehensive tool for converting MRC files to TIFF format, featuring a GUI for easy interaction. It allows users to navigate through frames of MRC files, apply denoising and smoothing filters, and convert selected frames to TIFF with customizable options such as resolution and order reversal. Additionally, it introduces a scale bar to the image display, enhancing the interpretability of the microscopy images.

## Features

- **GUI for Easy Interaction**: Select MRC files and output directories through a user-friendly interface.
- **Frame Navigation**: Browse through the frames of an MRC file using a simple slider control.
- **Image Processing**: Apply denoising and smoothing filters to enhance image quality.
- **Conversion Options**: Customize the conversion process by selecting the resolution, deciding on the order of frames, and choosing between saving as separate files or as a stack.
- **Scale Bar**: Adds a visible scale bar to the images, indicating the scale in nanometers or micrometers, to provide a reference for the size of features in the images.

## Installation

Ensure you have Python installed on your system (recommended version: 3.8 or newer). This script also requires the following Python libraries:

- Pillow
- NumPy
- mrcfile
- tifffile
- scipy

You can install these dependencies using pip:

```bash
pip install Pillow numpy mrcfile tifffile scipy
