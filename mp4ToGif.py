import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy.editor import VideoFileClip
import numpy as np
from PIL import Image
import threading
from functools import partial
import math

def resize_image(image, newsize):
    # Use direct PIL resize for better performance
    return np.array(Image.fromarray(image).resize(newsize, resample=Image.LANCZOS))

def convert_mp4_to_gif(input_path, output_path, start_time=0, duration=None, fps=10, scale=0.5, progress_callback=None):
    try:
        # Load video with reduced IO operations
        video = VideoFileClip(input_path, audio=False)
        
        # Apply subclip
        if duration:
            video = video.subclip(start_time, start_time + duration)
        else:
            video = video.subclip(start_time)
        
        # Calculate new dimensions once
        new_width = int(video.w * scale)
        new_height = int(video.h * scale)
        
        # Create resize function with fixed dimensions
        resize_func = partial(resize_image, newsize=(new_width, new_height))
        resized_video = video.fl_image(resize_func)
        
        # Set optimal gif parameters
        resized_video.write_gif(
            output_path,
            fps=fps,
            opt='wu',  # Use Wu quantization for better quality/size ratio
            program='ffmpeg',
            logger=None  # Disable logger for better performance
        )
        
        # Clean up resources
        video.close()
        resized_video.close()
        
        if progress_callback:
            progress_callback(100)
        return True
    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")
        if progress_callback:
            progress_callback(-1)
        return False

# Create a tooltip class
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create a toplevel window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Helvetica", "9", "normal"), padx=5, pady=2)
        label.pack(ipadx=1)
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class HelpDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("MP4 to GIF Converter Help")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog on the parent window
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = 600
        dialog_height = 400
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Add a notebook for tabbed help sections
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Time inputs tab
        time_frame = ttk.Frame(notebook, padding=10)
        notebook.add(time_frame, text="Time Inputs")
        
        time_help = tk.Text(time_frame, wrap=tk.WORD, height=15, width=60)
        time_help.pack(fill=tk.BOTH, expand=True)
        time_help.insert(tk.END, """
Time Input Guide:

Start Time:
- Enter a value in seconds to start the GIF at a specific point in the video
- Examples: 
  • 30 = Start at 30 seconds
  • 60 = Start at 1 minute
  • 90 = Start at 1 minute, 30 seconds
  • 120 = Start at 2 minutes

Duration:
- Enter how long you want the GIF to be (in seconds)
- Leave empty to use the entire video from the start time
- Examples:
  • 5 = Create a 5-second GIF
  • 10 = Create a 10-second GIF
  • 30 = Create a 30-second GIF

Time Conversion Reference:
• 60 seconds = 1 minute
• 120 seconds = 2 minutes
• 180 seconds = 3 minutes
• 300 seconds = 5 minutes
        """)
        time_help.config(state=tk.DISABLED)
        
        # Parameters tab
        param_frame = ttk.Frame(notebook, padding=10)
        notebook.add(param_frame, text="Parameters")
        
        param_help = tk.Text(param_frame, wrap=tk.WORD, height=15, width=60)
        param_help.pack(fill=tk.BOTH, expand=True)
        param_help.insert(tk.END, """
Parameter Guide:

FPS (Frames Per Second):
- Controls the smoothness of the animation
- Higher values = smoother animation but larger file size
- Recommended values: 10-15 for most cases
- For very smooth animation: 20-24

Scale:
- Resizes the output GIF relative to the original video size
- Values between 0 and 1
- Examples:
  • 0.5 = Half the original size (recommended)
  • 0.25 = Quarter of the original size
  • 1.0 = Original size (will create a large file)
        """)
        param_help.config(state=tk.DISABLED)
        
        # File size tab
        size_frame = ttk.Frame(notebook, padding=10)
        notebook.add(size_frame, text="File Size")
        
        size_help = tk.Text(size_frame, wrap=tk.WORD, height=15, width=60)
        size_help.pack(fill=tk.BOTH, expand=True)
        size_help.insert(tk.END, """
File Size Considerations:

GIF file size depends on several factors:
- Duration: Longer GIFs = larger files
- FPS: Higher frame rates = larger files
- Scale: Larger dimensions = larger files
- Content: Complex scenes with lots of motion = larger files

Tips to reduce file size:
- Decrease the FPS (8-10 is often sufficient)
- Reduce the scale (try 0.3-0.5)
- Keep the duration short (under 10 seconds if possible)
- Choose scenes with less movement/complexity
        """)
        size_help.config(state=tk.DISABLED)
        
        # Close button
        close_button = ttk.Button(self.dialog, text="Close", command=self.dialog.destroy)
        close_button.pack(pady=10)

