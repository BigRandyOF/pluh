import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime
import json
import os

# Function to create a gradient background
def create_gradient(width, height, start_color, end_color):
    base = Image.new('RGB', (width, height), start_color)
    top = Image.new('RGB', (width, height), end_color)
    mask = Image.new("L", (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return ImageTk.PhotoImage(base)

# Function to create a rounded rectangle image (for glassmorphism effect)
def create_rounded_rectangle(width, height, radius, color, opacity):
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=color + (opacity,))
    return ImageTk.PhotoImage(image)

class CheckInOut:
    def __init__(self, root):
        self.root = root
        self.root.title("Check In")
        self.root.attributes("-fullscreen", True)  # Set to full-screen

        # Dictionary to track check-in data for multiple students
        self.check_in_data = {}

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Create a gradient background
        gradient_bg = create_gradient(screen_width, screen_height, '#1a2a6c', '#f72585')
        bg_label = tk.Label(root, image=gradient_bg)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = gradient_bg  # Keep a reference to avoid garbage collection

        # Glassmorphism effect frame (rounded semi-transparent panel)
        glass_frame = tk.Label(root, image=create_rounded_rectangle(400, 250, 30, (255, 255, 255), 128))
        glass_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title label
        title_label = tk.Label(root, text="Check In", font=("Helvetica", 20, "bold"), bg="white", fg="#333")
        title_label.place(relx=0.5, rely=0.25, anchor="center")

        # Entry for student ID on glass frame
        self.create_rounded_entry(0.5, 0.45)

        # Create rounded buttons using Canvas
        self.create_rounded_button("Check In", self.check_in, 0.45, 0.55, "#6a0dad")
        self.create_rounded_button("Check Out", self.check_out, 0.55, 0.55, "#d63384")

    def create_rounded_entry(self, relx, rely):
        entry_canvas = tk.Canvas(self.root, width=220, height=40, bg='white', highlightthickness=0)
        entry_canvas.place(relx=relx, rely=rely, anchor="center")

        # Draw a single rounded rectangle for the text entry box
        entry_canvas.create_oval(0, 0, 20, 40, fill='white', outline='black', width=2)  # Top left corner
        entry_canvas.create_oval(200, 0, 220, 40, fill='white', outline='black', width=2)  # Top right corner
        entry_canvas.create_rectangle(20, 0, 200, 40, fill='white', outline='black', width=2)  # Middle part

        # Entry widget for student ID
        self.id_entry = tk.Entry(
            self.root, font=("Helvetica", 14), bd=0, justify="center", highlightthickness=0
        )
        self.id_entry.place(relx=relx, rely=rely, anchor="center", width=200, height=30)

    def create_rounded_button(self, text, command, relx, rely, color):
        button_canvas = tk.Canvas(self.root, width=100, height=40, bg='white', highlightthickness=0)
        button_canvas.place(relx=relx, rely=rely, anchor="center")

        # Draw the rounded rectangle
        button_canvas.create_oval(0, 0, 40, 40, fill=color, outline=color)  # Top left corner
        button_canvas.create_oval(60, 0, 100, 40, fill=color, outline=color)  # Top right corner
        button_canvas.create_rectangle(20, 0, 80, 40, fill=color, outline=color)  # Middle part

        # Create button text
        button_canvas.create_text(50, 20, text=text, fill="white", font=("Helvetica", 12, "bold"))
        button_canvas.bind("<Button-1>", lambda event: command())  # Bind click event

    def check_in(self):
        # Retrieve the student ID
        student_id = self.id_entry.get()
        if not student_id:
            print("Please enter a Student ID.")
            return
    
        # Check if the student is already checked in
        if student_id in self.check_in_data:
            print(f"Student ID {student_id} is already checked in.")
            return

        # Record the check-in time
        self.check_in_data[student_id] = datetime.now()
        print(f"Checked in: {student_id} at {self.check_in_data[student_id]}")

        # Clear the text in the ID entry after check-in
        self.id_entry.delete(0, tk.END)  # Clear the text but keep the box visible

    def check_out(self):
        # Retrieve the student ID for check-out
        student_id = self.id_entry.get()
        if student_id not in self.check_in_data:
            print(f"No active check-in for Student ID {student_id}. Please check in first.")
            return

        # Record the check-out time and calculate time spent
        check_out_time = datetime.now()
        time_spent = check_out_time - self.check_in_data[student_id]
        print(f"Checked out: {student_id} at {check_out_time}")
        print(f"Time spent: {time_spent}")

        # Log to JSON file
        self.log_time_data(student_id, self.check_in_data[student_id], check_out_time, time_spent)
    
        # Remove the student from check-in data
        del self.check_in_data[student_id]

        # Clear the ID entry text after check-out
        self.id_entry.delete(0, tk.END)  # Clear the text but keep the box visible

    def log_time_data(self, student_id, check_in_time, check_out_time, time_spent):
        # Convert time spent to total hours
        total_hours = time_spent.total_seconds() / 3600.0 #noqa

        # Format data to be logged
        data = {
            "check_in": check_in_time.strftime("%Y-%m-%d %H:%M:%S"),
            "check_out": check_out_time.strftime("%Y-%m-%d %H:%M:%S"),
            "time_spent": str(time_spent),
            "date": check_in_time.strftime("%Y-%m-%d"),
        }

        # Define directory for logs
        log_directory = "Student Logs"
        os.makedirs(log_directory, exist_ok=True)  # Create directory if it doesn't exist

        # Create a filename based on the student ID
        individual_filename = os.path.join(log_directory, f"{student_id}.json")
        master_filename = os.path.join(log_directory, "master_log.json")

        # Initialize records for individual log
        individual_records = {
            "compiled_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "logs": [],
        }

        # Log individual record
        if os.path.exists(individual_filename):
            with open(individual_filename, 'r') as f:
                individual_records = json.load(f)

        individual_records['logs'].append(data)

        with open(individual_filename, 'w') as f:
            json.dump(individual_records, f, indent=4)

        # Log to master record
        master_records = {"logs": []}  # Initialize empty master log structure

        if os.path.exists(master_filename) and os.path.getsize(master_filename) > 0:  # Check for file existence and size
            with open(master_filename, 'r') as f:
                try:
                    master_records = json.load(f)
                except json.JSONDecodeError:
                    print("Master log is corrupted or empty. Initializing new log.")
                    master_records = {"logs": []}

        master_records['logs'].append(data)

        with open(master_filename, 'w') as f:
            json.dump(master_records, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = CheckInOut(root)
    root.mainloop()
