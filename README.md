# MP4 to GIF Converter

## Description

MP4 to GIF Converter is a user-friendly desktop application that allows you to convert MP4 video files to GIF format. Built with Python and Tkinter, this tool provides a graphical interface for easy conversion of single files or batch processing of multiple files.

## Features

- Convert single MP4 files to GIF
- Batch convert multiple MP4 files in a folder
- Customize conversion parameters:
  - Start time
  - Duration
  - Frame rate (FPS)
  - Output scale
- User-friendly graphical interface
- Progress bar for conversion tracking

## Requirements

- Python 3.x
- tkinter
- moviepy
- numpy
- Pillow (PIL)

## Installation

1. Ensure you have Python 3.x installed on your system.
2. Install the required dependencies:

```
pip install moviepy numpy Pillow
```

3. Download the `mp4_to_gif_converter.py` file.

## Usage

1. Run the script:

```
python mp4_to_gif_converter.py
```

2. The application window will open.

3. For single file conversion:
   - Click "Browse File" to select an MP4 file
   - Choose an output location and filename
   - Set conversion parameters (optional)
   - Click "Convert"

4. For batch conversion:
   - Click "Browse Folder" to select a folder containing MP4 files
   - Choose an output folder
   - Set conversion parameters (optional)
   - Click "Convert"

5. Monitor the progress bar for conversion status.

## Conversion Parameters

- **Start Time**: The starting point in the video (in seconds) from which to begin the GIF.
- **Duration**: The length of the GIF (in seconds). If left empty, it will convert the entire video.
- **FPS**: Frames per second for the output GIF. Default is 10.
- **Scale**: Resize factor for the output GIF. Default is 0.5 (half the original size).

## Notes

- The application uses a custom resize function to maintain better quality in the output GIF.
- Error handling is implemented to manage conversion issues and provide user feedback.

## License

MIT

## Author

Ricky Segura

## Acknowledgments

This project uses the following open-source libraries:
- moviepy
- numpy
- Pillow (PIL)

Special thanks to the Neospaces team for inspiration and support.
