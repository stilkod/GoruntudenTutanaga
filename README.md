# Görüntüden Tutanağa

[![Lisans](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Sürüm](https://img.shields.io/github/v/release/stilkod/goruntuden-tutanaga)](https://github.com/stilkod/goruntuden-tutanaga/releases)

**Görüntüden Tutanağa**, video kayıtları üzerinde adli veya analitik incelemeler yapmak için geliştirilmiş, güçlü bir masaüstü uygulamasıdır. Video akışındaki önemli anları işaretlemenize, ekran görüntüleri almanıza, açıklamalar eklemenize ve tüm bulgularınızı tek bir Word dokümanında profesyonel bir rapora dönüştürmenize olanak tanır.


## 📝 Temel Amaç

Bu araç, güvenlik kayıtları, saha çalışmaları, spor analizleri veya herhangi bir video tabanlı araştırma sürecinde, kanıtların ve önemli olayların zaman damgalarıyla birlikte sistematik bir şekilde belgelenmesini sağlar. Manuel olarak not alma ve ekran görüntüsü yakalama zahmetini ortadan kaldırarak inceleme sürecini hızlandırır ve standartlaştırır.

## ✨ Ana Özellikler

*   **Hassas Video Oynatma:** VLC tabanlı güçlü medya oynatıcı ile MP4, AVI, MKV gibi popüler video formatlarını sorunsuz oynatın.
*   **Zaman Damgalı Tespit Ekleme:**
    *   **Metinsel Tespit:** Videodaki önemli bir anda durup, o ana ait açıklamalarınızı yazarak kaydedin. Tespit, o anın ekran görüntüsüyle birlikte listeye eklenir.
    *   **İşaretçili Tespit:** Video duraklatıldığında açılan yeni bir pencerede, ekran görüntüsü üzerine oklar çizip metin etiketleri ekleyerek görsel kanıtlar oluşturun.
*   **Kolay Video Kontrolü:** Oynat/Duraklat, İleri/Geri Sarma ve zaman çubuğu üzerinden hassas gezinme imkanı.
*   **Klavye Kısayolları:**
    *   **Boşluk (Space):** Videoyu Oynat/Duraklat.
    *   **Sağ/Sol Ok Tuşları:** Videoyu 500ms ileri/geri sar.
*   **Dinamik Tespit Listesi:** Eklenen tüm tespitleri zaman damgası ve açıklamalarıyla birlikte bir listede görüntüleyin ve dilediğinizi silin.
*   **Otomatik Rapor Oluşturma:** Tek bir tuşa basarak, eklediğiniz tüm tespitleri, ekran görüntülerini ve açıklamaları içeren, önceden tanımlanmış bir şablona uygun şekilde profesyonel bir **Word (.docx)** raporu oluşturun.
*   **Şablon Desteği:** Raporlarınızın formatını ve görünümünü `RPSABLON.docx` adlı bir şablon dosyası üzerinden tamamen kendinize göre özelleştirin.

## 🚀 Başlarken

### Gereksinimler

*   Python 3.8 veya üstü
*   VLC Media Player'ın bilgisayarınızda kurulu olması (python-vlc kütüphanesinin çalışması için gereklidir).
*   Proje klasöründe `RPSABLON.docx` adında bir Word şablon dosyası.

### Kurulum ve Çalıştırma

1.  **Bu depoyu klonlayın:**
    ```bash
    git clone https://github.com/stilkod/goruntuden-tutanaga.git
    cd goruntuden-tutanaga
    ```

2.  **Sanal bir ortam oluşturup aktif hale getirin (önerilir):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Gerekli Python kütüphanelerini yükleyin:**
    ```bash
    pip install python-vlc Pillow python-docx
    ```
    *Veya `requirements.txt` dosyasını kullanarak:*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Uygulamayı çalıştırın:**
    ```bash
    python GoruntudenTutanaga.py 
    ```
    *Not: Python dosyanızın adı farklıysa komutu ona göre güncelleyin.*

## 🛠️ Teknoloji Yığını

*   **Dil:** Python
*   **Arayüz (GUI):** Tkinter
*   **Video Oynatma:** `python-vlc` (VLC Kütüphanesi için Python bağlayıcısı)
*   **Görüntü İşleme:** Pillow (PIL Fork)
*   **Raporlama:** `python-docx`

## 🤝 Katkıda Bulunma

Projeye yapılan katkılar, onu daha da geliştirecektir. Katkıda bulunmak isterseniz:

1.  Bu depoyu **Fork**'layın.
2.  Yeni bir özellik dalı oluşturun (`git checkout -b ozellik/YeniRaporFormati`).
3.  Değişikliklerinizi **Commit**'leyin (`git commit -m 'Yeni rapor formatı için destek eklendi'`).
4.  Dalınızı **Push**'layın (`git push origin ozellik/YeniRaporFormati`).
5.  Bir **Pull Request** açın.

Hata bildirimleri veya özellik istekleri için lütfen [Issues](https://github.com/stilkod/goruntuden-tutanaga/issues) bölümünü kullanın.

## 📝 Lisans

Bu proje, **MIT Lisansı** ile lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakınız.
