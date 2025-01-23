import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import csv
import json


def dersleri_csv_olarak_kaydet(dersler, dosya_adi="dersler.csv"):
    with open(dosya_adi, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Ders Kodu", "Ders Adı", "Program Çıktıları",
            "Ders Öğrenme Çıktıları", "Değerlendirme Kriterleri",
            "Tablo 1", "Tablo 2", "Notlar",              
            "Öğrenci Listesi"                            
        ])
        
        for ders_kodu, ders_verisi in dersler.items():

            writer.writerow([
                ders_kodu,
                ders_verisi["ad"],
                json.dumps(ders_verisi["program_ciktilari"]),
                json.dumps(ders_verisi["ders_ogrenme_ciktilari"]),
                json.dumps(ders_verisi["degerlendirme_kriterleri"]),
                json.dumps(ders_verisi["tablo_1"]),
                json.dumps(ders_verisi["tablo_2"]),
                json.dumps(ders_verisi["notlar"]),
                json.dumps(ders_verisi["ogrenci_listesi"])
            ])



def dersleri_csvden_yukle(dosya_adi="dersler.csv"):
    dersler = {}
    try:
        with open(dosya_adi, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                ders_kodu = row["Ders Kodu"]
                try:

                    dersler[ders_kodu] = {
                        "ad": row["Ders Adı"],
                        "program_ciktilari": json.loads(row["Program Çıktıları"] or "[]"),
                        "ders_ogrenme_ciktilari": json.loads(row["Ders Öğrenme Çıktıları"] or "[]"),
                        "degerlendirme_kriterleri": json.loads(row["Değerlendirme Kriterleri"] or "{}"),
                        "tablo_1": json.loads(row["Tablo 1"] or "[]"),
                        "tablo_2": json.loads(row["Tablo 2"] or "null"),
                        "notlar": json.loads(row["Notlar"] or "[]"),
                        "ogrenci_listesi": json.loads(row["Öğrenci Listesi"] or "[]")   
                    }
                except json.JSONDecodeError:
                    print(f"JSON çözümleme hatası: {ders_kodu} dersinde veri hatası var.")
    except FileNotFoundError:
        print("CSV dosyası bulunamadı, yeni bir dosya oluşturulacak.")
    except Exception as e:
        print(f"Yükleme hatası: {e}")
    return dersler



class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ders Çıktıları ve Değerlendirme Takip Sistemi")
        self.geometry("1000x600")

        # Ders verilerini yükle
        self.dersler = dersleri_csvden_yukle()
        self.secili_ders = None

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        self.frames = {}
        
          
        for F in (DersSecimSayfasi, DersEkleSayfasi, ProgramCiktilariSayfasi,
                  DersOgrenmeCiktilariSayfasi, DegerlendirmeKriterleriSayfasi,
                  NotlarSayfasi, OgrenciListesiSayfasi,Tablo1Sayfasi,Tablo2Sayfasi,Tablo3Sayfasi,Tablo4Sayfasi): 
            frame_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Başlangıçta DersSecimSayfasi'ni göster
        self.show_frame("DersSecimSayfasi")

        # Ders listesi güncellemesi
        self.frames["DersSecimSayfasi"].update_ders_listesi()

    def show_frame(self, page_name):
        frame = self.frames[page_name]

        # İlgili sayfaya özel yükleme işlemleri
        if page_name == "ProgramCiktilariSayfasi":
            frame.yukle()
        elif page_name == "DersOgrenmeCiktilariSayfasi":
            frame.yukle()
        elif page_name == "DegerlendirmeKriterleriSayfasi":
            frame.yukle()
        elif page_name == "NotlarSayfasi":
            frame.yukle()
        elif page_name == "OgrenciListesiSayfasi": 
            frame.yukle()
        elif page_name == "Tablo1Sayfasi": 
            frame.yukle()        
        elif page_name == "Tablo2Sayfasi": 
            frame.yukle()
        elif page_name == "Tablo3Sayfasi": 
            frame.yukle()        
        elif page_name == "Tablo4Sayfasi": 
            frame.yukle()        

        frame.tkraise()



    def on_close(self):
        dersleri_csv_olarak_kaydet(self.dersler)
        self.destroy()



class DersSecimSayfasi(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Ders Seçin veya Yeni Ders Ekleyin").pack(pady=10)

        self.ders_combobox = ttk.Combobox(self, values=[])
        self.ders_combobox.pack(pady=5)

        tk.Button(self, text="Yeni Ders Ekle",
                  command=lambda: controller.show_frame("DersEkleSayfasi")).pack(pady=5)

        # Devam Et butonu ile seçilen derse git
        tk.Button(self, text="Devam Et", command=self.dersi_sec).pack(pady=5)

    def update_ders_listesi(self):
        """
        Ders combobox'ının içeriğini günceller.
        Ders kodu – Ders Adı şeklinde gösterir.
        Örnek: "YZM 331 – Yazılım Lab I"
        """
        ders_listesi = [
            f"{kod} – {veri['ad']}"
            for kod, veri in self.controller.dersler.items()
        ]
        self.ders_combobox["values"] = ders_listesi

        # ComboBox içeriği boş değilse ilkini seç
        if ders_listesi:
            self.ders_combobox.current(0)

    def dersi_sec(self):
        """
        Devam butonuna basıldığında, seçilen derse ilerler.
        Ancak en az 3 ders eklenmesi zorunluluğu kontrol edilir.
        """
        # 1) En az 3 ders ekleme kontrolü
        if len(self.controller.dersler) < 3:
            messagebox.showwarning(
                "Uyarı",
                "Devam edebilmek için en az 3 ders eklemeniz gerekmektedir!"
            )
            return

        secili = self.ders_combobox.get().strip()
        if secili:
            # 2) "Ders Kodu – Ders Adı" şeklinden sadece "Ders Kodu"nu ayırma
            ders_kodu = secili.split("–")[0].strip()
            self.controller.secili_ders = ders_kodu
            self.controller.show_frame("OgrenciListesiSayfasi")
        else:
            messagebox.showwarning("Uyarı", "Lütfen bir ders seçiniz!")


class DersEkleSayfasi(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Ders Kodu:").pack(pady=5)
        self.entry_ders_kodu = tk.Entry(self)
        self.entry_ders_kodu.pack()

        tk.Label(self, text="Ders Adı:").pack(pady=5)
        self.entry_ders_adi = tk.Entry(self)
        self.entry_ders_adi.pack()

        tk.Button(self, text="Ekle", command=self.dersi_ekle).pack(pady=10)
        tk.Button(self, text="Geri",
                  command=lambda: controller.show_frame("DersSecimSayfasi")).pack()

    def dersi_ekle(self):
        kod = self.entry_ders_kodu.get().strip()
        ad = self.entry_ders_adi.get().strip()

        if kod and ad:
            if kod not in self.controller.dersler:
                  
                self.controller.dersler[kod] = {
                    "ad": ad,
                    "program_ciktilari": [],
                    "ders_ogrenme_ciktilari": [],
                    "degerlendirme_kriterleri": {},
                    "tablo_1": None,
                    "tablo_2": None,
                    "notlar": None,
                    "ogrenci_listesi": []   
                }
                messagebox.showinfo("Başarılı", f"{kod} - {ad} eklendi.")
                
                # Ders seçme sayfasını güncelle
                self.controller.frames["DersSecimSayfasi"].update_ders_listesi()

                # Alanları temizle
                self.entry_ders_kodu.delete(0, tk.END)
                self.entry_ders_adi.delete(0, tk.END)

                # Ders seçimi sayfasına dön
                self.controller.show_frame("DersSecimSayfasi")
            else:
                messagebox.showerror("Hata", "Bu ders kodu zaten kayıtlı!")
        else:
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurunuz!")
class OgrenciListesiSayfasi(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Öğrenci Listesi").pack(pady=10)

        # Öğrenci numaralarının gösterileceği Text alanı
        self.text_ogrenci_no = tk.Text(self, width=50, height=20)
        self.text_ogrenci_no.pack(pady=5)

        # Excel'den yükleme butonu
        tk.Button(self, text="Excel'den Yükle", command=self.excel_yukle).pack(pady=5)

        # Devam butonu
        tk.Button(self, text="Devam", command=lambda: self.kaydet_ve_devam(controller)).pack(pady=5)

        # Geri butonu
        tk.Button(self, text="Geri", command=lambda: controller.show_frame("DersSecimSayfasi")).pack(pady=5)

    def yukle(self):
        """
        Seçili dersin öğrenci listesini text alanına yükler.
        """
        self.text_ogrenci_no.delete("1.0", tk.END)
        secili_ders = self.controller.secili_ders
        if secili_ders and secili_ders in self.controller.dersler:
            ogrenci_listesi = self.controller.dersler[secili_ders].get("ogrenci_listesi", [])
            for ogr_no in ogrenci_listesi:
                self.text_ogrenci_no.insert(tk.END, f"{ogr_no}\n")

    def excel_yukle(self):
        """
        Excel dosyasından öğrenci listesi verilerini yükler.
        """
        file_path = filedialog.askopenfilename(
            title="Excel Dosyasını Seçin",
            filetypes=(("Excel Dosyaları", "*.xlsx;*.xls"), ("Tüm Dosyalar", "*.*"))
        )
        if file_path:
            try:
                df = pd.read_excel(file_path)
                self.text_ogrenci_no.delete("1.0", tk.END)

                # DataFrame'deki verileri Text kutusuna aktar
                for row in df.itertuples(index=False):
                    satir = "\t".join(map(str, row))
                    self.text_ogrenci_no.insert(tk.END, f"{satir}\n")

                messagebox.showinfo("Başarılı", "Excel dosyasından öğrenci listesi yüklendi.")
            except Exception as e:
                messagebox.showerror("Hata", f"Excel yükleme hatası: {e}")

    def kaydet(self):
        """
        Text alanındaki öğrenci numaralarını seçili derse kaydeder.
        """
        secili_ders = self.controller.secili_ders
        if not secili_ders:
            messagebox.showwarning("Uyarı", "Önce bir ders seçmelisiniz!")
            return False   
        ogrenciler = self.text_ogrenci_no.get("1.0", tk.END).strip().splitlines()
        if not ogrenciler:
            messagebox.showwarning("Uyarı", "Öğrenci listesi boş kaydedilemez!")
            return False   
        self.controller.dersler[secili_ders]["ogrenci_listesi"] = ogrenciler
        messagebox.showinfo("Kaydedildi", "Öğrenci listesi kaydedildi.")
        return True  # Başarılı

    def kaydet_ve_devam(self, controller):
        """
        Kaydet ve bir sonraki sayfaya geçiş yap.
        """
        if self.kaydet():  # Eğer    başarılı olursa
            controller.show_frame("ProgramCiktilariSayfasi")

class ProgramCiktilariSayfasi(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Program Çıktıları (Excel'den veya Manuel)").pack(pady=10)

        # 1) Manuel giriş için Text
        self.text_progcikti = tk.Text(self, width=120, height=20)
        self.text_progcikti.pack(pady=5)

        # 2) Excel'den yükleme butonu
        tk.Button(self, text="Excel'den Yükle", command=self.excel_yukle).pack(pady=5)

        # 3) Devam butonu (Kaydet ve Devam)
        tk.Button(self,text="Devam",command=lambda: self.kaydet_ve_devam(controller)).pack(pady=5)

        # 4) Geri butonu
        tk.Button(self, text="Geri", command=lambda: controller.show_frame("OgrenciListesiSayfasi")).pack(pady=5)

    def kaydet(self):
        """
        Program çıktıları metnini seçili derse kaydeder.
        """
        secili_ders = self.controller.secili_ders
        if not secili_ders:
            messagebox.showwarning("Uyarı", "Önce bir ders seçmelisiniz!")
            return False      
        metin = self.text_progcikti.get("1.0", tk.END).strip()
        if not metin:
            messagebox.showwarning("Uyarı", "Boş metin kaydedilemez!")
            return False      
        # Satır satır listeye dönüştür
        program_ciktilari = metin.splitlines()
        self.controller.dersler[secili_ders]["program_ciktilari"] = program_ciktilari
        messagebox.showinfo("Kaydedildi", "Program çıktıları kaydedildi.")
        return True    

    def kaydet_ve_devam(self, controller):
        """
        Kaydet ve bir sonraki sayfaya geçiş yap.
        """
        if self.kaydet():  # Eğer    başarılı olursa
            controller.show_frame("DersOgrenmeCiktilariSayfasi")

    def excel_yukle(self):
        """
        Excel dosyasından Tablo 1 verilerini yükler.
        """
        file_path = filedialog.askopenfilename(
            title="Excel Dosyasını Seçin",
            filetypes=(("Excel Dosyaları", "*.xlsx;*.xls"), ("Tüm Dosyalar", "*.*"))
        )
        if file_path:
            try:
                df = pd.read_excel(file_path)
                self.text_progcikti.delete("1.0", tk.END)

                # DataFrame'deki verileri Text kutusuna aktar
                for row in df.itertuples(index=False):
                    satir = "\t".join(map(str, row))
                    self.text_progcikti.insert(tk.END, f"{satir}\n")

                messagebox.showinfo("Başarılı", "Excel dosyasından Tablo 1 yüklendi.")
            except Exception as e:
                messagebox.showerror("Hata", f"Excel yükleme hatası: {e}")

    def yukle(self):
        """
        Seçilen derse ait program çıktıları metin kutusuna yüklenir.
        """
        self.text_progcikti.delete("1.0", tk.END)
        secili_ders = self.controller.secili_ders
        if secili_ders in self.controller.dersler:
            program_ciktilari = self.controller.dersler[secili_ders].get("program_ciktilari", [])
            for cikti in program_ciktilari:
                self.text_progcikti.insert(tk.END, f"{cikti}\n")



class DersOgrenmeCiktilariSayfasi(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Ders Öğrenme Çıktıları (Excel'den veya Manuel)").pack(pady=10)

        # 1) Manuel giriş için Text
        self.text_derscikti = tk.Text(self, width=120, height=20)
        self.text_derscikti.pack(pady=5)

        # 2) Excel'den yükleme butonu
        tk.Button(self, text="Excel'den Yükle", command=self.excel_yukle).pack(pady=5)

        # 3) Devam ve Geri butonları
        tk.Button(self,text="Devam",command=lambda: self.kaydet_ve_devam(controller)).pack(pady=5)
        tk.Button(self,text="Geri",command=lambda: controller.show_frame("ProgramCiktilariSayfasi")).pack(pady=5)

    def yukle(self):
        """
        Seçilen derse ait öğrenme çıktıları metin kutusuna yüklenir.
        """
        self.text_derscikti.delete("1.0", tk.END)
        secili_ders = self.controller.secili_ders
        if secili_ders in self.controller.dersler:
            ders_ogrenme_ciktilari = self.controller.dersler[secili_ders].get("ders_ogrenme_ciktilari", [])
            for cikti in ders_ogrenme_ciktilari:
                self.text_derscikti.insert(tk.END, f"{cikti}\n")

    def excel_yukle(self):
        """
        Excel dosyasından öğrenme çıktıları verilerini yükler.
        """
        file_path = filedialog.askopenfilename(
            title="Excel Dosyasını Seçin",
            filetypes=(("Excel Dosyaları", "*.xlsx;*.xls"), ("Tüm Dosyalar", "*.*"))
        )
        if file_path:
            try:
                df = pd.read_excel(file_path)
                self.text_derscikti.delete("1.0", tk.END)

                # DataFrame'deki verileri Text kutusuna aktar
                for row in df.itertuples(index=False):
                    satir = "\t".join(map(str, row))
                    self.text_derscikti.insert(tk.END, f"{satir}\n")

                messagebox.showinfo("Başarılı", "Excel dosyasından öğrenme çıktıları yüklendi.")
            except FileNotFoundError:
                messagebox.showerror("Hata", "Dosya bulunamadı. Lütfen geçerli bir dosya seçin.")
            except Exception as e:
                messagebox.showerror("Hata", f"Excel yükleme hatası: {e}")

    def kaydet(self):
        """
        Dersin öğrenme çıktılarını seçili derse kaydeder.
        """
        secili_ders = self.controller.secili_ders
        if not secili_ders:
            messagebox.showwarning("Uyarı", "Önce bir ders seçmelisiniz!")
            return False   
        metin = self.text_derscikti.get("1.0", tk.END).strip()
        if not metin:
            messagebox.showwarning("Uyarı", "Boş metin kaydedilemez!")
            return False   
        ders_ogrenme_ciktilari = metin.splitlines()
        self.controller.dersler[secili_ders]["ders_ogrenme_ciktilari"] = ders_ogrenme_ciktilari
        messagebox.showinfo("Kaydedildi", "Ders öğrenme çıktıları kaydedildi.")
        return True  # Başarılı

    def kaydet_ve_devam(self, controller):
        """
        Kaydet ve bir sonraki sayfaya geçiş yap.
        """
        if self.kaydet():  # Eğer    başarılı olursa
            controller.show_frame("DegerlendirmeKriterleriSayfasi")



class DegerlendirmeKriterleriSayfasi(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Değerlendirme Kriterleri ve Ağırlıkları").pack(pady=10)

        self.entry_kriter = tk.Entry(self, width=50)
        self.entry_kriter.pack(pady=5)
        self.entry_kriter.insert(0, "Kriter Adı")

        self.entry_agirlik = tk.Entry(self, width=20)
        self.entry_agirlik.pack(pady=5)
        self.entry_agirlik.insert(0, "Ağırlık (%)")

        tk.Button(self, text="Ekle", command=self.kriter_ekle).pack(pady=5)

        self.kriter_listbox = tk.Listbox(self, width=100)
        self.kriter_listbox.pack(pady=10)

        tk.Button(self, text="Seçilen Sil", command=self.secilen_sil).pack(pady=5)
        
        tk.Button(self, text="Devam", command=self.kaydet_ve_devam).pack(pady=5)

        tk.Button(self, text="Geri",
                  command=lambda: controller.show_frame("DersOgrenmeCiktilariSayfasi")).pack(pady=5)



    def kriter_ekle(self):
        kriter = self.entry_kriter.get().strip()
        agirlik = self.entry_agirlik.get().strip()

        if kriter and agirlik.isdigit():
            agirlik = int(agirlik)
            mevcut_kriterler = [self.kriter_listbox.get(i).split(" - ")[0] for i in range(self.kriter_listbox.size())]

            # Kriter adı benzersiz hale getirilir
            orijinal_kriter = kriter
            sayac = 2
            while kriter in mevcut_kriterler:
                kriter = f"{orijinal_kriter} ({sayac})"
                sayac += 1

            self.kriter_listbox.insert(tk.END, f"{kriter} - {agirlik}%")
            messagebox.showinfo("Başarılı", f"Kriter '{kriter}' başarıyla eklendi.")
        else:
            messagebox.showwarning("Uyarı", "Kriter adı veya ağırlık geçersiz!")

    def secilen_sil(self):
        """
        Seçilen değerlendirme kriterini listeden siler.
        """
        try:
            selected_index = self.kriter_listbox.curselection()[0]  # Seçilen öğeyi al
            self.kriter_listbox.delete(selected_index)  # Öğeyi listeden sil
        except IndexError:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kriter seçin!")

    def kaydet(self):
        """
        Değerlendirme kriterlerini seçilen derse kaydeder.
        """
        secili_ders = self.controller.secili_ders
        if not secili_ders:
            messagebox.showwarning("Uyarı", "Önce bir ders seçmelisiniz!")
            return False   

        toplam = 0
        kriterler = {}
        for i in range(self.kriter_listbox.size()):
            item = self.kriter_listbox.get(i)
            parts = item.split("-")
            if len(parts) == 2:
                k = parts[0].strip()
                try:
                    a = int(parts[1].strip().replace("%", ""))
                    toplam += a
                    kriterler[k] = a
                except ValueError:
                    messagebox.showerror("Hata", f"Kriter '{k}' için geçersiz ağırlık!")
                    return False   

        # 5 kriter kontrolü
        if len(kriterler) < 5:
            messagebox.showerror("Hata", "En az 5 değerlendirme kriteri eklenmelidir!")
            return False   

        # Ağırlıkların toplamı kontrolü
        if toplam != 100:
            messagebox.showerror("Hata", "Ağırlıkların toplamı 100 olmalıdır!")
            return False   

        self.controller.dersler[secili_ders]["degerlendirme_kriterleri"] = kriterler
        messagebox.showinfo("Kaydedildi", f"{secili_ders} dersinin kriterleri kaydedildi.")
        return True  # Başarılı



    def kaydet_ve_devam(self):
        """
        Kaydet ve başarılı olursa bir sonraki sayfaya geç.
        """
        if self.kaydet():  # Eğer    başarılı olursa
            self.controller.show_frame("NotlarSayfasi")

    def yukle(self):
        """
        Seçilen dersin kriterlerini liste kutusuna yükler.
        """
        self.kriter_listbox.delete(0, tk.END)  # Mevcut kriterleri temizle
        secili_ders = self.controller.secili_ders
        if secili_ders and secili_ders in self.controller.dersler:
            kriterler = self.controller.dersler[secili_ders].get("degerlendirme_kriterleri", {})
            for kriter, agirlik in kriterler.items():
                self.kriter_listbox.insert(tk.END, f"{kriter} - {agirlik}%")


class NotlarSayfasi(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Notlar").pack(pady=10)

        self.text_notlar = tk.Text(self, width=100, height=20)
        self.text_notlar.pack()

        tk.Button(self, text="Excel'den Yükle", command=self.excel_yukle).pack(pady=5)
        tk.Button(self, text="Kaydet", command=self.kaydet).pack(pady=5)
        tk.Button(self, text="tablo 1", command=self.kaydet_ve_gec).pack(pady=5)

    def yukle(self):
        """
        Seçili dersin notlarını metin kutusuna yükler.
        """
        secili_ders = self.controller.secili_ders
        if secili_ders:
            self.text_notlar.delete("1.0", tk.END)  # Mevcut içeriği temizle
            notlar = self.controller.dersler[secili_ders].get("notlar", [])
            if notlar:
                # Her bir notu metin kutusuna ekle
                for not_line in notlar:
                    self.text_notlar.insert(tk.END, f"{not_line}\n")
        else:
            self.text_notlar.delete("1.0", tk.END)

    def excel_yukle(self):
        """
        Excel dosyasından not verilerini yükler.
        """
        file_path = filedialog.askopenfilename(
            title="Excel Dosyasını Seçin",
            filetypes=(("Excel Dosyaları", "*.xlsx;*.xls"), ("Tüm Dosyalar", "*.*"))
        )
        if file_path:
            try:
                df = pd.read_excel(file_path)
                self.text_notlar.delete("1.0", tk.END)

                # DataFrame'deki verileri Text kutusuna aktar
                for row in df.itertuples(index=False):
                    satir = "\t".join(map(str, row))
                    self.text_notlar.insert(tk.END, f"{satir}\n")

                messagebox.showinfo("Başarılı", "Excel dosyasından notlar yüklendi.")
            except FileNotFoundError:
                messagebox.showerror("Hata", "Dosya bulunamadı. Lütfen geçerli bir dosya seçin.")
            except Exception as e:
                messagebox.showerror("Hata", f"Excel yükleme hatası: {e}")

    def kaydet(self):
        """
        Metin kutusundaki notları seçili derse kaydeder.
        """
        secili_ders = self.controller.secili_ders
        if not secili_ders:
            messagebox.showwarning("Uyarı", "Önce bir ders seçmelisiniz!")
            return False   

        lines = self.text_notlar.get("1.0", tk.END).strip().splitlines()
        self.controller.dersler[secili_ders]["notlar"] = lines
        messagebox.showinfo("Kaydedildi", "Notlar kaydedildi.")
        return True  # Başarılı

    def kaydet_ve_gec(self):
        """
           işleminden sonra başka bir derse geçiş yapar.
        """
        if self.kaydet():  # Eğer    başarılı olursa
            self.controller.show_frame("Tablo1Sayfasi")


class Tablo1Sayfasi(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Tablo 1: Program Çıktıları ve Ders Öğrenme Çıktıları İlişkisi").pack(pady=10)

        tk.Button(self, text="Excel'den Yükle", command=self.excel_yukle).pack(pady=5)

        tk.Label(self, text="Manuel Veri Girişi (Satırları Program Çıktısı, Sütunları Ders Öğrenme Çıktısı)").pack(pady=5)
        self.text_tablo = tk.Text(self, width=120, height=20)
        self.text_tablo.pack(pady=5)

        tk.Button(self, text="Güncelle", command=self.guncelle).pack(pady=5)
        tk.Button(self, text="Kaydet", command=self.kaydet).pack(pady=5)

        tk.Button(self, text="Tablo 2", command=lambda: self.kaydet_ve_gec("Tablo2Sayfasi")).pack(pady=5)
        tk.Button(self, text="Geri", command=lambda: controller.show_frame("NotlarSayfasi")).pack(pady=5)

    def yukle(self):
        self.text_tablo.delete("1.0", tk.END)
        secili_ders = self.controller.secili_ders
        if secili_ders and secili_ders in self.controller.dersler:
            ders_verisi = self.controller.dersler[secili_ders]
            program_ciktilari = ders_verisi.get("program_ciktilari", [])
            ders_ogrenme_ciktilari = ders_verisi.get("ders_ogrenme_ciktilari", [])
            tablo_data = ders_verisi.get("tablo_1", [])

            if not tablo_data:
                tablo_data = [[0 for _ in range(len(ders_ogrenme_ciktilari) + 1)] for _ in range(len(program_ciktilari))]
                ders_verisi["tablo_1"] = tablo_data

            baslik = "Prg Çıktı\t" + "\t".join([str(i + 1) for i in range(len(ders_ogrenme_ciktilari))]) + "\tİlişki Değ.\n"
            self.text_tablo.insert(tk.END, baslik)

            for i, satir in enumerate(tablo_data):
                toplam = sum(satir[:-1])
                satir[-1] = toplam / len(ders_ogrenme_ciktilari) if ders_ogrenme_ciktilari else 0
                self.text_tablo.insert(tk.END, f"{i + 1}\t" + "\t".join(map(str, satir)) + "\n")

    def guncelle(self):
        secili_ders = self.controller.secili_ders
        if secili_ders and secili_ders in self.controller.dersler:
            ders_verisi = self.controller.dersler[secili_ders]
            tablo_data = ders_verisi.get("tablo_1", [])

            for satir in tablo_data:
                toplam = sum(satir[:-1])
                satir[-1] = toplam / (len(satir) - 1)

            self.yukle()

    def kaydet(self):
        secili_ders = self.controller.secili_ders
        if not secili_ders:
            messagebox.showwarning("Uyarı", "Önce bir ders seçmelisiniz!")
            return False

        metin = self.text_tablo.get("1.0", tk.END).strip()
        if not metin:
            messagebox.showwarning("Uyarı", "Tablo boş olamaz!")
            return False

        try:
            tablo_data = []
            for index, satir in enumerate(metin.splitlines()):
                if index == 0:
                    continue
                parçalar = satir.split("\t")
                tablo_data.append([float(x) for x in parçalar[1:]])

            self.controller.dersler[secili_ders]["tablo_1"] = tablo_data
            messagebox.showinfo("Başarılı", "Tablo 2 kaydedildi.")
            return True
        except ValueError as e:
            messagebox.showerror("Hata", f"Tabloyu kaydederken bir hata oluştu: {e}")
            return False

    def kaydet_ve_gec(self, sonraki_sayfa):
        if self.kaydet():
            self.controller.show_frame(sonraki_sayfa)

    def excel_yukle(self):
        file_path = filedialog.askopenfilename(
            title="Excel Dosyasını Seçin",
            filetypes=(("Excel Dosyaları", "*.xlsx;*.xls"), ("Tüm Dosyalar", "*.*"))
        )
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            self.text_tablo.delete("1.0", tk.END)
            for row in df.itertuples(index=False):
                self.text_tablo.insert(tk.END, "\t".join(map(str, row)) + "\n")
            messagebox.showinfo("Başarılı", "Excel'den tablo verileri yüklendi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Excel yükleme hatası: {e}")

    def kaydet(self):
        secili_ders = self.controller.secili_ders
        if not secili_ders:
            messagebox.showwarning("Uyarı", "Önce bir ders seçmelisiniz!")
            return False

        metin = self.text_tablo.get("1.0", tk.END).strip()
        if not metin:
            messagebox.showwarning("Uyarı", "Tablo boş olamaz!")
            return False

        try:
            tablo_data = []
            for index, satir in enumerate(metin.splitlines()):
                if index == 0:
                    continue
                parçalar = satir.split("\t")
                tablo_data.append([float(x) for x in parçalar[1:]])

            self.controller.dersler[secili_ders]["tablo_1"] = tablo_data
            messagebox.showinfo("Başarılı", "Tablo 1 kaydedildi.")
            return True
        except ValueError as e:
            messagebox.showerror("Hata", f"Tabloyu kaydederken bir hata oluştu: {e}")
            return False


class Tablo2Sayfasi(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Başlık
        tk.Label(self, text="Tablo 2: Ders Çıktıları ve Değerlendirme Kriterleri").pack(pady=10)

        # Güncelle Butonu
        tk.Button(self, text="Güncelle", command=self.guncelle).pack(pady=5)

        # Excel'den yükleme butonu
        tk.Button(self, text="Excel'den Yükle", command=self.excel_yukle).pack(pady=5)

        # Manuel giriş için Text kutusu
        tk.Label(self, text="Manuel Veri Girişi").pack(pady=5)
        self.text_tablo = tk.Text(self, width=100, height=20)
        self.text_tablo.pack(pady=5)

        # Kaydet butonu
        tk.Button(self, text="Kaydet", command=self.kaydet).pack(pady=5)

        # Devam ve Geri butonları
        tk.Button(self, text="Yeni Derse Geç",
                  command=lambda: controller.show_frame("Tablo3Sayfasi")).pack(pady=5)
        tk.Button(self, text="Geri", command=lambda: controller.show_frame("Tablo1Sayfasi")).pack(pady=5)

    def yukle(self):
        self.text_tablo.delete("1.0", tk.END)
        secili_ders = self.controller.secili_ders
        if secili_ders and secili_ders in self.controller.dersler:
            ders_verisi = self.controller.dersler[secili_ders]
            ders_ciktilari = ders_verisi.get("ders_ogrenme_ciktilari", [])
            degerlendirme_kriterleri = ders_verisi.get("degerlendirme_kriterleri", {})

            # tablo_2 verisini al
            tablo_data = ders_verisi.get("tablo_2")

            # Eğer tablo_data None ise, kriter sayısı kadar sütun oluştur
            kriterler = list(degerlendirme_kriterleri.keys())
            if tablo_data is None:
                tablo_data = [
                    [0 for _ in range(len(kriterler))]
                    for _ in range(len(ders_ciktilari))
                ]
                ders_verisi["tablo_2"] = tablo_data

            # Ağırlıkları yazdıran ilk satır (opsiyonel)
            agirliklar = [degerlendirme_kriterleri[k] for k in kriterler]
            baslik_agirlik = " " * 12 + "".join(f"{str(ag).center(12)}" for ag in agirliklar)
            # Eğer TOPLAM sütununu da başlıkta göstermek isterseniz:
            baslik_agirlik += "TOPLAM".center(12)
            baslik_agirlik += "\n"
            self.text_tablo.insert(tk.END, baslik_agirlik)

            # Kriter adlarının yazıldığı ikinci satır
            baslik_kriter = "DersÇıktı".ljust(12) + "".join(f"{k.center(12)}" for k in kriterler)
            baslik_kriter += "TOPLAM".center(12)
            baslik_kriter += "\n"
            self.text_tablo.insert(tk.END, baslik_kriter)

            # Tablo satırlarını yazdırma
            for i, satir in enumerate(tablo_data):
                toplam = sum(satir)
                satir_text = "".join(f"{str(deger).center(12)}" for deger in satir)
                self.text_tablo.insert(
                    tk.END,
                    f"{str(i+1).ljust(12)}{satir_text}{str(toplam).center(12)}\n"
                )


    def guncelle(self):
        """
        Güncelle butonuna basıldığında toplam sütunlarını yeniden hesaplar ve tabloyu günceller.
        """
        secili_ders = self.controller.secili_ders
        if secili_ders and secili_ders in self.controller.dersler:
            ders_verisi = self.controller.dersler[secili_ders]
            tablo_data = ders_verisi.get("tablo_2", [])

            self.yukle()

    def kaydet(self):
        secili_ders = self.controller.secili_ders
        if not secili_ders:
            messagebox.showwarning("Uyarı", "Önce bir ders seçmelisiniz!")
            return False

        metin = self.text_tablo.get("1.0", tk.END).strip()
        if not metin:
            messagebox.showwarning("Uyarı", "Tablo boş olamaz!")
            return False

        try:
            ders_verisi = self.controller.dersler[secili_ders]
            degerlendirme_kriterleri = ders_verisi.get("degerlendirme_kriterleri", {})
            kriter_sayisi = len(degerlendirme_kriterleri)

            lines = metin.splitlines()
            # ilk 2 satır başlıkları atla (ağırlık satırı ve kriter adları satırı)
            tablo_data = []
            for idx, line in enumerate(lines):
                if idx < 2:
                    continue
                hucreler = line.split()
                numeric_values = [float(x) for x in hucreler[1 : 1 + kriter_sayisi]]
                tablo_data.append(numeric_values)

            self.controller.dersler[secili_ders]["tablo_2"] = tablo_data
            messagebox.showinfo("Başarılı", "Tablo 2 kaydedildi.")
            return True

        except ValueError as e:
            messagebox.showerror("Hata", f"Tabloyu kaydederken bir hata oluştu: {e}")
            return False



    def excel_yukle(self):
        file_path = filedialog.askopenfilename(
            title="Excel Dosyasını Seçin",
            filetypes=(("Excel Dosyaları", "*.xlsx;*.xls"), ("Tüm Dosyalar", "*.*"))
        )
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            self.text_tablo.delete("1.0", tk.END)
            for row in df.itertuples(index=False):
                self.text_tablo.insert(tk.END, "\t".join(map(str, row)) + "\n")
            messagebox.showinfo("Başarılı", "Excel'den tablo verileri yüklendi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Excel yükleme hatası: {e}")


class Tablo3Sayfasi(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Tablo 3: Ağırlıklı Değerlendirme Tablosu").pack(pady=10)

        # Metin kutusu
        self.text_tablo = tk.Text(self, width=100, height=20)
        self.text_tablo.pack(pady=5)

        # Güncelle Butonu
        tk.Button(self, text="Güncelle", command=self.guncelle).pack(pady=5)

        # Kaydet ve Geri butonları
        tk.Button(self, text="Kaydet", command=self.kaydet).pack(pady=5)
        tk.Button(self, text="devam", command=lambda: controller.show_frame("Tablo4Sayfasi")).pack(pady=5)
        tk.Button(self, text="Geri", command=lambda: controller.show_frame("Tablo2Sayfasi")).pack(pady=5)

    def yukle(self):
        """
        Tablo 3 verilerini yükler ve hesaplar.
        """
        self.text_tablo.delete("1.0", tk.END)
        secili_ders = self.controller.secili_ders
        if not secili_ders or secili_ders not in self.controller.dersler:
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir ders seçiniz!")
            return

        ders_verisi = self.controller.dersler[secili_ders]
        tablo_2 = ders_verisi.get("tablo_2", [])
        degerlendirme_kriterleri = ders_verisi.get("degerlendirme_kriterleri", {})
        kriter_agirliklari = [degerlendirme_kriterleri[k] / 100 for k in degerlendirme_kriterleri]

        if not tablo_2 or not kriter_agirliklari:
            messagebox.showerror("Hata", "Tablo 2 veya değerlendirme kriterleri eksik!")
            return

        # Tablo başlıkları
        baslik = "Ders Çıktı".ljust(15) + "".join(f"Kriter {i + 1}".ljust(15) for i in range(len(kriter_agirliklari))) + "TOPLAM".ljust(15) + "\n"
        self.text_tablo.insert(tk.END, baslik)

        # Ağırlıklı değerlendirme hesaplamaları
        tablo_3 = []
        for ders_cikti_index, ders_cikti_satir in enumerate(tablo_2):
            agirlikli_degerler = [kriter_agirliklari[i] * ders_cikti_satir[i] for i in range(len(kriter_agirliklari))]
            toplam = sum(agirlikli_degerler)
            tablo_3.append(agirlikli_degerler + [toplam])

            satir_text = f"{ders_cikti_index + 1}".ljust(15) + "".join(f"{deger:.2f}".ljust(15) for deger in agirlikli_degerler) + f"{toplam:.2f}".ljust(15) + "\n"
            self.text_tablo.insert(tk.END, satir_text)

        # Tablo 3'ü ders verisine kaydet
        ders_verisi["tablo_3"] = tablo_3

    def kaydet(self):
        """
        Tablo 3'ü kaydeder.
        """
        secili_ders = self.controller.secili_ders
        if not secili_ders:
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir ders seçiniz!")
            return False

        ders_verisi = self.controller.dersler[secili_ders]
        metin = self.text_tablo.get("1.0", tk.END).strip()
        if not metin:
            messagebox.showwarning("Uyarı", "Tablo boş olamaz!")
            return False

        messagebox.showinfo("Başarılı", "Tablo 3 kaydedildi.")
        return True

    def guncelle(self):
        """
        Güncelle butonuna basıldığında tabloyu yeniden yükler.
        """
        self.yukle()
class Tablo4Sayfasi(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Tablo 4: Ders Çıktıları Başarı Oranları").pack(pady=10)

        # Text kutusu
        self.text_tablo = tk.Text(self, width=120, height=20)
        self.text_tablo.pack(pady=5)

        # Kaydet ve Geri butonları
        tk.Button(self, text="ders seçim", command=lambda: controller.show_frame("DersSecimSayfasi")).pack(pady=5)
        tk.Button(self, text="Geri", command=lambda: controller.show_frame("Tablo3Sayfasi")).pack(pady=5)

    def yukle(self):
        """
        Tüm öğrenciler için Tablo 4 verilerini hesaplar ve görüntüler.
        """
        secili_ders = self.controller.secili_ders
        if not secili_ders:
            messagebox.showwarning("Uyarı", "Lütfen bir ders seçiniz!")
            return

        ders_verisi = self.controller.dersler[secili_ders]
        tablo_3 = ders_verisi.get("tablo_3", [])
        notlar = ders_verisi.get("notlar", [])

        if not tablo_3 or not notlar:
            self.text_tablo.delete("1.0", tk.END)
            self.text_tablo.insert(tk.END, "Tablo 3 veya Öğrenci Notları eksik!")
            return

        ders_ciktilari = ders_verisi.get("ders_ogrenme_ciktilari", [])
        tablo_4_text = ""

        # Tüm öğrenciler için tablo oluşturma
        for not_satir in notlar:
            ogr_no, *ogrenci_notlari = not_satir.split("\t")
            ogrenci_notlari = list(map(float, ogrenci_notlari))

            tablo_4_text += f"TABLO 4: Öğrenci {ogr_no} için\n"
            tablo_4_text += "Ders Çıktı\tkriter1\tkriter 2\tkriter 3\tkriter 4\tkriter 5\tTOPLAM\tMAX\t% Başarı\n"

            for i, satir in enumerate(tablo_3):
                ogrenci_skorlari = [
                    round(satir[j] * ogrenci_notlari[j] / 100, 2) for j in range(len(ogrenci_notlari))
                ]
                toplam = sum(ogrenci_skorlari)
                max_not = round(satir[-1] * 100, 2)
                basari_orani = round((toplam / max_not) * 100, 2) if max_not > 0 else 0

                tablo_4_text += f"{i + 1}\t" + "\t".join(map(str, ogrenci_skorlari)) + f"\t{toplam}\t{max_not}\t{basari_orani}\n"

            tablo_4_text += "\n"

        # Metin kutusuna yazdır
        self.text_tablo.delete("1.0", tk.END)
        self.text_tablo.insert(tk.END, tablo_4_text)
if __name__ == "__main__":
    app = MainApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()