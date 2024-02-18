import customtkinter
import tkinter as tk
from tkinter import messagebox
import pyautogui
from PIL import Image
import easyocr
from openai import OpenAI

# Global variables
global crop_left_var, crop_top_var, crop_right_var, crop_bottom_var, \
    language_box, context_box, model_box, extracted_box, response_box, \
    show_full_screen_button, show_crop_button, error_label, tab_view, \
    language_options, model_options, context_entry, key_entry, result_str, \
    result_list, client, output
full_screen_mode = "off"


# Sets up the OpenAI client with the user's API key.
def set_client():
    global client, key_entry
    user_key = key_entry.get()
    client = OpenAI(api_key=user_key)


# Takes a full screen screenshot and saves it.
def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot_path = 'images/full_screen.png'
    screenshot.save(screenshot_path)
    return screenshot_path


# Crops the screenshot based on user-defined coordinates.
def crop_screenshot():
    global crop_left_var, crop_top_var, crop_right_var, crop_bottom_var
    crop_left_int = int(crop_left_var.get())
    crop_top_int = int(crop_top_var.get())
    crop_right_int = int(crop_right_var.get())
    crop_bottom_int = int(crop_bottom_var.get())
    screenshot = Image.open('images/full_screen.png')
    box = (crop_left_int, crop_top_int, crop_right_int, crop_bottom_int)
    screenshot_cropped = screenshot.crop(box)
    screenshot_cropped.save('images/crop.png')


# Uses OCR to read text from the screenshot.
def read_screenshot():
    reader = easyocr.Reader(['en'])
    global result_list
    if full_screen_mode.get() == "on":
        result_list = reader.readtext('images/full_screen.png', detail=0, height_ths=1, width_ths=1)
    elif full_screen_mode.get() == "off":
        result_list = reader.readtext('images/crop.png', detail=0, height_ths=1, width_ths=1)
    global result_str
    result_str = ', '.join(result_list)
    return result_str


# Inserts results into the GUI.
def insert_results():
    global language_options, context_entry, model_options, output, result_str
    global language_box, context_box, model_box, extracted_box, response_box, tab_view

    tab_view.set("Results")

    language_box.configure(state="normal")
    language_box.delete("0.0", "end")
    language_box.insert("0.0", language_options.get())
    language_box.configure(state="disabled")

    context_box.configure(state="normal")
    context_box.delete("0.0", "end")
    context_box.insert("0.0", context_entry.get())
    context_box.configure(state="disabled")

    model_box.configure(state="normal")
    model_box.delete("0.0", "end")
    model_box.insert("0.0", model_options.get())
    model_box.configure(state="disabled")

    extracted_box.configure(state="normal")
    extracted_box.delete("0.0", "end")
    extracted_box.insert("0.0", result_str)
    extracted_box.configure(state="disabled")

    response_box.configure(state="normal")
    response_box.delete("0.0", "end")
    response_box.insert("0.0", output)
    response_box.configure(state="disabled")


# Sends a question to the OpenAI API and handles the response.
def ask_question(question, context):
    global client, model_options
    prompt = f"Question: {question}\nContext: {context}"
    response = client.chat.completions.create(
        model=model_options.get(),
        messages=[
            {"role": "system", "content": "Respond."},
            {"role": "user", "content": f"{prompt}"}
        ]
    )
    for choice in response.choices:
        global output
        output = choice.message.content
        print(f"Output: {output}")
        insert_results()


# Handles the full screen screenshot mode.
def full_screen():
    take_screenshot()
    read_screenshot()
    global result_str, context_entry
    ask_question(result_str, context_entry.get())


# Handles the cropped screenshot mode.
def crop():
    take_screenshot()
    crop_screenshot()
    read_screenshot()
    global result_str, context_entry
    ask_question(result_str, context_entry.get())


# Starts the process based on the user's input and selected mode.
def start():
    global error_label, context_entry
    if len(context_entry.get().split()) > 0:
        global key_entry
        if len(key_entry.get().split()) > 0:
            set_client()
            if full_screen_mode.get() == "on":
                global show_full_screen_button, show_crop_button
                show_full_screen_button.configure(state="normal", fg_color="#2FA572")
                show_crop_button.configure(state="disabled", fg_color="#17472E")
                full_screen()
            elif full_screen_mode.get() == "off":
                global crop_left_var, crop_top_var, crop_right_var, crop_bottom_var
                if crop_left_var.get().isnumeric() and crop_top_var.get().isnumeric() and crop_right_var.get().isnumeric() and crop_bottom_var.get().isnumeric():
                    show_full_screen_button.configure(state="normal", fg_color="#2FA572")
                    show_crop_button.configure(state="normal", fg_color="#2FA572")
                    error_label.configure(text=" ")
                    crop()
                else:
                    error_label.configure(text="Error: Crop value is not numeric.")
        elif len(key_entry.get().split()) == 0:
            error_label.configure(text="Error: API key is missing.")
            key_entry.focus()
    elif len(context_entry.get().split()) == 0:
        error_label.configure(text="Error: Context is missing.")
        context_entry.focus()