class ModernGUIApp:
    def __init__(self, master):
        self.master = master
        master.title("MP4 to GIF Converter - Neospaces")
        
        # Make window start maximized (full screen)
        w, h = master.winfo_screenwidth(), master.winfo_screenheight()
        master.geometry(f"{w}x{h}+0+0")
        master.state('zoomed')  # Windows
        
        # Fallback to reasonable size if maximizing doesn't work
        master.minsize(650, 600)
        
        master.configure(bg="#f0f0f0")
        
        # Ensure window properly resizes all widgets
        master.pack_propagate(False)
        master.grid_propagate(False)
        
        # Set styles
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#3498db")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))  # Bigger header
        self.style.configure("Example.TLabel", font=("Helvetica", 9, "italic"), foreground="#666666")
        self.style.configure("Help.TButton", font=("Helvetica", 8))
        
        # Create a canvas with scrollbar for scrolling
        self.canvas = tk.Canvas(master, bg="#f0f0f0", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create main frame inside canvas
        main_frame = ttk.Frame(self.canvas, padding="20 20 20 20", style="TFrame")
        
        # Configure main frame to center content
        main_frame.columnconfigure(0, weight=1)  # Left padding column
        main_frame.columnconfigure(1, weight=0)  # Content column
        main_frame.columnconfigure(2, weight=1)  # Right padding column
        
        # Main content frame (centered)
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=0, column=1, sticky="n")
        
        # Add main frame to canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=main_frame, anchor="nw", width=w)
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        main_frame.bind("<Configure>", configure_scroll_region)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mousewheel for different platforms
        if master.tk.call('tk', 'windowingsystem') == 'win32':
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        else:
            self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
            self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.conversion_active = False
        self.video_info = {"duration": 0, "width": 0, "height": 0}
        
        # Header
        header_frame = ttk.Frame(content_frame)
        header_frame.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        header_label = ttk.Label(header_frame, text="MP4 to GIF Converter", style="Header.TLabel")
        header_label.pack(side=tk.LEFT)
        
        # Help button
        help_button = ttk.Button(header_frame, text="?", width=3, 
                               command=lambda: HelpDialog(self.master))
        help_button.pack(side=tk.LEFT, padx=(10, 0))
        ToolTip(help_button, "Open help documentation")
        
        # Input section
        file_frame = ttk.LabelFrame(content_frame, text="File Selection", padding="10 10 10 10")
        file_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Input:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.input_entry = ttk.Entry(file_frame, textvariable=self.input_path, width=50)
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ToolTip(self.input_entry, "Path to the input MP4 file or folder containing video files")
        
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=0, column=2, padx=5)
        
        self.file_btn = ttk.Button(button_frame, text="File", command=self.browse_input_file)
        self.file_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(self.file_btn, "Select a single video file to convert")
        
        self.folder_btn = ttk.Button(button_frame, text="Folder", command=self.browse_input_folder)
        self.folder_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(self.folder_btn, "Select a folder with multiple video files for batch conversion")
        
        ttk.Label(file_frame, text="Output:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.output_entry = ttk.Entry(file_frame, textvariable=self.output_path, width=50)
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ToolTip(self.output_entry, "Path where the GIF file(s) will be saved")
        
        self.output_btn = ttk.Button(file_frame, text="Browse", command=self.browse_output)
        self.output_btn.grid(row=1, column=2, padx=5, pady=5)
        ToolTip(self.output_btn, "Select the output location for your GIF file(s)")
        
        # Parameters section
        param_frame = ttk.LabelFrame(content_frame, text="Conversion Settings", padding="10 10 10 10")
        param_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 15))
        param_frame.columnconfigure(1, weight=1)
        param_frame.columnconfigure(3, weight=1)
        
        # First column - Time inputs
        time_label_frame = ttk.Frame(param_frame)
        time_label_frame.grid(row=0, column=0, sticky="w", padx=5, pady=8)
        
        ttk.Label(time_label_frame, text="Start Time (s):").pack(anchor="w")
        
        self.start_time = ttk.Entry(param_frame, width=10)
        self.start_time.grid(row=0, column=1, sticky="w", padx=5, pady=8)
        self.start_time.insert(0, "0")
        ToolTip(self.start_time, "Enter the starting point in seconds (e.g., 30 for 30 seconds into the video, 90 for 1:30)")
        
        # Example label for start time (with better space utilization)
        start_example_frame = ttk.Frame(param_frame)
        start_example_frame.grid(row=0, column=2, columnspan=2, sticky="w", padx=5, pady=8)
        ttk.Label(start_example_frame, text="← seconds from beginning", 
                style="Example.TLabel").pack(anchor="w")
        ttk.Label(start_example_frame, text="   Examples: 60s = 1min, 90s = 1:30", 
                style="Example.TLabel").pack(anchor="w")
        
        ttk.Label(param_frame, text="Duration (s):").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        self.duration = ttk.Entry(param_frame, width=10)
        self.duration.grid(row=1, column=1, sticky="w", padx=5, pady=8)
        ToolTip(self.duration, "Enter the length of the GIF in seconds (e.g., 5 for 5 seconds). Leave empty to use the entire video from the start time")
        
        # Example label for duration (with better space utilization)
        duration_example_frame = ttk.Frame(param_frame)
        duration_example_frame.grid(row=1, column=2, columnspan=2, sticky="w", padx=5, pady=8)
        ttk.Label(duration_example_frame, text="← leave empty for full video from start", 
                style="Example.TLabel").pack(anchor="w")
        ttk.Label(duration_example_frame, text="   Examples: 5 for 5 seconds, 10 for 10 seconds", 
                style="Example.TLabel").pack(anchor="w")
        
        # Second column - FPS and Scale
        ttk.Label(param_frame, text="FPS:").grid(row=2, column=0, sticky="w", padx=5, pady=8)
        self.fps = ttk.Entry(param_frame, width=10)
        self.fps.grid(row=2, column=1, sticky="w", padx=5, pady=8)
        self.fps.insert(0, "10")
        ToolTip(self.fps, "Frames Per Second - higher values give smoother animations but larger file sizes")
        
        # Example label for FPS
        ttk.Label(param_frame, text="← 10-15 recommended (higher = smoother but larger)", 
                style="Example.TLabel").grid(row=2, column=2, sticky="w", padx=5, pady=8)
        
        ttk.Label(param_frame, text="Scale:").grid(row=3, column=0, sticky="w", padx=5, pady=8)
        self.scale = ttk.Entry(param_frame, width=10)
        self.scale.grid(row=3, column=1, sticky="w", padx=5, pady=8)
        self.scale.insert(0, "0.5")
        ToolTip(self.scale, "Resize factor (0.5 = half size, 1.0 = original size). Lower values reduce file size")
        
        # Example label for scale
        ttk.Label(param_frame, text="← 0.5 = half size, 0.25 = quarter size", 
                style="Example.TLabel").grid(row=3, column=2, sticky="w", padx=5, pady=8)
        
        # File size estimation
        size_frame = ttk.LabelFrame(content_frame, text="Output Estimation", padding="10 10 10 10")
        size_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 15))
        size_frame.columnconfigure(1, weight=1)
        
        ttk.Label(size_frame, text="Estimated File Size:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.est_size_var = tk.StringVar(value="Select a file to see estimate")
        self.est_size_label = ttk.Label(size_frame, textvariable=self.est_size_var)
        self.est_size_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(size_frame, text="Video Info:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.video_info_var = tk.StringVar(value="No video loaded")
        self.video_info_label = ttk.Label(size_frame, textvariable=self.video_info_var)
        self.video_info_label.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Recalculate button for size estimation
        ttk.Button(size_frame, text="Recalculate", 
                 command=self.update_size_estimation).grid(row=0, column=2, rowspan=2, padx=5, pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(content_frame)
        action_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        # Convert button style
        self.style.configure("Convert.TButton", font=("Helvetica", 12, "bold"), padding=10)
        
        self.convert_button = ttk.Button(action_frame, text="Convert", 
                                      command=self.start_conversion, 
                                      style="Convert.TButton", 
                                      width=20)  # Make button wider
        self.convert_button.pack(pady=10)
        ToolTip(self.convert_button, "Start the conversion process with the current settings")
        
        # Progress section
        progress_frame = ttk.Frame(content_frame)
        progress_frame.grid(row=5, column=0, columnspan=4, sticky="ew", pady=5)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky="w", padx=5)
        
        # Add extra space at the bottom to ensure everything is visible when scrolling
        ttk.Frame(content_frame, height=20).grid(row=6, column=0, columnspan=4)
        
        # Bind events for calculating file size
        self.fps.bind("<KeyRelease>", lambda e: self.update_size_estimation())
        self.scale.bind("<KeyRelease>", lambda e: self.update_size_estimation())
        self.duration.bind("<KeyRelease>", lambda e: self.update_size_estimation())
    
    def get_video_info(self, file_path):
        """Get video information for size estimation"""
        try:
            if not os.path.isfile(file_path):
                return
                
            video = VideoFileClip(file_path, audio=False)
            self.video_info = {
                "duration": video.duration,
                "width": video.w,
                "height": video.h,
                "fps": video.fps
            }
            video.close()
            
                # Update video info display
            info_text = f"Duration: {self.format_time(self.video_info['duration'])}, " \
                      f"Resolution: {self.video_info['width']}x{self.video_info['height']}, " \
                      f"FPS: {self.video_info['fps']:.1f}"
            self.video_info_var.set(info_text)
            
            # Make sure the window recalculates its scroll region
            self.master.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Update size estimation
            self.update_size_estimation()
            
        except Exception as e:
            self.video_info_var.set(f"Error loading video info: {str(e)}")
    
    def format_time(self, seconds):
        """Format seconds as MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"
    
    def update_size_estimation(self):
        """Update the file size estimation based on current parameters"""
        try:
            if not self.input_path.get() or not os.path.isfile(self.input_path.get()):
                self.est_size_var.set("Select a file to see estimate")
                return
            
            # Get parameters
            try:
                fps = float(self.fps.get())
                scale = float(self.scale.get())
                duration_input = self.duration.get()
                duration = float(duration_input) if duration_input else self.video_info.get("duration", 0)
            except (ValueError, TypeError):
                self.est_size_var.set("Invalid parameter values")
                return
            
            if duration <= 0:
                duration = self.video_info.get("duration", 0)
            
            # Calculate size
            width = int(self.video_info.get("width", 0) * scale)
            height = int(self.video_info.get("height", 0) * scale)
            
            if width == 0 or height == 0:
                self.est_size_var.set("Unable to estimate (video info missing)")
                return
            
            # Rough GIF size estimation
            # This is a simplistic model - actual results will vary
            pixels_per_frame = width * height
            frames = fps * duration
            bytes_per_pixel = 0.7  # Approximate for GIF with moderately complex content
            
            # Apply compression factor based on content complexity
            # Lower scale and FPS improves compression
            compression_factor = 0.7 * (1 - 0.3 * (1 - scale)) * (1 - 0.2 * (1 - min(fps, 30) / 30))
            
            estimated_size_bytes = pixels_per_frame * frames * bytes_per_pixel * compression_factor
            
            # Convert to appropriate unit
            if estimated_size_bytes < 1024:
                size_text = f"{estimated_size_bytes:.1f} bytes"
            elif estimated_size_bytes < 1024 * 1024:
                size_text = f"{estimated_size_bytes / 1024:.1f} KB"
            else:
                size_text = f"{estimated_size_bytes / (1024 * 1024):.1f} MB"
            
            duration_text = f"for {duration:.1f}s"
            if not duration_input:
                duration_text += " (full video)"
            
            self.est_size_var.set(f"~{size_text} {duration_text}")
            
            # Add warning for large files
            if estimated_size_bytes > 10 * 1024 * 1024:
                self.est_size_var.set(f"{self.est_size_var.get()} - WARNING: Very large file!")
            
        except Exception as e:
            self.est_size_var.set(f"Error calculating: {str(e)}")
    
    def browse_input_file(self):
        file = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All Video Files", "*.mp4 *.avi *.mov *.mkv")])
        if file:
            self.input_path.set(file)
            # Auto-generate output path
            if not self.output_path.get():
                output = os.path.splitext(file)[0] + ".gif"
                self.output_path.set(output)
            # Get video info for estimation
            self.get_video_info(file)

    def browse_input_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_path.set(folder)
            # Clear output path if it's a file path
            if self.output_path.get() and not os.path.isdir(self.output_path.get()):
                self.output_path.set("")
            # Reset video info
            self.video_info_var.set("Batch mode - size varies by file")
            self.est_size_var.set("Varies by file")

    def browse_output(self):
        input_path = self.input_path.get()
        if os.path.isdir(input_path):
            folder = filedialog.askdirectory()
            if folder:
                self.output_path.set(folder)
        else:
            default_name = os.path.splitext(os.path.basename(input_path))[0] + ".gif" if input_path else ""
            file = filedialog.asksaveasfilename(
                defaultextension=".gif",
                filetypes=[("GIF files", "*.gif")],
                initialfile=default_name
            )
            if file:
                self.output_path.set(file)

    def update_progress(self, value, message=None):
        """Update progress bar and status message"""
        self.master.after(0, lambda: self._update_progress_ui(value, message))

    def _update_progress_ui(self, value, message):
        if value < 0:  # Error
            self.progress['value'] = 0
            self.status_var.set("Error: Conversion failed")
            self.convert_button["state"] = "normal"
            self.conversion_active = False
        elif value >= 100:  # Complete
            self.progress['value'] = 100
            self.status_var.set(message or "Conversion complete!")
            self.convert_button["state"] = "normal"
            self.conversion_active = False
        else:  # In progress
            self.progress['value'] = value
            self.status_var.set(message or f"Converting... {value}%")
        
        # Ensure progress bar is visible
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)  # Scroll to bottom
            
    def validate_inputs(self):
        """Validate all input parameters"""
        input_path = self.input_path.get()
        output_path = self.output_path.get()
        
        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select both input and output paths.")
            return False
            
        try:
            start_time = float(self.start_time.get())
            duration = float(self.duration.get()) if self.duration.get() else None
            fps = int(self.fps.get())
            scale = float(self.scale.get())
            
            if start_time < 0:
                raise ValueError("Start time must be positive")
            if duration is not None and duration <= 0:
                raise ValueError("Duration must be positive")
            if fps <= 0:
                raise ValueError("FPS must be positive")
            if scale <= 0 or scale > 1:
                raise ValueError("Scale must be between 0 and 1")
                
            return {
                "start_time": start_time,
                "duration": duration,
                "fps": fps,
                "scale": scale
            }
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid parameter values: {str(e)}")
            return False

    def convert_single_file(self, input_path, output_path, params):
        """Convert a single file in a separate thread"""
        def run_conversion():
            success = convert_mp4_to_gif(
                input_path, 
                output_path, 
                params["start_time"], 
                params["duration"], 
                params["fps"], 
                params["scale"],
                progress_callback=lambda v: self.update_progress(v)
            )
            
            if success:
                self.update_progress(100, "File converted successfully!")
                # Show notification only if app is not in foreground
                if not self.master.focus_displayof():
                    messagebox.showinfo("Conversion Complete", "File converted successfully!")
            else:
                self.update_progress(-1)
        
        # Start conversion thread
        conversion_thread = threading.Thread(target=run_conversion)
        conversion_thread.daemon = True
        conversion_thread.start()

    def convert_batch(self, input_dir, output_dir, params):
        """Convert multiple files in a separate thread"""
        def run_batch_conversion():
            mp4_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
            total_files = len(mp4_files)
            
            if total_files == 0:
                self.update_progress(-1, "No video files found in the input directory")
                return
                
            # Create output directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            converted = 0
            failed = 0
            
            for i, filename in enumerate(mp4_files):
                input_file = os.path.join(input_dir, filename)
                output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.gif")
                
                self.update_progress(
                    int(i / total_files * 100), 
                    f"Converting {i+1}/{total_files}: {filename}"
                )
                
                success = convert_mp4_to_gif(
                    input_file, 
                    output_file, 
                    params["start_time"], 
                    params["duration"], 
                    params["fps"], 
                    params["scale"]
                )
                
                if success:
                    converted += 1
                else:
                    failed += 1
            
            # Final update
            self.update_progress(
                100, 
                f"Converted: {converted}, Failed: {failed}"
            )
            
            # Show notification only if app is not in foreground
            if not self.master.focus_displayof():
                messagebox.showinfo("Batch Conversion Complete", 
                                   f"Converted: {converted}\nFailed: {failed}")
        
        # Start conversion thread
        conversion_thread = threading.Thread(target=run_batch_conversion)
        conversion_thread.daemon = True
        conversion_thread.start()

    def start_conversion(self):
        # Prevent multiple conversions
        if self.conversion_active:
            return
            
        # Validate inputs
        params = self.validate_inputs()
        if not params:
            return
            
        input_path = self.input_path.get()
        output_path = self.output_path.get()
        
        # Reset progress bar
        self.progress['value'] = 0
        self.status_var.set("Starting conversion...")
        self.conversion_active = True
        self.convert_button["state"] = "disabled"
        
        if os.path.isfile(input_path):
            # Single file conversion
            self.convert_single_file(input_path, output_path, params)
        elif os.path.isdir(input_path):
            # Batch conversion
            self.convert_batch(input_path, output_path, params)
        else:
            messagebox.showerror("Error", "Invalid input path.")
            self.convert_button["state"] = "normal"
            self.conversion_active = False

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernGUIApp(root)
    root.mainloop()