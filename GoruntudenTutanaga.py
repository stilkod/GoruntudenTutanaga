import tkinter as tk
from tkinter import filedialog, messagebox
import vlc
from docx import Document
from docx.shared import Inches
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import os, time
from PIL import Image, ImageTk, ImageDraw, ImageFont

def format_time(seconds):
    """Saniye cinsinden alınan zamanı hh:mm:ss ya da mm:ss formatında döndürür."""
    seconds = int(seconds)
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    else:
        return f"{mins:02d}:{secs:02d}"

class VideoAnnotationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Görüntü İzleme ve Tutanak Uygulaması")
        self.geometry("1024x768")
        
        # VLC nesnesi ve medya oynatıcı oluşturuluyor.
        vlc_options = [
            '--file-caching=5000',
            '--network-caching=5000',
            '--clock-jitter=0',
            '--clock-synchro=0',
            '--avcodec-hw=none',  # Disable hardware acceleration
            '--no-drop-late-frames',
            '--no-skip-frames',
            '--sout-mux-caching=5000',
            '--avcodec-threads=4',
            '--avcodec-fast',
            '--no-video-title-show',
            '--vout=vdummy'  # Use software-based video output
        ]
        self.vlc_instance = vlc.Instance(vlc_options)
        self.player = self.vlc_instance.media_player_new()
        
        # Video görüntüsünün gösterileceği alan
        self.video_panel = tk.Frame(self, bg="white")
        self.video_panel.pack(fill=tk.BOTH, expand=True)
        

        # Sürükleme slider için ayar
        self.slider_dragging = False

        # Kaydedilecek tespitlerin listesi (her biri bir sözlük)
        self.event_list = []
        
        # Açılan video dosyasının bilgisini tutan değişken.
        self.current_video = None
        
        # Alt kontrol alanı
        controls_frame = tk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.open_button = tk.Button(controls_frame, text="Video Aç", command=self.open_video)
        self.open_button.pack(side=tk.LEFT, padx=2)
        self.play_button = tk.Button(controls_frame, text="Oynat", command=self.play_video)
        self.play_button.pack(side=tk.LEFT, padx=2)
        self.pause_button = tk.Button(controls_frame, text="Duraklat", command=self.pause_video)
        self.pause_button.pack(side=tk.LEFT, padx=2)
        self.skip_backward_button = tk.Button(controls_frame, text="Geri Sar", command=self.skip_backward)
        self.skip_backward_button.pack(side=tk.LEFT, padx=2)
        self.skip_forward_button = tk.Button(controls_frame, text="İleri Sar", command=self.skip_forward)
        self.skip_forward_button.pack(side=tk.LEFT, padx=2)
        
        tk.Label(controls_frame, text="Tespit Edilen Durum:").pack(side=tk.LEFT, padx=5)
        self.event_entry = tk.Entry(controls_frame, width=50)
        self.event_entry.pack(side=tk.LEFT, padx=2)
        self.event_entry.bind("<Return>", lambda event: self.add_text_event())
        
        tk.Button(controls_frame, text="Tespit Ekle", command=self.add_text_event).pack(side=tk.LEFT, padx=2)
        tk.Button(controls_frame, text="İşaretçi Ekle", command=self.add_pointer_event).pack(side=tk.LEFT, padx=2)
        tk.Button(controls_frame, text="Rapor Oluştur", command=self.create_report).pack(side=tk.LEFT, padx=2)
        tk.Button(controls_frame, text="Tespit Sil", command=self.delete_event).pack(side=tk.LEFT, padx=2)
        
        self.events_listbox = tk.Listbox(self, height=8)
        self.events_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        # Zaman araç çubuğu
        self.time_slider = tk.Scale(self, from_=0, to=1000, orient=tk.HORIZONTAL)
        self.time_slider.pack(fill=tk.X, padx=5, pady=5)

        self.time_slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.time_slider.bind("<ButtonRelease-1>", self.on_slider_release)

               
        self.time_label = tk.Label(self, text="00:00:00 / 00:00:00")
        self.time_label.pack(pady=5)
        
        self.bind("<Configure>", self.set_video_panel)
        self.is_playing = False  # Video oynatma durumunu takip eden değişken
        self.video_loaded = False  # Video yüklendi mi kontrolü
        self.player_initialized = False  # Player initialized kontrolü
        self.bind("<space>", self.toggle_play_pause)
        self.bind("<Right>", self.on_right_arrow)
        self.bind("<Left>", self.on_left_arrow)
        self.update_time()
        self.messagebox_options = {"parent": self}  # Messagebox options to center on the app window

    def on_slider_press(self, event):
        self.slider_dragging = True

    def on_slider_release(self, event):
        self.slider_dragging = False
        # Slider bırakıldığında yeni zamanı ayarla:
        slider_value = self.time_slider.get()
        video_length = self.player.get_length()
        if video_length > 0:
            new_time = slider_value * video_length // 1000  # 1000 slider max değeri
            self.player.set_time(new_time)

    def set_video_panel(self, event=None):
        if os.name == "nt":
            self.player.set_hwnd(self.video_panel.winfo_id())
        elif os.uname().sysname == "Darwin":
            self.player.set_nsobject(self.video_panel.winfo_id())
        else:
            self.player.set_xwindow(self.video_panel.winfo_id())
        if self.video_loaded and not self.player_initialized:
            self.player.set_hwnd(self.video_panel.winfo_id())  # Ensure the video panel is set
            self.player_initialized = True

    def open_video(self):
        video_path = filedialog.askopenfilename(
            title="Video Seç", 
            filetypes=[("Video Dosyaları", "*.mp4 *.avi *.mkv"), ("Tüm Dosyalar", "*.*")]
        )
        if video_path:
            self.current_video = video_path  # Açılan video bilgisini sakla.
            media = self.vlc_instance.media_new(video_path)
            self.player.set_media(media)
            self.video_loaded = True
            self.play_video()
            self.set_video_panel()

    def play_video(self):
        if self.video_loaded:
            if not self.player_initialized:
                self.set_video_panel()
            self.player.play()
            self.player.set_rate(1.0)  # Normal hızda oynat
            self.is_playing = True
            self.update_time()
        else:
            messagebox.showwarning("Uyarı", "Lütfen önce bir video dosyası açın.", **self.messagebox_options)

    def pause_video(self):
        self.player.pause()
        self.is_playing = False

    def skip_forward(self):
        current_time = self.player.get_time()
        length = self.player.get_length()
        if current_time != -1 and length != -1:
            new_time = min(current_time + 500, length)
            self.player.set_time(new_time)
            if new_time >= length:
                self.is_playing = False
            self.update_time()

    def skip_backward(self):
        current_time = self.player.get_time()
        if current_time != -1:
            new_time = max(current_time - 500, 0)
            self.player.set_time(new_time)
            self.is_playing = True
            self.update_time()

    def add_text_event(self):
        current_time_ms = self.player.get_time()
        if current_time_ms == -1:
            messagebox.showerror("Hata", "Video oynatılmadı veya zaman bilgisi alınamadı!", **self.messagebox_options)
            return
        current_time_sec = current_time_ms / 1000
        event_text = self.event_entry.get().strip()
        if not event_text:
            messagebox.showwarning("Uyarı", "Lütfen tespit edilen durumu girin.", **self.messagebox_options)
            return
        
        timestamp = time.time()
        screenshot_filename = f"ekrangoruntusu_{timestamp:.2f}.png"
        result = self.player.video_take_snapshot(0, screenshot_filename, 0, 0)
        if result != 0 or not os.path.exists(screenshot_filename):
            messagebox.showerror("Hata", "Ekran görüntüsü alınamadı!", **self.messagebox_options)
            return
        
        event_info = {
            "type": "screenshot",
            "time": current_time_sec,
            "description": event_text,
            "image": screenshot_filename,
            "video": self.current_video
        }
        self.event_list.append(event_info)
        display_text = f"Tespit {len(self.event_list)} - Zaman: {format_time(current_time_sec)} - {event_text}"
        self.events_listbox.insert(tk.END, display_text)
        self.event_entry.delete(0, tk.END)
        messagebox.showinfo("Bilgi", "Tespit eklendi.", **self.messagebox_options)

    def add_pointer_event(self):
        was_playing = self.is_playing  # Track if the video was playing
        self.pause_video()  # Ensure the video is paused
        current_time_ms = self.player.get_time()
        if current_time_ms == -1:
            messagebox.showerror("Hata", "Video oynatılmadı veya zaman bilgisi alınamadı!", **self.messagebox_options)
            return
        current_time_sec = current_time_ms / 1000
        
        timestamp = time.time()
        screenshot_filename = f"ekrangoruntusu_{timestamp:.2f}.png"
        result = self.player.video_take_snapshot(0, screenshot_filename, 0, 0)
        if result != 0 or not os.path.exists(screenshot_filename):
            messagebox.showerror("Hata", "Ekran görüntüsü alınamadı!", **self.messagebox_options)
            return
        
        # Anotasyon penceresi açıldığında video tamamen duraklatılır.
        AnnotationWindow(self, screenshot_filename, current_time_sec, was_playing)

    def create_report(self):
        if not self.event_list:
            messagebox.showinfo("Bilgi", "Eklenmiş tespit bilgisi bulunmamaktadır.", **self.messagebox_options)
            return
        
        # Load the template document
        template_path = "RPSABLON.docx"
        if not os.path.exists(template_path):
            messagebox.showerror("Hata", "Şablon dosyası bulunamadı!", **self.messagebox_options)
            return
        
        try:
            doc = Document(template_path)
        except Exception as e:
            messagebox.showerror("Hata", f"Şablon dosyası yüklenemedi: {e}", **self.messagebox_options)
            return
        
        # Tespitleri video dosyasına göre gruplayalım.
        videos = {}
        for event in self.event_list:
            vid = event.get("video", "Bilinmeyen Video")
            video_name = os.path.basename(vid)
            videos.setdefault(video_name, []).append(event)
        
        for video_file, events in videos.items():
            doc.add_heading(f"Video: {video_file}", level=1)
            for idx, event in enumerate(events, start=1):
                doc.add_heading(f"Tespit {idx}", level=2)
                doc.add_paragraph(f"Zaman: {format_time(event['time'])}")
                if event.get("image"):
                    try:
                        doc.add_picture(event["image"], width=Inches(6))
                    except Exception as e:
                        doc.add_paragraph(f"[Resim eklenemedi: {e}]")
                if event.get("description"):
                    doc.add_paragraph(f"Açıklama: {event['description']}")
                # Add a separator line
                # doc.add_paragraph("\n" + "#Tespit sonu.#" + "\n")
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Dosyası", "*.docx")],
            title="Raporu Kaydet"
        )
        if save_path:
            try:
                doc.save(save_path)
                messagebox.showinfo("Başarılı", "Rapor başarıyla kaydedildi.", **self.messagebox_options)
            except Exception as e:
                messagebox.showerror("Hata", f"Rapor kaydedilirken hata oluştu:\n{e}", **self.messagebox_options)

    def delete_event(self):
        selected_index = self.events_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz tespiti seçin.", **self.messagebox_options)
            return
        
        selected_index = selected_index[0]
        del self.event_list[selected_index]
        self.events_listbox.delete(selected_index)
        messagebox.showinfo("Bilgi", "Tespit silindi.", **self.messagebox_options)
    
    def on_time_slider(self, value):
        if self.video_loaded:
            new_time = int(value) * self.player.get_length() // 1000
            self.player.set_time(new_time)
            self.update_time()

    def update_time(self):
        current_time_ms = self.player.get_time()
        if current_time_ms != -1:
            length_ms = self.player.get_length()
            if length_ms > 0:
                current_time_sec = current_time_ms // 1000
                length_sec = length_ms // 1000
                self.time_slider.set(current_time_ms * 1000 // length_ms)
                self.time_label.config(text=f"{format_time(current_time_sec)} / {format_time(length_sec)}")
        self.after(1000, self.update_time)

    def toggle_play_pause(self, event):
        if self.focus_get() == self.event_entry:
            return
        if self.is_playing:
            self.pause_video()
        else:
            self.play_video()

    def on_right_arrow(self, event):
        self.skip_forward()

    def on_left_arrow(self, event):
        self.skip_backward()

class AnnotationWindow(tk.Toplevel):
    def __init__(self, parent, screenshot_path, current_time_sec, was_playing):
        super().__init__(parent)
        self.parent = parent
        self.screenshot_path = screenshot_path
        self.current_time_sec = current_time_sec
        self.was_playing = was_playing  # Track if the video was playing
        self.title("İşaretçi Anotasyonu")
        
        # Pencere kapatılırsa video devam etsin.
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # PIL ile ekran görüntüsünü açıp anotasyon için kopyasını oluşturuyoruz.
        self.image = Image.open(screenshot_path)
        
        # Video panelinin boyutlarını al
        video_panel_width = self.parent.video_panel.winfo_width()
        video_panel_height = self.parent.video_panel.winfo_height()
        
        # İmajın boyutlarını kontrol et ve video paneline göre yeniden boyutlandır
        aspect_ratio = self.image.height / self.image.width
        new_width = video_panel_width
        new_height = int(new_width * aspect_ratio)
        if new_height > video_panel_height:
            new_height = video_panel_height
            new_width = int(new_height / aspect_ratio)
        self.image = self.image.resize((new_width, new_height), Image.LANCZOS)
        
        self.annotated_image = self.image.copy()
        self.draw = ImageDraw.Draw(self.annotated_image)
        
        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        self.canvas.pack()
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas_image = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        
        self.start_x = None
        self.start_y = None
        self.arrow_id = None
        self.arrow_end = None
        
        self.text_entry = None  # Initialize text_entry to None
        
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        
        tk.Button(button_frame, text="Kaydet ve Ekle", command=self.save_annotation).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Sıfırla", command=self.reset_annotations).pack(side=tk.LEFT, padx=5)
        self.messagebox_options = {"parent": self}  # Messagebox options to center on the annotation window

    def reset_annotations(self):
        self.annotated_image = self.image.copy()
        self.draw = ImageDraw.Draw(self.annotated_image)
        self.canvas.delete("all")
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas_image = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.start_x = None
        self.start_y = None
        self.arrow_id = None
        self.arrow_end = None
        self.text_entry = None

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.arrow_id = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                                  arrow=tk.LAST, fill="red", width=3)
    
    def on_mouse_drag(self, event):
        if self.arrow_id:
            self.canvas.coords(self.arrow_id, self.start_x, self.start_y, event.x, event.y)
    
    def on_button_release(self, event):
        if self.arrow_id:
            self.arrow_end = (event.x, event.y)
            # Kalıcı olarak ok çizgisini PIL resmine işle
            self.draw.line((self.start_x, self.start_y, event.x, event.y), fill="red", width=3)
            self.prompt_for_text(event.x, event.y)
    
    def prompt_for_text(self, x, y):
        if self.text_entry:
            self.text_entry.destroy()
        self.text_entry = tk.Entry(self)  # Properly initialize text_entry
        self.text_entry.place(x=x, y=y)  # Place the Entry widget at the specified coordinates
        self.text_entry.focus_set()
        self.text_entry.bind("<Return>", self.on_text_entered)
        self.text_entry.bind("<Escape>", self.cancel_text_entry)
        self.text_entry.bind("<Delete>", self.delete_arrow)
    
    def on_text_entered(self, event):
        text = self.text_entry.get().strip()
        if text:
            x, y = self.arrow_end  # Okun bitiş koordinatları
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except IOError:
                font = ImageFont.load_default()
            # textbbox, metnin sol üst noktasını ve sağ alt noktasını içeren bir tuple döndürür.
            bbox = self.draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0] + 10
            text_height = bbox[3] - bbox[1] + 10
            # Arka plan dikdörtgeni çiz: kırmızı arka plan
            self.draw.rectangle([x, y, x + text_width, y + text_height], fill="red")
            # Metni, beyaz renkle çiz.
            self.draw.text((x, y), text, fill="white", font=font)
        self.text_entry.destroy()
        self.text_entry = None
        self.update_canvas_image()
    
    def cancel_text_entry(self, event):
        if self.text_entry:
            self.text_entry.destroy()
            self.text_entry = None
            self.update_canvas_image()
    
    def delete_arrow(self, event):
        if self.arrow_id:
            self.canvas.delete(self.arrow_id)
            self.arrow_id = None
            self.arrow_end = None
        if self.text_entry:
            self.text_entry.destroy()
            self.text_entry = None
    
    def update_canvas_image(self):
        self.photo = ImageTk.PhotoImage(self.annotated_image)
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
    
    def save_annotation(self):
        annotated_filename = f"isaretedilen_{time.time():.2f}.png"
        try:
            self.annotated_image.save(annotated_filename)
        except Exception as e:
            messagebox.showerror("Hata", f"Anotasyon kaydedilemedi: {e}")
            self.destroy()
            self.parent.play_video()
            return
        
        event_info = {
            "type": "screenshot",
            "time": self.current_time_sec,
            "description": "İşaretçi ile tespit",
            "image": annotated_filename,
            "video": self.parent.current_video
        }
        self.parent.event_list.append(event_info)
        display_text = f"Tespit {len(self.parent.event_list)} - Zaman: {format_time(self.current_time_sec)} - İşaretçi ile tespit"
        self.parent.events_listbox.insert(tk.END, display_text)
        messagebox.showinfo("Bilgi", "İşaretçi tespiti eklenmiştir.")
        self.destroy()
        self.parent.play_video()
    
    def on_close(self):
        self.destroy()
        if self.was_playing:
            self.parent.play_video()
        else:
            self.parent.pause_video()  # Ensure the video remains paused

if __name__ == "__main__":
    app = VideoAnnotationApp()
    app.mainloop()