import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import os

class TypingTestApp:
    """A typing test application built with Tkinter, featuring a modern GUI,
    multiple test options, and real-time performance tracking."""
    def __init__(self, master):
        self.master = master
        self.master.title("Python Typing Test")
        self.master.geometry("1000x800")
        self.master.minsize(800, 600)

        # Set up a dictionary of sample texts for different difficulty levels.
        self.texts = {
            "easy": [
                "The quick brown fox jumps over the lazy dog. A journey of a thousand miles begins with a single step.",
                "Programming is fun and challenging. Practice makes a person perfect. Enjoy your day and keep learning.",
                "An apple a day keeps the doctor away. The sun always shines after the rain. Good things come to those who wait."
            ],
            "medium": [
                "The burgeoning technology sector is reshaping economies and societies globally, with innovation as its core driver.",
                "Quantum computing promises to revolutionize fields like cryptography and medicine by solving problems currently deemed intractable.",
                "The complexities of international trade agreements often involve a delicate balance between national interests and global cooperation."
            ],
            "hard": [
                "The quintessential philosophical dilemma of determinism versus free will has captivated thinkers for centuries, exploring the nature of choice.",
                "Neuroplasticity, the brain's remarkable ability to reorganize itself by forming new neural connections throughout life, is a fascinating phenomenon.",
                "The anachronistic political structures of certain states often struggle to adapt to the rapid pace of technological and social change."
            ]
        }

        # Initialize game state variables
        self.username = ""
        self.timer_seconds = 0
        self.start_time = 0
        self.wpm = 0
        self.accuracy = 0.0
        self.is_running = False
        self.test_text = ""
        self.user_input = ""
        self.correct_chars = 0
        self.timer_after_id = None # ID for the scheduled timer event

        # --- GUI STYLES ---
        style = ttk.Style()
        style.theme_use('clam')  # Using a modern theme
        style.configure("TFrame", background="#f4f4f9")
        style.configure("TButton", font=("Arial", 12), padding=10, relief="flat", background="#007bff", foreground="white")
        style.map("TButton", background=[('active', '#0056b3')])
        style.configure("TLabel", font=("Arial", 12), background="#f4f4f9", foreground="#333")
        style.configure("Title.TLabel", font=("Arial", 24, "bold"), foreground="#007bff")
        style.configure("Result.TLabel", font=("Arial", 16, "bold"), foreground="#333")
        style.configure("Input.TEntry", font=("Courier", 14), fieldbackground="#ffffff", borderwidth=1, relief="solid")
        
        # Create frames for different screens
        self.main_frame = ttk.Frame(master, padding="40", style="TFrame")
        self.options_frame = ttk.Frame(master, padding="40", style="TFrame")
        self.test_frame = ttk.Frame(master, padding="40", style="TFrame")
        self.results_frame = ttk.Frame(master, padding="40", style="TFrame")

        self.show_main_screen()

    # --- SCREEN MANAGEMENT FUNCTIONS ---
    def hide_all_frames(self):
        """Hides all frames to switch screens."""
        for frame in [self.main_frame, self.options_frame, self.test_frame, self.results_frame]:
            frame.pack_forget()

    def show_main_screen(self):
        """Shows the initial username input screen."""
        self.hide_all_frames()
        self.main_frame.pack(expand=True, fill="both")
        
        ttk.Label(self.main_frame, text="Welcome to the Typing Test!", style="Title.TLabel").pack(pady=30)
        ttk.Label(self.main_frame, text="Please enter your username:", style="TLabel").pack(pady=10)
        
        self.username_entry = ttk.Entry(self.main_frame, font=("Arial", 14), width=30)
        self.username_entry.pack(pady=10)
        self.username_entry.focus()
        
        ttk.Button(self.main_frame, text="Continue", command=self.show_options_screen).pack(pady=30)

    def show_options_screen(self):
        """Shows the screen for selecting test options."""
        self.username = self.username_entry.get().strip()
        if not self.username:
            messagebox.showerror("Error", "Please enter a valid username.")
            return

        self.hide_all_frames()
        self.options_frame.pack(expand=True, fill="both")

        ttk.Label(self.options_frame, text=f"Hello, {self.username}!", style="Title.TLabel").pack(pady=20)
        ttk.Label(self.options_frame, text="Choose your test options:", style="TLabel").pack(pady=10)
        
        # Test Type selection
        ttk.Label(self.options_frame, text="Select Test Type:", style="Result.TLabel").pack(pady=(20, 5))
        self.test_type = tk.StringVar(value="paragraph")
        ttk.Radiobutton(self.options_frame, text="Paragraph", variable=self.test_type, value="paragraph").pack(anchor="center")
        ttk.Radiobutton(self.options_frame, text="Sentence-wise", variable=self.test_type, value="sentence").pack(anchor="center")

        # Timer selection
        ttk.Label(self.options_frame, text="Select Timer Duration (seconds):", style="Result.TLabel").pack(pady=(20, 5))
        self.timer_duration = tk.IntVar(value=60)
        for duration in [30, 60, 90, 120, 180]:
            ttk.Radiobutton(self.options_frame, text=f"{duration} seconds", variable=self.timer_duration, value=duration).pack(anchor="center")

        # Difficulty selection
        ttk.Label(self.options_frame, text="Select Difficulty Level:", style="Result.TLabel").pack(pady=(20, 5))
        self.difficulty_level = tk.StringVar(value="easy")
        ttk.Radiobutton(self.options_frame, text="Easy", variable=self.difficulty_level, value="easy").pack(anchor="center")
        ttk.Radiobutton(self.options_frame, text="Medium", variable=self.difficulty_level, value="medium").pack(anchor="center")
        ttk.Radiobutton(self.options_frame, text="Hard", variable=self.difficulty_level, value="hard").pack(anchor="center")
        
        ttk.Button(self.options_frame, text="Start Test", command=self.start_test_screen).pack(pady=40)

    def start_test_screen(self):
        """Prepares and shows the typing test screen."""
        self.hide_all_frames()
        self.test_frame.pack(expand=True, fill="both")
        
        # Choose text based on user selections
        if self.test_type.get() == "paragraph":
            self.test_text = random.choice(self.texts[self.difficulty_level.get()])
        else: # Sentence-wise
            all_sentences = ' '.join(self.texts[self.difficulty_level.get()]).split('.')
            self.test_text = ' '.join(random.sample([s.strip() for s in all_sentences if s.strip()], 3))

        # --- TEST GUI WIDGETS ---
        ttk.Label(self.test_frame, text="Type the text below:", style="Title.TLabel").pack(pady=10)
        
        self.text_display = tk.Text(self.test_frame, wrap="word", height=8, width=70, font=("Courier", 14), bg="#fff", bd=1, relief="solid")
        self.text_display.insert(tk.END, self.test_text)
        self.text_display.config(state="disabled")
        self.text_display.pack(pady=10)
        
        self.input_entry = ttk.Entry(self.test_frame, width=70, font=("Courier", 14), style="Input.TEntry")
        self.input_entry.pack(pady=10)
        self.input_entry.bind("<KeyRelease>", self.check_input)
        self.input_entry.bind("<BackSpace>", self.check_input) # Handle backspace key
        
        self.metrics_frame = ttk.Frame(self.test_frame, style="TFrame")
        self.metrics_frame.pack(pady=20)

        self.timer_label = ttk.Label(self.metrics_frame, text="Time: 0s", style="Result.TLabel")
        self.timer_label.grid(row=0, column=0, padx=20)
        
        self.wpm_label = ttk.Label(self.metrics_frame, text="WPM: 0", style="Result.TLabel")
        self.wpm_label.grid(row=0, column=1, padx=20)
        
        self.accuracy_label = ttk.Label(self.metrics_frame, text="Accuracy: 0%", style="Result.TLabel")
        self.accuracy_label.grid(row=0, column=2, padx=20)

        # Set up text tags for coloring
        self.text_display.tag_configure("correct", foreground="green")
        self.text_display.tag_configure("incorrect", foreground="red")
        self.text_display.tag_configure("current", background="#e0e0e0")

        # Start the test
        self.is_running = True
        self.start_time = time.time()
        self.input_entry.focus()
        self.update_timer()

    def show_results_screen(self):
        """Shows the final results screen and prompts for re-attempt."""
        self.hide_all_frames()
        self.results_frame.pack(expand=True, fill="both")
        
        ttk.Label(self.results_frame, text="Test Complete!", style="Title.TLabel").pack(pady=20)
        ttk.Label(self.results_frame, text=f"Username: {self.username}", style="Result.TLabel").pack(pady=5)
        ttk.Label(self.results_frame, text=f"Final WPM: {self.wpm:.2f}", style="Result.TLabel").pack(pady=5)
        ttk.Label(self.results_frame, text=f"Final Accuracy: {self.accuracy:.2f}%", style="Result.TLabel").pack(pady=5)
        
        # Save the score
        self.save_score()

        ttk.Label(self.results_frame, text="Would you like to try again?", style="TLabel").pack(pady=20)
        
        # Re-attempt buttons
        re_attempt_frame = ttk.Frame(self.results_frame, style="TFrame")
        re_attempt_frame.pack(pady=10)
        ttk.Button(re_attempt_frame, text="Take Same Test", command=self.restart_same_test).grid(row=0, column=0, padx=10)
        ttk.Button(re_attempt_frame, text="Take a Different Test", command=self.show_options_screen).grid(row=0, column=1, padx=10)

    # --- GAME LOGIC FUNCTIONS ---
    def update_timer(self):
        """Updates the timer and checks if the test is over."""
        if not self.is_running:
            return
        
        elapsed_time = time.time() - self.start_time
        self.timer_seconds = int(elapsed_time)
        self.timer_label.config(text=f"Time: {self.timer_seconds}s")
        
        if self.timer_seconds >= self.timer_duration.get():
            self.end_test()
        else:
            self.timer_after_id = self.master.after(1000, self.update_timer)

    def check_input(self, event):
        """Checks user input against the text and updates metrics in real-time."""
        if not self.is_running:
            return

        self.user_input = self.input_entry.get()
        typed_length = len(self.user_input)
        
        # Calculate WPM
        num_words = len(self.user_input.split())
        elapsed_minutes = (time.time() - self.start_time) / 60
        if elapsed_minutes > 0:
            self.wpm = num_words / elapsed_minutes
        self.wpm_label.config(text=f"WPM: {self.wpm:.2f}")

        # Calculate accuracy
        self.correct_chars = 0
        for i in range(typed_length):
            if i < len(self.test_text) and self.user_input[i] == self.test_text[i]:
                self.correct_chars += 1
        
        if typed_length > 0:
            self.accuracy = (self.correct_chars / typed_length) * 100
        else:
            self.accuracy = 0.0
        self.accuracy_label.config(text=f"Accuracy: {self.accuracy:.2f}%")

        # Color the displayed text
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        
        for i, char in enumerate(self.test_text):
            tag = "default"
            if i < typed_length:
                if self.user_input[i] == char:
                    tag = "correct"
                else:
                    tag = "incorrect"
            
            self.text_display.insert(tk.END, char, tag)
            
        self.text_display.config(state="disabled")

    def end_test(self):
        """Finalizes the test, calculates final scores, and shows results."""
        self.is_running = False
        if self.timer_after_id:
            self.master.after_cancel(self.timer_after_id)
        
        self.input_entry.config(state="disabled")
        
        # Calculate final WPM and accuracy based on total input
        typed_words = len(self.user_input.split())
        elapsed_minutes = self.timer_duration.get() / 60
        self.wpm = typed_words / elapsed_minutes
        
        self.correct_chars = 0
        for i in range(min(len(self.user_input), len(self.test_text))):
            if self.user_input[i] == self.test_text[i]:
                self.correct_chars += 1
        
        if len(self.user_input) > 0:
            self.accuracy = (self.correct_chars / len(self.user_input)) * 100
        else:
            self.accuracy = 0.0
            
        self.show_results_screen()
        
    def save_score(self):
        """Saves the user's score to a file."""
        if not os.path.exists("scores.txt"):
            with open("scores.txt", "w") as f:
                f.write("Username,WPM,Accuracy\n")
        
        with open("scores.txt", "a") as f:
            f.write(f"{self.username},{self.wpm:.2f},{self.accuracy:.2f}\n")

    def restart_same_test(self):
        """Restarts the test with the same text and settings."""
        if self.timer_after_id:
            self.master.after_cancel(self.timer_after_id)

        # Reset all test variables
        self.timer_seconds = 0
        self.start_time = 0
        self.wpm = 0
        self.accuracy = 0.0
        self.user_input = ""
        self.correct_chars = 0

        # Reset widgets and state
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert(tk.END, self.test_text)
        self.text_display.config(state="disabled")
        
        self.input_entry.delete(0, tk.END)
        self.input_entry.config(state="normal")
        self.input_entry.focus()
        
        self.timer_label.config(text="Time: 0s")
        self.wpm_label.config(text="WPM: 0")
        self.accuracy_label.config(text="Accuracy: 0%")

        # Start the test again
        self.is_running = True
        self.start_time = time.time()
        self.hide_all_frames()
        self.test_frame.pack(expand=True, fill="both")
        self.update_timer()


if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTestApp(root)
    root.mainloop()
