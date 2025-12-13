import customtkinter as ctk
import os
import threading
import re
from src.utils.encoding_utils import safe_load_dotenv
from src.agents.sql_agent import run_sql_agent
from src.agents.mongo_agent import run_mongo_agent

# Configuración Inicial
safe_load_dotenv(verbose=True)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(1.0)  # Fix for "too big" UI
ctk.set_window_scaling(1.0)  # Fix for "too big" UI

class DatabaseAgentApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Ventana ---
        self.title("Agente de Base de Datos - AI Assistant")
        self.geometry("900x700")
        
        # Fuentes (para usar en tags)
        self.FONT_MAIN = "Segoe UI"
        self.FONT_MONO = "Consolas"

        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Header
        self.header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=("white", "#2b2b2b"))
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Agente de Datos", font=(self.FONT_MAIN, 20, "bold"))
        self.title_label.pack(side="left", padx=20, pady=15)

        self.db_var = ctk.StringVar(value="PostgreSQL")
        self.db_selector = ctk.CTkSegmentedButton(
            self.header_frame, 
            values=["PostgreSQL", "MongoDB"], 
            variable=self.db_var, 
            command=self.change_db_color,
            font=(self.FONT_MAIN, 13, "bold")
        )
        self.db_selector.pack(side="right", padx=20, pady=15)

        # 2. Chat Area
        self.chat_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_scroll.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # 3. Input Area
        self.input_frame = ctk.CTkFrame(self, height=80, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Escribe tu consulta aquí...", 
            height=50,
            font=(self.FONT_MAIN, 16),
            border_width=2,
            corner_radius=25
        )
        self.input_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.input_entry.bind("<Return>", self.send_query_event)

        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="↑", 
            width=50, 
            height=50,
            font=(self.FONT_MAIN, 26), # Larger for thin arrow visibility
            corner_radius=25,
            command=self.send_query
        )
        self.send_button.grid(row=0, column=1)
        
        self.status_label = ctk.CTkLabel(self.input_frame, text="", text_color="gray", font=(self.FONT_MAIN, 11))
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 0))

        # Bienvenida
        self.add_message("Sistema", "**Sistema**: Bienvenido. Selecciona la base de datos y escribe tu consulta.", "system")

    def change_db_color(self, value):
        if value == "MongoDB":
            self.db_selector.configure(selected_color="#00ed64", selected_hover_color="#00c050", text_color="white")
        else:
            self.db_selector.configure(selected_color="#336791", selected_hover_color="#28527a", text_color="white")

    def render_rich_text(self, textbox, markdown_text):
        """Simple markdown parser for CTkTextbox."""
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        
        # Normalize line endings
        markdown_text = markdown_text.replace('\r\n', '\n')
        
        # Configure Tags via underlying tk widget
        # RESTORING READABLE SIZES (approx 13-14px)
        textbox._textbox.tag_config("bold", font=(self.FONT_MAIN, 13, "bold"))
        textbox._textbox.tag_config("italic", font=(self.FONT_MAIN, 13, "italic"))
        textbox._textbox.tag_config("header", font=(self.FONT_MAIN, 16, "bold"))
        textbox._textbox.tag_config("code_block", font=(self.FONT_MONO, 12), background="#2b2b2b", foreground="#a5d6a7")
        textbox._textbox.tag_config("code_inline", font=(self.FONT_MONO, 12), background="#333333", foreground="#e0e0e0")
        # Removed "normal" tag config, relying on base font set in constructor
        
        # Split by tokens pattern
        pattern = r'(```[\s\S]*?```|\*\*.*?\*\*|`[^`\n]+`|###\s.*?$|\*.*?\*)'
        tokens = re.split(pattern, markdown_text, flags=re.MULTILINE)
        
        for token in tokens:
            if not token: continue
            
            if token.startswith("```") and token.endswith("```"):
                content = token[3:-3]
                if content.startswith('\n'): content = content[1:]
                first_line_end = content.find('\n')
                if first_line_end != -1 and first_line_end < 20: 
                     potential_lang = content[:first_line_end].strip()
                     if potential_lang and " " not in potential_lang:
                         content = content[first_line_end+1:]
                textbox.insert("end", f"\n{content}\n", "code_block")
                
            elif token.startswith("**") and token.endswith("**"):
                content = token[2:-2]
                textbox.insert("end", content, "bold")
            elif token.startswith("`") and token.endswith("`"):
                content = token[1:-1]
                textbox.insert("end", f" {content} ", "code_inline")
            elif token.startswith("### "):
                content = token[4:] + "\n"
                textbox.insert("end", content, "header")
            elif token.startswith("*") and token.endswith("*"):
                content = token[1:-1]
                textbox.insert("end", content, "italic")
            else:
                # Insert normal text without specific tag
                textbox.insert("end", token)

    def add_message(self, sender, text, msg_type="agent"):
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=5)

        # Colors & Alignment
        if msg_type == "user":
            bg_color = "#1f538d"
            text_color = "white"
            side = "right"
            padx_bubble = (50, 10)
            font_choice = (self.FONT_MAIN, 13)
        elif msg_type == "code":
            bg_color = "black" # Terminal black
            text_color = "#00ff00" # Hacker green
            side = "left"
            padx_bubble = (10, 50)
            font_choice = (self.FONT_MONO, 13)
        elif msg_type == "system":
            bg_color = "transparent"
            text_color = "gray"
            side = "top" 
            padx_bubble = (10, 10)
            font_choice = (self.FONT_MAIN, 12)
        elif msg_type == "error":
            bg_color = "#c62828"
            text_color = "white"
            side = "left"
            padx_bubble = (10, 50)
            font_choice = (self.FONT_MAIN, 13)
        else: # agent
            bg_color = ("#e0e0e0", "#3a3a3a")
            text_color = ("black", "white")
            side = "left"
            padx_bubble = (10, 50)
            font_choice = (self.FONT_MAIN, 13)

        # Bubble Container
        if msg_type == "system":
            lbl = ctk.CTkLabel(row, text=text, font=(self.FONT_MAIN, 12, "italic"), text_color="gray")
            lbl.pack(pady=2)
            return

        bubble = ctk.CTkFrame(row, fg_color=bg_color, corner_radius=16)
        bubble.pack(side=side, padx=padx_bubble)

        # Rich Text Box inside Bubble
        # Estimating height typically requires complex logic. 
        # For simplicity, we create a textbox with a reasonable width and 'auto' height behaviour simulation by lines.
        lines = text.count('\n') + len(text) // 60 + 1
        height = min(lines * 22, 400) # Max height limit
        
        # Rich Text Box inside Bubble
        # Dynamic height calculation
        # 1. Create with arbitrary height
        # CRITICAL: Pass font here for base text to ensure correct rendering/spacing
        textbox = ctk.CTkTextbox(
            bubble, 
            width=500 if msg_type == "code" else 400, 
            height=50, 
            fg_color="transparent", 
            text_color=text_color,
            wrap="word",
            font=font_choice if 'font_choice' in locals() else (self.FONT_MAIN, 13),
            activate_scrollbars=False 
        )
        textbox.pack(padx=10, pady=5)
        
        # 2. Render content
        self.render_rich_text(textbox, text)
        
        # 3. Calculate real height
        textbox.update_idletasks() 
        try:
            # Using dlineinfo to find the bottom of the text
            dline = textbox._textbox.dlineinfo("end-1c")
            if dline:
                check_y = dline[1]
                check_h = dline[3]
                new_height = check_y + check_h + 15
            else:
                # Fallback: Count displaylines (wrapped)
                count = textbox._textbox.count("1.0", "end", "displaylines") or [0]
                num_lines = int(count[0])
                if num_lines == 0: num_lines = text.count('\n') + 1
                new_height = (num_lines * 18) + 10
        except Exception:
            new_height = 50
        
        new_height = max(30, new_height)
        textbox.configure(height=new_height, state="disabled")
        self.after(50, self._scroll_down)

    def _scroll_down(self):
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def send_query_event(self, event):
        self.send_query()

    def send_query(self):
        query = self.input_entry.get().strip()
        if not query: return
        
        self.input_entry.delete(0, "end")
        self.add_message("Tú", f"**{query}**", "user") # User text bold automatically
        
        self.status_label.configure(text="Pensando...")
        self.input_entry.configure(state="disabled")
        self.send_button.configure(state="disabled")
        
        threading.Thread(target=self._process_backend, args=(query,)).start()

    def _process_backend(self, query):
        db_type = self.db_var.get()
        try:
            if db_type == "PostgreSQL":
                result = run_sql_agent(query)
            else:
                result = run_mongo_agent(query)
            
            self.after(0, lambda: self._on_response(result))
        except Exception as e:
            self.after(0, lambda: self._on_error(str(e)))

    def _on_response(self, result):
        self.status_label.configure(text="")
        self.input_entry.configure(state="normal")
        self.send_button.configure(state="normal")
        self.input_entry.focus()

        # Mostrar Código (si existe)
        if result.get("sql_queries"):
            for code in result["sql_queries"]:
                # Enviamos raw code para que use el estilo 'code' de add_message
                self.add_message("System", f"> Generated Query:\n{code}", "code")

        # Mostrar Respuesta
        if result.get("error"):
             self.add_message("System", f"**Error**: {result['error']}", "error")
        else:
             answer = result.get("answer", "Sin respuesta")
             self.add_message("Agent", answer, "agent")

    def _on_error(self, error_msg):
        self.status_label.configure(text="Error")
        self.input_entry.configure(state="normal")
        self.send_button.configure(state="normal")
        self.add_message("System", f"**Crash**: {error_msg}", "error")

if __name__ == "__main__":
    app = DatabaseAgentApp()
    app.mainloop()
