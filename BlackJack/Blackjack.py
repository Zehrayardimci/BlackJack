import os
import sys
import random
from PIL import Image
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QUrl, QPropertyAnimation, QPoint, QEasingCurve
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QMessageBox, QGridLayout, QVBoxLayout, QDialog,QHBoxLayout)

class BakiyeWidget(QWidget):
    def __init__(self, bakiye, parent=None):
        super().__init__(parent)
        self.bakiye = bakiye
        self.setFixedSize(160, 50)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.transparent)

        # Para ikonu
        icon_x, icon_y, icon_diameter = 10, 10, 40
        painter.setBrush(QColor(243, 211, 0))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(icon_x, icon_y, icon_diameter, icon_diameter)

        painter.setPen(QColor(255, 255, 255))
        font_icon = QFont("Arial", 23, QFont.Bold)
        painter.setFont(font_icon)

        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance("$")
        text_height = metrics.height()

        text_x = icon_x + (icon_diameter - text_width) / 2
        text_y = icon_y + (icon_diameter + text_height) / 2 - metrics.descent()

        painter.drawText(int(text_x), int(text_y), "$")

        # Bakiye tutarı
        bakiye_x = icon_x + icon_diameter + 5
        bakiye_y = icon_y + icon_diameter / 2 + text_height / 4

        painter.setPen(Qt.white)
        font_text = QFont("Arial", 16, QFont.Bold)
        painter.setFont(font_text)
        painter.drawText(int(bakiye_x), int(bakiye_y), f"{self.bakiye}")


