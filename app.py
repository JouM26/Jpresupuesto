import csv
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform as kivy_platform
from kivy.uix.boxlayout import BoxLayout as KivyBoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton as MDMiniButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except Exception:
    FPDF_AVAILABLE = False

# --- INTERFAZ DE USUARIO (LENGUAJE KV) ---
KV = '''
MDBoxLayout:
    orientation: 'vertical'

    MDTopAppBar:
        title: "Control de Cotizaciones"
        elevation: 4
        md_bg_color: app.color_primary
        specific_text_color: 1, 1, 1, 1

    MDBottomNavigation:
        panel_color: app.color_secondary

        # PESTAÑA 1: CREAR PRESUPUESTO
        MDBottomNavigationItem:
            name: 'screen_nuevo'
            text: 'Nuevo'
            icon: 'file-plus'

            ScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: "20dp"
                    spacing: "15dp"
                    size_hint_y: None
                    height: self.minimum_height

                    MDTextField:
                        id: cliente_nombre_input
                        hint_text: "Nombre del Cliente"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: cliente_rut_input
                        hint_text: "RUT"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: cliente_correo_input
                        hint_text: "Correo"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: cliente_celular_input
                        hint_text: "Numero Celular"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: cliente_direccion_input
                        hint_text: "Direccion"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: fecha_input
                        hint_text: "Fecha (YYYY-MM-DD)"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDLabel:
                        text: "Items"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: app.color_primary

                    MDBoxLayout:
                        size_hint_y: None
                        height: "42dp"
                        spacing: "8dp"

                        MDRaisedButton:
                            text: "+ Agregar Item"
                            md_bg_color: app.color_primary
                            text_color: 1, 1, 1, 1
                            on_release: app.agregar_fila_item()

                        MDRaisedButton:
                            text: "Limpiar Items"
                            md_bg_color: app.color_secondary
                            text_color: app.color_primary
                            on_release: app.limpiar_items()

                    MDBoxLayout:
                        size_hint_y: None
                        height: "26dp"
                        spacing: "4dp"

                        MDLabel:
                            text: "Item"
                        MDLabel:
                            text: "Descripcion"
                        MDLabel:
                            text: "Cant."
                        MDLabel:
                            text: "P. Unitario"
                        MDLabel:
                            text: "P. Total"
                        MDLabel:
                            text: ""

                    ScrollView:
                        size_hint_y: None
                        height: "220dp"

                        MDBoxLayout:
                            id: items_container
                            orientation: "vertical"
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: "6dp"

                    MDTextField:
                        id: notas_input
                        hint_text: "Notas (opcional)"
                        mode: "rectangle"
                        multiline: True
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: condiciones_input
                        hint_text: "Condiciones comerciales (opcional)"
                        mode: "rectangle"
                        multiline: True
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: vencimiento_dias_input
                        hint_text: "Vigencia en dias (ej: 15)"
                        mode: "rectangle"
                        input_filter: "int"
                        text: "15"
                        line_color_focus: app.color_primary

                    MDLabel:
                        text: "Resumen de Totales"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: app.color_primary

                    MDCard:
                        size_hint_y: None
                        height: "135dp"
                        md_bg_color: app.color_surface
                        radius: [14, 14, 14, 14]
                        elevation: 2
                        padding: "12dp"

                        MDBoxLayout:
                            orientation: "vertical"
                            spacing: "8dp"

                            MDLabel:
                                id: neto_label
                                text: "Valor Neto: 0.00"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: app.color_primary

                            MDLabel:
                                id: iva_label
                                text: "IVA 19%: 0.00"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: app.color_primary

                            MDLabel:
                                id: total_label
                                text: "Valor Total: 0.00"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: app.color_accent

                    MDRaisedButton:
                        text: "Guardar y Generar PDF"
                        pos_hint: {"center_x": .5}
                        md_bg_color: app.color_primary
                        text_color: 1, 1, 1, 1
                        on_release: app.procesar_nuevo_presupuesto()

        # PESTAÑA 2: HISTORIAL DE PRESUPUESTOS
        MDBottomNavigationItem:
            name: 'screen_historial'
            text: 'Historial'
            icon: 'history'
            on_tab_press: app.cargar_historial()

            MDBoxLayout:
                orientation: 'vertical'
                padding: "10dp"
                spacing: "8dp"

                MDTextField:
                    id: filtro_input
                    hint_text: "Buscar por cliente, proyecto o numero"
                    mode: "rectangle"
                    line_color_focus: app.color_primary
                    on_text: app.cargar_historial(self.text)

                MDBoxLayout:
                    size_hint_y: None
                    height: "46dp"
                    spacing: "8dp"

                    MDRaisedButton:
                        text: "Actualizar"
                        md_bg_color: app.color_primary
                        text_color: 1, 1, 1, 1
                        on_release: app.cargar_historial(root.ids.filtro_input.text)

                    MDRaisedButton:
                        text: "Exportar CSV"
                        md_bg_color: app.color_secondary
                        text_color: app.color_primary
                        on_release: app.exportar_historial_csv()

                    MDRaisedButton:
                        text: "Exportar PDF"
                        md_bg_color: app.color_secondary
                        text_color: app.color_primary
                        on_release: app.exportar_historial_pdf()

                ScrollView:
                    MDBoxLayout:
                        id: historial_cards
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: "10dp"
                        padding: "2dp"

        # PESTAÑA 3: CONFIGURACIÓN EMPRESA
        MDBottomNavigationItem:
            name: 'screen_config'
            text: 'Configuracion'
            icon: 'cog-outline'
            on_tab_press: app.cargar_configuracion_ui()

            ScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: "20dp"
                    spacing: "12dp"
                    size_hint_y: None
                    height: self.minimum_height

                    MDLabel:
                        text: "Datos de la Empresa Emisora"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: app.color_primary

                    MDTextField:
                        id: config_empresa_nombre_input
                        hint_text: "Nombre Empresa"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: config_empresa_rut_input
                        hint_text: "RUT Empresa"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: config_empresa_correo_input
                        hint_text: "Correo Empresa"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: config_empresa_celular_input
                        hint_text: "Celular Empresa"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: config_empresa_direccion_input
                        hint_text: "Direccion Empresa"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDTextField:
                        id: config_logo_path_input
                        hint_text: "Logo Empresa (ruta de imagen)"
                        mode: "rectangle"
                        line_color_focus: app.color_primary

                    MDBoxLayout:
                        size_hint_y: None
                        height: "46dp"
                        spacing: "8dp"

                        MDRaisedButton:
                            text: "Guardar Datos"
                            md_bg_color: app.color_primary
                            text_color: 1, 1, 1, 1
                            on_release: app.guardar_configuracion_empresa()

                        MDRaisedButton:
                            text: "Limpiar"
                            md_bg_color: app.color_secondary
                            text_color: app.color_primary
                            on_release: app.confirmar_limpiar_configuracion()
'''

class PresupuestoApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.moneda_default = "CLP"
        self.color_primary = (0.12, 0.22, 0.35, 1)
        self.color_secondary = (0.88, 0.92, 0.96, 1)
        self.color_surface = (0.96, 0.97, 0.99, 1)
        self.color_accent = (0.04, 0.46, 0.34, 1)
        self.empresa_nombre = "Mi Empresa"
        self.empresa_rut = "RUT 00.000.000-0"
        self.empresa_correo = "contacto@miempresa.com"
        self.empresa_celular = ""
        self.empresa_direccion = ""
        self.empresa_logo_path = ""
        self.empresa_contacto = "contacto@miempresa.com"
        self.filtro_actual = ""
        self.item_rows = []
        Window.clearcolor = (0.95, 0.96, 0.98, 1)
        
        # Inicializar la Base de Datos al arrancar la app
        self.init_db()
        
        return Builder.load_string(KV)

    def on_start(self):
        self.root.ids.fecha_input.text = datetime.now().strftime("%Y-%m-%d")
        self.limpiar_items()
        self.cargar_configuracion_ui()
        self.cargar_historial("")

    # --- LÓGICA DE BASE DE DATOS (SQLITE) ---
    def init_db(self):
        """Crea la base de datos y la tabla si no existen."""
        self.conn = sqlite3.connect("presupuestos.db")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT,
                cliente TEXT NOT NULL,
                cliente_rut TEXT DEFAULT '',
                cliente_correo TEXT DEFAULT '',
                cliente_celular TEXT DEFAULT '',
                cliente_direccion TEXT DEFAULT '',
                fecha_documento TEXT DEFAULT '',
                proyecto TEXT NOT NULL,
                costo REAL NOT NULL,
                neto REAL DEFAULT 0,
                iva REAL DEFAULT 0,
                total REAL DEFAULT 0,
                items_json TEXT DEFAULT '[]',
                moneda TEXT DEFAULT 'USD',
                notas TEXT DEFAULT '',
                condiciones TEXT DEFAULT '',
                fecha_creacion TEXT,
                fecha_vencimiento TEXT,
                pdf_path TEXT DEFAULT ''
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion_empresa (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                nombre TEXT DEFAULT '',
                rut TEXT DEFAULT '',
                correo TEXT DEFAULT '',
                celular TEXT DEFAULT '',
                direccion TEXT DEFAULT '',
                logo_path TEXT DEFAULT ''
            )
        ''')
        self.aplicar_migraciones()
        self.aplicar_migraciones_configuracion()
        self.cursor.execute("UPDATE cotizaciones SET numero = ('COT-' || printf('%06d', id)) WHERE numero IS NULL OR numero = ''")
        self.cursor.execute(
            '''
            INSERT INTO configuracion_empresa (id, nombre, rut, correo, celular, direccion, logo_path)
            SELECT 1, ?, ?, ?, ?, ?, ?
            WHERE NOT EXISTS (SELECT 1 FROM configuracion_empresa WHERE id = 1)
            ''',
            (
                self.empresa_nombre,
                self.empresa_rut,
                self.empresa_correo,
                self.empresa_celular,
                self.empresa_direccion,
                self.empresa_logo_path,
            ),
        )
        self.cargar_configuracion_empresa_desde_db()
        self.conn.commit()

    def aplicar_migraciones_configuracion(self):
        """Agrega columnas faltantes en la configuración de empresa."""
        self.cursor.execute("PRAGMA table_info(configuracion_empresa)")
        columnas = {col[1] for col in self.cursor.fetchall()}
        if "logo_path" not in columnas:
            self.cursor.execute("ALTER TABLE configuracion_empresa ADD COLUMN logo_path TEXT DEFAULT ''")

    def actualizar_contacto_empresa(self):
        partes = [self.empresa_correo.strip(), self.empresa_celular.strip()]
        contacto = " | ".join([x for x in partes if x])
        self.empresa_contacto = contacto or "Sin contacto"

    def cargar_configuracion_empresa_desde_db(self):
        """Carga datos de empresa guardados y actualiza variables de la app."""
        self.cursor.execute("SELECT nombre, rut, correo, celular, direccion, logo_path FROM configuracion_empresa WHERE id = 1")
        row = self.cursor.fetchone()
        if not row:
            return
        self.empresa_nombre = row["nombre"] or "Mi Empresa"
        self.empresa_rut = row["rut"] or "RUT 00.000.000-0"
        self.empresa_correo = row["correo"] or ""
        self.empresa_celular = row["celular"] or ""
        self.empresa_direccion = row["direccion"] or ""
        self.empresa_logo_path = row["logo_path"] or ""
        self.actualizar_contacto_empresa()

    def cargar_configuracion_ui(self):
        """Pinta en la UI los datos de empresa almacenados."""
        self.cargar_configuracion_empresa_desde_db()
        if not self.root:
            return
        self.root.ids.config_empresa_nombre_input.text = self.empresa_nombre
        self.root.ids.config_empresa_rut_input.text = self.empresa_rut
        self.root.ids.config_empresa_correo_input.text = self.empresa_correo
        self.root.ids.config_empresa_celular_input.text = self.empresa_celular
        self.root.ids.config_empresa_direccion_input.text = self.empresa_direccion
        self.root.ids.config_logo_path_input.text = self.empresa_logo_path

    def guardar_configuracion_empresa(self):
        """Guarda datos de empresa para usar en todas las cotizaciones."""
        nombre = self.root.ids.config_empresa_nombre_input.text.strip()
        rut = self.root.ids.config_empresa_rut_input.text.strip()
        correo = self.root.ids.config_empresa_correo_input.text.strip()
        celular = self.root.ids.config_empresa_celular_input.text.strip()
        direccion = self.root.ids.config_empresa_direccion_input.text.strip()
        logo_path = self.root.ids.config_logo_path_input.text.strip()

        if not nombre:
            self.mostrar_mensaje("El nombre de empresa es obligatorio")
            return

        try:
            self.cursor.execute(
                '''
                UPDATE configuracion_empresa
                SET nombre = ?, rut = ?, correo = ?, celular = ?, direccion = ?, logo_path = ?
                WHERE id = 1
                ''',
                (nombre, rut, correo, celular, direccion, logo_path),
            )
            self.conn.commit()
            self.empresa_nombre = nombre
            self.empresa_rut = rut
            self.empresa_correo = correo
            self.empresa_celular = celular
            self.empresa_direccion = direccion
            self.empresa_logo_path = logo_path
            self.actualizar_contacto_empresa()
            self.mostrar_mensaje("Datos de empresa guardados")
        except sqlite3.Error as e:
            self.conn.rollback()
            self.mostrar_mensaje(f"Error al guardar configuracion: {e}")

    def confirmar_limpiar_configuracion(self):
        """Solicita confirmación antes de borrar la configuración de empresa."""
        layout = KivyBoxLayout(orientation='vertical', spacing=10, padding=10)
        botones = KivyBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=42)
        btn_cancelar = Button(text='Cancelar')
        btn_confirmar = Button(text='Si, limpiar')
        botones.add_widget(btn_cancelar)
        botones.add_widget(btn_confirmar)
        layout.add_widget(TextInput(text='Se eliminaran los datos de empresa guardados.', readonly=True, multiline=True))
        layout.add_widget(botones)

        popup = Popup(
            title='Confirmar limpieza',
            content=layout,
            size_hint=(0.85, 0.35),
            auto_dismiss=False,
        )

        def cancelar(_instance):
            popup.dismiss()

        def confirmar(_instance):
            popup.dismiss()
            self.limpiar_configuracion_empresa()

        btn_cancelar.bind(on_release=cancelar)
        btn_confirmar.bind(on_release=confirmar)
        popup.open()

    def limpiar_configuracion_empresa(self):
        """Borra datos de empresa y deja valores por defecto."""
        try:
            self.cursor.execute(
                '''
                UPDATE configuracion_empresa
                SET nombre = ?, rut = ?, correo = ?, celular = ?, direccion = ?, logo_path = ?
                WHERE id = 1
                ''',
                ("Mi Empresa", "RUT 00.000.000-0", "", "", "", ""),
            )
            self.conn.commit()
            self.cargar_configuracion_ui()
            self.mostrar_mensaje("Configuracion de empresa limpiada")
        except sqlite3.Error as e:
            self.conn.rollback()
            self.mostrar_mensaje(f"Error al limpiar configuracion: {e}")

    def aplicar_migraciones(self):
        """Agrega columnas faltantes en instalaciones antiguas."""
        self.cursor.execute("PRAGMA table_info(cotizaciones)")
        columnas = {col[1] for col in self.cursor.fetchall()}

        migraciones = [
            ("numero", "TEXT"),
            ("cliente_rut", "TEXT DEFAULT ''"),
            ("cliente_correo", "TEXT DEFAULT ''"),
            ("cliente_celular", "TEXT DEFAULT ''"),
            ("cliente_direccion", "TEXT DEFAULT ''"),
            ("fecha_documento", "TEXT DEFAULT ''"),
            ("neto", "REAL DEFAULT 0"),
            ("iva", "REAL DEFAULT 0"),
            ("total", "REAL DEFAULT 0"),
            ("items_json", "TEXT DEFAULT '[]'"),
            ("moneda", "TEXT DEFAULT 'USD'"),
            ("notas", "TEXT DEFAULT ''"),
            ("condiciones", "TEXT DEFAULT ''"),
            ("fecha_creacion", "TEXT"),
            ("fecha_vencimiento", "TEXT"),
            ("pdf_path", "TEXT DEFAULT ''"),
        ]

        for nombre_col, definicion in migraciones:
            if nombre_col not in columnas:
                self.cursor.execute(f"ALTER TABLE cotizaciones ADD COLUMN {nombre_col} {definicion}")

    def guardar_en_db(self, payload):
        """Inserta un registro nuevo en SQLite y devuelve su id."""
        try:
            self.cursor.execute(
                '''
                INSERT INTO cotizaciones (
                    numero, cliente, cliente_rut, cliente_correo, cliente_celular, cliente_direccion,
                    fecha_documento, proyecto, costo, neto, iva, total, items_json,
                    moneda, notas, condiciones,
                    fecha_creacion, fecha_vencimiento, pdf_path
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    "",
                    payload["cliente"],
                    payload.get("cliente_rut", ""),
                    payload.get("cliente_correo", ""),
                    payload.get("cliente_celular", ""),
                    payload.get("cliente_direccion", ""),
                    payload.get("fecha_documento", ""),
                    payload["proyecto"],
                    float(payload["costo"]),
                    float(payload.get("neto", 0)),
                    float(payload.get("iva", 0)),
                    float(payload.get("total", payload["costo"])),
                    payload.get("items_json", "[]"),
                    payload["moneda"],
                    payload["notas"],
                    payload["condiciones"],
                    payload["fecha_creacion"],
                    payload["fecha_vencimiento"],
                    payload.get("pdf_path", ""),
                )
            )
            nuevo_id = self.cursor.lastrowid
            numero = self.generar_numero_cotizacion(nuevo_id)
            self.cursor.execute("UPDATE cotizaciones SET numero = ? WHERE id = ?", (numero, nuevo_id))
            self.conn.commit()
            return nuevo_id
        except sqlite3.Error as e:
            self.conn.rollback()
            self.mostrar_mensaje(f"Error de BD al guardar: {e}")
            return None

    def actualizar_en_db(self, cotizacion_id, payload):
        """Actualiza un registro existente."""
        try:
            self.cursor.execute(
                '''
                UPDATE cotizaciones
                SET cliente = ?, proyecto = ?, costo = ?, moneda = ?, notas = ?,
                    condiciones = ?, fecha_vencimiento = ?
                WHERE id = ?
                ''',
                (
                    payload["cliente"],
                    payload["proyecto"],
                    float(payload["costo"]),
                    payload["moneda"],
                    payload["notas"],
                    payload["condiciones"],
                    payload["fecha_vencimiento"],
                    cotizacion_id,
                )
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            self.mostrar_mensaje(f"Error de BD al actualizar: {e}")
            return False

    def eliminar_de_db(self, cotizacion_id):
        """Elimina una cotizacion por id."""
        try:
            self.cursor.execute("DELETE FROM cotizaciones WHERE id = ?", (cotizacion_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            self.mostrar_mensaje(f"Error de BD al eliminar: {e}")
            return False

    def actualizar_pdf_path(self, cotizacion_id, ruta_pdf):
        """Guarda la ruta de PDF del registro."""
        try:
            self.cursor.execute("UPDATE cotizaciones SET pdf_path = ? WHERE id = ?", (ruta_pdf, cotizacion_id))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            self.mostrar_mensaje(f"No se pudo guardar la ruta PDF: {e}")

    def obtener_todos(self, filtro=""):
        """Recupera los presupuestos guardados con filtro opcional."""
        texto = (filtro or "").strip()
        if texto:
            like = f"%{texto}%"
            self.cursor.execute(
                '''
                SELECT id, numero, cliente, proyecto, costo, moneda, notas, condiciones,
                      fecha_creacion, fecha_vencimiento, pdf_path, total, neto, iva,
                      cliente_rut, cliente_correo, cliente_celular, cliente_direccion,
                      fecha_documento, items_json
                FROM cotizaciones
                WHERE cliente LIKE ? OR proyecto LIKE ? OR numero LIKE ?
                ORDER BY id DESC
                ''',
                (like, like, like),
            )
        else:
            self.cursor.execute(
                '''
                SELECT id, numero, cliente, proyecto, costo, moneda, notas, condiciones,
                      fecha_creacion, fecha_vencimiento, pdf_path, total, neto, iva,
                      cliente_rut, cliente_correo, cliente_celular, cliente_direccion,
                      fecha_documento, items_json
                FROM cotizaciones
                ORDER BY id DESC
                '''
            )
        return self.cursor.fetchall()

    # --- UTILIDADES ---
    def mostrar_mensaje(self, texto):
        """Muestra feedback en UI y conserva print como respaldo."""
        try:
            Snackbar(text=texto, duration=2.5).open()
        except Exception:
            print(texto)

    def generar_numero_cotizacion(self, cotizacion_id):
        return f"COT-{cotizacion_id:06d}"

    def simbolo_moneda(self, moneda):
        simbolos = {
            "USD": "$",
            "CLP": "$",
            "EUR": "EUR ",
            "MXN": "$",
        }
        return simbolos.get(moneda.upper(), f"{moneda.upper()} ")

    def formatear_monto(self, monto, moneda):
        simbolo = self.simbolo_moneda(moneda)
        return f"{simbolo}{monto:,.2f}"

    def calcular_fecha_vencimiento(self, dias_texto):
        dias = 15
        if dias_texto:
            dias = int(dias_texto)
        if dias <= 0 or dias > 365:
            raise ValueError("La vigencia debe estar entre 1 y 365 dias")
        return (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")

    def parse_numero(self, texto):
        valor = (texto or "").strip().replace(",", ".")
        if not valor:
            return 0.0
        return float(valor)

    def agregar_fila_item(self):
        """Agrega una fila editable de item en la UI."""
        contenedor = self.root.ids.items_container
        fila = KivyBoxLayout(orientation='horizontal', spacing=4, size_hint_y=None, height=42)

        item_input = TextInput(multiline=False, hint_text="Item")
        descripcion_input = TextInput(multiline=False, hint_text="Descripcion")
        cantidad_input = TextInput(multiline=False, hint_text="0", input_filter='float')
        unitario_input = TextInput(multiline=False, hint_text="0", input_filter='float')
        total_input = TextInput(multiline=False, text="0.00", readonly=True)
        btn_quitar = Button(text="X", size_hint_x=None, width=32)

        item_input.size_hint_x = 1.0
        descripcion_input.size_hint_x = 2.0
        cantidad_input.size_hint_x = 0.8
        unitario_input.size_hint_x = 1.0
        total_input.size_hint_x = 1.0

        fila_ref = {
            "row": fila,
            "item": item_input,
            "descripcion": descripcion_input,
            "cantidad": cantidad_input,
            "unitario": unitario_input,
            "total": total_input,
        }

        cantidad_input.bind(text=lambda _inst, _val, ref=fila_ref: self.actualizar_total_fila(ref))
        unitario_input.bind(text=lambda _inst, _val, ref=fila_ref: self.actualizar_total_fila(ref))
        btn_quitar.bind(on_release=lambda _inst, ref=fila_ref: self.eliminar_fila_item(ref))

        for widget in [item_input, descripcion_input, cantidad_input, unitario_input, total_input, btn_quitar]:
            fila.add_widget(widget)

        contenedor.add_widget(fila)
        self.item_rows.append(fila_ref)
        self.actualizar_totales_ui()

    def eliminar_fila_item(self, fila_ref):
        if len(self.item_rows) <= 1:
            self.mostrar_mensaje("Debe existir al menos un item")
            return
        if fila_ref in self.item_rows:
            self.root.ids.items_container.remove_widget(fila_ref["row"])
            self.item_rows.remove(fila_ref)
            self.actualizar_totales_ui()

    def limpiar_items(self):
        contenedor = self.root.ids.items_container
        contenedor.clear_widgets()
        self.item_rows = []
        self.agregar_fila_item()

    def actualizar_total_fila(self, fila_ref):
        try:
            cantidad = self.parse_numero(fila_ref["cantidad"].text)
            unitario = self.parse_numero(fila_ref["unitario"].text)
            total = cantidad * unitario
            fila_ref["total"].text = f"{total:.2f}"
        except ValueError:
            fila_ref["total"].text = "0.00"
        self.actualizar_totales_ui()

    def construir_items_desde_ui(self):
        """Recopila y valida items desde la grilla dinámica."""
        items = []
        for fila in self.item_rows:
            item_txt = fila["item"].text.strip()
            descripcion = fila["descripcion"].text.strip()
            cantidad_txt = fila["cantidad"].text.strip()
            unitario_txt = fila["unitario"].text.strip()

            if not any([item_txt, descripcion, cantidad_txt, unitario_txt]):
                continue

            if not descripcion:
                self.mostrar_mensaje("Cada item debe tener descripcion")
                return None

            try:
                cantidad = self.parse_numero(cantidad_txt)
                unitario = self.parse_numero(unitario_txt)
            except ValueError:
                self.mostrar_mensaje("Cantidad y precio unitario deben ser numericos")
                return None

            if cantidad <= 0 or unitario < 0:
                self.mostrar_mensaje("Cantidad debe ser > 0 y precio unitario >= 0")
                return None

            total = cantidad * unitario
            fila["total"].text = f"{total:.2f}"
            items.append(
                {
                    "item": item_txt or f"Item {len(items) + 1}",
                    "descripcion": descripcion,
                    "cantidad": cantidad,
                    "precio_unitario": unitario,
                    "precio_total": total,
                }
            )

        if not items:
            self.mostrar_mensaje("Debes ingresar al menos un item")
            return None
        return items

    def calcular_totales_desde_items(self, items):
        neto = sum(x["precio_total"] for x in items)
        iva = neto * 0.19
        total = neto + iva
        return neto, iva, total

    def actualizar_totales_ui(self):
        moneda = self.moneda_default
        items = []
        for fila in self.item_rows:
            try:
                total = self.parse_numero(fila["total"].text)
            except ValueError:
                total = 0
            items.append({"precio_total": total})
        neto = sum(x["precio_total"] for x in items)
        iva = neto * 0.19
        total = neto + iva
        self.root.ids.neto_label.text = f"Valor Neto: {self.formatear_monto(neto, moneda)}"
        self.root.ids.iva_label.text = f"IVA 19%: {self.formatear_monto(iva, moneda)}"
        self.root.ids.total_label.text = f"Valor Total: {self.formatear_monto(total, moneda)}"

    # --- ACCIONES DE LA INTERFAZ ---
    def procesar_nuevo_presupuesto(self):
        """Captura datos de la UI, valida y prepara guardado."""
        cliente = self.root.ids.cliente_nombre_input.text.strip()
        cliente_rut = self.root.ids.cliente_rut_input.text.strip()
        cliente_correo = self.root.ids.cliente_correo_input.text.strip()
        cliente_celular = self.root.ids.cliente_celular_input.text.strip()
        cliente_direccion = self.root.ids.cliente_direccion_input.text.strip()
        fecha_documento = self.root.ids.fecha_input.text.strip()
        moneda = self.moneda_default
        notas = self.root.ids.notas_input.text.strip()
        condiciones = self.root.ids.condiciones_input.text.strip()
        vencimiento_dias = self.root.ids.vencimiento_dias_input.text.strip()

        if not all([cliente, cliente_rut, cliente_correo, cliente_celular, cliente_direccion, fecha_documento]):
            self.mostrar_mensaje("Completa todos los datos del cliente y fecha")
            return

        if len(cliente) > 120:
            self.mostrar_mensaje("Nombre de cliente demasiado largo")
            return

        items = self.construir_items_desde_ui()
        if items is None:
            return
        neto, iva, total = self.calcular_totales_desde_items(items)

        try:
            datetime.strptime(fecha_documento, "%Y-%m-%d")
            fecha_vencimiento = self.calcular_fecha_vencimiento(vencimiento_dias)
        except ValueError:
            self.mostrar_mensaje("Fecha o vigencia invalidas")
            return

        proyecto = " | ".join([f"{x['item']}: {x['descripcion']}" for x in items])

        payload = {
            "cliente": cliente,
            "cliente_rut": cliente_rut,
            "cliente_correo": cliente_correo,
            "cliente_celular": cliente_celular,
            "cliente_direccion": cliente_direccion,
            "fecha_documento": fecha_documento,
            "proyecto": proyecto,
            "costo": total,
            "neto": neto,
            "iva": iva,
            "total": total,
            "items_json": json.dumps(items, ensure_ascii=False),
            "moneda": moneda,
            "notas": notas,
            "condiciones": condiciones,
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_vencimiento": fecha_vencimiento,
            "pdf_path": "",
        }

        # Pedir nombre de archivo antes de guardar y exportar.
        self.mostrar_dialogo_nombre_archivo(payload)

    def mostrar_dialogo_nombre_archivo(self, payload):
        """Muestra una ventana para confirmar o editar el nombre del PDF."""
        layout = KivyBoxLayout(orientation='vertical', spacing=10, padding=10)
        nombre_sugerido = self.sanitizar_nombre_archivo(f"Cotizacion_{payload['cliente']}")

        input_nombre = TextInput(
            text=nombre_sugerido,
            multiline=False,
            size_hint_y=None,
            height=40
        )

        layout.add_widget(input_nombre)

        botones = KivyBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=45)
        btn_cancelar = Button(text='Cancelar')
        btn_guardar = Button(text='Guardar y generar PDF')
        botones.add_widget(btn_cancelar)
        botones.add_widget(btn_guardar)
        layout.add_widget(botones)

        popup = Popup(
            title='Nombre del archivo PDF',
            content=layout,
            size_hint=(0.9, 0.35),
            auto_dismiss=False
        )

        def cancelar(_instance):
            popup.dismiss()

        def confirmar(_instance):
            nombre_archivo = input_nombre.text.strip()
            if not nombre_archivo:
                self.mostrar_mensaje("Debes indicar un nombre de archivo")
                return

            popup.dismiss()
            self.guardar_y_generar_presupuesto(payload, nombre_archivo)

        btn_cancelar.bind(on_release=cancelar)
        btn_guardar.bind(on_release=confirmar)
        popup.open()

    def guardar_y_generar_presupuesto(self, payload, nombre_archivo):
        """Guarda en BD y luego exporta/abre el PDF."""
        nuevo_id = self.guardar_en_db(payload)
        if not nuevo_id:
            return

        payload["id"] = nuevo_id
        payload["numero"] = self.generar_numero_cotizacion(nuevo_id)

        ruta_pdf = self.generar_y_abrir_pdf(payload, nombre_archivo)
        if ruta_pdf:
            self.actualizar_pdf_path(nuevo_id, ruta_pdf)
            self.mostrar_mensaje("Cotizacion guardada y PDF generado")
        else:
            self.mostrar_mensaje("Cotizacion guardada, pero hubo error al generar el PDF")

        # Limpiar los campos para un nuevo ingreso
        self.root.ids.cliente_nombre_input.text = ""
        self.root.ids.cliente_rut_input.text = ""
        self.root.ids.cliente_correo_input.text = ""
        self.root.ids.cliente_celular_input.text = ""
        self.root.ids.cliente_direccion_input.text = ""
        self.root.ids.fecha_input.text = datetime.now().strftime("%Y-%m-%d")
        self.root.ids.notas_input.text = ""
        self.root.ids.condiciones_input.text = ""
        self.limpiar_items()

        self.cargar_historial(self.filtro_actual)

    def cargar_historial(self, filtro=""):
        """Refresca la lista visible en la pestaña Historial."""
        self.filtro_actual = (filtro or "").strip()
        contenedor = self.root.ids.historial_cards
        contenedor.clear_widgets()

        registros = self.obtener_todos(self.filtro_actual)
        for item in registros:
            proyecto_corto = item["proyecto"][:35] + ("..." if len(item["proyecto"]) > 35 else "")
            monto = self.formatear_monto(item["total"] if item["total"] else item["costo"], item["moneda"])

            tarjeta = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height="120dp",
                padding="10dp",
                radius=[12, 12, 12, 12],
                elevation=1,
                md_bg_color=self.color_surface,
            )

            titulo = MDLabel(
                text=f"{item['numero']} | {item['cliente']}",
                bold=True,
                theme_text_color="Custom",
                text_color=self.color_primary,
                size_hint_y=None,
                height="26dp",
            )

            detalle = MDLabel(
                text=f"{monto} | {item['fecha_creacion']}\\n{proyecto_corto}",
                theme_text_color="Custom",
                text_color=(0.33, 0.38, 0.45, 1),
                size_hint_y=None,
                height="40dp",
            )

            acciones = KivyBoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=36)
            btn_editar = MDMiniButton(
                text="Editar",
                md_bg_color=self.color_secondary,
                text_color=self.color_primary,
            )
            btn_pdf = MDMiniButton(
                text="PDF",
                md_bg_color=self.color_primary,
                text_color=(1, 1, 1, 1),
            )
            btn_editar.bind(on_release=lambda _x, registro=dict(item): self.abrir_dialogo_edicion(registro))
            btn_pdf.bind(on_release=lambda _x, registro=dict(item): self.re_generar_pdf_desde_historial(registro))

            acciones.add_widget(btn_editar)
            acciones.add_widget(btn_pdf)

            tarjeta.add_widget(titulo)
            tarjeta.add_widget(detalle)
            tarjeta.add_widget(acciones)
            contenedor.add_widget(tarjeta)

        if not registros:
            self.mostrar_mensaje("No hay resultados en el historial")

    def abrir_dialogo_edicion(self, registro):
        """Abre formulario de edicion para un registro del historial."""
        layout = KivyBoxLayout(orientation='vertical', spacing=8, padding=10)

        cliente_input = TextInput(text=registro["cliente"], multiline=False, size_hint_y=None, height=38)
        proyecto_input = TextInput(text=registro["proyecto"], multiline=True, size_hint_y=None, height=110)
        costo_input = TextInput(text=str(registro["costo"]), multiline=False, size_hint_y=None, height=38)
        moneda_input = TextInput(text=registro["moneda"], multiline=False, size_hint_y=None, height=38)
        notas_input = TextInput(text=registro["notas"] or "", multiline=True, size_hint_y=None, height=75)
        cond_input = TextInput(text=registro["condiciones"] or "", multiline=True, size_hint_y=None, height=75)

        for widget in [cliente_input, proyecto_input, costo_input, moneda_input, notas_input, cond_input]:
            layout.add_widget(widget)

        botones = KivyBoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=42)
        btn_cancelar = Button(text='Cerrar')
        btn_guardar = Button(text='Guardar cambios')
        btn_eliminar = Button(text='Eliminar')
        botones.add_widget(btn_cancelar)
        botones.add_widget(btn_guardar)
        botones.add_widget(btn_eliminar)
        layout.add_widget(botones)

        popup = Popup(title=f"Editar {registro['numero']}", content=layout, size_hint=(0.92, 0.9), auto_dismiss=False)

        def cerrar(_instance):
            popup.dismiss()

        def guardar(_instance):
            try:
                costo_val = float(costo_input.text.strip())
                if costo_val <= 0:
                    raise ValueError("Costo invalido")
            except ValueError:
                self.mostrar_mensaje("Costo invalido en edicion")
                return

            payload = {
                "cliente": cliente_input.text.strip(),
                "proyecto": proyecto_input.text.strip(),
                "costo": costo_val,
                "moneda": (moneda_input.text.strip().upper() or "USD"),
                "notas": notas_input.text.strip(),
                "condiciones": cond_input.text.strip(),
                "fecha_vencimiento": registro["fecha_vencimiento"],
            }
            if not payload["cliente"] or not payload["proyecto"]:
                self.mostrar_mensaje("Cliente y proyecto son obligatorios")
                return

            if self.actualizar_en_db(registro["id"], payload):
                self.mostrar_mensaje("Cotizacion actualizada")
                popup.dismiss()
                self.cargar_historial(self.filtro_actual)

        def eliminar(_instance):
            if self.eliminar_de_db(registro["id"]):
                self.mostrar_mensaje("Cotizacion eliminada")
                popup.dismiss()
                self.cargar_historial(self.filtro_actual)

        btn_cancelar.bind(on_release=cerrar)
        btn_guardar.bind(on_release=guardar)
        btn_eliminar.bind(on_release=eliminar)
        popup.open()

    def re_generar_pdf_desde_historial(self, registro):
        """Regenera PDF para un registro existente y actualiza su ruta."""
        ruta_pdf = self.generar_y_abrir_pdf(dict(registro), f"Cotizacion_{registro['numero']}")
        if ruta_pdf:
            self.actualizar_pdf_path(registro["id"], ruta_pdf)
            self.mostrar_mensaje("PDF regenerado")

    def exportar_historial_csv(self):
        """Exporta el historial filtrado a CSV en Descargas."""
        registros = self.obtener_todos(self.filtro_actual)
        if not registros:
            self.mostrar_mensaje("No hay datos para exportar")
            return

        ruta_csv = self.obtener_ruta_unica("Historial_Cotizaciones", ".csv")
        try:
            with open(ruta_csv, "w", newline="", encoding="utf-8") as archivo:
                writer = csv.writer(archivo)
                writer.writerow([
                    "id", "numero", "cliente", "rut", "correo", "celular", "direccion", "fecha_documento",
                    "neto", "iva", "total", "moneda", "fecha_creacion", "fecha_vencimiento", "pdf_path"
                ])
                for row in registros:
                    writer.writerow([
                        row["id"], row["numero"], row["cliente"], row["cliente_rut"], row["cliente_correo"],
                        row["cliente_celular"], row["cliente_direccion"], row["fecha_documento"],
                        row["neto"], row["iva"], row["total"], row["moneda"], row["fecha_creacion"],
                        row["fecha_vencimiento"], row["pdf_path"]
                    ])
            self.mostrar_mensaje("CSV exportado en Descargas")
            self.abrir_pdf(ruta_csv)
        except OSError as e:
            self.mostrar_mensaje(f"Error al exportar CSV: {e}")

    def exportar_historial_pdf(self):
        """Exporta un reporte PDF del historial filtrado."""
        if not FPDF_AVAILABLE:
            self.mostrar_mensaje("Exportar PDF no disponible en esta compilacion")
            return

        registros = self.obtener_todos(self.filtro_actual)
        if not registros:
            self.mostrar_mensaje("No hay datos para exportar")
            return

        ruta_pdf = self.obtener_ruta_unica("Historial_Cotizaciones", ".pdf")
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=12)
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, self._safe_pdf_text("REPORTE DE HISTORIAL DE COTIZACIONES"), ln=1)
            pdf.ln(2)

            # Encabezado de tabla
            headers = ["Numero", "Cliente", "Monto", "Fecha"]
            widths = [38, 72, 40, 40]
            pdf.set_font("Helvetica", "B", 10)
            for i, head in enumerate(headers):
                pdf.cell(widths[i], 8, self._safe_pdf_text(head), border=1, align="L")
            pdf.ln()

            pdf.set_font("Helvetica", "", 9)
            for row in registros:
                monto = self.formatear_monto(row["total"] if row["total"] else row["costo"], row["moneda"])
                fila = [
                    str(row["numero"] or ""),
                    str(row["cliente"] or ""),
                    str(monto),
                    str(row["fecha_creacion"] or ""),
                ]
                for i, col in enumerate(fila):
                    texto = self._safe_pdf_text(col)
                    if len(texto) > 28 and i == 1:
                        texto = texto[:28] + "..."
                    pdf.cell(widths[i], 7, texto, border=1, align="L")
                pdf.ln()

            pdf.output(ruta_pdf)
            self.mostrar_mensaje("PDF de historial exportado")
            self.abrir_pdf(ruta_pdf)
        except Exception as e:
            self.mostrar_mensaje(f"Error al exportar PDF: {e}")

    # --- LÓGICA DE GENERACIÓN DE PDF ---
    def sanitizar_nombre_archivo(self, nombre_archivo):
        """Limpia caracteres no permitidos para nombres de archivo."""
        limpio = re.sub(r'[<>:"/\\|?*]', '_', nombre_archivo).strip().rstrip('.')
        return limpio or "Cotizacion"

    def obtener_carpeta_descargas(self):
        """Devuelve la ruta de la carpeta Descargas del usuario."""
        if kivy_platform == "android":
            carpeta = os.path.join(self.user_data_dir, "pdfs")
            os.makedirs(carpeta, exist_ok=True)
            return carpeta
        carpeta = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.isdir(carpeta):
            carpeta = os.path.expanduser("~")
        return carpeta

    def obtener_ruta_unica(self, nombre_base, extension):
        """Devuelve ruta disponible para no sobreescribir archivos."""
        nombre_limpio = self.sanitizar_nombre_archivo(nombre_base)
        carpeta = self.obtener_carpeta_descargas()
        ruta = os.path.join(carpeta, f"{nombre_limpio}{extension}")
        contador = 1
        while os.path.exists(ruta):
            ruta = os.path.join(carpeta, f"{nombre_limpio}_{contador}{extension}")
            contador += 1
        return ruta

    def generar_y_abrir_pdf(self, payload, nombre_archivo=None):
        """Genera el PDF y lo abre automáticamente."""
        ruta_pdf = self.exportar_a_pdf(payload, nombre_archivo)
        if ruta_pdf:
            self.abrir_pdf(ruta_pdf)
            return ruta_pdf
        return None

    def abrir_pdf(self, ruta_pdf):
        """Abre archivo con la aplicación predeterminada del sistema."""
        try:
            if kivy_platform == "android":
                # En Android evitamos apertura forzada para no romper en dispositivos sin visor asociado.
                self.mostrar_mensaje(f"Archivo generado en: {ruta_pdf}")
                return
            if os.name == "nt":
                os.startfile(ruta_pdf)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", ruta_pdf])
            else:
                subprocess.Popen(["xdg-open", ruta_pdf])
        except Exception as e:
            self.mostrar_mensaje(f"Error al abrir archivo: {e}")

    def construir_items_para_pdf(self, payload):
        """Crea items para el PDF desde items_json o fallback antiguo."""
        if payload.get("items"):
            items = payload.get("items", [])
            return [
                (
                    x.get("item", ""),
                    x.get("descripcion", ""),
                    float(x.get("cantidad", 0)),
                    float(x.get("precio_unitario", 0)),
                    float(x.get("precio_total", 0)),
                )
                for x in items
            ]

        if payload.get("items_json"):
            try:
                parsed = json.loads(payload.get("items_json", "[]"))
                if parsed:
                    return [
                        (
                            x.get("item", ""),
                            x.get("descripcion", ""),
                            float(x.get("cantidad", 0)),
                            float(x.get("precio_unitario", 0)),
                            float(x.get("precio_total", 0)),
                        )
                        for x in parsed
                    ]
            except (json.JSONDecodeError, ValueError, TypeError):
                pass

        lineas = [x.strip() for x in payload.get("proyecto", "").splitlines() if x.strip()]
        items = []
        for linea in lineas:
            if "|" in linea:
                partes = [p.strip() for p in linea.split("|")]
                if len(partes) >= 3:
                    try:
                        cantidad = float(partes[1])
                        unitario = float(partes[2])
                        items.append((f"Item {len(items)+1}", partes[0], cantidad, unitario, cantidad * unitario))
                        continue
                    except ValueError:
                        pass
            items.append((f"Item {len(items)+1}", linea, 1.0, float(payload.get("costo", 0)), float(payload.get("costo", 0))))

        if not items:
            items = [("Item 1", payload.get("proyecto", "Servicio"), 1.0, float(payload.get("costo", 0)), float(payload.get("costo", 0)))]
        return items

    def exportar_a_pdf(self, payload, nombre_archivo_personalizado=None):
        """Construye el archivo PDF estructurado con fpdf2."""
        if not FPDF_AVAILABLE:
            self.mostrar_mensaje("Generacion PDF no disponible en esta compilacion")
            return None

        if nombre_archivo_personalizado:
            base_nombre = self.sanitizar_nombre_archivo(nombre_archivo_personalizado)
        else:
            base_nombre = self.sanitizar_nombre_archivo(f"Cotizacion_{payload['numero']}_{payload['cliente']}")

        ruta_pdf = self.obtener_ruta_unica(base_nombre, ".pdf")

        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=12)
            pdf.add_page()

            if self.empresa_logo_path and os.path.isfile(self.empresa_logo_path):
                try:
                    pdf.image(self.empresa_logo_path, x=10, y=8, w=30)
                    pdf.ln(24)
                except Exception:
                    self.mostrar_mensaje("No se pudo cargar el logo para el PDF")

            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, self._safe_pdf_text("DOCUMENTO DE COTIZACION"), ln=1)

            pdf.set_font("Helvetica", "", 10)
            encabezado = [
                f"Proveedor: {self.empresa_nombre} | {self.empresa_rut}",
                f"Contacto: {self.empresa_contacto}",
                f"Direccion Empresa: {self.empresa_direccion}" if self.empresa_direccion else "",
                f"Numero: {payload['numero']}",
                f"Fecha documento: {payload.get('fecha_documento', payload['fecha_creacion'])}",
                f"Fecha emision: {payload['fecha_creacion']}",
                f"Valido hasta: {payload['fecha_vencimiento']}",
                f"Cliente: {payload['cliente']}",
                f"RUT: {payload.get('cliente_rut', '')}",
                f"Correo: {payload.get('cliente_correo', '')}",
                f"Celular: {payload.get('cliente_celular', '')}",
                f"Direccion: {payload.get('cliente_direccion', '')}",
            ]
            for linea in encabezado:
                if linea:
                    pdf.multi_cell(0, 6, self._safe_pdf_text(linea))
            pdf.ln(2)

            # Tabla de items
            items = self.construir_items_para_pdf(payload)
            widths = [22, 72, 18, 38, 40]
            headers = ["Item", "Descripcion", "Cant.", "P. Unitario", "P. Total"]

            pdf.set_font("Helvetica", "B", 9)
            for i, head in enumerate(headers):
                pdf.cell(widths[i], 8, self._safe_pdf_text(head), border=1)
            pdf.ln()

            pdf.set_font("Helvetica", "", 8)
            neto = 0
            for item_nombre, descripcion, cantidad, unitario, subtotal in items:
                neto += subtotal
                row = [
                    self._safe_pdf_text(str(item_nombre)[:14]),
                    self._safe_pdf_text(str(descripcion)[:45]),
                    self._safe_pdf_text(f"{cantidad:g}"),
                    self._safe_pdf_text(self.formatear_monto(unitario, payload["moneda"])),
                    self._safe_pdf_text(self.formatear_monto(subtotal, payload["moneda"])),
                ]
                for i, val in enumerate(row):
                    align = "R" if i >= 2 else "L"
                    pdf.cell(widths[i], 7, val, border=1, align=align)
                pdf.ln()

            iva = neto * 0.19
            total = neto + iva
            resumen = [
                ("VALOR NETO", self.formatear_monto(neto, payload["moneda"])),
                ("IVA 19%", self.formatear_monto(iva, payload["moneda"])),
                ("VALOR TOTAL", self.formatear_monto(total, payload["moneda"])),
            ]

            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            for titulo, valor in resumen:
                pdf.cell(45, 8, self._safe_pdf_text(titulo), border=1)
                pdf.cell(45, 8, self._safe_pdf_text(valor), border=1, ln=1, align="R")

            pdf.ln(3)
            pdf.set_font("Helvetica", "", 9)
            if payload.get("notas"):
                pdf.multi_cell(0, 6, self._safe_pdf_text(f"Notas: {payload['notas']}"))
            if payload.get("condiciones"):
                pdf.multi_cell(0, 6, self._safe_pdf_text(f"Condiciones comerciales: {payload['condiciones']}"))
            pdf.ln(4)
            pdf.cell(0, 7, self._safe_pdf_text("Firma / Aprobacion: __________________________"), ln=1)

            pdf.output(ruta_pdf)
            self.mostrar_mensaje(f"PDF guardado: {os.path.basename(ruta_pdf)}")
            return ruta_pdf
        except Exception as e:
            self.mostrar_mensaje(f"Error al generar PDF: {e}")
            return None

    def _safe_pdf_text(self, value):
        """Convierte texto a latin-1 para mantener compatibilidad con fuentes base de fpdf2."""
        texto = str(value or "")
        return texto.encode("latin-1", "replace").decode("latin-1")

    def on_stop(self):
        """Cierra la conexión a la base de datos al salir de la aplicación."""
        self.conn.close()

if __name__ == '__main__':
    PresupuestoApp().run()