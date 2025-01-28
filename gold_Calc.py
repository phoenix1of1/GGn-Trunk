import tkinter as tk
from tkinter import ttk

def calculate_gold():
    gold_pool = float(gold_pool_entry.get())
    seeders = int(seeders_entry.get())

    # Calculate gold for new seeder (0 months)
    new_seeder_gold = gold_pool / seeders

    # Calculate gold for 5 months seeder
    if seeders == 1:
        max_percentage = 1.0
    elif seeders == 2:
        max_percentage = 0.85
    elif seeders == 3:
        max_percentage = 0.75
    elif seeders == 4:
        max_percentage = 0.60
    elif seeders == 5:
        max_percentage = 0.50
    else:
        max_percentage = 0.40

    five_months_gold = gold_pool * max_percentage

    # Calculate gold for different seeder groups
    gold_100_percent = (five_months_gold * 0.40) / seeders
    gold_75_percent = (five_months_gold * 0.40) / (seeders * 0.75)
    gold_50_percent = (five_months_gold * 0.40) / (seeders * 0.50)
    gold_25_percent = (five_months_gold * 0.40) / (seeders * 0.25)

    new_seeder_result.set(f"{new_seeder_gold:.2f} gold/hour")
    five_months_result.set(f"{five_months_gold:.2f} gold/hour")
    gold_100_percent_result.set(f"{gold_100_percent:.2f} gold/hour")
    gold_75_percent_result.set(f"{gold_75_percent:.2f} gold/hour")
    gold_50_percent_result.set(f"{gold_50_percent:.2f} gold/hour")
    gold_25_percent_result.set(f"{gold_25_percent:.2f} gold/hour")

# Create the main window
root = tk.Tk()
root.title("Gold Calculator")

# Create and place the input fields
ttk.Label(root, text="Gold Pool:").grid(column=0, row=0, padx=10, pady=5)
gold_pool_entry = ttk.Entry(root)
gold_pool_entry.grid(column=1, row=0, padx=10, pady=5)

ttk.Label(root, text="Number of Seeders:").grid(column=0, row=1, padx=10, pady=5)
seeders_entry = ttk.Entry(root)
seeders_entry.grid(column=1, row=1, padx=10, pady=5)

# Create and place the calculate button
calculate_button = ttk.Button(root, text="Calculate", command=calculate_gold)
calculate_button.grid(column=0, row=2, columnspan=2, pady=10)

# Create and place the result labels
new_seeder_result = tk.StringVar()
ttk.Label(root, text="Gold as New Seeder:").grid(column=0, row=3, padx=10, pady=5)
ttk.Label(root, textvariable=new_seeder_result).grid(column=1, row=3, padx=10, pady=5)

five_months_result = tk.StringVar()
ttk.Label(root, text="Gold as 5 Months Seeder:").grid(column=0, row=4, padx=10, pady=5)
ttk.Label(root, textvariable=five_months_result).grid(column=1, row=4, padx=10, pady=5)

gold_100_percent_result = tk.StringVar()
ttk.Label(root, text="Gold (100% of 5 months and over):").grid(column=0, row=5, padx=10, pady=5)
ttk.Label(root, textvariable=gold_100_percent_result).grid(column=1, row=5, padx=10, pady=5)

gold_75_percent_result = tk.StringVar()
ttk.Label(root, text="Gold (75% of 5 months and over):").grid(column=0, row=6, padx=10, pady=5)
ttk.Label(root, textvariable=gold_75_percent_result).grid(column=1, row=6, padx=10, pady=5)

gold_50_percent_result = tk.StringVar()
ttk.Label(root, text="Gold (50% of 5 months and over):").grid(column=0, row=7, padx=10, pady=5)
ttk.Label(root, textvariable=gold_50_percent_result).grid(column=1, row=7, padx=10, pady=5)

gold_25_percent_result = tk.StringVar()
ttk.Label(root, text="Gold (25% of 5 months and over):").grid(column=0, row=8, padx=10, pady=5)
ttk.Label(root, textvariable=gold_25_percent_result).grid(column=1, row=8, padx=10, pady=5)

# Run the application
root.mainloop()