class BlackjackGirisEkrani(QWidget):
    def __init__(self):
        super().__init__()
        self.sonuc_yazisi = QLabel(self)
        self.sonuc_yazisi.setAlignment(Qt.AlignCenter)
        self.sonuc_yazisi.setWordWrap(True)
        self.sonuc_yazisi.setStyleSheet("""
            color:{renk};
            font-size: 42px;
            font-family: 'Segoe UI', 'Arial', sans-serif;                       
            font-weight: 800;
            background: none;
            border: none;

        """)
        self.sonuc_yazisi.setGeometry((self.width() - 600) // 2, 350, 600, 150)
        self.sonuc_yazisi.setVisible(False)

        self.setWindowTitle("Blackjack Oyunu")
        self.setFixedSize(1000, 650)

        self.bg_path = "images/main_background.jpg"
        self.bg_pixmap = QPixmap(self.bg_path).scaled(
            self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )

        self.ses_acik = True

        self.click_ses = QSoundEffect()
        self.click_ses.setSource(QUrl.fromLocalFile("sounds/click.wav"))
        self.click_ses.setVolume(0.5)  # Ses seviyesi

        self.bahis_sesi = QSoundEffect()
        self.bahis_sesi.setSource(QUrl.fromLocalFile("sounds/bet_click.wav"))
        self.bahis_sesi.setVolume(1)

        self.kart_dagit_sesi = QSoundEffect()
        self.kart_dagit_sesi.setSource(QUrl.fromLocalFile("sounds/card_deal.wav"))
        self.kart_dagit_sesi.setVolume(0.5)

        self.baslangic_kart_sesi = QSoundEffect()
        self.baslangic_kart_sesi.setSource(QUrl.fromLocalFile("sounds/card_deal_fast.wav"))
        self.baslangic_kart_sesi.setVolume(0.5)

        self.initUI()

    def sesi_degistir(self):
        self.click_ses.play()
        self.ses_acik = not self.ses_acik
        if self.ses_acik:
            self.ses_buton.setIcon(QIcon("images/sound_on.png"))
        else:
            self.ses_buton.setIcon(QIcon("images/sound_off.png"))

    def yeni_oyunu_baslat(self):
        self.temizle_oyun_ogeleri()
        self.oyunu_baslat()

    def initUI(self):
        # Ses Aç/Kapat butonu
        self.ses_buton = QPushButton(self)
        self.ses_buton.setGeometry(700, 20, 40, 40)
        self.ses_buton.setIcon(QIcon("images/sound_on.png"))
        self.ses_buton.setIconSize(QSize(30, 30))
        self.ses_buton.setCursor(Qt.PointingHandCursor)

        self.ses_buton.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #d3d3d3;
            }
        """)

        self.ses_buton.clicked.connect(self.sesi_degistir)

        # Çıkış butonu
        self.cikis_buton = QPushButton("Çıkış", self)
        self.cikis_buton.setGeometry(910, 20, 80, 40)
        self.cikis_buton.setStyleSheet("""
            font-size: 16px;
            border-radius: 15px;
            background-color: #f0f0f0;
            color: black;
            border: none;
        }
        QPushButton:hover {
            background-color: #D3D3D3;
            border-radius: 15px;
            border: none;
        }
        """)
        self.cikis_buton.clicked.connect(self.close)

        # Kuralları Görüntüle butonu
        self.kurallar_buton = QPushButton("Kuralları Görüntüle", self)
        self.kurallar_buton.setGeometry(750, 20, 150, 40)
        self.kurallar_buton.setStyleSheet("""
            font-size: 16px;
            border-radius: 15px;
            background-color: #f0f0f0;
            color: black;
            border: none;
        }
        QPushButton:hover {
            background-color: #D3D3D3;
            border-radius: 15px;
            border: none;
        }
        """)
        self.kurallar_buton.clicked.connect(self.kurallari_goster)

        # Oyuna Başla butonu
        self.basla_buton = QPushButton("Oyuna Başla", self)
        self.basla_buton.setGeometry(380, 520, 200, 60)
        self.basla_buton.setStyleSheet("""
            font-weight: bold;
            font-size: 25px;
            color: black;
            border-radius: 15px;
            background-color: #f0f0f0;
            border: none;
        }
        QPushButton:hover {
            background-color: #3bb300;
            border-radius: 15px;
            border: none;
        }
        """)
        self.basla_buton.clicked.connect(self.oyunu_baslat)

    def kart_animasyonu_goster(self, label, hedef_x, hedef_y, kart_sesi=True):
        label.show()

        baslangic_x = self.kart_destesi_label.x()
        baslangic_y = self.kart_destesi_label.y()

        label.move(baslangic_x, baslangic_y)

        animasyon = QPropertyAnimation(label, b"pos")
        animasyon.setDuration(500)
        animasyon.setStartValue(label.pos())
        animasyon.setEndValue(QPoint(hedef_x, hedef_y))
        animasyon.setEasingCurve(QEasingCurve.OutCubic)
        animasyon.start()

        if kart_sesi and self.ses_acik:
            self.baslangic_kart_sesi.play()

        if not hasattr(self, 'animasyonlar'):
            self.animasyonlar = []
        self.animasyonlar.append(animasyon)

    def sonuc_goster(self, mesaj, renk):
        if mesaj == "Krupiye battı! Kazandınız.":
            emoji = "🥳"
        elif "Kazandınız" in mesaj:
            emoji = "🎉"
        elif "21'i geçtiniz" in mesaj or "Krupiye kazandı" in mesaj:
            emoji = "😞"
        elif "Berabere" in mesaj:
            emoji = "🤝"
        else:
            emoji = "🔔"

        self.sonuc_yazisi.setText(f"{emoji} {mesaj}")

        self.sonuc_yazisi.setStyleSheet(f"""
            color: {renk};
            font-size: 48px;
            font-weight: bold;
            background: none;
            border: none;
        """)

        self.sonuc_yazisi.raise_()
        self.sonuc_yazisi.setVisible(True)

        # Yukarıdan kayan animasyon
        start_x = (self.width() - self.sonuc_yazisi.width()) // 2
        start_y = -100
        end_y = 200

        self.sonuc_yazisi.move(start_x, start_y)
        self.animasyon = QPropertyAnimation(self.sonuc_yazisi, b"pos")
        self.animasyon.setDuration(800)
        self.animasyon.setStartValue(QPoint(start_x, start_y))
        self.animasyon.setEndValue(QPoint(start_x, end_y))
        self.animasyon.start()

        QTimer.singleShot(2000, lambda: self.sonuc_yazisi.setVisible(False))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.bg_pixmap)

    def kurallar_penceresi(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Blackjack Kuralları")
        dialog.setFixedSize(500, 450)
        dialog.setWindowFlags(Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        dialog.setStyleSheet("""
            background-color: #f0f0f0;
            border: 3px solid #09506f;
            border-radius: 15px;
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        baslik = QLabel("Blackjack Kuralları", dialog)
        baslik.setStyleSheet("font-size: 24px; font-weight: bold; color: #09506f;")
        baslik.setAlignment(Qt.AlignCenter)
        layout.addWidget(baslik)

        kurallar_label = QLabel(dialog)
        kurallar_label.setText(
            "• Amaç: 21 sayısına ulaşmak veya krupiyeden yüksek puan elde etmek.\n\n"
            "• Kart değerleri:\n"
            "   - 2–10: Sayı değeri\n"
            "   - J, Q, K: 10 puan\n"
            "   - A: 1 veya 11 (hangisi işine yarıyorsa)\n\n"
            "• Blackjack: As + 10 = 21 (En güçlü el)\n\n"
            "• Hamleler:\n"
            "   - Kart Al (Hit)\n"
            "   - Dur (Stand)\n"
            "   - İkiye Katla (Double)\n\n"
            "• Krupiye 17 ve üzeri sayıda durur.\n\n"
            "• 21’i geçersen oyunu kaybedersin."
        )
        kurallar_label.setStyleSheet("font-size: 16px; color: black;")
        kurallar_label.setWordWrap(True)
        layout.addWidget(kurallar_label)

        buton_layout = QHBoxLayout()
        tamam_buton = QPushButton("Tamam", dialog)
        tamam_buton.setFixedSize(80, 25)
        tamam_buton.setStyleSheet("""
            background-color: #09506f;
            color: white;
            font-weight: bold;
            border-radius: 10px;
        """)
        tamam_buton.clicked.connect(dialog.accept)
        buton_layout.addStretch()
        buton_layout.addWidget(tamam_buton)
        buton_layout.addStretch()

        layout.addLayout(buton_layout)
        ana_x = self.x()
        ana_y = self.y()
        dialog.move(ana_x + self.width() - dialog.width() - 700, ana_y - 10)
        dialog.exec_()

    def kurallari_goster(self):
        self.kurallar_penceresi()

    def oyunu_baslat(self):
        if self.ses_acik:
            self.click_ses.play()
        # İlk seferde çalışması için kontrol
        if not os.path.exists("images/cards_white_bg"):
            os.makedirs("images/cards_white_bg", exist_ok=True)

            for filename in os.listdir("cards"):
                if filename.endswith(".png"):
                    image_path = os.path.join("cards", filename)
                    image = Image.open(image_path).convert("RGBA")

                    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
                    background.paste(image, mask=image.split()[3])  # alpha channel

                    final_image = background.convert("RGB")
                    final_image.save(os.path.join("images/cards_white_bg", filename))

        if hasattr(self, "cikis_buton") and self.cikis_buton is not None:
            self.cikis_buton.deleteLater()
            self.cikis_buton = None

        if hasattr(self, "kurallar_buton") and self.kurallar_buton is not None:
            self.kurallar_buton.deleteLater()
            self.kurallar_buton = None

        if hasattr(self, "basla_buton") and self.basla_buton is not None:
            self.basla_buton.deleteLater()
            self.basla_buton = None

        if hasattr(self, "ses_buton") and self.ses_buton is not None:
            self.ses_buton.setGeometry(860, 20, 40, 40)

        self.bg_path = "images/game_background.png"
        self.bg_pixmap = QPixmap(self.bg_path).scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.update()

        # Sol üstte bakiye gösterimi
        self.bakiye_miktar = 500
        self.bakiye_gosterge = BakiyeWidget(self.bakiye_miktar, self)
        self.bakiye_gosterge.setGeometry(20, 20, 160, 50)
        self.bakiye_gosterge.show()

        # Yeni çıkış butonu
        self.cikis_buton_oyun = QPushButton("Çıkış", self)
        self.cikis_buton_oyun.setGeometry(self.width() - 90, 20, 80, 40)
        self.cikis_buton_oyun.setStyleSheet("""
            font-size: 16px;
            border-radius: 15px;
            background-color: #f0f0f0;
            color: black;
            border: none;
        }
        QPushButton:hover {
            background-color: #D3D3D3;
            border-radius: 15px;
            border: none;
        }
        """)
        self.cikis_buton_oyun.clicked.connect(self.close)
        self.cikis_buton_oyun.show()

        # Bahis tutarı göstergesi
        self.bahis_tutar = 0
        self.secilen_bahisler = []
        self.bahis_label = QLabel("BET: 10", self)
        self.bahis_label.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 130);
            border-radius: 10px;
        """)
        self.bahis_label.setAlignment(Qt.AlignCenter)
        self.bahis_label.setGeometry((self.width() - 120) // 2, self.height() - 150, 140, 50)
        self.bahis_label.show()

        # Bahis jetonları
        self.bahis_degerleri = [10, 20, 50, 100]
        self.bahis_butonlari = []

        # Kart destesini yerleştir
        self.kart_destesi_label = QLabel(self)
        self.kart_destesi_pixmap = QPixmap("images/deck_back.png").scaled(130, 182, Qt.KeepAspectRatio,
                                                                          Qt.SmoothTransformation)
        self.kart_destesi_label.setPixmap(self.kart_destesi_pixmap)
        self.kart_destesi_label.setGeometry(self.width() - 160, 130, 130, 182)
        self.kart_destesi_label.show()

        # DEAL butonu
        self.deal_buton = QPushButton("DEAL", self)
        self.deal_buton.setGeometry(40, self.height() - 110, 100, 60)
        self.deal_buton.setStyleSheet("""
            font-weight: bold;
            font-size: 24px;
            color: white;
            background-color: #28a745; 
            border-radius: 15px;
            border: none;
        }
        QPushButton:hover {
            background-color: #1e7e34; 
        }
        """)
        self.deal_buton.clicked.connect(self.kartlari_dagit)
        self.deal_buton.show()

        # Kart isimleri dosya adları
        self.cards = [
            f"{value}_of_{suit}"
            for suit in ["clubs", "diamonds", "hearts", "spades"]
            for value in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
        ]

        for i, deger in enumerate(self.bahis_degerleri):
            buton = QPushButton(self)
            buton.setIcon(QIcon(f"images/chip_{deger}.png"))
            buton.setIconSize(QSize(70, 70))
            buton.setGeometry(self.width() - 320 + i * 75, self.height() - 110, 70, 70)
            buton.setStyleSheet("border: none;")
            buton.clicked.connect(lambda _, d=deger: self.bahis_arttir(d))
            buton.show()
            self.bahis_butonlari.append(buton)

        # Bahis ikonları alanı
        self.bahis_ikon_widget = QWidget(self)
        self.bahis_ikon_widget.setGeometry(20, 120, 200, 350)
        self.bahis_ikon_layout = QGridLayout(self.bahis_ikon_widget)
        self.bahis_ikon_layout.setContentsMargins(0, 0, 0, 0)
        self.bahis_ikon_layout.setVerticalSpacing(0)
        self.bahis_ikon_widget.setStyleSheet("background-color: transparent;")
        self.bahis_ikon_widget.show()
        self.ikonlar = []

        # Clear butonu
        self.clear_buton = QPushButton("Clear", self)
        self.clear_buton.setGeometry(65, 430, 100, 35)
        self.clear_buton.setStyleSheet("""
            background-color: #cc0000;
            color: white;
            font-weight: bold;
            font-size: 16px;
            border-radius: 10px;
        }
        QPushButton:hover {
            background-color: #ff4d4d;
        }
        """)
        self.clear_buton.clicked.connect(self.bahisleri_temizle)
        self.clear_buton.hide()

    def bahis_arttir(self, miktar):
        self.bahis_sesi.stop()
        if self.ses_acik:
            self.bahis_sesi.play()

        toplam_bahis = sum(self.secilen_bahisler) + miktar
        yeni_toplam = toplam_bahis + 10

        if yeni_toplam <= self.bakiye_miktar:
            self.secilen_bahisler.append(miktar)
            self.bahis_label.setText(f"BET: {yeni_toplam}")

            ikon = QLabel(self.bahis_ikon_widget)
            ikon.setPixmap(
                QPixmap(f"images/chip_{miktar}.png").scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            ikon.setFixedSize(60, 60)

            index = len(self.ikonlar)

            if index < 12:
                col = index % 3
                row = index // 3
            else:
                repeat_index = index % 12
                col = repeat_index % 3
                row = repeat_index // 3

            x = col * 65
            y = row * (65 + 10)
            ikon.move(x, y)
            ikon.show()

            self.ikonlar.append(ikon)

            if not self.clear_buton.isVisible():
                self.clear_buton.show()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Yetersiz Bakiye")
            msg.setText("Bu bahis için yeterli bakiyeniz yok.")
            msg.setIcon(QMessageBox.NoIcon)
            msg.setStandardButtons(QMessageBox.Ok)
            ok_button = msg.button(QMessageBox.Ok)
            ok_button.setText("Tamam")
            msg.exec_()

    def bahisleri_temizle(self):
        self.secilen_bahisler.clear()
        self.bahis_label.setText("BET: 10")

        for ikon in self.ikonlar:
            self.bahis_ikon_layout.removeWidget(ikon)
            ikon.deleteLater()
        self.ikonlar.clear()
        self.clear_buton.hide()

    def temizle_oyun_ogeleri(self):
        # Önceki widget'ları sil
        for attr in [
            "bakiye_gosterge", "bahis_label", "clear_buton", "deal_buton",
            "kart_destesi_label", "bahis_ikon_widget", "cikis_buton_oyun"
        ]:
            if hasattr(self, attr):
                widget = getattr(self, attr)
                if widget is not None:
                    widget.deleteLater()
                    setattr(self, attr, None)

        if hasattr(self, "bahis_butonlari"):
            for buton in self.bahis_butonlari:
                if buton is not None:
                    buton.deleteLater()
            self.bahis_butonlari = []

        # Kart destesini sıfırla
        self.cards = [
            f"{value}_of_{suit}"
            for suit in ["clubs", "diamonds", "hearts", "spades"]
            for value in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
        ]

    def deste_yeniden_olustur(self):
        self.cards = [
            f"{value}_of_{suit}"
            for suit in ["clubs", "diamonds", "hearts", "spades"]
            for value in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
        ]
        random.shuffle(self.cards)

    def kartlari_dagit(self):
        if self.ses_acik:
            self.click_ses.play()
        if self.bakiye_miktar <= 0 and not self.secilen_bahisler:
            dialog = QDialog(self)
            dialog.setWindowTitle("Oyun Bitti")
            dialog.setModal(True)
            dialog.setFixedSize(400, 170)
            dialog.setStyleSheet("background-color: white;")

            label = QLabel("Bakiyeniz tükendi.\nYeni tur başlatılamaz.", dialog)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
            label.setGeometry(20, 10, 360, 80)

            # Yeni Oyun Butonu
            yeni_oyun_btn = QPushButton("Yeni Oyun Başlat", dialog)
            yeni_oyun_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    padding: 5px;
                    font-size: 21px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            yeni_oyun_btn.setFixedSize(180, 40)
            yeni_oyun_btn.move(50, 100)  # x, y

            # Çıkış Butonu
            cikis_btn = QPushButton("Çıkış", dialog)
            cikis_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    padding: 5px;
                    font-size: 21px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            cikis_btn.setFixedSize(100, 40)
            cikis_btn.move(250, 100)  # x, y

            # Bağlantılar
            yeni_oyun_btn.clicked.connect(lambda: (dialog.close(), self.yeni_oyunu_baslat()))
            cikis_btn.clicked.connect(QApplication.instance().quit)

            dialog.exec_()
            return

        toplam_bahis = sum(self.secilen_bahisler)
        baslangic = 10
        toplam_dusulecek = toplam_bahis + baslangic

        self.bakiye_miktar -= toplam_dusulecek
        self.bakiye_gosterge.bakiye = self.bakiye_miktar
        self.bakiye_gosterge.update()
        self.kaydedilen_bahis = sum(self.secilen_bahisler) + 10
        self.secilen_bahisler.clear()

        random.shuffle(self.cards)

        if len(self.cards) < 4:
            self.deste_yeniden_olustur()

        # Kart konumları ve boyut ayarları
        kart_genislik = 100
        kart_yukseklik = 140
        aralik = 30
        merkez_x = (self.width() - kart_genislik - aralik) // 2

        # --- Oyuncu kartları ---
        oyuncu_kart1 = self.cards.pop()
        oyuncu_kart2 = self.cards.pop()

        self.oyuncu1 = QLabel(self)
        self.oyuncu2 = QLabel(self)

        pixmap_oy1 = QPixmap(f"images/cards_white_bg/{oyuncu_kart1}.png").scaled(kart_genislik, kart_yukseklik,
                                                                                 Qt.KeepAspectRatio,
                                                                                 Qt.SmoothTransformation)
        pixmap_oy2 = QPixmap(f"images/cards_white_bg/{oyuncu_kart2}.png").scaled(kart_genislik, kart_yukseklik,
                                                                                 Qt.KeepAspectRatio,
                                                                                 Qt.SmoothTransformation)
        self.oyuncu1.setPixmap(pixmap_oy1)
        self.oyuncu2.setPixmap(pixmap_oy2)

        oyuncu_y = 305
        self.kart_animasyonu_goster(self.oyuncu1, merkez_x, oyuncu_y)
        QTimer.singleShot(600, lambda: self.kart_animasyonu_goster(self.oyuncu2, merkez_x + aralik, oyuncu_y))
        QTimer.singleShot(1200, lambda: self.kart_animasyonu_goster(self.krupiye1, merkez_x, krupiye_y))
        QTimer.singleShot(1800, lambda: self.kart_animasyonu_goster(self.krupiye2, merkez_x + aralik, krupiye_y))
        QTimer.singleShot(2200, lambda: self.oyuncu_toplam_label.show())
        QTimer.singleShot(2200, lambda: self.krupiye_toplam_label.show())

        # Oyuncu toplamını göster
        oyuncu_toplam = self.kart_degeri_hesapla([oyuncu_kart1, oyuncu_kart2])
        self.oyuncu_toplam_label = QLabel(str(oyuncu_toplam), self)
        self.oyuncu_toplam_label.setStyleSheet("""
            background-color: #1E90FF;
            color: white;
            font-size: 20px;
            font-weight: bold;
            border-radius: 8px;
            padding: 6px;
        """)
        self.oyuncu_toplam_label.adjustSize()
        self.oyuncu_toplam_label.move(merkez_x - 60, oyuncu_y + 50)

        # Krupiye kartları
        if not self.cards:
            self.deste_yeniden_olustur()
        krupiye_kart = self.cards.pop()
        self.krupiye1_kart = krupiye_kart  # Krupiyenin ilk kartını kaydet

        self.krupiye1 = QLabel(self)
        self.krupiye2 = QLabel(self)

        pixmap_kr1 = QPixmap(f"images/cards_white_bg/{krupiye_kart}.png").scaled(kart_genislik, kart_yukseklik,
                                                                                 Qt.KeepAspectRatio,
                                                                                 Qt.SmoothTransformation)
        pixmap_kr2 = QPixmap("images/cards_white_bg/card_back.png").scaled(kart_genislik, kart_yukseklik,
                                                                           Qt.KeepAspectRatio,
                                                                           Qt.SmoothTransformation)
        self.krupiye1.setPixmap(pixmap_kr1)
        self.krupiye2.setPixmap(pixmap_kr2)

        krupiye_y = 145
        self.krupiye1.setGeometry(merkez_x, krupiye_y, kart_genislik, kart_yukseklik)
        self.krupiye2.setGeometry(merkez_x + aralik, krupiye_y, kart_genislik, kart_yukseklik)

        # Krupiye açık kart toplamı
        krupiye_toplam = self.kart_degeri_hesapla([krupiye_kart])
        self.krupiye_toplam_label = QLabel(str(krupiye_toplam), self)
        self.krupiye_toplam_label.setStyleSheet("""
            background-color: #1E90FF;
            color: white;
            font-size: 20px;
            font-weight: bold;
            border-radius: 8px;
            padding: 6px;
        """)
        self.krupiye_toplam_label.adjustSize()
        self.krupiye_toplam_label.move(merkez_x - 60, krupiye_y + 50)

        # Eski butonları gizle
        self.deal_buton.hide()
        self.clear_buton.hide()
        for buton in self.bahis_butonlari:
            buton.hide()

        # Oyuncu kartları sakla
        self.oyuncu_kartlar = [oyuncu_kart1, oyuncu_kart2]
        self.oyuncu_labels = [self.oyuncu1, self.oyuncu2]
        self.krupiye_kartlar = [krupiye_kart]
        self.krupiye_labels = [self.krupiye1, self.krupiye2]

        # --- ANİMASYONLU GÖSTERİM ---
        def animasyonlu_goster():
            self.oyuncu1.show()
            #if self.ses_acik:
                #self.baslangic_kart_sesi.play()

            QTimer.singleShot(500, lambda: (
                self.oyuncu2.show(),
                self.baslangic_kart_sesi.play() if self.ses_acik else None
            ))
            QTimer.singleShot(1100, lambda: (
                self.krupiye1.show(),
                self.baslangic_kart_sesi.play() if self.ses_acik else None
            ))
            QTimer.singleShot(1700, lambda: (
                self.krupiye2.show(),
                self.baslangic_kart_sesi.play() if self.ses_acik else None
            ))
            QTimer.singleShot(2200, lambda: self.oyuncu_toplam_label.show())
            QTimer.singleShot(2200, lambda: self.krupiye_toplam_label.show())

        # STAND butonu
        self.stand_buton = QPushButton("Stand", self)
        self.stand_buton.setGeometry(40, self.height() - 110, 100, 60)
        self.stand_buton.setStyleSheet("""
                        font-weight: bold;
                        font-size: 22px;
                        color: white;
                        background-color: #ffc107;  /* Sarı */
                        border-radius: 15px;
                        border: none;
                    """)
        self.stand_buton.clicked.connect(self.stand_oyna)
        self.stand_buton.show()

        # DOUBLE butonu
        self.double_buton = QPushButton("Double", self)
        self.double_buton.setGeometry(self.width() - 160, self.height() - 110, 100, 60)
        self.double_buton.setStyleSheet("""
                        font-weight: bold;
                        font-size: 22px;
                        color: white;
                        background-color: #1E90FF;  /* Mavi */
                        border-radius: 15px;
                        border: none;
                    """)
        self.double_buton.clicked.connect(self.double_oyna)
        self.double_buton.show()

        self.double_buton.setEnabled(True)
        self.double_buton.setVisible(True)
        self.double_hakki_var = True

        # HIT butonu
        self.hit_buton = QPushButton("Hit", self)
        self.hit_buton.setGeometry(self.width() - 270, self.height() - 110, 100, 60)
        self.hit_buton.setStyleSheet("""
                        font-weight: bold;
                        font-size: 22px;
                        color: white;
                        background-color: #1E90FF;  /* Mavi */
                        border-radius: 15px;
                        border: none;
                    """)
        self.hit_buton.clicked.connect(self.hit_oyna)

        # Başlat
        QTimer.singleShot(200, animasyonlu_goster)
        self.hit_buton.show()

        # Oyuncu kartlarını ve QLabel'larını sakla
        self.oyuncu_kartlar = [oyuncu_kart1, oyuncu_kart2]
        self.oyuncu_labels = [self.oyuncu1, self.oyuncu2]

    def oyunu_sifirla(self):
        self.stand_buton.hide()
        self.hit_buton.hide()
        self.double_buton.hide()
        self.deal_buton.show()

        self.bahis_label.setText("BET: 10")
        self.secilen_bahisler.clear()

        for buton in self.bahis_butonlari:
            buton.show()

        self.krupiye_kart_listesi = []

    def stand_oyna(self):
        # Krupiyenin kapalı kartını aç
        if not self.cards:
            self.deste_yeniden_olustur()
        self.krupiye_kartlar = [self.krupiye1_kart, self.cards.pop()]

        pixmap_kr2 = QPixmap(f"images/cards_white_bg/{self.krupiye_kartlar[1]}.png").scaled(
            100, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.krupiye2.setPixmap(pixmap_kr2)
        self.krupiye2.repaint()

        # Krupiye toplamını hesapla
        krupiye_toplam = self.kart_degeri_hesapla(self.krupiye_kartlar)
        self.krupiye_toplam_label.setText(str(krupiye_toplam))
        self.krupiye_toplam_label.adjustSize()

        merkez_x = (self.width() - 100 - 30) // 2
        self.krupiye_kart_index = 2

        # Oyuncu toplamını alma
        oyuncu_toplam_final = int(self.oyuncu_toplam_label.text())
        bahis = self.kaydedilen_bahis
        kazanc = bahis * 2

        def kart_cek_animasyonlu():
            nonlocal merkez_x
            krupiye_toplam = self.kart_degeri_hesapla(self.krupiye_kartlar)

            if krupiye_toplam < 17:
                if not self.cards:  # Eğer deste boşsa yeniden oluştur
                    self.deste_yeniden_olustur()

                yeni_kart = self.cards.pop()
                self.krupiye_kartlar.append(yeni_kart)

                yeni_label = QLabel(self)
                yeni_pixmap = QPixmap(f"images/cards_white_bg/{yeni_kart}.png").scaled(
                    100, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                yeni_label.setPixmap(yeni_pixmap)
                self.kart_animasyonu_goster(yeni_label, merkez_x + self.krupiye_kart_index * 30, 145)
                yeni_label.show()
                self.krupiye_labels.append(yeni_label)

                self.krupiye_kart_index += 1

                # Krupiye toplamını güncelle
                krupiye_toplam = self.kart_degeri_hesapla(self.krupiye_kartlar)
                self.krupiye_toplam_label.setText(str(krupiye_toplam))
                self.krupiye_toplam_label.adjustSize()

                QTimer.singleShot(600, kart_cek_animasyonlu)  # 600 ms sonra sıradaki kartı çek
            else:
                QTimer.singleShot(600, mesaj_goster)  # 600 ms sonra mesaj göster

        def mesaj_goster():
            krupiye_toplam = self.kart_degeri_hesapla(self.krupiye_kartlar)

            if krupiye_toplam > 21:
                self.sonuc_goster("Krupiye battı! Kazandınız.", "gold")
                self.bakiye_miktar += kazanc
            elif krupiye_toplam > oyuncu_toplam_final:
                self.sonuc_goster("Krupiye kazandı!", "red")
            elif krupiye_toplam < oyuncu_toplam_final:
                self.sonuc_goster("Kazandınız!", "gold")
                self.bakiye_miktar += kazanc
            else:
                self.sonuc_goster("Berabere!", "blue")
                self.bakiye_miktar += bahis

            # Bakiye güncelle
            self.bakiye_gosterge.bakiye = self.bakiye_miktar
            self.bakiye_gosterge.update()

            # Temizliği 2 saniye sonra yap
            QTimer.singleShot(2000, lambda: (
                self.turu_temizle(),
                self.stand_buton.hide(),
                self.hit_buton.hide(),
                self.double_buton.hide(),
                self.deal_buton.show(),
                [buton.show() for buton in self.bahis_butonlari],
                self.bahis_label.setText("BET: 10"),
                self.secilen_bahisler.clear(),
                self.bahisleri_temizle()
            ))

        # İlk kart dağıtımı animasyonu başlat
        QTimer.singleShot(400, kart_cek_animasyonlu)

    def hit_oyna(self):
        self.double_hakki_var = False
        self.double_buton.setEnabled(False)
        self.double_buton.setVisible(False)

        if not self.cards:
            self.deste_yeniden_olustur()

        # Yeni kart çek
        yeni_kart = self.cards.pop()
        self.oyuncu_kartlar.append(yeni_kart)

        yeni_label = QLabel(self)
        yeni_pixmap = QPixmap(f"images/cards_white_bg/{yeni_kart}.png").scaled(100, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        kart_sayisi = len(self.oyuncu_labels)
        merkez_x = (self.width() - 100 - 30) // 2
        yeni_label.setPixmap(yeni_pixmap)
        self.kart_animasyonu_goster(yeni_label, merkez_x + kart_sayisi * 30, 305)
        self.oyuncu_labels.append(yeni_label)

        # Toplamı güncelle
        oyuncu_toplam = self.kart_degeri_hesapla(self.oyuncu_kartlar)
        self.oyuncu_toplam_label.setText(str(oyuncu_toplam))
        self.oyuncu_toplam_label.adjustSize()

        # 300 ms sonra hem oyuncu kartını hem kurpiyeyi göster
        def kartlari_goster():
            yeni_label.show()

            if oyuncu_toplam > 21 and len(self.krupiye_kartlar) == 1:
                if not self.cards:
                    self.deste_yeniden_olustur()
                ikinci_kart = self.cards.pop()
                self.krupiye_kartlar.append(ikinci_kart)

                pixmap_kr2 = QPixmap(f"images/cards_white_bg/{ikinci_kart}.png").scaled(
                    100, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.krupiye2.setPixmap(pixmap_kr2)
                self.krupiye2.repaint()

                # Krupiye toplamını güncelle
                krupiye_toplam = self.kart_degeri_hesapla(self.krupiye_kartlar)
                self.krupiye_toplam_label.setText(str(krupiye_toplam))
                self.krupiye_toplam_label.adjustSize()

        QTimer.singleShot(300, kartlari_goster)

        if oyuncu_toplam > 21:
            def kaybetti_mesaj():
                self.sonuc_goster("21'i geçtiniz! Krupiye kazandı.", "red")

                # Tüm temizlik işlemlerini 2 saniye sonra yap
                QTimer.singleShot(2000, lambda: (
                    self.turu_temizle(),
                    self.stand_buton.hide(),
                    self.hit_buton.hide(),
                    self.double_buton.hide(),
                    self.deal_buton.show(),
                    [buton.show() for buton in self.bahis_butonlari],
                    self.bahis_label.setText("BET: 10"),
                    self.secilen_bahisler.clear(),
                    self.bahisleri_temizle()
                ))

            QTimer.singleShot(600, kaybetti_mesaj)
            return

    def double_oyna(self):
        # Gerekli miktarı hesapla (mevcut bahis kadar daha düşecek)
        gerekli_bakiye = self.kaydedilen_bahis

        if self.bakiye_miktar < gerekli_bakiye:
            QMessageBox.warning(self, "Yetersiz Bakiye", "Double yapacak kadar bakiyeniz yok!")
            return

        # Bakiye yeterliyse double işlemini uygula
        self.double_hakki_var = False
        self.double_buton.setEnabled(False)
        self.double_buton.setVisible(False)

        # Bakiye düşür
        self.bakiye_miktar -= gerekli_bakiye
        self.bakiye_gosterge.bakiye = self.bakiye_miktar
        self.bakiye_gosterge.update()

        # Bahisi iki katına çıkar
        self.kaydedilen_bahis *= 2
        self.bahis_label.setText(f"BET: {self.kaydedilen_bahis}")

        # Oyuncuya bir kart daha ver
        if not self.cards:
            self.deste_yeniden_olustur()

        yeni_kart = self.cards.pop()
        self.oyuncu_kartlar.append(yeni_kart)

        yeni_label = QLabel(self)
        yeni_pixmap = QPixmap(f"images/cards_white_bg/{yeni_kart}.png").scaled(100, 140, Qt.KeepAspectRatio,
                                                                               Qt.SmoothTransformation)

        kart_sayisi = len(self.oyuncu_labels)
        merkez_x = (self.width() - 100 - 30) // 2
        yeni_label.setPixmap(yeni_pixmap)
        self.kart_animasyonu_goster(yeni_label, merkez_x + kart_sayisi * 30, 305)
        yeni_label.show()
        self.oyuncu_labels.append(yeni_label)

        # Toplamı güncelle
        oyuncu_toplam = self.kart_degeri_hesapla(self.oyuncu_kartlar)
        self.oyuncu_toplam_label.setText(str(oyuncu_toplam))
        self.oyuncu_toplam_label.adjustSize()

        # Eğer 21'i geçtiyse oyuncu kaybeder
        if oyuncu_toplam > 21:
            def kaybetti_mesaj():
                self.sonuc_goster("21'i geçtiniz! Krupiye kazandı.", "red")

                # Tüm temizlik işlemlerini 2 saniye sonra yap
                QTimer.singleShot(2000, lambda: (
                    self.turu_temizle(),
                    self.stand_buton.hide(),
                    self.hit_buton.hide(),
                    self.double_buton.hide(),
                    self.deal_buton.show(),
                    [buton.show() for buton in self.bahis_butonlari],
                    self.bahis_label.setText("BET: 10"),
                    self.secilen_bahisler.clear(),
                    self.bahisleri_temizle()
                ))

            QTimer.singleShot(600, kaybetti_mesaj)  # 600ms sonra mesaj gözüksün
            return

        # Eğer 21'i geçmediyse, kartı gösterdikten 600ms sonra Stand'a geç
        QTimer.singleShot(600, self.stand_oyna)

    def kart_degeri_hesapla(self, kartlar):
        toplam = 0
        as_sayisi = 0

        for kart in kartlar:
            deger = kart.split("_")[0]
            if deger in ["jack", "queen", "king"]:
                toplam += 10
            elif deger == "ace":
                toplam += 11
                as_sayisi += 1
            else:
                toplam += int(deger)

        # As 11 → 1 dönüşümü
        while toplam > 21 and as_sayisi > 0:
            toplam -= 10
            as_sayisi -= 1

        return toplam

    def turu_temizle(self):
        # Oyuncu kartlarını temizle
        if hasattr(self, "oyuncu_labels"):
            for label in self.oyuncu_labels:
                if label:
                    label.setParent(None)
                    label.deleteLater()
            self.oyuncu_labels = []
            self.oyuncu_kartlar = []

        # Krupiye kartlarını temizle
        if hasattr(self, "krupiye_labels"):
            for label in self.krupiye_labels:
                if label:
                    label.setParent(None)
                    label.deleteLater()
            self.krupiye_labels = []
            self.krupiye_kartlar = []

        # Toplam kutularını sil
        for attr in ["oyuncu_toplam_label", "krupiye_toplam_label"]:
            if hasattr(self, attr):
                try:
                    label = getattr(self, attr)
                    if label:
                        label.setParent(None)
                        label.deleteLater()
                except RuntimeError:
                    pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = BlackjackGirisEkrani()
    pencere.show()
    sys.exit(app.exec_())