import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.cm as cm
import numpy as np
import pymysql
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ModernFinanceDashboard:

    def __init__(self, root):
        self.root = root
        self.root.title("FINANCIAL INTELLIGENCE DASHBOARD")
        
        # Color Palette Definition
        self.BG_MAIN = "#0F172A"       # Slate 900
        self.BG_CARD = "#1E293B"       # Slate 800
        self.BG_INPUT = "#334155"      # Slate 700
        self.TEXT_PRIMARY = "#F8FAFC"  # Slate 50
        self.TEXT_MUTED = "#94A3B8"    # Slate 400
        
        self.COLOR_GREEN = "#10B981"   # Emerald
        self.COLOR_RED = "#EF4444"     # Rose
        self.COLOR_BLUE = "#3B82F6"    # Indigo/Blue
        self.COLOR_AMBER = "#F59E0B"   # Amber/Orange
        self.COLOR_PURPLE = "#8B5CF6"  # Purple Accent

        self.root.configure(bg=self.BG_MAIN)
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        app_w = min(1280, int(screen_w * 0.9))
        app_h = min(720, int(screen_h * 0.88))
        self.root.geometry(f"{app_w}x{app_h}")
        self.root.minsize(1024, 600)

        self.analysis_canvas = None

        self.setup_styles()
        self.build_header()
        
        self.main_container = tk.Frame(self.root, bg=self.BG_MAIN)
        self.main_container.pack(fill="both", expand=True, padx=15, pady=10)

        self.build_left_panel()
        self.build_right_panel()

        self.init_database()
        self.refresh_company_list()
        self.update_table_view()

    def setup_styles(self):
        """Configures modern styling rules for ttk widgets."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure(
            "Treeview",
            background=self.BG_CARD,
            foreground=self.TEXT_PRIMARY,
            fieldbackground=self.BG_CARD,
            rowheight=26,
            font=("Segoe UI", 9),
            borderwidth=0,
        )
        self.style.map(
            "Treeview",
            background=[("selected", self.COLOR_BLUE)],
            foreground=[("selected", "#FFFFFF")],
        )
        self.style.configure(
            "Treeview.Heading",
            background=self.BG_INPUT,
            foreground=self.TEXT_PRIMARY,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
        )
        self.style.map("Treeview.Heading", background=[("active", self.COLOR_BLUE)])

        self.style.configure(
            "TCombobox",
            fieldbackground=self.BG_INPUT,
            background=self.BG_INPUT,
            foreground=self.TEXT_PRIMARY,
            darkcolor=self.BG_INPUT,
            lightcolor=self.BG_INPUT,
            arrowcolor=self.TEXT_PRIMARY,
            bordercolor=self.BG_INPUT,
            padding=4,
        )

    def build_header(self):
        """Compact Top Header Banner Layout."""
        header_frame = tk.Frame(self.root, bg=self.BG_CARD, height=50)
        header_frame.pack(fill="x", side="top")
        
        border_line = tk.Frame(self.root, bg=self.COLOR_BLUE, height=2)
        border_line.pack(fill="x", side="top")

        title = tk.Label(
            header_frame,
            text="⚡ FINANCIAL MANAGEMENT & CATEGORY AUDIT DASHBOARD",
            font=("Segoe UI", 14, "bold"),
            fg=self.TEXT_PRIMARY,
            bg=self.BG_CARD,
            pady=10,
            padx=20
        )
        title.pack(side="left")

    def build_left_panel(self):
        """Builds the Action Input Form Control Panel."""
        left_frame = tk.Frame(self.main_container, bg=self.BG_CARD, width=320)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        panel_title = tk.Label(
            left_frame,
            text="TRANSACTION CONTROL",
            font=("Segoe UI", 11, "bold"),
            fg=self.COLOR_BLUE,
            bg=self.BG_CARD,
            anchor="w",
        )
        panel_title.pack(fill="x", padx=15, pady=(12, 6))

        form_frame = tk.Frame(left_frame, bg=self.BG_CARD)
        form_frame.pack(fill="x", padx=15)

        # Inputs
        self.create_label(form_frame, "COMPANY / CLIENT")
        self.company_combo = ttk.Combobox(form_frame, font=("Segoe UI", 10), style="TCombobox")
        self.company_combo.pack(fill="x", pady=(0, 6))

        self.create_label(form_frame, "AMOUNT (Rs.)")
        self.amount = self.create_entry(form_frame)
        self.amount.pack(fill="x", pady=(0, 6))

        self.create_label(form_frame, "CATEGORY / DESCRIPTION")
        self.type = self.create_entry(form_frame)
        self.type.pack(fill="x", pady=(0, 12))

        # Action Buttons Stack
        self.create_button(form_frame, "➕ ADD INFLOW (INCOME)", self.COLOR_GREEN, self.incomefun)
        self.create_button(form_frame, "➖ ADD OUTFLOW (EXPENSE)", self.COLOR_RED, self.expfun)
        self.create_button(form_frame, "📊 AUDIT & VISUALIZE DATA", self.COLOR_BLUE, self.auditfun)
        
        sep = tk.Frame(form_frame, bg=self.BG_INPUT, height=1)
        sep.pack(fill="x", pady=8)
        
        self.create_button(form_frame, "🗑️ PURGE COMPANY RECORD", "#DC2626", self.deletefun)

    def build_right_panel(self):
        """Builds the Data Dashboard Viewports."""
        right_frame = tk.Frame(self.main_container, bg=self.BG_MAIN)
        right_frame.pack(side="right", fill="both", expand=True)

        table_card = tk.Frame(right_frame, bg=self.BG_CARD)
        table_card.pack(fill="both", expand=True, pady=(0, 10))

        card_title = tk.Label(
            table_card,
            text="LIVE LEDGER DATABASE LOGS",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_MUTED,
            bg=self.BG_CARD,
            anchor="w"
        )
        card_title.pack(fill="x", padx=15, pady=(8, 4))

        tree_container = tk.Frame(table_card, bg=self.BG_CARD)
        tree_container.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        scroll_y = ttk.Scrollbar(tree_container, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        self.table = ttk.Treeview(
            tree_container,
            yscrollcommand=scroll_y.set,
            columns=("company", "category", "Income", "Expence", "Audit"),
            selectmode="browse"
        )
        scroll_y.config(command=self.table.yview)

        self.table.heading("company", text="Company / Client Name", anchor="w")
        self.table.heading("category", text="All Categories Logged", anchor="w")
        self.table.heading("Income", text="Total Income (Rs.)", anchor="e")
        self.table.heading("Expence", text="Total Expense (Rs.)", anchor="e")
        self.table.heading("Audit", text="Net Balance (Rs.)", anchor="e")

        self.table.column("company", anchor="w", width=140)
        self.table.column("category", anchor="w", width=180)
        self.table.column("Income", anchor="e", width=100)
        self.table.column("Expence", anchor="e", width=100)
        self.table.column("Audit", anchor="e", width=100)

        self.table["show"] = "headings"
        self.table.pack(fill="both", expand=True)
        
        self.table.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.chart_card = tk.Frame(right_frame, bg=self.BG_CARD, height=270)
        self.chart_card.pack(fill="x", side="bottom")
        self.chart_card.pack_propagate(False)

        chart_title = tk.Label(
            self.chart_card,
            text="DUAL VISUALIZATION DASHBOARD (BALANCE + ALL-CATEGORY DISTRIBUTION)",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_MUTED,
            bg=self.BG_CARD,
            anchor="w"
        )
        chart_title.pack(fill="x", padx=15, pady=(6, 2))

    def create_label(self, parent, text):
        lbl = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 8, "bold"),
            fg=self.TEXT_MUTED,
            bg=self.BG_CARD,
            anchor="w"
        )
        lbl.pack(fill="x", pady=(3, 1))
        return lbl

    def create_entry(self, parent):
        return tk.Entry(
            parent,
            font=("Segoe UI", 10),
            bg=self.BG_INPUT,
            fg=self.TEXT_PRIMARY,
            insertbackground=self.TEXT_PRIMARY,
            relief="flat",
            bd=3
        )

    def create_button(self, parent, text, color, command):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 9, "bold"),
            bg=color,
            fg="#FFFFFF",
            activebackground=color,
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            pady=5
        )
        btn.pack(fill="x", pady=3)
        return btn

    def on_tree_select(self, event):
        selected_item = self.table.selection()
        if selected_item:
            values = self.table.item(selected_item[0], "values")
            if values:
                self.company_combo.set(values[0])

    def dbconnectfun(self):
        self.con = pymysql.connect(
            host="localhost",
            user="root",
            passwd=#enter your password,
            database=#enter your database name,
        )
        self.cur = self.con.cursor()

    def init_database(self):
        try:
            self.dbconnectfun()
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS finance (
                    company VARCHAR(100) PRIMARY KEY,
                    income INT DEFAULT 0,
                    expence INT DEFAULT 0,
                    balance INT DEFAULT 0
                )
            """)
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    company VARCHAR(100),
                    category VARCHAR(100),
                    amount INT,
                    type VARCHAR(20)
                )
            """)
            self.con.commit()
            self.sync_finance_summary()
        except Exception:
            pass
        finally:
            if hasattr(self, 'con') and self.con.open:
                self.con.close()

    def sync_finance_summary(self):
        """Consolidates transaction logs into merged company records."""
        try:
            self.cur.execute("TRUNCATE TABLE finance")
            summary_query = """
                INSERT INTO finance (company, income, expence, balance)
                SELECT 
                    company,
                    SUM(CASE WHEN type = 'INCOME' THEN amount ELSE 0 END) as inc,
                    SUM(CASE WHEN type = 'EXPENSE' THEN amount ELSE 0 END) as exp,
                    SUM(CASE WHEN type = 'INCOME' THEN amount ELSE 0 END) - SUM(CASE WHEN type = 'EXPENSE' THEN amount ELSE 0 END) as bal
                FROM transactions
                GROUP BY company
            """
            self.cur.execute(summary_query)
            self.con.commit()
        except Exception:
            pass

    def refresh_company_list(self):
        try:
            self.dbconnectfun()
            self.cur.execute("SELECT DISTINCT company FROM transactions")
            rows = self.cur.fetchall()
            companies = [r[0] for r in rows]
            self.company_combo['values'] = companies
        except Exception:
            pass
        finally:
            if hasattr(self, 'con') and self.con.open:
                self.con.close()

    def update_table_view(self):
        self.table.delete(*self.table.get_children())
        try:
            self.dbconnectfun()
            query = """
                SELECT 
                    company,
                    COALESCE(
                        (SELECT GROUP_CONCAT(DISTINCT category SEPARATOR ', ') 
                         FROM transactions t2 
                         WHERE t2.company = t1.company), 'General'
                    ) as categories,
                    SUM(CASE WHEN type = 'INCOME' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN type = 'EXPENSE' THEN amount ELSE 0 END) as total_expense,
                    SUM(CASE WHEN type = 'INCOME' THEN amount ELSE 0 END) - SUM(CASE WHEN type = 'EXPENSE' THEN amount ELSE 0 END) as net_balance
                FROM transactions t1
                GROUP BY company
            """
            self.cur.execute(query)
            all_data = self.cur.fetchall()
            for row in all_data:
                formatted_row = (
                    row[0],
                    row[1],
                    f"₹ {int(row[2]):,}",
                    f"₹ {int(row[3]):,}",
                    f"₹ {int(row[4]):,}"
                )
                self.table.insert("", tk.END, values=formatted_row)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to refresh table: {e}")
        finally:
            if hasattr(self, 'con') and self.con.open:
                self.con.close()

    def incomefun(self):
        comp = self.company_combo.get().strip().upper()
        amount = self.amount.get().strip()
        tp = self.type.get().strip() or "General Income"

        if comp and amount:
            try:
                amount_int = int(amount)
                self.dbconnectfun()
                
                log_query = "INSERT INTO transactions (company, category, amount, type) VALUES (%s, %s, %s, 'INCOME')"
                self.cur.execute(log_query, (comp, tp, amount_int))

                self.sync_finance_summary()
                self.con.commit()
                
                tk.messagebox.showinfo("Success", f"Rs. {amount_int:,} added as Income under '{tp}' for {comp}")
                
                self.refresh_company_list()
                self.update_table_view()
                self.amount.delete(0, tk.END)
                self.type.delete(0, tk.END)

            except ValueError:
                tk.messagebox.showerror("Format Error", "Amount field must be a valid integer number")
            except Exception as e:
                tk.messagebox.showerror("Database Error", f"Error: {e}")
            finally:
                if hasattr(self, 'con') and self.con.open:
                    self.con.close()
        else:
            tk.messagebox.showerror("Inputs Error", "Please provide Company Name and Amount.")

    def expfun(self):
        comp = self.company_combo.get().strip().upper()
        amount = self.amount.get().strip()
        tp = self.type.get().strip() or "Misc Expense"

        if comp and amount:
            try:
                amount_int = int(amount)
                self.dbconnectfun()

                log_query = "INSERT INTO transactions (company, category, amount, type) VALUES (%s, %s, %s, 'EXPENSE')"
                self.cur.execute(log_query, (comp, tp, amount_int))

                self.sync_finance_summary()
                self.con.commit()

                tk.messagebox.showinfo("Success", f"Rs. {amount_int:,} added as Expense under '{tp}' for {comp}")

                self.refresh_company_list()
                self.update_table_view()
                self.amount.delete(0, tk.END)
                self.type.delete(0, tk.END)

            except ValueError:
                tk.messagebox.showerror("Format Error", "Amount field must be a valid integer number")
            except Exception as e:
                tk.messagebox.showerror("Database Error", f"Error: {e}")
            finally:
                if hasattr(self, 'con') and self.con.open:
                    self.con.close()
        else:
            tk.messagebox.showerror("Inputs Error", "Please provide Company Name and Amount.")

    def deletefun(self):
        comp = self.company_combo.get().strip().upper()
        if not comp:
            tk.messagebox.showerror("Selection Error", "Please select or enter a Company name to delete.")
            return

        confirm = tk.messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete data for '{comp}'?",
        )
        if not confirm:
            return

        try:
            self.dbconnectfun()
            self.cur.execute("DELETE FROM finance WHERE company=%s", (comp,))
            self.cur.execute("DELETE FROM transactions WHERE company=%s", (comp,))
            self.con.commit()

            tk.messagebox.showinfo("Success", f"Data for '{comp}' deleted successfully!")

            self.company_combo.set('')
            self.refresh_company_list()
            self.update_table_view()

            if self.analysis_canvas:
                self.analysis_canvas.get_tk_widget().destroy()
                self.analysis_canvas = None

        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to delete record:\n{e}")
        finally:
            if hasattr(self, 'con') and self.con.open:
                self.con.close()

    def auditfun(self):
        """Dynamic multi-category chart rendering across ALL logged income/expense categories."""
        comp = self.company_combo.get().strip().upper()
        if not comp:
            tk.messagebox.showerror("Selection Error", "Please select a company to run analysis.")
            return

        try:
            self.dbconnectfun()
            
            # 1. Total Inflow & Outflow Calculation
            sum_query = """
                SELECT 
                    SUM(CASE WHEN type = 'INCOME' THEN amount ELSE 0 END),
                    SUM(CASE WHEN type = 'EXPENSE' THEN amount ELSE 0 END)
                FROM transactions 
                WHERE company = %s
            """
            self.cur.execute(sum_query, (comp,))
            data = self.cur.fetchone()
            
            if not data or (data[0] is None and data[1] is None):
                tk.messagebox.showwarning("Data Void", f"No transaction logs found for '{comp}'.")
                return

            inc = int(data[0]) if data[0] is not None else 0
            exp = int(data[1]) if data[1] is not None else 0
            audit = inc - exp

            # 2. Query ALL categories (both Income and Expense) dynamically grouped
            cat_query = """
                SELECT category, type, SUM(amount) 
                FROM transactions 
                WHERE company = %s 
                GROUP BY category, type
            """
            self.cur.execute(cat_query, (comp,))
            cat_data = self.cur.fetchall()

            self.update_table_view()

            if self.analysis_canvas:
                self.analysis_canvas.get_tk_widget().destroy()

            fig = Figure(figsize=(8.5, 2.3), dpi=100)
            fig.patch.set_facecolor(self.BG_CARD)

            # SUBPLOT 1: Balance Summary Bar Chart
            ax1 = fig.add_subplot(121)
            ax1.set_facecolor(self.BG_CARD)

            metrics = ["Inflow", "Outflow", "Balance"]
            values = [inc, exp, audit]
            bar_colors = [
                self.COLOR_GREEN,
                self.COLOR_RED,
                self.COLOR_BLUE if audit >= 0 else self.COLOR_AMBER,
            ]

            bars = ax1.bar(metrics, values, color=bar_colors, width=0.45, edgecolor=self.BG_CARD)

            for bar in bars:
                height = float(bar.get_height())
                va_align = 'bottom' if height >= 0 else 'top'
                y_pos = height if height >= 0 else height - (max(abs(v) for v in values) * 0.08 if values else 1)
                ax1.annotate(
                    f"₹{int(height):,}",
                    xy=(bar.get_x() + bar.get_width() / 2, y_pos),
                    xytext=(0, 2 if height >= 0 else -6),
                    textcoords="offset points",
                    ha='center', va=va_align,
                    fontsize=7, fontweight='bold',
                    color=self.TEXT_PRIMARY
                )

            ax1.set_title(f"Balance Summary ({comp})", fontsize=9, fontweight="bold", color=self.TEXT_PRIMARY)
            ax1.tick_params(colors=self.TEXT_MUTED, labelsize=8)
            ax1.grid(axis="y", linestyle="--", alpha=0.15, color=self.TEXT_PRIMARY)
            for spine in ax1.spines.values():
                spine.set_visible(False)

            # SUBPLOT 2: Dynamic All-Category Distribution Pie Chart
            ax2 = fig.add_subplot(122)
            ax2.set_facecolor(self.BG_CARD)

            if cat_data:
                categories = []
                amounts = []

                for r in cat_data:
                    cat_name = str(r[0])
                    tx_type = str(r[1])
                    amt = float(r[2]) if r[2] is not None else 0.0
                    
                    prefix = "[IN]" if tx_type == "INCOME" else "[OUT]"
                    categories.append(f"{prefix} {cat_name}")
                    amounts.append(amt)

                if amounts and sum(amounts) > 0:
                    num_cats = len(categories)
                    # FIX: Using matplotlib.colormaps to maintain modern compatibility
                    import matplotlib.pyplot as plt
                    cmap = plt.get_cmap('tab20' if num_cats > 10 else 'tab10')
                    generated_colors = [cmap(i / max(1, num_cats - 1)) for i in range(num_cats)]

                    wedges, texts, autotexts = ax2.pie(
                        amounts,
                        labels=categories,
                        autopct='%1.1f%%',
                        startangle=140,
                        colors=generated_colors,
                        textprops=dict(color=self.TEXT_PRIMARY, fontsize=7, fontweight='bold'),
                        wedgeprops=dict(width=0.5, edgecolor=self.BG_CARD)
                    )
                    for autotext in autotexts:
                        autotext.set_color('#FFFFFF')
                    ax2.set_title("All Categories Logged", fontsize=9, fontweight="bold", color=self.TEXT_PRIMARY)
                else:
                    ax2.text(0.5, 0.5, "No Category Data", ha='center', va='center', color=self.TEXT_MUTED, fontsize=8)
                    ax2.axis('off')
            else:
                ax2.text(0.5, 0.5, "No Category Data", ha='center', va='center', color=self.TEXT_MUTED, fontsize=8)
                ax2.axis('off')

            fig.tight_layout()

            self.analysis_canvas = FigureCanvasTkAgg(fig, master=self.chart_card)
            self.analysis_canvas.draw()
            self.analysis_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 5))

        except Exception as e:
            tk.messagebox.showerror("Audit Error", f"Audit calculations halted:\n{e}")
        finally:
            if hasattr(self, 'con') and self.con.open:
                self.con.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernFinanceDashboard(root)
    root.mainloop()