# Layout configuration for the GUI.
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Screenshot GPT")
        self.resizable(width=False, height=False)
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("green")
        customtkinter.deactivate_automatic_dpi_awareness()

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=10, sticky="nsew")

        self.title_label = customtkinter.CTkLabel(self.sidebar_frame, text="Screenshot GPT",
                                                  font=customtkinter.CTkFont(size=20, weight="normal"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(15, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:")
        self.appearance_mode_label.grid(row=2, column=0, padx=20, pady=(15, 3))
        self.appearance_mode = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"],
                                                           width=130, command=self.change_appearance_event)
        self.appearance_mode.grid(row=3, column=0, padx=20, pady=(0, 0))

        def open_info():
            messagebox.showinfo("Screenshot GPT", """
OpenAI Secret API Key: https://platform.openai.com/api-keys

GPT-4 models can solve difficult problems with greater accuracy.

GPT-3.5 models can understand and generate natural language.

Context Window:
    gpt-4-0125-preview: 128,000 tokens
    gpt-4-turbo-preview: 128,000 tokens
    gpt-4-1106-preview: 128,000 tokens
    gpt-3.5-turbo-1106: 16,385 tokens
    gpt-3.5-turbo-16k: 16,385 tokens
    gpt-3.5-turbo: 4,096 tokens

Training Data:
    gpt-4-0125-preview: Up to Dec 2023
    gpt-4-turbo-preview: Up to Dec 2023
    gpt-4-1106-preview: Up to Apr 2023
    gpt-3.5-turbo-1106: Up to Sep 2021
    gpt-3.5-turbo-16k: Up to Sep 2021
    gpt-3.5-turbo: Up to Sep 2021
""")

        self.info_label = customtkinter.CTkLabel(self.sidebar_frame, text="Need Help?")
        self.info_label.grid(row=4, column=0, padx=20, pady=(15, 3))

        self.info_button = customtkinter.CTkButton(self.sidebar_frame, text="Information",
                                                   width=130, command=open_info)
        self.info_button.grid(row=5, column=0, padx=20, pady=(0, 3))

        global error_label
        error_label = customtkinter.CTkLabel(self.sidebar_frame, text=" ", text_color="#FF5454")
        error_label.grid(row=4, column=0, padx=20, pady=(3, 3))

        global tab_view
        tab_view = customtkinter.CTkTabview(self)
        tab_view.grid(row=0, column=1, padx=20, pady=15)

        tab_view.add("Options")
        tab_view.add("Results")
        tab_view.set("Options")

        def full_screen_event():
            print("Full Screen:", full_screen_mode.get())
            if full_screen_mode.get() == "on":
                self.crop_left_entry.delete(0, tk.END)
                self.crop_left_entry.configure(state="disabled")

                self.crop_top_entry.delete(0, tk.END)
                self.crop_top_entry.configure(state="disabled")

                self.crop_right_entry.delete(0, tk.END)
                self.crop_right_entry.configure(state="disabled")

                self.crop_bottom_entry.delete(0, tk.END)
                self.crop_bottom_entry.configure(state="disabled")

            elif full_screen_mode.get() == "off":
                self.crop_left_entry.configure(state="normal")
                self.crop_top_entry.configure(state="normal")
                self.crop_right_entry.configure(state="normal")
                self.crop_bottom_entry.configure(state="normal")

        self.full_screen_label = customtkinter.CTkLabel(master=tab_view.tab("Options"), text="Full Screen")
        self.full_screen_label.grid(row=1, column=1, padx=(10, 0), pady=(15, 0), sticky="w")

        global full_screen_mode
        full_screen_mode = customtkinter.StringVar(value="on")
        self.full_screen_switch = customtkinter.CTkSwitch(master=tab_view.tab("Options"), text=" ",
                                                          command=full_screen_event, variable=full_screen_mode,
                                                          onvalue="on", offvalue="off")
        self.full_screen_switch.deselect()
        self.full_screen_switch.grid(row=1, column=2, padx=10, pady=(15, 3), sticky="w")

        self.crop_left_label = customtkinter.CTkLabel(master=tab_view.tab("Options"), text="Crop Left")
        self.crop_left_label.grid(row=2, column=1, padx=10, pady=(3, 0), sticky="w")

        global crop_left_var
        crop_left_var = customtkinter.StringVar(value='200')

        self.crop_left_entry = customtkinter.CTkEntry(master=tab_view.tab("Options"), width=120,
                                                      textvariable=crop_left_var)
        self.crop_left_entry.grid(row=2, column=2, padx=10, pady=(3, 0), sticky="w")

        self.crop_top_label = customtkinter.CTkLabel(master=tab_view.tab("Options"), text="Crop Top")
        self.crop_top_label.grid(row=3, column=1, padx=10, pady=(3, 0), sticky="w")

        global crop_top_var
        crop_top_var = customtkinter.StringVar(value='325')

        self.crop_top_entry = customtkinter.CTkEntry(master=tab_view.tab("Options"), width=120,
                                                     textvariable=crop_top_var)
        self.crop_top_entry.grid(row=3, column=2, padx=10, pady=(3, 0), sticky="w")

        self.crop_right_label = customtkinter.CTkLabel(master=tab_view.tab("Options"), text="Crop Right")
        self.crop_right_label.grid(row=4, column=1, padx=10, pady=(3, 0), sticky="w")

        global crop_right_var
        crop_right_var = customtkinter.StringVar(value='1500')

        self.crop_right_entry = customtkinter.CTkEntry(master=tab_view.tab("Options"), width=120,
                                                       textvariable=crop_right_var)
        self.crop_right_entry.grid(row=4, column=2, padx=10, pady=(3, 0), sticky="w")

        self.crop_bottom_label = customtkinter.CTkLabel(master=tab_view.tab("Options"), text="Crop Bottom")
        self.crop_bottom_label.grid(row=5, column=1, padx=10, pady=(3, 0), sticky="w")

        global crop_bottom_var
        crop_bottom_var = customtkinter.StringVar(value='800')

        self.crop_bottom_entry = customtkinter.CTkEntry(master=tab_view.tab("Options"), width=120,
                                                        textvariable=crop_bottom_var)
        self.crop_bottom_entry.grid(row=5, column=2, padx=10, pady=(3, 0), sticky="w")

        global context_entry
        self.context_label = customtkinter.CTkLabel(master=tab_view.tab("Options"), text="Context")
        self.context_label.grid(row=6, column=1, padx=10, pady=(15, 0), sticky="w")
        context_entry = customtkinter.CTkEntry(master=tab_view.tab("Options"), placeholder_text="", width=302)
        context_entry.grid(row=6, column=2, padx=10, pady=(15, 0), sticky="w")

        def clear_context():
            context_entry.delete(0, tk.END)

        self.clear_context_button = customtkinter.CTkButton(master=tab_view.tab("Options"), text="Clear", width=46,
                                                            fg_color=("#0C955A", "#106A43"),
                                                            hover_color=("#0B6E3D", "#17472E"),
                                                            command=clear_context)
        self.clear_context_button.grid(row=6, column=2, padx=(0, 10), pady=(15, 0), sticky="e")

        global language_options
        self.language_label = customtkinter.CTkLabel(master=tab_view.tab("Options"), text="Language")
        self.language_label.grid(row=7, column=1, padx=10, pady=(3, 0), sticky="w")
        language_options = customtkinter.CTkOptionMenu(master=tab_view.tab("Options"), values=["English"], width=350)
        language_options.grid(row=7, column=2, padx=10, pady=(3, 0), sticky="w")

        global key_entry
        self.api_key_label = customtkinter.CTkLabel(master=tab_view.tab("Options"), text="API Key")
        self.api_key_label.grid(row=8, column=1, padx=10, pady=(15, 0), sticky="w")
        key_entry = customtkinter.CTkEntry(master=tab_view.tab("Options"), placeholder_text="", show="*", width=302)
        key_entry.grid(row=8, column=2, padx=(10, 0), pady=(15, 0), sticky="w")

        def show_key():
            if key_entry.cget("show") == "*":
                key_entry.configure(show="")
                self.show_key_button.configure(text="Hide")
            else:
                key_entry.configure(show="*")
                self.show_key_button.configure(text="Show")

        self.show_key_button = customtkinter.CTkButton(master=tab_view.tab("Options"), text="Show", width=46,
                                                       fg_color=("#0C955A", "#106A43"),
                                                       hover_color=("#0B6E3D", "#17472E"),
                                                       command=show_key)
        self.show_key_button.grid(row=8, column=2, padx=(0, 10), pady=(15, 0), sticky="e")

        global model_options
        self.model_label = customtkinter.CTkLabel(master=tab_view.tab("Options"), text="Model")
        self.model_label.grid(row=9, column=1, padx=10, pady=(3, 0), sticky="w")
        model_options = customtkinter.CTkOptionMenu(master=tab_view.tab("Options"),
                                                    values=["gpt-4-0125-preview", "gpt-4-turbo-preview",
                                                            "gpt-4-1106-preview", "gpt-3.5-turbo-1106",
                                                            "gpt-3.5-turbo-16k", "gpt-3.5-turbo"],
                                                    width=350)
        model_options.grid(row=9, column=2, padx=10, pady=(3, 0), sticky="w")

        def start_event():
            start()

        self.start_button = customtkinter.CTkButton(tab_view.tab("Options"), text="Start",
                                                    width=130, command=start_event)
        self.start_button.grid(row=10, column=2, padx=10, pady=(15, 15), sticky="e")

        options_title_label = customtkinter.CTkLabel(tab_view.tab("Results"), text="Options",
                                                     font=customtkinter.CTkFont(size=20, weight="normal"))
        options_title_label.grid(row=0, column=0, padx=10, pady=(15, 0), sticky="w")

        global context_box
        self.context_option_label = customtkinter.CTkLabel(master=tab_view.tab("Results"), text="Context")
        self.context_option_label.grid(row=1, column=0, padx=10, pady=(3, 0), sticky="w")
        context_box = customtkinter.CTkTextbox(master=tab_view.tab("Results"), width=363, height=30, state="disabled")
        context_box.grid(row=1, column=1, padx=10, pady=(3, 0), sticky="w")

        global language_box
        self.lang_option_label = customtkinter.CTkLabel(master=tab_view.tab("Results"), text="Language")
        self.lang_option_label.grid(row=2, column=0, padx=10, pady=(3, 0), sticky="w")
        language_box = customtkinter.CTkTextbox(master=tab_view.tab("Results"), width=363, height=30, state="disabled")
        language_box.grid(row=2, column=1, padx=10, pady=(3, 0), sticky="w")

        global model_box
        self.model_option_label = customtkinter.CTkLabel(master=tab_view.tab("Results"), text="Model")
        self.model_option_label.grid(row=3, column=0, padx=10, pady=(3, 15), sticky="w")
        model_box = customtkinter.CTkTextbox(master=tab_view.tab("Results"), width=363, height=30, state="disabled")
        model_box.grid(row=3, column=1, padx=10, pady=(3, 15), sticky="w")

        results_title_label = customtkinter.CTkLabel(tab_view.tab("Results"), text="Results",
                                                     font=customtkinter.CTkFont(size=20, weight="normal"))
        results_title_label.grid(row=4, column=0, padx=10, pady=(15, 0), sticky="w")

        def show_full_screen_event():
            full_screen_image = Image.open('images/full_screen.png')
            full_screen_image.show()

        def show_crop_event():
            crop_image = Image.open('images/crop.png')
            crop_image.show()

        self.image_label = customtkinter.CTkLabel(master=tab_view.tab("Results"), text="Images")
        self.image_label.grid(row=5, column=0, padx=10, pady=(3, 0), sticky="w")

        global show_full_screen_button, show_crop_button
        show_full_screen_button = customtkinter.CTkButton(master=tab_view.tab("Results"), text="Full Screen",
                                                          width=180, state="disabled", fg_color=("#0B6E3D", "#17472E"),
                                                          command=show_full_screen_event)
        show_full_screen_button.grid(row=5, column=1, padx=10, pady=(3, 0), sticky="w")
        show_crop_button = customtkinter.CTkButton(master=tab_view.tab("Results"), text="Cropped (if available)",
                                                   width=180, state="disabled", fg_color=("#0B6E3D", "#17472E"),
                                                   command=show_crop_event)
        show_crop_button.grid(row=5, column=1, padx=10, pady=(3, 0), sticky="e")

        global extracted_box
        self.extracted_label = customtkinter.CTkLabel(master=tab_view.tab("Results"), text="Extracted")
        self.extracted_label.grid(row=6, column=0, padx=10, pady=(3, 0), sticky="nw")
        extracted_box = customtkinter.CTkTextbox(master=tab_view.tab("Results"), width=363, height=100,
                                                 state="disabled")
        extracted_box.grid(row=6, column=1, padx=10, pady=(3, 0), sticky="w")

        global response_box
        self.result_label = customtkinter.CTkLabel(master=tab_view.tab("Results"), text="Response")
        self.result_label.grid(row=7, column=0, padx=10, pady=(3, 15), sticky="nw")
        response_box = customtkinter.CTkTextbox(master=tab_view.tab("Results"), width=363, height=100, state="disabled")
        response_box.grid(row=7, column=1, padx=10, pady=(3, 15), sticky="w")

    def change_appearance_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)


# Initialization
if __name__ == "__main__":
    app = App()
    app.mainloop()
