import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy.editor import VideoFileClip
import numpy as np
from PIL import Image

def resize_image(image, newsize):
    return np.array(Image.fromarray(image).resize(newsize, resample=Image.BILINEAR))

def convert_mp4_to_gif(input_path, output_path, start_time=0, duration=None, fps=10, scale=0.5):
    try:
        video = VideoFileClip(input_path)
        if duration:
            video = video.subclip(start_time, start_time + duration)
        else:
            video = video.subclip(start_time)
        
        # Custom resize function
        new_width = int(video.w * scale)
        new_height = int(video.h * scale)
        resized_video = video.fl_image(lambda image: resize_image(image, (new_width, new_height)))
        
        resized_video.write_gif(output_path, fps=fps)
        video.close()
        resized_video.close()
        return True
    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")
        return False

class GUIApp:
    def __init__(self, master):
        self.master = master
        master.title("MP4 to GIF Converter - Neospaces")
        master.geometry("600x400")

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()

        # Input selection
        tk.Label(master, text="Input:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(master, textvariable=self.input_path, width=50).grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        tk.Button(master, text="Browse File", command=self.browse_input_file).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(master, text="Browse Folder", command=self.browse_input_folder).grid(row=1, column=3, padx=5, pady=5)

        # Output selection
        tk.Label(master, text="Output:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(master, textvariable=self.output_path, width=50).grid(row=2, column=1, columnspan=2, padx=5, pady=5)
        tk.Button(master, text="Browse", command=self.browse_output).grid(row=2, column=3, padx=5, pady=5)

        # Conversion parameters
        tk.Label(master, text="Start Time (s):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.start_time = tk.Entry(master, width=10)
        self.start_time.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.start_time.insert(0, "0")

        tk.Label(master, text="Duration (s):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.duration = tk.Entry(master, width=10)
        self.duration.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        tk.Label(master, text="FPS:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.fps = tk.Entry(master, width=10)
        self.fps.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        self.fps.insert(0, "10")

        tk.Label(master, text="Scale:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.scale = tk.Entry(master, width=10)
        self.scale.grid(row=6, column=1, sticky="w", padx=5, pady=5)
        self.scale.insert(0, "0.5")

        # Convert button
        tk.Button(master, text="Convert", command=self.start_conversion).grid(row=7, column=1, pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(master, length=300, mode='determinate')
        self.progress.grid(row=8, column=0, columnspan=4, padx=5, pady=5)

    def browse_input_file(self):
        file = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if file:
            self.input_path.set(file)

    def browse_input_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_path.set(folder)

    def browse_output(self):
        if os.path.isdir(self.input_path.get()):
            folder = filedialog.askdirectory()
            if folder:
                self.output_path.set(folder)
        else:
            file = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif")])
            if file:
                self.output_path.set(file)

    def start_conversion(self):
        input_path = self.input_path.get()
        output_path = self.output_path.get()
        
        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select both input and output paths.")
            return

        try:
            start_time = float(self.start_time.get())
            duration = float(self.duration.get()) if self.duration.get() else None
            fps = int(self.fps.get())
            scale = float(self.scale.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid parameter values. Please enter numbers.")
            return

        if os.path.isfile(input_path):
            # Single file conversion
            self.progress['value'] = 0
            self.master.update_idletasks()
            if convert_mp4_to_gif(input_path, output_path, start_time, duration, fps, scale):
                self.progress['value'] = 100
                self.master.update_idletasks()
                messagebox.showinfo("Conversion Complete", "File converted successfully!")
            else:
                messagebox.showerror("Error", "Failed to convert the file.")
        elif os.path.isdir(input_path):
            # Batch conversion
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            
            mp4_files = [f for f in os.listdir(input_path) if f.endswith('.mp4')]
            total_files = len(mp4_files)
            converted = 0
            failed = 0

            for i, filename in enumerate(mp4_files):
                input_file = os.path.join(input_path, filename)
                output_file = os.path.join(output_path, f"{os.path.splitext(filename)[0]}.gif")
                
                if convert_mp4_to_gif(input_file, output_file, start_time, duration, fps, scale):
                    converted += 1
                else:
                    failed += 1
                
                self.progress['value'] = (i + 1) / total_files * 100
                self.master.update_idletasks()

            messagebox.showinfo("Conversion Complete", 
                                f"Converted: {converted}\nFailed: {failed}")
        else:
            messagebox.showerror("Error", "Invalid input path.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()