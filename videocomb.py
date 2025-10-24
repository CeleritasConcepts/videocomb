#!/usr/bin/env python3
"""
VideoComb - Professional Video Concatenation Tool
A modern GUI application for combining video files using FFmpeg
"""

import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import subprocess
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
import re


# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VideoFile:
    """Represents a video file in the list"""
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)


class VideoCombApp(ctk.CTk, TkinterDnD.DnDWrapper):
    """Main application class for VideoComb"""
    
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        self.title("VideoComb - Video Concatenation Tool")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Video files list
        self.video_files = []
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the user interface"""
        
        # Header frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="VideoComb",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(side="left")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Combine multiple videos into one seamlessly",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        subtitle_label.pack(side="left", padx=(15, 0))
        
        # Main content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Drop zone frame
        drop_zone_frame = ctk.CTkFrame(content_frame, height=120)
        drop_zone_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        drop_zone_frame.grid_propagate(False)
        
        # Drop zone label
        self.drop_zone_label = ctk.CTkLabel(
            drop_zone_frame,
            text="📁 Drop video files here or click to browse",
            font=ctk.CTkFont(size=16),
            fg_color=("gray75", "gray25"),
            corner_radius=10,
            height=100
        )
        self.drop_zone_label.pack(fill="both", expand=True, padx=10, pady=10)
        self.drop_zone_label.bind("<Button-1>", lambda e: self.browse_files())
        
        # Enable drag and drop
        self.drop_zone_label.drop_target_register(DND_FILES)
        self.drop_zone_label.dnd_bind('<<Drop>>', self.on_drop)
        
        # Video list frame
        list_container = ctk.CTkFrame(content_frame)
        list_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)
        
        # List label
        list_label = ctk.CTkLabel(
            list_container,
            text="Video Files (drag to reorder)",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        list_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Scrollable frame for video list
        self.video_list_frame = ctk.CTkScrollableFrame(
            list_container,
            fg_color=("gray85", "gray20")
        )
        self.video_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.video_list_frame.grid_columnconfigure(0, weight=1)
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(10, 15))
        action_frame.grid_columnconfigure(1, weight=1)
        
        # Clear all button
        self.clear_button = ctk.CTkButton(
            action_frame,
            text="Clear All",
            command=self.clear_all,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            width=120,
            height=36
        )
        self.clear_button.grid(row=0, column=0, padx=(0, 10))
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            action_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50")
        )
        self.progress_label.grid(row=0, column=1, sticky="w", padx=10)
        
        # Combine button
        self.combine_button = ctk.CTkButton(
            action_frame,
            text="⚡ Combine Videos",
            command=self.combine_videos,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=200
        )
        self.combine_button.grid(row=0, column=2)
        
    def browse_files(self):
        """Open file browser to select video files"""
        filetypes = (
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v"),
            ("All files", "*.*")
        )
        filenames = filedialog.askopenfilenames(
            title="Select video files",
            filetypes=filetypes
        )
        
        if filenames:
            for filename in filenames:
                self.add_video_file(filename)
    
    def on_drop(self, event):
        """Handle drag and drop event"""
        files = self.parse_drop_files(event.data)
        for file in files:
            if os.path.isfile(file):
                self.add_video_file(file)
    
    def parse_drop_files(self, data):
        """Parse dropped file paths"""
        files = []
        # Handle different formats of dropped data
        if data.startswith('{'):
            # Files with spaces are wrapped in braces
            pattern = r'\{([^}]+)\}|(\S+)'
            matches = re.finditer(pattern, data)
            for match in matches:
                file_path = match.group(1) if match.group(1) else match.group(2)
                if file_path:
                    files.append(file_path)
        else:
            files = data.split()
        return files
    
    def add_video_file(self, filepath):
        """Add a video file to the list"""
        # Check if file already exists
        for vf in self.video_files:
            if vf.filepath == filepath:
                return
        
        video_file = VideoFile(filepath)
        self.video_files.append(video_file)
        self.refresh_video_list()
    
    def refresh_video_list(self):
        """Refresh the video list display"""
        # Clear existing widgets
        for widget in self.video_list_frame.winfo_children():
            widget.destroy()
        
        # Add video items
        for idx, video_file in enumerate(self.video_files):
            self.create_video_item(idx, video_file)
    
    def create_video_item(self, index, video_file):
        """Create a video item widget"""
        item_frame = ctk.CTkFrame(
            self.video_list_frame,
            fg_color=("gray90", "gray17"),
            corner_radius=8
        )
        item_frame.grid(row=index, column=0, sticky="ew", pady=5, padx=5)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Index label
        index_label = ctk.CTkLabel(
            item_frame,
            text=f"{index + 1}",
            font=ctk.CTkFont(size=18, weight="bold"),
            width=40,
            fg_color=("gray75", "gray25"),
            corner_radius=6
        )
        index_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Filename label
        filename_label = ctk.CTkLabel(
            item_frame,
            text=video_file.filename,
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        filename_label.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        # Button frame
        button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, padx=5, pady=5)
        
        # Move up button
        if index > 0:
            up_button = ctk.CTkButton(
                button_frame,
                text="▲",
                width=40,
                height=32,
                command=lambda idx=index: self.move_up(idx),
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray35")
            )
            up_button.pack(side="left", padx=2)
        
        # Move down button
        if index < len(self.video_files) - 1:
            down_button = ctk.CTkButton(
                button_frame,
                text="▼",
                width=40,
                height=32,
                command=lambda idx=index: self.move_down(idx),
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray35")
            )
            down_button.pack(side="left", padx=2)
        
        # Remove button
        remove_button = ctk.CTkButton(
            button_frame,
            text="✕",
            width=40,
            height=32,
            command=lambda idx=index: self.remove_file(idx),
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red")
        )
        remove_button.pack(side="left", padx=2)
    
    def move_up(self, index):
        """Move a video file up in the list"""
        if index > 0:
            self.video_files[index], self.video_files[index - 1] = \
                self.video_files[index - 1], self.video_files[index]
            self.refresh_video_list()
    
    def move_down(self, index):
        """Move a video file down in the list"""
        if index < len(self.video_files) - 1:
            self.video_files[index], self.video_files[index + 1] = \
                self.video_files[index + 1], self.video_files[index]
            self.refresh_video_list()
    
    def remove_file(self, index):
        """Remove a video file from the list"""
        if 0 <= index < len(self.video_files):
            self.video_files.pop(index)
            self.refresh_video_list()
    
    def clear_all(self):
        """Clear all video files"""
        if self.video_files:
            self.video_files.clear()
            self.refresh_video_list()
    
    def combine_videos(self):
        """Combine all video files using FFmpeg"""
        if len(self.video_files) < 2:
            messagebox.showwarning(
                "Insufficient Files",
                "Please add at least 2 video files to combine."
            )
            return
        
        # Check if ffmpeg is available
        if not self.check_ffmpeg():
            messagebox.showerror(
                "FFmpeg Not Found",
                "FFmpeg is not installed or not in PATH.\n\n"
                "Please install FFmpeg:\n"
                "- Windows: Download from ffmpeg.org\n"
                "- macOS: brew install ffmpeg\n"
                "- Linux: sudo apt install ffmpeg"
            )
            return
        
        # Ask for output file
        output_file = filedialog.asksaveasfilename(
            title="Save combined video as",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        
        if not output_file:
            return
        
        # Disable combine button
        self.combine_button.configure(state="disabled")
        self.progress_label.configure(text="Processing...")
        
        # Run in thread to avoid freezing UI
        thread = threading.Thread(
            target=self.run_ffmpeg_combine,
            args=(output_file,),
            daemon=True
        )
        thread.start()
    
    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def run_ffmpeg_combine(self, output_file):
        """Run FFmpeg to combine videos"""
        try:
            # Create a temporary file list for FFmpeg
            temp_dir = Path("/tmp/videocomb")
            temp_dir.mkdir(exist_ok=True)
            list_file = temp_dir / "filelist.txt"
            
            # Write file list in FFmpeg concat format
            with open(list_file, 'w') as f:
                for video_file in self.video_files:
                    # Escape single quotes and wrap path in quotes
                    safe_path = video_file.filepath.replace("'", "'\\''")
                    f.write(f"file '{safe_path}'\n")
            
            # Run FFmpeg concat
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_file),
                "-c", "copy",
                "-y",  # Overwrite output file
                output_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            # Clean up temp file
            list_file.unlink(missing_ok=True)
            
            # Update UI in main thread
            self.after(0, self.on_combine_complete, result.returncode == 0, output_file)
            
        except Exception as e:
            self.after(0, self.on_combine_error, str(e))
    
    def on_combine_complete(self, success, output_file):
        """Handle completion of video combination"""
        self.combine_button.configure(state="normal")
        self.progress_label.configure(text="")
        
        if success:
            messagebox.showinfo(
                "Success",
                f"Videos combined successfully!\n\nOutput: {output_file}"
            )
        else:
            messagebox.showerror(
                "Error",
                "Failed to combine videos. Please check that all videos have "
                "compatible formats and codecs."
            )
    
    def on_combine_error(self, error_msg):
        """Handle error during video combination"""
        self.combine_button.configure(state="normal")
        self.progress_label.configure(text="")
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}")


def main():
    """Main entry point"""
    app = VideoCombApp()
    app.mainloop()


if __name__ == "__main__":
    main()
