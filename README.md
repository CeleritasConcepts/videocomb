# VideoComb

A professional video concatenation tool with a modern GUI interface.

## Features

- 🎨 Modern, professional UI/UX with dark mode
- 📁 Drag and drop video files or browse to select
- 🔄 Reorder videos by dragging them up/down
- ⚡ Fast video combination using FFmpeg
- 🎬 Supports multiple video formats (MP4, AVI, MOV, MKV, FLV, WMV, M4V)

## Requirements

- Python 3.8 or higher
- FFmpeg (must be installed and available in PATH)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install FFmpeg:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

## Usage

Run the application:
```bash
python videocomb.py
```

### How to Use

1. **Add Videos**: 
   - Drag and drop video files into the drop zone, or
   - Click the drop zone to browse and select files

2. **Reorder Videos**:
   - Use the ▲ and ▼ buttons to move videos up or down
   - Videos will be combined in the order shown

3. **Combine Videos**:
   - Click the "⚡ Combine Videos" button
   - Choose where to save the output file
   - Wait for processing to complete

## Notes

- The application uses FFmpeg's concat demuxer with stream copy mode for fast, lossless concatenation
- All input videos should ideally have the same codec, resolution, and frame rate for best results
- The output file will be in MP4 format by default
