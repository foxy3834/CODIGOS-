import sys
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QLineEdit, QStackedWidget, QFrame, 
    QProgressBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# --- CONFIGURAÇÕES VISUAIS LIGHT (Branco, Vermelho e Azul) ---
COR_FUNDO = "#F3F4F6"      # Cinza claríssimo (quase branco)
COR_CARD = "#FFFFFF"       # Branco Puro
COR_INPUT = "#FFFFFF"      # Branco
COR_TEXTO = "#1F2937"      # Slate 900 (para contraste no branco)
COR_SUBTEXTO = "#6B7280"   # Cinza Médio
COR_PRIMARIA = "#1E40AF"   # Azul Royal (Principal)
COR_DESTAQUE = "#DC2626"   # Vermelho Vibrante
COR_BORDA = "#E5E7EB"      # Cinza de contorno
COR_SUCCESS = "#059669"    # Verde Sucesso (mantido para feedback positivo)

class AlumiEasyUltimate(QWidget):
    def _init_(self):
        super()._init_()
        self.modo_calculo = 1
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("AlumiEasy Pro v2.0")
        self.setFixedSize(400, 620)
        self.setStyleSheet(f"background-color: {COR_FUNDO}; color: {COR_TEXTO}; font-family: 'Segoe UI', sans-serif;")

        self.stack = QStackedWidget()
        self.stack.addWidget(self.tela_menu())
        self.stack.addWidget(self.tela_calculo())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.stack)

    def style_card(self):
        return f"QFrame {{ background-color: {COR_CARD}; border-radius: 15px; border: 1px solid {COR_BORDA}; }}"

    # --- TELAS ---
    def tela_menu(self):
        tela = QWidget()
        layout = QVBoxLayout(tela)

        # Cabeçalho com Ícone Simbólico
        icon_label = QLabel("⧉")
        icon_label.setStyleSheet(f"font-size: 50px; color: {COR_DESTAQUE}; margin-bottom: -10px;")
        icon_label.setAlignment(Qt.AlignCenter)
        
        titulo = QLabel("ALUMIEASY")
        titulo.setStyleSheet(f"font-size: 26px; font-weight: 900; letter-spacing: 3px; color: {COR_PRIMARIA};")
        titulo.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet(self.style_card())
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(20, 30, 20, 30)

        opcoes = [
            ("TAMANHOS CAMARÃO", 1),
            ("CONTA FOLHAS – TIPO 2", 2),
            ("CONTA FOLHAS – TIPO 3", 3),
            ("CONTA FOLHAS – TIPO 4", 4)
        ]

        for texto, modo in opcoes:
            btn = QPushButton(texto)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COR_PRIMARIA}; color: white; border-radius: 8px;
                    padding: 14px; font-weight: bold; border: none;
                }}
                QPushButton:hover {{ background-color: {COR_DESTAQUE}; }}
            """)
            btn.clicked.connect(lambda checked, m=modo: self.abrir_modo(m))
            card_layout.addWidget(btn)

        layout.addWidget(icon_label)
        layout.addWidget(titulo)
        layout.addSpacing(30)
        layout.addWidget(card)
        layout.addStretch()
        return tela

    def tela_calculo(self):
        tela = QWidget()
        layout = QVBoxLayout(tela)

        self.lbl_modo = QLabel("MODO")
        self.lbl_modo.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COR_DESTAQUE}; letter-spacing: 1px;")
        self.lbl_modo.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet(self.style_card())
        card_layout = QVBoxLayout(card)

        # Inputs Modernos
        estilo_input = f"""
            QLineEdit {{
                background-color: {COR_INPUT}; border: 1px solid {COR_BORDA};
                border-radius: 10px; padding: 12px; color: {COR_TEXTO}; font-size: 15px;
            }}
            QLineEdit:focus {{ border: 2px solid {COR_PRIMARIA}; background-color: white; }}
        """
        self.in_vao = QLineEdit(); self.in_vao.setPlaceholderText("Vão Total (mm)"); self.in_vao.setStyleSheet(estilo_input)
        self.in_nf = QLineEdit(); self.in_nf.setPlaceholderText("Nº de Folhas"); self.in_nf.setStyleSheet(estilo_input)

        # Barra de Progresso
        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(6)
        self.pbar.setTextVisible(False)
        self.pbar.setStyleSheet(f"""
            QProgressBar {{ background-color: {COR_BORDA}; border-radius: 3px; border: none; }}
            QProgressBar::chunk {{ background-color: {COR_PRIMARIA}; border-radius: 3px; }}
        """)
        self.pbar.hide()

        btn_calcular = QPushButton("PROCESSAR MEDIDAS")
        btn_calcular.setCursor(Qt.PointingHandCursor)
        btn_calcular.setStyleSheet(f"""
            QPushButton {{
                background-color: {COR_DESTAQUE}; color: white; border-radius: 10px;
                padding: 15px; font-weight: 800; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #B91C1C; }}
        """)
        btn_calcular.clicked.connect(self.animar_calculo)

        # Área de Resultados
        self.frame_res = QFrame()
        self.frame_res.setStyleSheet(f"background-color: {COR_FUNDO}; border-radius: 10px; border: 1px dashed {COR_BORDA};")
        res_layout = QVBoxLayout(self.frame_res)
        self.txt_r1 = QLabel("---"); self.txt_r2 = QLabel("---")
        for t in [self.txt_r1, self.txt_r2]:
            t.setAlignment(Qt.AlignCenter)
            t.setStyleSheet(f"color: {COR_SUBTEXTO}; font-family: 'Consolas', monospace; font-size: 16px;")
        res_layout.addWidget(self.txt_r1); res_layout.addWidget(self.txt_r2)

        btn_voltar = QPushButton("VOLTAR AO INÍCIO")
        btn_voltar.setStyleSheet(f"background: transparent; color: {COR_PRIMARIA}; border: 1px solid {COR_PRIMARIA}; padding: 10px; border-radius: 8px;")
        btn_voltar.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        card_layout.addSpacing(10)
        card_layout.addWidget(self.in_vao); card_layout.addWidget(self.in_nf)
        card_layout.addWidget(self.pbar)
        card_layout.addWidget(btn_calcular)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.frame_res)
        card_layout.addStretch()
        card_layout.addWidget(btn_voltar)

        layout.addWidget(self.lbl_modo)
        layout.addWidget(card)
        return tela

    # --- LÓGICA E ANIMAÇÕES ---
    def abrir_modo(self, modo):
        self.modo_calculo = modo
        titulos = {1: "📐 TAMANHOS CAMARÃO", 2: "📄 TIPO 2", 3: "📄 TIPO 3", 4: "📄 TIPO 4"}
        self.lbl_modo.setText(titulos[modo])
        self.in_vao.clear(); self.in_nf.clear()
        self.frame_res.setStyleSheet(f"background-color: {COR_FUNDO}; border-radius: 10px; border: 1px dashed {COR_BORDA};")
        self.txt_r1.setText("---"); self.txt_r2.setText("---")
        self.txt_r1.setStyleSheet(f"color: {COR_SUBTEXTO}; font-size: 16px;")
        self.txt_r2.setStyleSheet(f"color: {COR_SUBTEXTO}; font-size: 16px;")
        self.stack.setCurrentIndex(1)

    def animar_calculo(self):
        self.pbar.show()
        self.pbar.setValue(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pbar)
        self.timer.start(15)

    def update_pbar(self):
        val = self.pbar.value() + 5
        self.pbar.setValue(val)
        if val >= 100:
            self.timer.stop()
            self.pbar.hide()
            self.efetuar_calculo()

    def efetuar_calculo(self):
        try:
            vao = float(self.in_vao.text().replace(',', '.'))
            nf = float(self.in_nf.text())
            ec = {4: 5, 6: 10, 8: 15}.get(nf, 0)

            if self.modo_calculo == 1:
                y = (vao / 2) / (nf / 2)
                fmenor = (y - 81 + 5) if nf == 4 else (y - 81)
                fmaior = (((y * 2) - ec - 2.5) / 2) + 11
            elif self.modo_calculo == 2:
                fmenor, fmaior = (vao / nf) - 50, (vao / nf) + 30
            elif self.modo_calculo == 3:
                fmenor = (vao * 0.45) / nf
                fmaior = fmenor + 25
            else: # modo 4
                fmenor = (vao / 3) - (nf * 2)
                fmaior = fmenor + 40

            self.txt_r1.setText(f"FOLHA MENOR: {fmenor:.2f}mm")
            self.txt_r2.setText(f"FOLHA MAIOR: {fmaior:.2f}mm")
            self.txt_r1.setStyleSheet(f"color: {COR_SUCCESS}; font-weight: bold; font-size: 18px;")
            self.txt_r2.setStyleSheet(f"color: {COR_SUCCESS}; font-weight: bold; font-size: 18px;")
            self.frame_res.setStyleSheet(f"background-color: #ECFDF5; border-radius: 10px; border: 2px solid {COR_SUCCESS};")

        except:
            self.txt_r1.setText("ERRO TÉCNICO")
            self.txt_r2.setText("Verifique os números")
            self.frame_res.setStyleSheet(f"background-color: #FEF2F2; border-radius: 10px; border: 2px solid {COR_DESTAQUE};")
            self.txt_r1.setStyleSheet(f"color: {COR_DESTAQUE}; font-weight: bold;")
            self.txt_r2.setStyleSheet(f"color: {COR_DESTAQUE};")

if __name__ == "_main_":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = AlumiEasyUltimate()
    win.show()
    sys.exit(app.exec())