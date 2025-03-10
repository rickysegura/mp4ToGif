import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy.editor import VideoFileClip
import numpy as np
from PIL import Image
import threading
from functools import partial

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

class ModernGUIApp:
    def __init__(self, master):
        self.master = master
        master.title("MP4 to GIF Converter - Neospaces")
        master.geometry("650x500")
        master.configure(bg="#f0f0f0")
        
        # Set styles
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#3498db")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        
        # Create main frame
        main_frame = ttk.Frame(master, padding="20 20 20 20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.conversion_active = False
        
        # Header
        header_label = ttk.Label(main_frame, text="MP4 to GIF Converter", style="Header.TLabel")
        header_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Input section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10 10 10 10")
        file_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Input:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="File", command=self.browse_input_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Folder", command=self.browse_input_folder).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(file_frame, text="Output:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Parameters section
        param_frame = ttk.LabelFrame(main_frame, text="Conversion Settings", padding="10 10 10 10")
        param_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 15))
        param_frame.columnconfigure(1, weight=1)
        param_frame.columnconfigure(3, weight=1)
        
        # First column
        ttk.Label(param_frame, text="Start Time (s):").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.start_time = ttk.Entry(param_frame, width=10)
        self.start_time.grid(row=0, column=1, sticky="w", padx=5, pady=8)
        self.start_time.insert(0, "0")
        
        ttk.Label(param_frame, text="Duration (s):").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        self.duration = ttk.Entry(param_frame, width=10)
        self.duration.grid(row=1, column=1, sticky="w", padx=5, pady=8)
        
        # Second column
        ttk.Label(param_frame, text="FPS:").grid(row=0, column=2, sticky="w", padx=5, pady=8)
        self.fps = ttk.Entry(param_frame, width=10)
        self.fps.grid(row=0, column=3, sticky="w", padx=5, pady=8)
        self.fps.insert(0, "10")
        
        ttk.Label(param_frame, text="Scale:").grid(row=1, column=2, sticky="w", padx=5, pady=8)
        self.scale = ttk.Entry(param_frame, width=10)
        self.scale.grid(row=1, column=3, sticky="w", padx=5, pady=8)
        self.scale.insert(0, "0.5")
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        self.convert_button = ttk.Button(action_frame, text="Convert", command=self.start_conversion)
        self.convert_button.pack(pady=10)
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=5)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky="w", padx=5)
        
    def browse_input_file(self):
        file = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All Video Files", "*.mp4 *.avi *.mov *.mkv")])
        if file:
            self.input_path.set(file)
            # Auto-generate output path
            if not self.output_path.get():
                output = os.path.splitext(file)[0] + ".gif"
                self.output_path.set(output)

    def browse_input_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_path.set(folder)
            # Clear output path if it's a file path
            if self.output_path.get() and not os.path.isdir(self.output_path.get()):
                self.output_path.set("")

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