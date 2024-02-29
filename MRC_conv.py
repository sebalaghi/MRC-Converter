import os
from tkinter import Tk, Label, Button, filedialog, Frame, Checkbutton, BooleanVar, OptionMenu, StringVar, Scale, \
    HORIZONTAL, Menu, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import mrcfile
import numpy as np
import tifffile as tiff
from scipy.ndimage import gaussian_filter


class App:
    def __init__(self, root):
        self.root = root
        self.frames = None
        self.current_frame_index = 0
        self.pixel_size_nm = 1  # Default pixel size in nanometers
        root.title("Advanced MRC to TIFF Converter with Scale Bar")
        self.setup_gui()
        self.setup_menu()

    def setup_gui(self):
        self.frame = Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        Button(self.frame, text="Select MRC files", command=self.select_mrc_files).pack(side="left")
        Button(self.frame, text="Select output directory", command=self.select_output_dir).pack(side="left")

        self.resolution_var = StringVar(self.root)
        self.resolution_options = ["Full resolution", "1920x1080", "1280x720", "640x480"]
        self.resolution_var.set(self.resolution_options[0])
        OptionMenu(self.frame, self.resolution_var, *self.resolution_options).pack(side="left")

        self.save_reverse_order = BooleanVar(self.root)
        Checkbutton(self.frame, text="Reverse order", variable=self.save_reverse_order).pack(side="left")

        self.denoise_var = BooleanVar(self.root)
        Checkbutton(self.frame, text="Denoise", variable=self.denoise_var).pack(side="left")

        self.smooth_var = BooleanVar(self.root)
        Checkbutton(self.frame, text="Smooth", variable=self.smooth_var).pack(side="left")

        Button(self.frame, text="Convert", command=self.convert).pack(side="left")

    def setup_menu(self):
        menu_bar = Menu(self.root)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        about_menu = Menu(menu_bar, tearoff=0)
        about_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="About", menu=about_menu)

        self.root.config(menu=menu_bar)

    def show_about(self):
        messagebox.showinfo("About", "Designed by S. Esmael Balaghi\nhttps://github.com/sebalaghi")

    def select_mrc_files(self):
        self.mrc_filenames = filedialog.askopenfilenames(filetypes=[("MRC files", "*.mrc")])
        if self.mrc_filenames:
            self.load_mrc_frames(self.mrc_filenames[0])

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        if not self.output_dir:
            messagebox.showerror("Error", "No output directory selected.")

    def load_mrc_frames(self, mrc_filename):
        with mrcfile.open(mrc_filename, mode='r') as mrc:
            self.frames = np.array(mrc.data, dtype=np.float32)
            self.pixel_size_nm = mrc.voxel_size.x  # Assuming voxel size in x is in nm
            self.seeker = Scale(self.root, from_=0, to=len(self.frames) - 1, orient=HORIZONTAL,
                                command=self.update_frame_view)
            self.seeker.pack(fill="x", expand=True)
            self.update_frame_view(0)

    def update_frame_view(self, index):
        index = int(index)
        if self.frames is not None:
            frame = self.frames[index]
            frame = (frame - frame.min()) / (frame.max() - frame.min()) * 255
            frame = frame.astype(np.uint8)
            image = Image.fromarray(frame)
            image = self.add_scale_bar(image, self.pixel_size_nm)
            image = image.resize((500, 500), Image.Resampling.LANCZOS)
            if hasattr(self, 'image_label'):
                self.image_label.destroy()
            self.tk_image = ImageTk.PhotoImage(image)
            self.image_label = Label(self.root, image=self.tk_image)
            self.image_label.pack()

    def add_scale_bar(self, image, pixel_size_nm):
        draw = ImageDraw.Draw(image)
        scale_length_nm = 500  # Length of the scale bar in nanometers

        # Unit conversion and text formatting
        if scale_length_nm >= 1000:
            scale_length_text = f"{scale_length_nm / 1000:.1f} µm"
        else:
            scale_length_text = f"{scale_length_nm} nm"

        scale_length_pixels = int(scale_length_nm / pixel_size_nm)

        # Define scale bar and text properties
        image_width, image_height = image.size
        bar_height = 20  # Height of the scale bar
        font_size = 30  # Font size for the text
        text_offset = 5  # Space between the text and the scale bar
        background_height = font_size + 2 * text_offset  # Height of the text background

        # Positioning the scale bar and text
        bar_start = (image_width - scale_length_pixels - 20, image_height - 20 - bar_height)
        bar_end = (image_width - 20, image_height - 20)
        text_position = (bar_start[0], bar_start[1] - background_height)

        # Drawing the background for text to enhance readability
        background_start = (bar_start[0], text_position[1] - text_offset)
        background_end = (bar_end[0], bar_start[1] - text_offset)
        draw.rectangle([background_start, background_end], fill="black")

        # Drawing the scale bar
        draw.rectangle([bar_start, bar_end], fill="white")

        # Adding text above the scale bar
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        draw.text(text_position, scale_length_text, fill="white", font=font)

        return image

    def convert(self):
        if not self.mrc_filenames or not self.output_dir:
            messagebox.showwarning("Warning", "Please select MRC files and an output directory.")
            return
        for mrc_filename in self.mrc_filenames:
            self.mrc_to_tiff(mrc_filename)

    def mrc_to_tiff(self, mrc_filename):
        resolution_map = {"Full resolution": None, "1920x1080": (1920, 1080), "1280x720": (1280, 720),
                          "640x480": (640, 480)}
        resolution = resolution_map[self.resolution_var.get()]
        tiff_filename = os.path.join(self.output_dir, os.path.basename(mrc_filename).replace('.mrc', '.tiff'))

        with mrcfile.open(mrc_filename, mode='r') as mrc:
            data = np.array(mrc.data, dtype=np.float32)
            if self.save_reverse_order.get():
                data = data[::-1]
            if self.denoise_var.get():
                data = np.array([denoise_image(frame) for frame in data])
            if self.smooth_var.get():
                data = np.array([smooth_image(frame) for frame in data])
            if resolution:
                data = np.array(
                    [np.array(Image.fromarray(frame).resize(resolution, Image.Resampling.LANCZOS)) for frame in data])
            tiff.imwrite(tiff_filename, data, photometric='minisblack')


def denoise_image(data):
    return gaussian_filter(data, sigma=1)


def smooth_image(data):
    return gaussian_filter(data, sigma=2)


if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
