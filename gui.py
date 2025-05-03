# gui.py

import tkinter as tk  # Importing Tkinter for GUI components
from tkinter import ttk, messagebox, scrolledtext  # Additional Tkinter modules for treeview, message boxes, and scrollable text
import threading  # For running the scraper in a separate thread to keep the GUI responsive
import time  # For time-related functions (delays)
import random  # To add random delays between scraping actions
import pandas as pd  # For handling and saving scraped data in CSV format
from scraper import scrape_yellowpages  # Import the scrape_yellowpages function from Scraper.py

class YellowPagesScraperApp:
    def __init__(self, root):
        self.root = root  # The main Tkinter window
        self.root.title("YellowPages Scraper")  # Setting the title of the window
        self.root.geometry("900x500")  # Setting the size of the window
        self.root.configure(bg="#f4f4f4")  # Setting a background color for the window

        # Title Label
        tk.Label(root, text="YellowPages Scraper", font=("Arial", 16, "bold"), bg="#f4f4f4").pack(pady=10)

        # Label and Entry field for the business search term (e.g., "plumber")
        tk.Label(root, text="Enter Business Type or Keyword:", bg="#f4f4f4").pack()
        self.entry_search_term = tk.Entry(root, width=50)  # Entry field for the business search term
        self.entry_search_term.pack(pady=5)

        # Label and Entry field for the location (e.g., "New York")
        tk.Label(root, text="Enter Location:", bg="#f4f4f4").pack()
        self.entry_location = tk.Entry(root, width=50)  # Entry field for the location
        self.entry_location.pack(pady=5)

        # Start Button to begin the scraping process
        self.start_button = tk.Button(root, text="Start Scraping", command=self.start_scraping, bg="#4CAF50", fg="white", width=20)
        self.start_button.pack(pady=10)

        # Stop Button to stop the scraping process
        self.stop_button = tk.Button(root, text="Stop Scraping", command=self.stop_scraping, bg="#E74C3C", fg="white", width=20)
        self.stop_button.pack(pady=5)
        self.stop_button.config(state=tk.DISABLED)  # Initially, the stop button is disabled

        # Label for the status log
        tk.Label(root, text="Scraping Status:", bg="#f4f4f4").pack()

        # ScrolledText widget for displaying status messages (logs)
        self.status_text = scrolledtext.ScrolledText(root, width=80, height=4, wrap=tk.WORD)  # This widget allows scrolling
        self.status_text.pack(pady=5)

        # Label for the data table
        tk.Label(root, text="Collected Data:", bg="#f4f4f4").pack()

        # Define the columns for the Treeview (data table)
        columns = ("No.", "Business Name", "Address", "Phone", "Website")
        self.data_table = ttk.Treeview(root, columns=columns, show="headings")  # Create a Treeview widget to display the data

        # Set the headings for the columns and adjust their width
        for col in columns:
            self.data_table.heading(col, text=col, anchor="center")  # Align headers to the center
            self.data_table.column(col, width=100 if col == "No." else 200, anchor="center")  # Set column width

        self.data_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # Add the table to the GUI

        # Initialize threading variables
        self.scraping_thread = None  # Variable to hold the scraping thread
        self.is_scraping = False  # Flag to track whether scraping is ongoing

    def log_status(self, message):
        """Adds a message to the status log (scrollable text area)."""
        self.status_text.insert(tk.END, message + "\n")  # Append message to the log
        self.status_text.yview(tk.END)  # Automatically scroll to the bottom

    def start_scraping(self):
        """Starts the scraping process when the 'Start Scraping' button is clicked."""
        # Retrieve and clean the input fields (search term and location)
        search_term = self.entry_search_term.get().strip()
        location = self.entry_location.get().strip()

        # Check if both fields are filled
        if not search_term or not location:
            messagebox.showerror("Error", "Please enter both search term and location.")  # Show error if any field is empty
            return

        # Disable the start button and enable the stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_scraping = True  # Set the scraping flag to True
        self.log_status("🔍 Starting scraping...")  # Log the start of scraping

        # Clear previous data in the data table before starting fresh
        for row in self.data_table.get_children():
            self.data_table.delete(row)

        # Start the scraping process in a separate thread to keep the GUI responsive
        self.scraping_thread = threading.Thread(target=self.scrape_yellowpages, args=(search_term, location))
        self.scraping_thread.start()

    def stop_scraping(self):
        """Stops the scraping process when the 'Stop Scraping' button is clicked."""
        self.is_scraping = False  # Set the scraping flag to False
        self.start_button.config(state=tk.NORMAL)  # Enable the start button
        self.stop_button.config(state=tk.DISABLED)  # Disable the stop button
        self.log_status("🛑 Scraping stopped by user.")  # Log the stop message

    def scrape_yellowpages(self, search_term, location):
        """Scrapes YellowPages data based on the search term and location."""
        try:
            self.log_status("🔍 Scraping in progress...")

            # Call the updated scraper function that returns the filename
            filename = scrape_yellowpages(search_term, location)

            # Load the data from the returned CSV file and show it in Treeview
            df = pd.read_csv(filename)
            for i, row in df.iterrows():
                self.data_table.insert("", "end", values=(
                    i + 1, row["Business Name"], row["Address"], row["Phone"], row["Website"]
                ))

            self.log_status(f"✅ Scraping complete. Data saved to {filename}")

        except Exception as e:
            self.log_status(f"❌ Scraping error: {e}")

        finally:
            # Reset scraping flag and buttons after scraping is finished or stopped
            self.is_scraping = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_status("✅ Scraping finished.")

# Set up the main Tkinter window
root = tk.Tk()  # Create the Tkinter window
app = YellowPagesScraperApp(root)  # Create the application instance
root.mainloop()  # Start the Tkinter main loop
