import tkinter as tk
from model_training import predict_cwa   # THIS connects GUI to ML

def send_to_ml():
    current_cwa = float(current_cwa_entry.get())
    credit_load = int(credit_load_entry.get())
    study_hours = float(study_hours_entry.get())

    result = predict_cwa(current_cwa, credit_load, study_hours)

    result_label.config(text=f"Predicted CWA: {result}")

root = tk.Tk()
root.title("CWA Predictor")
root.geometry("400x300")

tk.Label(root, text="Current CWA").pack()
current_cwa_entry = tk.Entry(root)
current_cwa_entry.pack()

tk.Label(root, text="Credit Load").pack()
credit_load_entry = tk.Entry(root)
credit_load_entry.pack()

tk.Label(root, text="Study Hours per Week").pack()
study_hours_entry = tk.Entry(root)
study_hours_entry.pack()

tk.Button(root, text="Predict", command=send_to_ml).pack(pady=10)

result_label = tk.Label(root, text="")
result_label.pack()

root.mainloop()
