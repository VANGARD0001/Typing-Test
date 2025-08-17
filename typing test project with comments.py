# =============================================================================
#                            IMPORTS AND SETUP
# =============================================================================
# Import the modern 'ttkbootstrap' library instead of the standard tkinter 'ttk'.
# This gives us modern-looking widgets and themes out of the box.
import ttkbootstrap as ttk
from ttkbootstrap.constants import * # Imports constants like LEFT, RIGHT, for easier layout management.
from ttkbootstrap.scrolled import ScrolledFrame # Import a special frame that adds a scrollbar when content overflows.

# Import standard Python libraries.
import time      # For tracking time during the test.
import random    # For choosing random text passages.
import os        # For interacting with the operating system (e.g., checking if the scores file exists).
import csv       # UPDATED: Use csv module for robust CSV writing (handles quoting, commas properly).

# Import specific components from the standard 'tkinter' library.
from tkinter import messagebox, Text  # messagebox for showing pop-up errors; Text widget for multi-line text display.


# =============================================================================
#                            MAIN APPLICATION CLASS
# =============================================================================
# A 'class' is a blueprint for creating objects. We define our entire application
# within this TypingTestApp class to keep all related functions and variables organized.
class TypingTestApp:
    # The __init__ method is the "constructor" of the class. It runs automatically
    # as soon as we create a TypingTestApp object. It's where we set up everything.
    def __init__(self, master):
        # 'master' is the main window of our application. We save it as 'self.master'
        # so we can access it from any other function within the class.
        self.master = master
        self.master.title("Modern Python Typing Test")
        self.master.geometry("1000x800")  # Set the initial size of the window.
        self.master.minsize(800, 550)     # Set the smallest size the window can be resized to.

        # --- Sample Texts ---
        # A dictionary to hold all the typing passages, organized by difficulty.
        # This makes it easy to add more texts in the future.
        self.texts = {
            "easy": [
                "The quick brown fox jumps over the lazy dog. A journey of a thousand miles begins with a single step.",
                "Programming is fun and challenging. Practice makes a person perfect. Enjoy your day and keep learning.",
                "An apple a day keeps the doctor away. The sun always shines after the rain. Good things come to those who wait.",
                "Never underestimate the power of a good book. The world is full of amazing places to discover.",
                "The early bird catches the worm. Look for the silver lining in every cloud. Simple joys are the best."
            ],
            "medium": [
                "The burgeoning technology sector is reshaping economies and societies globally, with innovation as its core driver.",
                "Quantum computing promises to revolutionize fields like cryptography and medicine by solving problems currently deemed intractable.",
                "The complexities of international trade agreements often involve a delicate balance between national interests and global cooperation.",
                "Artificial intelligence is rapidly advancing, posing both unprecedented opportunities and profound ethical questions for humanity.",
                "Sustainability has become a critical imperative, forcing industries to reconsider their environmental impact and resource consumption."
            ],
            "hard": [
                "The quintessential philosophical dilemma of determinism versus free will has captivated thinkers for centuries, exploring the nature of choice.",
                "Neuroplasticity, the brain's remarkable ability to reorganize itself by forming new neural connections throughout life, is a fascinating phenomenon.",
                "The anachronistic political structures of certain states often struggle to adapt to the rapid pace of technological and social change.",
                "Epistemological inquiries challenge our fundamental assumptions about knowledge, truth, and justification, forming the bedrock of rational discourse.",
                "The Byzantine intricacies of quantum chromodynamics describe the strong nuclear force, binding quarks together to form protons and neutrons."
            ]
        }

        # --- State Variables ---
        # These variables act as the application's memory, tracking the current state of the test.
        self.username = ""              # Stores the player's name.
        self.timer_seconds = 0          # How many seconds have passed in the current test.
        self.start_time = 0             # The exact moment (timestamp) the test began.
        self.wpm = 0                    # The calculated words per minute.
        self.accuracy = 0.0             # The calculated accuracy percentage.
        self.is_running = False         # A boolean flag to check if a test is currently active.
        self.test_started = False       # A boolean flag to check if the user has typed the first key.
        self.test_text = ""             # The specific passage chosen for the current test.
        self.user_input = ""            # The current text typed by the user.
        self.correct_chars = 0          # A count of correctly typed characters.
        self.timer_after_id = None      # Stores the ID of the scheduled timer event, so we can cancel it.

        # --- Ghost/Pacemaker Variables ---
        self.ghost_wpm = ttk.IntVar(value=50) # A special tkinter variable to hold the target WPM for the ghost.
        self.ghost_position = 0               # The character index of the ghost cursor.
        self.ghost_after_id = None            # The ID for the ghost's scheduled movement event.

        # --- GUI Frames ---
        # Frames are invisible containers that hold widgets and help organize the layout.
        # We create one frame for each "screen" of our application.
        self.main_frame = ttk.Frame(master, padding="40")
        self.options_frame = ScrolledFrame(master, padding="40", autohide=True) # A scrollable frame for options.
        self.test_frame = ttk.Frame(master, padding="40")
        self.results_frame = ttk.Frame(master, padding="40")

        # Start the application by showing the initial welcome screen.
        self.show_main_screen()

    # =============================================================================
    #                        SCREEN MANAGEMENT FUNCTIONS
    # =============================================================================
    # This function hides all frames, giving us a blank slate to draw a new screen on.
    def hide_all_frames(self):
        for frame in [self.main_frame, self.options_frame, self.test_frame, self.results_frame]:
            frame.pack_forget() # .pack_forget() removes the frame from view.

    # Sets up and displays the initial username entry screen.
    def show_main_screen(self):
        self.hide_all_frames() # Clear the window first.
        self.main_frame.pack(expand=True, fill="both") # Show the main frame.

        # Create and place widgets for the main screen.
        ttk.Label(self.main_frame, text="Welcome to the Typing Test!", font=("Helvetica", 24, "bold"), bootstyle="primary").pack(pady=30)
        ttk.Label(self.main_frame, text="Please enter your username:", font=("Helvetica", 14)).pack(pady=10)

        self.username_entry = ttk.Entry(self.main_frame, font=("Arial", 14), width=30)
        self.username_entry.pack(pady=10)
        self.username_entry.focus() # Automatically place the cursor in this entry box.

        # Bind the "Enter" key to the on_press_enter_main function.
        # This means pressing Enter will act like clicking the "Continue" button.
        self.username_entry.bind("<Return>", self.on_press_enter_main)

        ttk.Button(self.main_frame, text="Continue", command=self.show_options_screen, bootstyle="success").pack(pady=30)

    # This function is called when the Enter key is pressed on the main screen.
    def on_press_enter_main(self, event=None): # 'event=None' is needed because the key binding passes an event object.
        self.show_options_screen()

    # Sets up and displays the screen where the user chooses test options.
    def show_options_screen(self):
        # Get the username from the entry box and remove any leading/trailing whitespace.
        self.username = self.username_entry.get().strip()
        if not self.username:
            messagebox.showerror("Error", "Please enter a valid username.")
            return # Stop the function if the username is empty.

        self.hide_all_frames()
        self.options_frame.pack(expand=True, fill="both") # Show the scrollable options frame.

        # Create and place all the option widgets (radio buttons, spinbox, etc.).
        ttk.Label(self.options_frame, text=f"Hello, {self.username}!", font=("Helvetica", 24, "bold"), bootstyle="primary").pack(pady=20)
        ttk.Label(self.options_frame, text="Choose your test options:", font=("Helvetica", 14)).pack(pady=10)

        # Test Type Selection
        ttk.Label(self.options_frame, text="Test Type", font=("Helvetica", 16, "bold")).pack(pady=(20, 5))
        self.test_type = ttk.StringVar(value="paragraph")
        ttk.Radiobutton(self.options_frame, text="Paragraph", variable=self.test_type, value="paragraph", bootstyle="info-toolbutton").pack(anchor="center", pady=2, fill='x', padx=200)
        ttk.Radiobutton(self.options_frame, text="Sentence-wise", variable=self.test_type, value="sentence", bootstyle="info-toolbutton").pack(anchor="center", pady=2, fill='x', padx=200)

        # Timer Duration Selection
        ttk.Label(self.options_frame, text="Timer Duration (seconds)", font=("Helvetica", 16, "bold")).pack(pady=(20, 5))
        self.timer_duration = ttk.IntVar(value=60)
        for duration in [30, 60, 90, 120, 180]:
            ttk.Radiobutton(self.options_frame, text=f"{duration} sec", variable=self.timer_duration, value=duration, bootstyle="info-toolbutton").pack(anchor="center", pady=2, fill='x', padx=200)

        # Difficulty Level Selection
        ttk.Label(self.options_frame, text="Difficulty Level", font=("Helvetica", 16, "bold")).pack(pady=(20, 5))
        self.difficulty_level = ttk.StringVar(value="easy")
        for level in ["easy", "medium", "hard"]:
             ttk.Radiobutton(self.options_frame, text=level.title(), variable=self.difficulty_level, value=level, bootstyle="info-toolbutton").pack(anchor="center", pady=2, fill='x', padx=200)

        # Pacemaker WPM Selection
        ttk.Label(self.options_frame, text="Pacemaker WPM", font=("Helvetica", 16, "bold")).pack(pady=(20, 5))
        ghost_frame = ttk.Frame(self.options_frame)
        ghost_frame.pack()
        ttk.Spinbox(ghost_frame, from_=20, to=200, increment=5, textvariable=self.ghost_wpm, width=5, font=("Helvetica", 12)).pack(side=LEFT, padx=5)
        ttk.Label(ghost_frame, text="WPM").pack(side=LEFT)

        # Start Button
        ttk.Button(self.options_frame, text="Start Test", command=self.start_test_screen, bootstyle="success-lg").pack(pady=40)

    # Prepares and displays the main typing test screen.
    def start_test_screen(self):
        self.hide_all_frames()
        self.test_frame.pack(expand=True, fill="both")

        # Choose the test text based on the user's selections from the options screen.
        if self.test_type.get() == "paragraph":
            self.test_text = random.choice(self.texts[self.difficulty_level.get()])
        else: # Sentence-wise mode
            all_sentences = ' '.join(self.texts[self.difficulty_level.get()]).split('.')
            self.test_text = ' '.join(random.sample([s.strip() for s in all_sentences if s.strip()], 3))

        # Create and place the widgets for the test screen.
        ttk.Label(self.test_frame, text="Type the text below:", font=("Helvetica", 20, "bold"), bootstyle="primary").pack(pady=10)

        self.text_display = Text(self.test_frame, wrap="word", height=8, width=70, font=("Courier New", 16), relief="solid", bd=1)
        self.text_display.pack(pady=10)

        self.input_entry = ttk.Entry(self.test_frame, width=70, font=("Courier New", 16))
        self.input_entry.pack(pady=10)
        # Every time a key is released in this entry box, the 'check_input' function will run.
        self.input_entry.bind("<KeyRelease>", self.check_input)

        # Create a frame to hold the live metrics (Time, WPM, Accuracy).
        self.metrics_frame = ttk.Frame(self.test_frame)
        self.metrics_frame.pack(pady=20)
        self.timer_label = ttk.Label(self.metrics_frame, text="Time: 0s", font=("Helvetica", 16, "bold"))
        self.timer_label.grid(row=0, column=0, padx=20)
        self.wpm_label = ttk.Label(self.metrics_frame, text="WPM: 0", font=("Helvetica", 16, "bold"))
        self.wpm_label.grid(row=0, column=1, padx=20)
        self.accuracy_label = ttk.Label(self.metrics_frame, text="Accuracy: 0%", font=("Helvetica", 16, "bold"))
        self.accuracy_label.grid(row=0, column=2, padx=20)

        # Define 'tags' for coloring the text in the text_display widget.
        # We can later apply these tags to specific characters.
        self.text_display.tag_configure("correct", foreground="#00bc8c")   # A green color for correct characters.
        self.text_display.tag_configure("incorrect", foreground="#e74c3c") # A red color for incorrect characters.
        self.text_display.tag_configure("ghost", background="#555555")    # A gray background for the ghost cursor.

        # Call the function that resets all variables and sets up the test.
        self.reset_and_start_test_setup()

    # Displays the final results screen after the test is over.
    def show_results_screen(self):
        self.hide_all_frames()
        self.results_frame.pack(expand=True, fill="both")

        # Display the final scores.
        ttk.Label(self.results_frame, text="Test Complete!", font=("Helvetica", 24, "bold"), bootstyle="primary").pack(pady=20)
        ttk.Label(self.results_frame, text=f"Username: {self.username}", font=("Helvetica", 16)).pack(pady=5)
        ttk.Label(self.results_frame, text=f"Final WPM: {self.wpm:.2f}", font=("Helvetica", 16)).pack(pady=5)
        ttk.Label(self.results_frame, text=f"Final Accuracy: {self.accuracy:.2f}%", font=("Helvetica", 16)).pack(pady=5)

        # Save the score to the file.
        self.save_score()

        # Create buttons for re-attempting the test or exiting.
        re_attempt_frame = ttk.Frame(self.results_frame)
        re_attempt_frame.pack(pady=30)
        ttk.Button(re_attempt_frame, text="Take Same Test", command=self.restart_same_test, bootstyle="secondary").grid(row=0, column=0, padx=10)
        ttk.Button(re_attempt_frame, text="Change Options", command=self.show_options_screen, bootstyle="info").grid(row=0, column=1, padx=10)
        ttk.Button(self.results_frame, text="Exit", command=self.master.destroy, bootstyle="danger").pack(pady=20)

    # =============================================================================
    #                            CORE TEST LOGIC
    # =============================================================================
    # This function runs on a loop to update the timer label every second.
    def update_timer(self):
        if not self.is_running: return # Stop the loop if the test has ended.

        # Calculate elapsed time and update the label.
        elapsed_time = time.time() - self.start_time
        self.timer_seconds = int(elapsed_time)
        self.timer_label.config(text=f"Time: {self.timer_seconds}s")

        # Check if the time limit has been reached.
        if self.timer_seconds >= self.timer_duration.get():
            self.end_test()
        else:
            # Schedule this function to run again after 1000ms (1 second).
            self.timer_after_id = self.master.after(1000, self.update_timer)

    # This function runs on a loop to move the ghost cursor forward.
    def update_ghost_cursor(self):
        if not self.is_running or self.ghost_position >= len(self.test_text):
            return # Stop if test is over or ghost reaches the end.

        # Make the text widget editable temporarily to change tags.
        self.text_display.config(state="normal")
        # UPDATED: Only remove the previous 'ghost' tag if there *was* a previous position.
        if self.ghost_position > 0:
            self.text_display.tag_remove("ghost", f"1.{self.ghost_position-1}")
        # Move the 'ghost' tag to the current character.
        self.text_display.tag_add("ghost", f"1.{self.ghost_position}")
        # Make the text widget read-only again.
        self.text_display.config(state="disabled")

        self.ghost_position += 1 # Move to the next character position.

        # Calculate the delay for the next movement based on the target WPM.
        # The standard is 5 characters per word.
        target_wpm = self.ghost_wpm.get()
        if target_wpm == 0: return # Avoid a division-by-zero error.
        chars_per_second = (target_wpm * 5) / 60
        delay_ms = int(1000 / chars_per_second)
        # Schedule this function to run again after the calculated delay.
        self.ghost_after_id = self.master.after(delay_ms, self.update_ghost_cursor)

    # This function is the heart of the test. It runs on every keypress.
    def check_input(self, event):
        if not self.is_running: return

        # --- Start the test on the very first keypress ---
        if not self.test_started:
            self.test_started = True
            self.start_time = time.time() # Record the precise start time.
            self.update_timer()           # Start the main timer loop.
            self.update_ghost_cursor()    # Start the ghost cursor loop.

        self.user_input = self.input_entry.get()
        typed_length = len(self.user_input)

        # --- Live WPM Calculation ---
        # The standard formula for WPM is (characters typed / 5) / minutes elapsed.
        elapsed_minutes = (time.time() - self.start_time) / 60
        self.wpm = (typed_length / 5) / elapsed_minutes if elapsed_minutes > 0 else 0
        self.wpm_label.config(text=f"WPM: {self.wpm:.2f}")

        # --- Live Accuracy and Coloring ---
        self.correct_chars = 0
        self.text_display.config(state="normal")
        # Remove all previous color tags before reapplying them. This is inefficient but simple.
        # A more advanced version would only update the last character.
        self.text_display.tag_remove("correct", "1.0", "end")
        self.text_display.tag_remove("incorrect", "1.0", "end")

        # Loop through the typed text and apply the correct color tag to each character.
        for i in range(typed_length):
            if i < len(self.test_text):
                if self.user_input[i] == self.test_text[i]:
                    self.correct_chars += 1
                    self.text_display.tag_add("correct", f"1.{i}")
                else:
                    self.text_display.tag_add("incorrect", f"1.{i}")

        # Calculate and update the accuracy label.
        self.accuracy = (self.correct_chars / typed_length) * 100 if typed_length > 0 else 0
        self.accuracy_label.config(text=f"Accuracy: {self.accuracy:.2f}%")
        self.text_display.config(state="disabled")

        # If the user has typed the entire text, end the test.
        if typed_length == len(self.test_text):
            self.end_test()

    # This function is called when the test finishes, either by time or by completion.
    def end_test(self):
        self.is_running = False
        # Cancel any scheduled 'after' events to stop the timer loops.
        if self.timer_after_id: self.master.after_cancel(self.timer_after_id)
        if self.ghost_after_id: self.master.after_cancel(self.ghost_after_id)

        self.input_entry.config(state="disabled") # Disable the input box.

        # --- Final Score Calculation ---
        # Recalculate the scores one last time to ensure they are based on the final state.
        typed_length = len(self.input_entry.get())
        # UPDATED: Use the *actual* elapsed time since the test started (works for early finish too).
        elapsed_minutes = max((time.time() - self.start_time) / 60, 1e-9)
        self.wpm = (typed_length / 5) / elapsed_minutes if elapsed_minutes > 0 else 0
        self.correct_chars = sum(
            1 for i in range(min(typed_length, len(self.test_text)))
            if self.input_entry.get()[i] == self.test_text[i]
        )
        self.accuracy = (self.correct_chars / typed_length) * 100 if typed_length > 0 else 0.0

        self.show_results_screen()

    # Saves the final score to a CSV file.
    def save_score(self):
        try:
            # UPDATED: Use csv.writer with UTF-8 to handle commas/encoding safely. Keep header logic.
            file_exists = os.path.exists("scores.csv")
            with open("scores.csv", "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists or os.stat("scores.csv").st_size == 0:
                    writer.writerow(["Username", "WPM", "Accuracy", "Difficulty", "TestType", "Duration"])
                writer.writerow([
                    self.username,
                    f"{self.wpm:.2f}",
                    f"{self.accuracy:.2f}",
                    self.difficulty_level.get(),
                    self.test_type.get(),
                    self.timer_duration.get()
                ])
        except IOError as e:
            # If the file cannot be opened (e.g., it's open in Excel), show an error message.
            messagebox.showerror("Save Error", f"Could not save score to file: {e}")

    # This function is called when the "Take Same Test" button is clicked.
    def restart_same_test(self):
        self.hide_all_frames()
        self.test_frame.pack(expand=True, fill="both")
        self.reset_and_start_test_setup() # Call the main reset function.

    # This function resets the application state to prepare for a new test.
    def reset_and_start_test_setup(self):
        # Cancel any lingering timer events from the previous test.
        if self.timer_after_id: self.master.after_cancel(self.timer_after_id)
        if self.ghost_after_id: self.master.after_cancel(self.ghost_after_id)

        # Reset all state variables to their default values.
        self.is_running = True
        self.test_started = False
        self.timer_seconds = 0
        self.wpm = 0
        self.accuracy = 0.0
        self.user_input = ""
        self.correct_chars = 0
        self.ghost_position = 0

        # Reset the display labels.
        self.timer_label.config(text="Time: 0s")
        self.wpm_label.config(text="WPM: 0")
        self.accuracy_label.config(text="Accuracy: 0%")

        # --- Reset the Text Display and Input Box ---
        # This section is crucial for fixing the "retake test" bug.
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", "end")         # Clear any old text.
        self.text_display.insert("1.0", self.test_text)# Insert the new text.
        self.text_display.tag_remove("correct", "1.0", "end") # Remove all color tags.
        self.text_display.tag_remove("incorrect", "1.0", "end")
        self.text_display.tag_remove("ghost", "1.0", "end")
        self.text_display.config(state="disabled")

        self.input_entry.config(state="normal")
        self.input_entry.delete(0, "end") # CRITICAL: Clear the input box from the last attempt.
        self.input_entry.focus()


# =============================================================================
#                            PROGRAM ENTRY POINT
# =============================================================================
# This is a standard Python construct. The code inside this 'if' block will only
# run when the script is executed directly (not when it's imported as a module).
if __name__ == "__main__":
    # Create the main application window using a ttkbootstrap theme.
    root = ttk.Window(themename="superhero")
    # Create an instance of our application class, passing the main window to it.
    app = TypingTestApp(root)
    # Start the tkinter event loop. The program will now wait for user actions
    # (like clicks and keypresses) and will stay open until the window is closed.
    root.mainloop()
