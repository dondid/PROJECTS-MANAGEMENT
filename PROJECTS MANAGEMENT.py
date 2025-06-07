import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
import json
import matplotlib.pyplot as plt
from matplotlib import dates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from tkinter import font as tkFont


class ProjectManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Complet de Management Proiecte")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

        # Inițializare bază de date
        self.init_database()

        # Variabile pentru tracking
        self.current_project_id = None
        self.projects_data = []
        self.tasks_data = []
        self.resources_data = []
        self.risks_data = []

        # Creare interfață
        self.create_main_interface()
        self.load_all_data()

    def init_database(self):
        """Inițializează baza de date SQLite"""
        self.conn = sqlite3.connect('project_management.db')
        self.cursor = self.conn.cursor()

        # Tabel proiecte
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                budget REAL,
                status TEXT,
                priority TEXT,
                project_manager TEXT,
                methodology TEXT,
                created_date TEXT
            )
        ''')

        # Tabel taskuri/activități
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                duration INTEGER,
                dependencies TEXT,
                assigned_to TEXT,
                status TEXT,
                progress INTEGER,
                priority TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # Tabel resurse
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                type TEXT,
                cost_per_unit REAL,
                quantity INTEGER,
                total_cost REAL,
                availability TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # Tabel riscuri
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS risks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                description TEXT NOT NULL,
                probability TEXT,
                impact TEXT,
                risk_level TEXT,
                mitigation_strategy TEXT,
                status TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # Tabel stakeholderi
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stakeholders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                role TEXT,
                influence TEXT,
                interest TEXT,
                communication_plan TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        self.conn.commit()

    def create_main_interface(self):
        """Creează interfața principală cu toate modulele"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="SISTEM COMPLET DE MANAGEMENT PROIECTE",
                               font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=15)

        # Notebook pentru taburi
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Taburi principale
        self.create_dashboard_tab()
        self.create_projects_tab()
        self.create_wbs_tab()
        self.create_gantt_tab()
        self.create_resources_tab()
        self.create_methodology_tab()

    def create_dashboard_tab(self):
        """Dashboard cu overview general"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="🏠 Dashboard")

        # Statistici generale
        stats_frame = tk.LabelFrame(dashboard_frame, text="Statistici Generale", font=('Arial', 12, 'bold'))
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        stats_inner = tk.Frame(stats_frame)
        stats_inner.pack(fill=tk.X, padx=10, pady=10)

        self.total_projects_var = tk.StringVar(value="0")
        self.active_projects_var = tk.StringVar(value="0")
        self.completed_projects_var = tk.StringVar(value="0")
        self.total_budget_var = tk.StringVar(value="0")

        tk.Label(stats_inner, text="Total Proiecte:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W,
                                                                                       padx=5)
        tk.Label(stats_inner, textvariable=self.total_projects_var, fg='blue').grid(row=0, column=1, sticky=tk.W,
                                                                                    padx=5)

        tk.Label(stats_inner, text="Proiecte Active:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W,
                                                                                        padx=5)
        tk.Label(stats_inner, textvariable=self.active_projects_var, fg='green').grid(row=0, column=3, sticky=tk.W,
                                                                                      padx=5)

        tk.Label(stats_inner, text="Proiecte Finalizate:", font=('Arial', 10, 'bold')).grid(row=1, column=0,
                                                                                            sticky=tk.W, padx=5)
        tk.Label(stats_inner, textvariable=self.completed_projects_var, fg='gray').grid(row=1, column=1, sticky=tk.W,
                                                                                        padx=5)

        tk.Label(stats_inner, text="Buget Total:", font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky=tk.W,
                                                                                    padx=5)
        tk.Label(stats_inner, textvariable=self.total_budget_var, fg='purple').grid(row=1, column=3, sticky=tk.W,
                                                                                    padx=5)

        # Grafic status proiecte
        chart_frame = tk.LabelFrame(dashboard_frame, text="Distribuția Proiectelor pe Status",
                                    font=('Arial', 12, 'bold'))
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.dashboard_fig, self.dashboard_ax = plt.subplots(figsize=(8, 4))
        self.dashboard_canvas = FigureCanvasTkAgg(self.dashboard_fig, chart_frame)
        self.dashboard_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Proiecte recente
        recent_frame = tk.LabelFrame(dashboard_frame, text="Proiecte Recente", font=('Arial', 12, 'bold'))
        recent_frame.pack(fill=tk.X, padx=10, pady=5)

        self.recent_listbox = tk.Listbox(recent_frame, height=3)
        self.recent_listbox.pack(fill=tk.X, padx=10, pady=10)

    def create_projects_tab(self):
        """Tab pentru managementul proiectelor"""
        projects_frame = ttk.Frame(self.notebook)
        self.notebook.add(projects_frame, text="📁 Proiecte")

        # Toolbar pentru proiecte
        toolbar_frame = tk.Frame(projects_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(toolbar_frame, text="➕ Adaugă Proiect", command=self.add_project,
                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar_frame, text="✏️ Editează", command=self.edit_project,
                  bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar_frame, text="🗑️ Șterge", command=self.delete_project,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar_frame, text="🔄 Reîmprospătează", command=self.load_projects,
                  bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        # Lista proiecte
        list_frame = tk.LabelFrame(projects_frame, text="Lista Proiecte", font=('Arial', 12, 'bold'))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview pentru proiecte
        columns = ('ID', 'Nume', 'Manager', 'Data Început', 'Data Sfârșit', 'Buget', 'Status', 'Prioritate')
        self.projects_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.projects_tree.heading(col, text=col)
            self.projects_tree.column(col, width=120, anchor=tk.CENTER)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.projects_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.projects_tree.xview)
        self.projects_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.projects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=(10, 0))

    def create_wbs_tab(self):
        """Tab pentru Work Breakdown Structure"""
        wbs_frame = ttk.Frame(self.notebook)
        self.notebook.add(wbs_frame, text="📋 WBS & Taskuri")

        # Selector proiect
        selector_frame = tk.Frame(wbs_frame)
        selector_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(selector_frame, text="Selectează Proiectul:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        self.project_combo = ttk.Combobox(selector_frame, width=30, state='readonly')
        self.project_combo.pack(side=tk.LEFT, padx=5)
        self.project_combo.bind('<<ComboboxSelected>>', self.on_project_selected)

        # Toolbar taskuri
        task_toolbar = tk.Frame(wbs_frame)
        task_toolbar.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(task_toolbar, text="➕ Adaugă Task", command=self.add_task,
                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(task_toolbar, text="✏️ Editează Task", command=self.edit_task,
                  bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(task_toolbar, text="🗑️ Șterge Task", command=self.delete_task,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        # Lista taskuri
        tasks_frame = tk.LabelFrame(wbs_frame, text="Structura Activităților (WBS)", font=('Arial', 12, 'bold'))
        tasks_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        task_columns = (
            'ID', 'Nume Task', 'Responsabil', 'Data Început', 'Data Sfârșit', 'Durată', 'Progres', 'Status',
            'Prioritate')
        self.tasks_tree = ttk.Treeview(tasks_frame, columns=task_columns, show='headings', height=12)

        for col in task_columns:
            self.tasks_tree.heading(col, text=col)
            self.tasks_tree.column(col, width=100, anchor=tk.CENTER)

        tasks_scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=tasks_scrollbar.set)

        self.tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        tasks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def create_gantt_tab(self):
        """Tab pentru diagrama Gantt"""
        gantt_frame = ttk.Frame(self.notebook)
        self.notebook.add(gantt_frame, text="📊 Diagrama Gantt")

        # Selector proiect pentru Gantt
        gantt_selector = tk.Frame(gantt_frame)
        gantt_selector.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(gantt_selector, text="Proiect pentru Gantt:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        self.gantt_project_combo = ttk.Combobox(gantt_selector, width=30, state='readonly')
        self.gantt_project_combo.pack(side=tk.LEFT, padx=5)

        tk.Button(gantt_selector, text="🔄 Generează Gantt", command=self.generate_gantt,
                  bg='#9b59b6', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

        # Canvas pentru diagrama Gantt
        gantt_chart_frame = tk.LabelFrame(gantt_frame, text="Diagrama Gantt", font=('Arial', 12, 'bold'))
        gantt_chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.gantt_fig, self.gantt_ax = plt.subplots(figsize=(12, 8))
        self.gantt_canvas = FigureCanvasTkAgg(self.gantt_fig, gantt_chart_frame)
        self.gantt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_resources_tab(self):
        """Tab pentru managementul resurselor"""
        resources_frame = ttk.Frame(self.notebook)
        self.notebook.add(resources_frame, text="👥 Resurse")

        # Selector proiect pentru resurse
        res_selector = tk.Frame(resources_frame)
        res_selector.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(res_selector, text="Proiect:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        self.resources_project_combo = ttk.Combobox(res_selector, width=30, state='readonly')
        self.resources_project_combo.pack(side=tk.LEFT, padx=5)
        self.resources_project_combo.bind('<<ComboboxSelected>>', self.load_resources)

        # Toolbar resurse
        res_toolbar = tk.Frame(resources_frame)
        res_toolbar.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(res_toolbar, text="➕ Adaugă Resursă", command=self.add_resource,
                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(res_toolbar, text="✏️ Editează", command=self.edit_resource,
                  bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(res_toolbar, text="🗑️ Șterge", command=self.delete_resource,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        # Lista resurse
        res_list_frame = tk.LabelFrame(resources_frame, text="Lista Resurse", font=('Arial', 12, 'bold'))
        res_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        res_columns = ('ID', 'Nume', 'Tip', 'Cost/Unitate', 'Cantitate', 'Cost Total', 'Disponibilitate')
        self.resources_tree = ttk.Treeview(res_list_frame, columns=res_columns, show='headings', height=10)

        for col in res_columns:
            self.resources_tree.heading(col, text=col)
            self.resources_tree.column(col, width=120, anchor=tk.CENTER)

        res_scrollbar = ttk.Scrollbar(res_list_frame, orient=tk.VERTICAL, command=self.resources_tree.yview)
        self.resources_tree.configure(yscrollcommand=res_scrollbar.set)

        self.resources_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        res_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def create_risks_tab(self):
        """Tab pentru managementul riscurilor"""
        risks_frame = ttk.Frame(self.notebook)
        self.notebook.add(risks_frame, text="⚠️ Riscuri")

        # Selector proiect pentru riscuri
        risk_selector = tk.Frame(risks_frame)
        risk_selector.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(risk_selector, text="Proiect:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        self.risks_project_combo = ttk.Combobox(risk_selector, width=30, state='readonly')
        self.risks_project_combo.pack(side=tk.LEFT, padx=5)
        self.risks_project_combo.bind('<<ComboboxSelected>>', self.load_risks)

        # Toolbar riscuri
        risk_toolbar = tk.Frame(risks_frame)
        risk_toolbar.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(risk_toolbar, text="➕ Adaugă Risc", command=self.add_risk,
                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(risk_toolbar, text="✏️ Editează", command=self.edit_risk,
                  bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(risk_toolbar, text="🗑️ Șterge", command=self.delete_risk,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        # Lista riscuri
        risks_list_frame = tk.LabelFrame(risks_frame, text="Registrul Riscurilor", font=('Arial', 12, 'bold'))
        risks_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        risk_columns = ('ID', 'Descriere', 'Probabilitate', 'Impact', 'Nivel Risc', 'Strategie Mitigare', 'Status')
        self.risks_tree = ttk.Treeview(risks_list_frame, columns=risk_columns, show='headings', height=10)

        for col in risk_columns:
            self.risks_tree.heading(col, text=col)
            self.risks_tree.column(col, width=140, anchor=tk.CENTER)

        risk_scrollbar = ttk.Scrollbar(risks_list_frame, orient=tk.VERTICAL, command=self.risks_tree.yview)
        self.risks_tree.configure(yscrollcommand=risk_scrollbar.set)

        self.risks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        risk_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def create_stakeholders_tab(self):
        """Tab pentru managementul stakeholderilor"""
        stakeholders_frame = ttk.Frame(self.notebook)
        self.notebook.add(stakeholders_frame, text="🤝 Stakeholderi")

        # Selector proiect
        stake_selector = tk.Frame(stakeholders_frame)
        stake_selector.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(stake_selector, text="Proiect:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        self.stakeholders_project_combo = ttk.Combobox(stake_selector, width=30, state='readonly')
        self.stakeholders_project_combo.pack(side=tk.LEFT, padx=5)
        self.stakeholders_project_combo.bind('<<ComboboxSelected>>', self.load_stakeholders)

        # Toolbar stakeholderi
        stake_toolbar = tk.Frame(stakeholders_frame)
        stake_toolbar.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(stake_toolbar, text="➕ Adaugă Stakeholder", command=self.add_stakeholder,
                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(stake_toolbar, text="📊 Matrice Stakeholderi", command=self.show_stakeholder_matrix,
                  bg='#9b59b6', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        # Lista stakeholderi
        stake_list_frame = tk.LabelFrame(stakeholders_frame, text="Lista Stakeholderi", font=('Arial', 12, 'bold'))
        stake_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        stake_columns = ('ID', 'Nume', 'Rol', 'Influență', 'Interes', 'Plan Comunicare')
        self.stakeholders_tree = ttk.Treeview(stake_list_frame, columns=stake_columns, show='headings', height=8)

        for col in stake_columns:
            self.stakeholders_tree.heading(col, text=col)
            self.stakeholders_tree.column(col, width=150, anchor=tk.CENTER)

        stake_scrollbar = ttk.Scrollbar(stake_list_frame, orient=tk.VERTICAL, command=self.stakeholders_tree.yview)
        self.stakeholders_tree.configure(yscrollcommand=stake_scrollbar.set)

        self.stakeholders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        stake_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def create_reports_tab(self):
        """Tab pentru rapoarte și analize"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="📈 Rapoarte")

        # Opțiuni rapoarte
        options_frame = tk.LabelFrame(reports_frame, text="Opțiuni Rapoarte", font=('Arial', 12, 'bold'))
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        buttons_frame = tk.Frame(options_frame)
        buttons_frame.pack(pady=10)

        tk.Button(buttons_frame, text="📊 Raport Progres General", command=self.generate_progress_report,
                  bg='#3498db', fg='white', font=('Arial', 10, 'bold'), width=20).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(buttons_frame, text="💰 Analiza Bugetară", command=self.generate_budget_analysis,
                  bg='#e67e22', fg='white', font=('Arial', 10, 'bold'), width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(buttons_frame, text="⏰ Analiza Timeline", command=self.generate_timeline_analysis,
                  bg='#8e44ad', fg='white', font=('Arial', 10, 'bold'), width=20).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(buttons_frame, text="⚠️ Raport Riscuri", command=self.generate_risk_report,
                  bg='#c0392b', fg='white', font=('Arial', 10, 'bold'), width=20).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(buttons_frame, text="👥 Analiza Resurse", command=self.generate_resource_analysis,
                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), width=20).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(buttons_frame, text="📋 Export Date", command=self.export_data,
                  bg='#34495e', fg='white', font=('Arial', 10, 'bold'), width=20).grid(row=1, column=2, padx=5, pady=5)

        # Zona afișare rapoarte
        display_frame = tk.LabelFrame(reports_frame, text="Rezultate Analize", font=('Arial', 12, 'bold'))
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.report_text = tk.Text(display_frame, wrap=tk.WORD, font=('Courier', 10))
        report_scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scrollbar.set)

        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def create_methodology_tab(self):
        """Tab pentru metodologii de management proiecte"""
        method_frame = ttk.Frame(self.notebook)
        self.notebook.add(method_frame, text="🔬 Metodologii")

        # Frame principal cu două coloane
        main_frame = tk.Frame(method_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Coloana stânga - lista metodologii
        left_frame = tk.LabelFrame(main_frame, text="Metodologii Disponibile", font=('Arial', 12, 'bold'))
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5), pady=5)

        methodologies = [
            "🏗️ Waterfall (Cascadă)",
            "🔄 Agile/Scrum",
            "⚡ Kanban",
            "🔶 PRINCE2",
            "📊 PMBOK",
            "🎯 Lean Six Sigma",
            "🚀 DevOps",
            "💎 Crystal",
            "🌪️ Spiral Model"
        ]

        self.method_listbox = tk.Listbox(left_frame, font=('Arial', 10), width=25)
        for method in methodologies:
            self.method_listbox.insert(tk.END, method)
        self.method_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.method_listbox.bind('<<ListboxSelect>>', self.show_methodology_details)

        # Coloana dreapta - detalii metodologie
        right_frame = tk.LabelFrame(main_frame, text="Detalii Metodologie", font=('Arial', 12, 'bold'))
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)

        self.method_details = tk.Text(right_frame, wrap=tk.WORD, font=('Arial', 10), height=15)
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.method_details.yview)
        self.method_details.configure(yscrollcommand=scrollbar.set)

        self.method_details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Butoane aplicare metodologie
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        tk.Button(button_frame, text="📌 Aplică la Proiect", command=self.apply_methodology,
                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="📊 Compară Metodologii", command=self.compare_methodologies,
                  bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5, pady=5)

    def show_methodology_details(self, event):
        """Afiseaza detaliile metodologiei selectate"""
        selection = self.method_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        method_name = self.method_listbox.get(index)

        # Detalii pentru fiecare metodologie
        methodologies_info = {
            "🏗️ Waterfall (Cascadă)": """
                    Metodologie liniară și secvențială cu faze bine definite:

                    • Faze: Cerințe > Design > Implementare > Testare > Mentenanță
                    • Avantaje: Planificare clară, documentație amplă
                    • Dezavantaje: Puțin flexibil, schimbări costisitoare
                    • Recomandat pentru: Proiecte cu cerințe stabile și bine definite
                    """,
            "🔄 Agile/Scrum": """
                    Metodologie iterativă și incrementală bazată pe sprints:

                    • Caracteristici: Sprints de 2-4 săptămâni, daily stand-ups
                    • Avantaje: Flexibilitate, adaptare rapidă la schimbări
                    • Dezavantaje: Necesită implicare mare a clientului
                    • Recomandat pentru: Proiecte cu cerințe dinamice
                    """,
            "⚡ Kanban": """
                    Metodologie vizuală bazată pe fluxul de lucru:

                    • Caracteristici: Tablă Kanban, limitare lucru în progres
                    • Avantaje: Vizibilitate mare, îmbunătățire continuă
                    • Dezavantaje: Poate duce la multitasking excesiv
                    • Recomandat pentru: Echipe de mentenanță/support
                    """,
            "🔶 PRINCE2": """
                    Metodologie proces-orientată din domeniul public:

                    • Principii: Justificare continuă, învățare din experiență
                    • Avantaje: Control bun, adaptabil la dimensiunea proiectului
                    • Dezavantaje: Birocratic, necesită certificări
                    • Recomandat pentru: Proiecte guvernamentale/mari
                    """,
            "📊 PMBOK": """
                    Standard de bune practici în managementul proiectelor:

                    • Domenii: Integrare, domeniu, timp, cost, calitate, resurse
                    • Avantaje: Cuprinzător, recunoscut global
                    • Dezavantaje: General, nu oferă o metodologie specifică
                    • Recomandat pentru: Toate tipurile de proiecte
                    """,
            "🎯 Lean Six Sigma": """
                    Metodologie combinată de eficiență și calitate:

                    • Principii: Eliminarea risipei, reducerea variației
                    • Avantaje: Calitate crescută, eficiență sporită
                    • Dezavantaje: Necesită training specializat
                    • Recomandat pentru: Proiecte de îmbunătățire procese
                    """,
            "🚀 DevOps": """
                    Metodologie pentru integrare continuă și livrare:

                    • Practici: Automatizare, CI/CD, monitorizare
                    • Avantaje: Livrare rapidă, colaborare dev/ops
                    • Dezavantaje: Necesită schimbare culturală
                    • Recomandat pentru: Dezvoltare software
                    """,
            "💎 Crystal": """
                    Familie de metodologii Agile adaptate la proiect:

                    • Caracteristici: Adaptabil la dimensiune și criticitate
                    • Avantaje: Flexibil, centrat pe oameni
                    • Dezavantaje: Necesită experiență în Agile
                    • Recomandat pentru: Echipe experimentate Agile
                    """,
            "🌪️ Spiral Model": """
                    Model hibrid între Waterfall și abordări iterative:

                    • Faze: Planificare, analiză risc, dezvoltare, evaluare
                    • Avantaje: Gestionare bună a riscurilor
                    • Dezavantaje: Costisitor, complex
                    • Recomandat pentru: Proiecte cu risc ridicat
                    """
        }

        self.method_details.config(state=tk.NORMAL)
        self.method_details.delete(1.0, tk.END)
        self.method_details.insert(tk.END,
                                   methodologies_info.get(method_name, "Selectați o metodologie pentru detalii"))
        self.method_details.config(state=tk.DISABLED)

    def apply_methodology(self):
        """Aplica metodologia selectata la proiectul curent"""
        selection = self.method_listbox.curselection()
        if not selection:
            messagebox.showwarning("Avertisment", "Selectați o metodologie mai întâi!")
            return

        if not self.current_project_id:
            messagebox.showwarning("Avertisment", "Selectați un proiect mai întâi!")
            return

        index = selection[0]
        method_name = self.method_listbox.get(index).split()[1]  # Elimina emoji-ul

        try:
            self.cursor.execute("UPDATE projects SET methodology=? WHERE id=?",
                                (method_name, self.current_project_id))
            self.conn.commit()
            messagebox.showinfo("Succes", f"Metodologia '{method_name}' a fost aplicată proiectului!")
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la aplicarea metodologiei: {str(e)}")

    def compare_methodologies(self):
        """Afiseaza o comparatie intre metodologii"""
        compare_window = tk.Toplevel(self.root)
        compare_window.title("Comparare Metodologii")
        compare_window.geometry("900x600")

        text = tk.Text(compare_window, wrap=tk.WORD, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(compare_window, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill=tk.BOTH, expand=True)

        comparison = """
                COMPARATIE METODOLOGII MANAGEMENT PROIECTE:

                ╔══════════════════╦═════════════════════════════╦════════════════════════════════╦═══════════════════════════════╗
                ║                  ║ Waterfall                   ║ Agile/Scrum                    ║ Kanban                        ║
                ╠══════════════════╬═════════════════════════════╬════════════════════════════════╬═══════════════════════════════╣
                ║ Flexibilitate    ║ Mică                        ║ Mare                           ║ Mare                          ║
                ║ Documentație     ║ Extensivă                   ║ Minimală                       ║ Minimală                      ║
                ║ Predictibilitate ║ Mare                        ║ Variabilă                      ║ Variabilă                     ║
                ║ Cerințe          ║ Fixe la început             ║ Evolutive                      ║ Evolutive                     ║
                ║ Feedback         ║ La final                    ║ Continuu                       ║ Continuu                      ║
                ║ Riscuri          ║ Identificate târziu         ║ Identificate devreme           ║ Identificate devreme          ║
                ║ Costuri          ║ Estimări precise            ║ Estimări iterative             ║ Estimări iterative            ║
                ╚══════════════════╩═════════════════════════════╩════════════════════════════════╩═══════════════════════════════╝

                ╔══════════════════╦═════════════════════════════╦════════════════════════════════╦═══════════════════════════════╗
                ║                  ║ PRINCE2                     ║ PMBOK                          ║ Lean Six Sigma                ║
                ╠══════════════════╬═════════════════════════════╬════════════════════════════════╬═══════════════════════════════╣
                ║ Flexibilitate    ║ Moderată                    ║ Depinde de implementare        ║ Moderată                      ║
                ║ Documentație     ║ Extensivă                   ║ Extensivă                      ║ Standardizată                 ║
                ║ Predictibilitate ║ Mare                        ║ Mare                           ║ Mare                          ║
                ║ Cerințe          ║ Bine definite               ║ Depinde                        ║ Bine definite                 ║
                ║ Feedback         ║ Pe etape                    ║ Continuu                       ║ Continuu                      ║
                ║ Riscuri          ║ Gestionate bine             ║ Gestionate bine                ║ Minimizate                    ║
                ║ Costuri          ║ Estimări precise            ║ Estimări precise               ║ Estimări precise              ║
                ╚══════════════════╩═════════════════════════════╩════════════════════════════════╩═══════════════════════════════╝
                """

        text.insert(tk.END, comparison)
        text.config(state=tk.DISABLED)

    def load_all_data(self):
        """Încarcă toate datele inițiale"""
        self.update_dashboard()

    def load_projects(self):
        """Încarcă lista de proiecte în toate combobox-urile"""
        self.cursor.execute("SELECT id, name FROM projects ORDER BY name")
        projects = self.cursor.fetchall()
        self.projects_data = projects

        # Actualizează toate combobox-urile
        project_names = [f"{pid} - {name}" for pid, name in projects]
        self.project_combo['values'] = project_names
        self.gantt_project_combo['values'] = project_names
        self.resources_project_combo['values'] = project_names
        self.risks_project_combo['values'] = project_names
        self.stakeholders_project_combo['values'] = project_names

        # Actualizează treeview-ul de proiecte
        self.projects_tree.delete(*self.projects_tree.get_children())
        self.cursor.execute('''SELECT id, name, project_manager, start_date, end_date, 
                                     budget, status, priority FROM projects''')
        for row in self.cursor.fetchall():
            self.projects_tree.insert('', tk.END, values=row)

        # Actualizează lista proiecte recente
        self.recent_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT name FROM projects ORDER BY created_date DESC LIMIT 3")
        for row in self.cursor.fetchall():
            self.recent_listbox.insert(tk.END, row[0])

    def on_project_selected(self, event):
        """Handler pentru selectarea unui proiect"""
        selection = self.project_combo.get()
        if not selection:
            return

        self.current_project_id = int(selection.split(' - ')[0])
        self.load_tasks()
        self.load_resources()
        self.load_risks()
        self.load_stakeholders()

    def load_tasks(self):
        """Încarcă task-urile pentru proiectul selectat"""
        if not self.current_project_id:
            return

        self.tasks_tree.delete(*self.tasks_tree.get_children())
        self.cursor.execute('''SELECT id, name, assigned_to, start_date, end_date, 
                                     duration, progress, status, priority FROM tasks 
                                     WHERE project_id=?''', (self.current_project_id,))

        for row in self.cursor.fetchall():
            self.tasks_tree.insert('', tk.END, values=row)

    def load_resources(self, event=None):
        """Încarcă resursele pentru proiectul selectat"""
        if not self.current_project_id:
            return

        self.resources_tree.delete(*self.resources_tree.get_children())
        self.cursor.execute('''SELECT id, name, type, cost_per_unit, quantity, 
                                     total_cost, availability FROM resources 
                                     WHERE project_id=?''', (self.current_project_id,))

        for row in self.cursor.fetchall():
            self.resources_tree.insert('', tk.END, values=row)

    def load_risks(self, event=None):
        """Încarcă riscurile pentru proiectul selectat"""
        if not self.current_project_id:
            return

        self.risks_tree.delete(*self.risks_tree.get_children())
        self.cursor.execute('''SELECT id, description, probability, impact, 
                                     risk_level, mitigation_strategy, status FROM risks 
                                     WHERE project_id=?''', (self.current_project_id,))

        for row in self.cursor.fetchall():
            self.risks_tree.insert('', tk.END, values=row)

    def load_stakeholders(self, event=None):
        """Încarcă stakeholderii pentru proiectul selectat"""
        if not self.current_project_id:
            return

        self.stakeholders_tree.delete(*self.stakeholders_tree.get_children())
        self.cursor.execute('''SELECT id, name, role, influence, interest, 
                                     communication_plan FROM stakeholders 
                                     WHERE project_id=?''', (self.current_project_id,))

        for row in self.cursor.fetchall():
            self.stakeholders_tree.insert('', tk.END, values=row)

    def update_dashboard(self):
        """Actualizează statisticile din dashboard"""
        # Total proiecte
        self.cursor.execute("SELECT COUNT(*) FROM projects")
        total = self.cursor.fetchone()[0]
        self.total_projects_var.set(total)

        # Proiecte active
        self.cursor.execute("SELECT COUNT(*) FROM projects WHERE status='In progres'")
        active = self.cursor.fetchone()[0]
        self.active_projects_var.set(active)

        # Proiecte finalizate
        self.cursor.execute("SELECT COUNT(*) FROM projects WHERE status='Finalizat'")
        completed = self.cursor.fetchone()[0]
        self.completed_projects_var.set(completed)

        # Buget total
        self.cursor.execute("SELECT SUM(budget) FROM projects")
        budget = self.cursor.fetchone()[0] or 0
        self.total_budget_var.set(f"{budget:,.2f} RON")

        # Grafic status proiecte
        self.cursor.execute("SELECT status, COUNT(*) FROM projects GROUP BY status")
        data = self.cursor.fetchall()

        self.dashboard_ax.clear()
        if data:
            statuses = [item[0] for item in data]
            counts = [item[1] for item in data]

            colors = ['#2ecc71' if s == 'In progres' else
                      '#3498db' if s == 'Planificare' else
                      '#e74c3c' if s == 'Blocat' else
                      '#95a5a6' for s in statuses]

            self.dashboard_ax.bar(statuses, counts, color=colors)
            self.dashboard_ax.set_title('Distribuție Proiecte pe Status')
            self.dashboard_ax.set_ylabel('Număr Proiecte')

        self.dashboard_canvas.draw()

    def add_project(self):
        """Deschide fereastra pentru adăugare proiect nou"""
        add_window = tk.Toplevel(self.root)
        add_window.title("Adăugare Proiect Nou")
        add_window.geometry("500x600")

        # Frame principal
        main_frame = tk.Frame(add_window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Câmpuri formular
        tk.Label(main_frame, text="Nume Proiect:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W,
                                                                                    pady=5)
        name_entry = tk.Entry(main_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Descriere:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(main_frame, width=40, height=5, wrap=tk.WORD)
        desc_text.grid(row=1, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Manager Proiect:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W,
                                                                                       pady=5)
        manager_entry = tk.Entry(main_frame, width=40)
        manager_entry.grid(row=2, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Data Început:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W,
                                                                                    pady=5)
        start_entry = tk.Entry(main_frame, width=40)
        start_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        start_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        tk.Label(main_frame, text="Data Sfârșit:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W,
                                                                                    pady=5)
        end_entry = tk.Entry(main_frame, width=40)
        end_entry.grid(row=4, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Buget (RON):", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=5)
        budget_entry = tk.Entry(main_frame, width=40)
        budget_entry.grid(row=5, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Status:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=5)
        status_combo = ttk.Combobox(main_frame, values=["Planificare", "In progres", "Blocat", "Finalizat"], width=37)
        status_combo.grid(row=6, column=1, sticky=tk.W, pady=5)
        status_combo.current(0)

        tk.Label(main_frame, text="Prioritate:", font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky=tk.W, pady=5)
        priority_combo = ttk.Combobox(main_frame, values=["Înaltă", "Medie", "Scăzută"], width=37)
        priority_combo.grid(row=7, column=1, sticky=tk.W, pady=5)
        priority_combo.current(1)

        tk.Label(main_frame, text="Metodologie:", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky=tk.W, pady=5)
        method_combo = ttk.Combobox(main_frame, values=["Waterfall", "Agile", "Scrum", "Kanban", "PRINCE2", "PMBOK"],
                                    width=37)
        method_combo.grid(row=8, column=1, sticky=tk.W, pady=5)

        # Butoane
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Salvează", command=lambda: self.save_project(
            name_entry.get(),
            desc_text.get("1.0", tk.END).strip(),
            manager_entry.get(),
            start_entry.get(),
            end_entry.get(),
            budget_entry.get(),
            status_combo.get(),
            priority_combo.get(),
            method_combo.get(),
            add_window
        ), bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Anulează", command=add_window.destroy,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

    def save_project(self, name, description, manager, start_date, end_date,
                     budget, status, priority, methodology, window):
        """Salvează proiectul nou în baza de date"""
        if not name:
            messagebox.showerror("Eroare", "Numele proiectului este obligatoriu!")
            return

        try:
            budget_value = float(budget) if budget else 0.0
            created_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.cursor.execute('''INSERT INTO projects 
                                        (name, description, project_manager, start_date, 
                                        end_date, budget, status, priority, methodology, created_date) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (name, description, manager, start_date, end_date,
                                 budget_value, status, priority, methodology, created_date))
            self.conn.commit()

            messagebox.showinfo("Succes", "Proiectul a fost adăugat cu succes!")
            window.destroy()
            self.load_projects()
            self.update_dashboard()
        except ValueError:
            messagebox.showerror("Eroare", "Bugetul trebuie să fie un număr valid!")
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare: {str(e)}")

    def edit_project(self):
        """Deschide fereastra pentru editare proiect"""
        selected = self.projects_tree.selection()
        if not selected:
            messagebox.showwarning("Avertisment", "Selectați un proiect pentru editare!")
            return

        project_id = self.projects_tree.item(selected[0], 'values')[0]

        self.cursor.execute("SELECT * FROM projects WHERE id=?", (project_id,))
        project_data = self.cursor.fetchone()

        if not project_data:
            messagebox.showerror("Eroare", "Proiectul selectat nu a putut fi găsit!")
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editare Proiect")
        edit_window.geometry("500x600")

        # Frame principal
        main_frame = tk.Frame(edit_window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Câmpuri formular
        tk.Label(main_frame, text="Nume Proiect:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W,
                                                                                    pady=5)
        name_entry = tk.Entry(main_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        name_entry.insert(0, project_data[1])

        tk.Label(main_frame, text="Descriere:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(main_frame, width=40, height=5, wrap=tk.WORD)
        desc_text.grid(row=1, column=1, sticky=tk.W, pady=5)
        desc_text.insert("1.0", project_data[2] or "")

        tk.Label(main_frame, text="Manager Proiect:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W,
                                                                                       pady=5)
        manager_entry = tk.Entry(main_frame, width=40)
        manager_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        manager_entry.insert(0, project_data[8] or "")

        tk.Label(main_frame, text="Data Început:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W,
                                                                                    pady=5)
        start_entry = tk.Entry(main_frame, width=40)
        start_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        start_entry.insert(0, project_data[3] or "")

        tk.Label(main_frame, text="Data Sfârșit:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W,
                                                                                    pady=5)
        end_entry = tk.Entry(main_frame, width=40)
        end_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        end_entry.insert(0, project_data[4] or "")

        tk.Label(main_frame, text="Buget (RON):", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=5)
        budget_entry = tk.Entry(main_frame, width=40)
        budget_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        budget_entry.insert(0, project_data[5] or "0")

        tk.Label(main_frame, text="Status:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=5)
        status_combo = ttk.Combobox(main_frame, values=["Planificare", "In progres", "Blocat", "Finalizat"], width=37)
        status_combo.grid(row=6, column=1, sticky=tk.W, pady=5)
        status_combo.set(project_data[6] or "Planificare")

        tk.Label(main_frame, text="Prioritate:", font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky=tk.W, pady=5)
        priority_combo = ttk.Combobox(main_frame, values=["Înaltă", "Medie", "Scăzută"], width=37)
        priority_combo.grid(row=7, column=1, sticky=tk.W, pady=5)
        priority_combo.set(project_data[7] or "Medie")

        tk.Label(main_frame, text="Metodologie:", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky=tk.W, pady=5)
        method_combo = ttk.Combobox(main_frame, values=["Waterfall", "Agile", "Scrum", "Kanban", "PRINCE2", "PMBOK"],
                                    width=37)
        method_combo.grid(row=8, column=1, sticky=tk.W, pady=5)
        method_combo.set(project_data[9] or "")

        # Butoane
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Salvează", command=lambda: self.update_project(
            project_id,
            name_entry.get(),
            desc_text.get("1.0", tk.END).strip(),
            manager_entry.get(),
            start_entry.get(),
            end_entry.get(),
            budget_entry.get(),
            status_combo.get(),
            priority_combo.get(),
            method_combo.get(),
            edit_window
        ), bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Anulează", command=edit_window.destroy,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

    def update_project(self, project_id, name, description, manager, start_date, end_date,
                       budget, status, priority, methodology, window):
        """Actualizează datele proiectului în baza de date"""
        if not name:
            messagebox.showerror("Eroare", "Numele proiectului este obligatoriu!")
            return

        try:
            budget_value = float(budget) if budget else 0.0

            self.cursor.execute('''UPDATE projects SET 
                                        name=?, description=?, project_manager=?, start_date=?, 
                                        end_date=?, budget=?, status=?, priority=?, methodology=? 
                                        WHERE id=?''',
                                (name, description, manager, start_date, end_date,
                                 budget_value, status, priority, methodology, project_id))
            self.conn.commit()

            messagebox.showinfo("Succes", "Proiectul a fost actualizat cu succes!")
            window.destroy()
            self.load_projects()
            self.update_dashboard()
        except ValueError:
            messagebox.showerror("Eroare", "Bugetul trebuie să fie un număr valid!")
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare: {str(e)}")

    def delete_project(self):
        """Șterge proiectul selectat"""
        selected = self.projects_tree.selection()
        if not selected:
            messagebox.showwarning("Avertisment", "Selectați un proiect pentru ștergere!")
            return

        project_id = self.projects_tree.item(selected[0], 'values')[0]
        project_name = self.projects_tree.item(selected[0], 'values')[1]

        confirm = messagebox.askyesno("Confirmare",
                                      f"Sunteți sigur că doriți să ștergeți proiectul '{project_name}'?")
        if not confirm:
            return

        try:
            # Ștergem toate datele asociate proiectului
            self.cursor.execute("DELETE FROM tasks WHERE project_id=?", (project_id,))
            self.cursor.execute("DELETE FROM resources WHERE project_id=?", (project_id,))
            self.cursor.execute("DELETE FROM risks WHERE project_id=?", (project_id,))
            self.cursor.execute("DELETE FROM stakeholders WHERE project_id=?", (project_id,))
            self.cursor.execute("DELETE FROM projects WHERE id=?", (project_id,))
            self.conn.commit()

            messagebox.showinfo("Succes", "Proiectul a fost șters cu succes!")
            self.load_projects()
            self.update_dashboard()

            # Resetăm selecția curentă dacă era proiectul șters
            if self.current_project_id == project_id:
                self.current_project_id = None
                self.project_combo.set('')
                self.tasks_tree.delete(*self.tasks_tree.get_children())
                self.resources_tree.delete(*self.resources_tree.get_children())
                self.risks_tree.delete(*self.risks_tree.get_children())
                self.stakeholders_tree.delete(*self.stakeholders_tree.get_children())
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare la ștergere: {str(e)}")

    def add_task(self):
        """Adaugă un task nou la proiectul curent"""
        if not self.current_project_id:
            messagebox.showwarning("Avertisment", "Selectați mai întâi un proiect!")
            return

        add_window = tk.Toplevel(self.root)
        add_window.title("Adăugare Task Nou")
        add_window.geometry("500x500")

        # Frame principal
        main_frame = tk.Frame(add_window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Câmpuri formular
        tk.Label(main_frame, text="Nume Task:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = tk.Entry(main_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Descriere:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(main_frame, width=40, height=3, wrap=tk.WORD)
        desc_text.grid(row=1, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Responsabil:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        assigned_entry = tk.Entry(main_frame, width=40)
        assigned_entry.grid(row=2, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Data Început:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W,
                                                                                    pady=5)
        start_entry = tk.Entry(main_frame, width=40)
        start_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        start_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        tk.Label(main_frame, text="Data Sfârșit:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W,
                                                                                    pady=5)
        end_entry = tk.Entry(main_frame, width=40)
        end_entry.grid(row=4, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Durată (zile):", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W,
                                                                                     pady=5)
        duration_entry = tk.Entry(main_frame, width=40)
        duration_entry.grid(row=5, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Progres (%):", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=5)
        progress_scale = tk.Scale(main_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        progress_scale.grid(row=6, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Status:", font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky=tk.W, pady=5)
        status_combo = ttk.Combobox(main_frame, values=["Neînceput", "În desfășurare", "Blocat", "Finalizat"], width=37)
        status_combo.grid(row=7, column=1, sticky=tk.W, pady=5)
        status_combo.current(0)

        tk.Label(main_frame, text="Prioritate:", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky=tk.W, pady=5)
        priority_combo = ttk.Combobox(main_frame, values=["Înaltă", "Medie", "Scăzută"], width=37)
        priority_combo.grid(row=8, column=1, sticky=tk.W, pady=5)
        priority_combo.current(1)

        # Butoane
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Salvează", command=lambda: self.save_task(
            self.current_project_id,
            name_entry.get(),
            desc_text.get("1.0", tk.END).strip(),
            assigned_entry.get(),
            start_entry.get(),
            end_entry.get(),
            duration_entry.get(),
            progress_scale.get(),
            status_combo.get(),
            priority_combo.get(),
            add_window
        ), bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Anulează", command=add_window.destroy,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

    def save_task(self, project_id, name, description, assigned_to, start_date, end_date,
                  duration, progress, status, priority, window):
        """Salvează task-ul în baza de date"""
        if not name:
            messagebox.showerror("Eroare", "Numele task-ului este obligatoriu!")
            return

        try:
            duration_value = int(duration) if duration else 0
            dependencies = "[]"  # Empty JSON array for now

            self.cursor.execute('''INSERT INTO tasks 
                                        (project_id, name, description, assigned_to, 
                                        start_date, end_date, duration, progress, 
                                        status, priority, dependencies) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (project_id, name, description, assigned_to,
                                 start_date, end_date, duration_value, progress,
                                 status, priority, dependencies))
            self.conn.commit()

            messagebox.showinfo("Succes", "Task-ul a fost adăugat cu succes!")
            window.destroy()
            self.load_tasks()
        except ValueError:
            messagebox.showerror("Eroare", "Durata trebuie să fie un număr întreg!")
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare: {str(e)}")

    def edit_task(self):
        """Editează un task existent"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Avertisment", "Selectați un task pentru editare!")
            return

        task_id = self.tasks_tree.item(selected[0], 'values')[0]

        self.cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        task_data = self.cursor.fetchone()

        if not task_data:
            messagebox.showerror("Eroare", "Task-ul selectat nu a putut fi găsit!")
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editare Task")
        edit_window.geometry("500x500")

        # Frame principal
        main_frame = tk.Frame(edit_window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Câmpuri formular
        tk.Label(main_frame, text="Nume Task:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = tk.Entry(main_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        name_entry.insert(0, task_data[2])

        tk.Label(main_frame, text="Descriere:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(main_frame, width=40, height=3, wrap=tk.WORD)
        desc_text.grid(row=1, column=1, sticky=tk.W, pady=5)
        desc_text.insert("1.0", task_data[3] or "")

        tk.Label(main_frame, text="Responsabil:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        assigned_entry = tk.Entry(main_frame, width=40)
        assigned_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        assigned_entry.insert(0, task_data[8] or "")

        tk.Label(main_frame, text="Data Început:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W,
                                                                                    pady=5)
        start_entry = tk.Entry(main_frame, width=40)
        start_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        start_entry.insert(0, task_data[4] or "")

        tk.Label(main_frame, text="Data Sfârșit:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W,
                                                                                    pady=5)
        end_entry = tk.Entry(main_frame, width=40)
        end_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        end_entry.insert(0, task_data[5] or "")

        tk.Label(main_frame, text="Durată (zile):", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W,
                                                                                     pady=5)
        duration_entry = tk.Entry(main_frame, width=40)
        duration_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        duration_entry.insert(0, task_data[6] or "0")

        tk.Label(main_frame, text="Progres (%):", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=5)
        progress_scale = tk.Scale(main_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        progress_scale.grid(row=6, column=1, sticky=tk.W, pady=5)
        progress_scale.set(task_data[11] or 0)

        tk.Label(main_frame, text="Status:", font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky=tk.W, pady=5)
        status_combo = ttk.Combobox(main_frame, values=["Neînceput", "În desfășurare", "Blocat", "Finalizat"], width=37)
        status_combo.grid(row=7, column=1, sticky=tk.W, pady=5)
        status_combo.set(task_data[12] or "Neînceput")

        tk.Label(main_frame, text="Prioritate:", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky=tk.W, pady=5)
        priority_combo = ttk.Combobox(main_frame, values=["Înaltă", "Medie", "Scăzută"], width=37)
        priority_combo.grid(row=8, column=1, sticky=tk.W, pady=5)
        priority_combo.set(task_data[13] or "Medie")

        # Butoane
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Salvează", command=lambda: self.update_task(
            task_id,
            name_entry.get(),
            desc_text.get("1.0", tk.END).strip(),
            assigned_entry.get(),
            start_entry.get(),
            end_entry.get(),
            duration_entry.get(),
            progress_scale.get(),
            status_combo.get(),
            priority_combo.get(),
            edit_window
        ), bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Anulează", command=edit_window.destroy,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

    def update_task(self, task_id, name, description, assigned_to, start_date, end_date,
                    duration, progress, status, priority, window):
        """Actualizează task-ul în baza de date"""
        if not name:
            messagebox.showerror("Eroare", "Numele task-ului este obligatoriu!")
            return

        try:
            duration_value = int(duration) if duration else 0

            self.cursor.execute('''UPDATE tasks SET 
                                        name=?, description=?, assigned_to=?, 
                                        start_date=?, end_date=?, duration=?, 
                                        progress=?, status=?, priority=? 
                                        WHERE id=?''',
                                (name, description, assigned_to,
                                 start_date, end_date, duration_value,
                                 progress, status, priority, task_id))
            self.conn.commit()

            messagebox.showinfo("Succes", "Task-ul a fost actualizat cu succes!")
            window.destroy()
            self.load_tasks()
        except ValueError:
            messagebox.showerror("Eroare", "Durata trebuie să fie un număr întreg!")
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare: {str(e)}")

    def delete_task(self):
        """Șterge task-ul selectat"""
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Avertisment", "Selectați un task pentru ștergere!")
            return

        task_id = self.tasks_tree.item(selected[0], 'values')[0]
        task_name = self.tasks_tree.item(selected[0], 'values')[1]

        confirm = messagebox.askyesno("Confirmare",
                                      f"Sunteți sigur că doriți să ștergeți task-ul '{task_name}'?")
        if not confirm:
            return

        try:
            self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            self.conn.commit()

            messagebox.showinfo("Succes", "Task-ul a fost șters cu succes!")
            self.load_tasks()
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare la ștergere: {str(e)}")

    def generate_gantt(self):
        """Generează diagrama Gantt pentru proiectul selectat"""
        selection = self.gantt_project_combo.get()
        if not selection:
            messagebox.showwarning("Avertisment", "Selectați un proiect pentru generarea Gantt!")
            return

        project_id = int(selection.split(' - ')[0])

        self.cursor.execute("SELECT name FROM projects WHERE id=?", (project_id,))
        project_name = self.cursor.fetchone()[0]

        self.cursor.execute('''SELECT name, start_date, end_date, progress, status 
                                    FROM tasks WHERE project_id=? ORDER BY start_date''', (project_id,))
        tasks = self.cursor.fetchall()

        if not tasks:
            messagebox.showinfo("Informație", "Nu există task-uri pentru acest proiect!")
            return

        # Procesare date pentru Gantt
        task_names = []
        start_dates = []
        end_dates = []
        colors = []

        for task in tasks:
            task_names.append(task[0])

            try:
                start_date = datetime.datetime.strptime(task[1], "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(task[2], "%Y-%m-%d").date()
            except:
                start_date = datetime.date.today()
                end_date = datetime.date.today() + datetime.timedelta(days=1)

            start_dates.append(start_date)
            end_dates.append(end_date)

            # Setează culoarea în funcție de status
            if task[4] == "Finalizat":
                colors.append('#2ecc71')  # Verde
            elif task[4] == "În desfășurare":
                colors.append('#3498db')  # Albastru
            elif task[4] == "Blocat":
                colors.append('#e74c3c')  # Roșu
            else:
                colors.append('#f39c12')  # Portocaliu

        # Convertim datele pentru matplotlib
        start_dates_num = [dates.date2num(d) for d in start_dates]
        durations = [dates.date2num(end) - dates.date2num(start)
                     for start, end in zip(start_dates, end_dates)]

        # Creare diagramă Gantt
        self.gantt_ax.clear()

        y_pos = range(len(task_names))
        self.gantt_ax.barh(y_pos, durations, left=start_dates_num, height=0.5,
                           align='center', color=colors)

        # Adăugăm procentul de completare pe fiecare bară
        for i, (task, progress) in enumerate(zip(tasks, [t[3] for t in tasks])):
            if progress > 0:
                x_pos = start_dates_num[i] + durations[i] * (progress / 100) / 2
                self.gantt_ax.text(x_pos, i, f"{progress}%",
                                   ha='center', va='center', color='white', fontweight='bold')

        # Formatare axă
        self.gantt_ax.set_yticks(y_pos)
        self.gantt_ax.set_yticklabels(task_names)
        self.gantt_ax.set_title(f"Diagrama Gantt - {project_name}")
        self.gantt_ax.set_xlabel("Timeline")
        self.gantt_ax.grid(True)

        # Formatare date pe axa X
        self.gantt_ax.xaxis_date()
        self.gantt_fig.autofmt_xdate()

        self.gantt_canvas.draw()

    def add_resource(self):
        """Adaugă o resursă nouă la proiectul curent"""
        if not self.current_project_id:
            messagebox.showwarning("Avertisment", "Selectați mai întâi un proiect!")
            return

        add_window = tk.Toplevel(self.root)
        add_window.title("Adăugare Resursă Nouă")
        add_window.geometry("500x400")

        # Frame principal
        main_frame = tk.Frame(add_window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Câmpuri formular
        tk.Label(main_frame, text="Nume Resursă:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W,
                                                                                    pady=5)
        name_entry = tk.Entry(main_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Tip Resursă:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        type_combo = ttk.Combobox(main_frame, values=["Uman", "Material", "Financiar", "Tehnic", "Informațional"],
                                  width=37)
        type_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        type_combo.current(0)

        tk.Label(main_frame, text="Cost per Unitate (RON):", font=('Arial', 10, 'bold')).grid(row=2, column=0,
                                                                                              sticky=tk.W, pady=5)
        cost_entry = tk.Entry(main_frame, width=40)
        cost_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        cost_entry.insert(0, "0.00")

        tk.Label(main_frame, text="Cantitate:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        quantity_entry = tk.Entry(main_frame, width=40)
        quantity_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        quantity_entry.insert(0, "1")

        tk.Label(main_frame, text="Disponibilitate:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W,
                                                                                       pady=5)
        avail_combo = ttk.Combobox(main_frame, values=["Disponibil", "Parțial", "Indisponibil"], width=37)
        avail_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
        avail_combo.current(0)

        # Butoane
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Salvează", command=lambda: self.save_resource(
            self.current_project_id,
            name_entry.get(),
            type_combo.get(),
            cost_entry.get(),
            quantity_entry.get(),
            avail_combo.get(),
            add_window
        ), bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Anulează", command=add_window.destroy,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

    def save_resource(self, project_id, name, type_res, cost, quantity, availability, window):
        """Salvează resursa în baza de date"""
        if not name:
            messagebox.showerror("Eroare", "Numele resursei este obligatoriu!")
            return

        try:
            cost_value = float(cost) if cost else 0.0
            quantity_value = int(quantity) if quantity else 1
            total_cost = cost_value * quantity_value

            self.cursor.execute('''INSERT INTO resources 
                                        (project_id, name, type, cost_per_unit, 
                                        quantity, total_cost, availability) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                (project_id, name, type_res, cost_value,
                                 quantity_value, total_cost, availability))
            self.conn.commit()

            messagebox.showinfo("Succes", "Resursa a fost adăugată cu succes!")
            window.destroy()
            self.load_resources()
        except ValueError:
            messagebox.showerror("Eroare", "Costul și cantitatea trebuie să fie numere valide!")
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare: {str(e)}")

    def edit_resource(self):
        """Editează o resursă existentă"""
        selected = self.resources_tree.selection()
        if not selected:
            messagebox.showwarning("Avertisment", "Selectați o resursă pentru editare!")
            return

        resource_id = self.resources_tree.item(selected[0], 'values')[0]

        self.cursor.execute("SELECT * FROM resources WHERE id=?", (resource_id,))
        resource_data = self.cursor.fetchone()

        if not resource_data:
            messagebox.showerror("Eroare", "Resursa selectată nu a putut fi găsită!")
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editare Resursă")
        edit_window.geometry("500x400")

        # Frame principal
        main_frame = tk.Frame(edit_window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Câmpuri formular
        tk.Label(main_frame, text="Nume Resursă:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W,
                                                                                    pady=5)
        name_entry = tk.Entry(main_frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        name_entry.insert(0, resource_data[2])

        tk.Label(main_frame, text="Tip Resursă:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        type_combo = ttk.Combobox(main_frame, values=["Uman", "Material", "Financiar", "Tehnic", "Informațional"],
                                  width=37)
        type_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        type_combo.set(resource_data[3] or "Uman")

        tk.Label(main_frame, text="Cost per Unitate (RON):", font=('Arial', 10, 'bold')).grid(row=2, column=0,
                                                                                              sticky=tk.W, pady=5)
        cost_entry = tk.Entry(main_frame, width=40)
        cost_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        cost_entry.insert(0, resource_data[4] or "0.00")

        tk.Label(main_frame, text="Cantitate:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        quantity_entry = tk.Entry(main_frame, width=40)
        quantity_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        quantity_entry.insert(0, resource_data[5] or "1")

        tk.Label(main_frame, text="Disponibilitate:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W,
                                                                                       pady=5)
        avail_combo = ttk.Combobox(main_frame, values=["Disponibil", "Parțial", "Indisponibil"], width=37)
        avail_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
        avail_combo.set(resource_data[7] or "Disponibil")

        # Butoane
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Salvează", command=lambda: self.update_resource(
            resource_id,
            name_entry.get(),
            type_combo.get(),
            cost_entry.get(),
            quantity_entry.get(),
            avail_combo.get(),
            edit_window
        ), bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Anulează", command=edit_window.destroy,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

    def update_resource(self, resource_id, name, type_res, cost, quantity, availability, window):
        """Actualizează resursa în baza de date"""
        if not name:
            messagebox.showerror("Eroare", "Numele resursei este obligatoriu!")
            return

        try:
            cost_value = float(cost) if cost else 0.0
            quantity_value = int(quantity) if quantity else 1
            total_cost = cost_value * quantity_value

            self.cursor.execute('''UPDATE resources SET 
                                        name=?, type=?, cost_per_unit=?, 
                                        quantity=?, total_cost=?, availability=? 
                                        WHERE id=?''',
                                (name, type_res, cost_value,
                                 quantity_value, total_cost, availability, resource_id))
            self.conn.commit()

            messagebox.showinfo("Succes", "Resursa a fost actualizată cu succes!")
            window.destroy()
            self.load_resources()
        except ValueError:
            messagebox.showerror("Eroare", "Costul și cantitatea trebuie să fie numere valide!")
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare: {str(e)}")

    def delete_resource(self):
        """Șterge resursa selectată"""
        selected = self.resources_tree.selection()
        if not selected:
            messagebox.showwarning("Avertisment", "Selectați o resursă pentru ștergere!")
            return

        resource_id = self.resources_tree.item(selected[0], 'values')[0]
        resource_name = self.resources_tree.item(selected[0], 'values')[1]

        confirm = messagebox.askyesno("Confirmare",
                                      f"Sunteți sigur că doriți să ștergeți resursa '{resource_name}'?")
        if not confirm:
            return

        try:
            self.cursor.execute("DELETE FROM resources WHERE id=?", (resource_id,))
            self.conn.commit()

            messagebox.showinfo("Succes", "Resursa a fost ștearsă cu succes!")
            self.load_resources()
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare la ștergere: {str(e)}")

    def add_risk(self):
        """Adaugă un risc nou la proiectul curent"""
        if not self.current_project_id:
            messagebox.showwarning("Avertisment", "Selectați mai întâi un proiect!")
            return

        add_window = tk.Toplevel(self.root)
        add_window.title("Adăugare Risc Nou")
        add_window.geometry("500x500")

        # Frame principal
        main_frame = tk.Frame(add_window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Câmpuri formular
        tk.Label(main_frame, text="Descriere Risc:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W,
                                                                                      pady=5)
        desc_text = tk.Text(main_frame, width=40, height=3, wrap=tk.WORD)
        desc_text.grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Probabilitate:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W,
                                                                                     pady=5)
        prob_combo = ttk.Combobox(main_frame, values=["Mică", "Medie", "Mare"], width=37)
        prob_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        prob_combo.current(1)

        tk.Label(main_frame, text="Impact:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        impact_combo = ttk.Combobox(main_frame, values=["Mic", "Mediu", "Mare"], width=37)
        impact_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        impact_combo.current(1)

        tk.Label(main_frame, text="Strategie Mitigare:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W,
                                                                                          pady=5)
        strategy_text = tk.Text(main_frame, width=40, height=5, wrap=tk.WORD)
        strategy_text.grid(row=3, column=1, sticky=tk.W, pady=5)

        tk.Label(main_frame, text="Status:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        status_combo = ttk.Combobox(main_frame, values=["Identificat", "Monitorizat", "Mitigat", "Realizat"], width=37)
        status_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
        status_combo.current(0)

        # Butoane
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Salvează", command=lambda: self.save_risk(
            self.current_project_id,
            desc_text.get("1.0", tk.END).strip(),
            prob_combo.get(),
            impact_combo.get(),
            strategy_text.get("1.0", tk.END).strip(),
            status_combo.get(),
            add_window
        ), bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Anulează", command=add_window.destroy,
                  bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)

    def save_risk(self, project_id, description, probability, impact, strategy, status, window):
        """Salvează riscul în baza de date"""
        if not description:
            messagebox.showerror("Eroare", "Descrierea riscului este obligatorie!")
            return

        try:
            # Calculăm nivelul riscului
            prob_values = {"Mică": 1, "Medie": 2, "Mare": 3}
            impact_values = {"Mic": 1, "Mediu": 2, "Mare": 3}

            risk_level_value = prob_values.get(probability, 1) * impact_values.get(impact, 1)
            risk_level = ""

            if risk_level_value <= 2:
                risk_level = "Scăzut"
            elif risk_level_value <= 4:
                risk_level = "Moderat"
            else:
                risk_level = "Ridicat"

            self.cursor.execute('''INSERT INTO risks 
                                        (project_id, description, probability, impact, 
                                        risk_level, mitigation_strategy, status) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                (project_id, description, probability, impact,
                                 risk_level, strategy, status))
            self.conn.commit()

            messagebox.showinfo("Succes", "Riscul a fost adăugat cu succes!")
            window.destroy()
            self.load_risks()
        except Exception as e:
            messagebox.showerror("Eroare", f"A apărut o eroare: {str(e)}")

    def edit_risk(self):
        """Editează un risc existent"""
        selected = self.risks_tree.selection()
        if not selected:
            messagebox.showwarning("Avertisment", "Selectați un risc pentru editare!")
            return

        risk_id = self.risks_tree.item(selected[0], 'values')[0]

        self.cursor.execute("SELECT * FROM risks WHERE id=?", (risk_id,))
        risk_data = self.cursor.fetchone()

        if not risk_data:
            messagebox.showerror("Eroare", "Riscul selectat nu a putut fi găsit!")
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editare Risc")
        edit_window.geometry("500x500")

        # Frame principal
        main_frame = tk.Frame(edit_window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Câmpuri formular
        tk.Label(main_frame, text="Descriere Risc:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W,
                                                                                      pady=5)
        desc_text = tk.Text(main_frame, width=40, height=3, wrap=tk.WORD)
        desc_text.grid(row=0, column=1, sticky=tk.W, pady=5)
        desc_text.insert("1.0", risk_data[2] or "")

        tk.Label(main_frame, text="Probabilitate:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W,
                                                                                     pady=5)
        prob_combo = ttk.Combobox(main_frame, values=["Mică", "Medie", "Mare"], width=37)
        prob_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        prob_combo.set(risk_data[3] or "Medie")

        tk.Label(main_frame, text="Impact:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        impact_combo = ttk.Combobox(main_frame, values=["Mic", "Mediu", "Mare"], width=37)
        impact_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        impact_combo.set(risk_data[4] or "Mediu")
        tk.Label(main_frame, text="Strategie Mitigare:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W,
                                                                                          pady=5)
        strategy_text = tk.Text(main_frame, width=40, height=5, wrap=tk.WORD)
        strategy_text.grid(row=3, column=1, sticky=tk.W, pady=5)
        strategy_text.insert("1.0", risk_data[6] or "")
        tk.Label(main_frame, text="Status:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        status_combo = ttk.Combobox(main_frame, values=["Identificat", "Monitorizat", "Mitigat", "Realizat"], width=37)
        status_combo.grid(row=4, column=1, sticky=tk.W, pady=5)
        status_combo.set(risk_data[7] or "Identificat")
        # Butoane
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectManagementApp(root)
    root.mainloop()