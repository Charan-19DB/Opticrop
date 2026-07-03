from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from utils.predict import return_prediction
import csv
import os
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "super_secret_opticrop_key" 

HISTORY_FILE = 'dataset/prediction_history.csv'

# Initialize CSV file if it doesn't exist
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['N', 'P', 'K', 'Temperature', 'Humidity', 'pH', 'Rainfall', 'Predicted Crop'])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            N = float(request.form['N'])
            P = float(request.form['P'])
            K = float(request.form['K'])
            temp = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            ph = float(request.form['ph'])
            rainfall = float(request.form['rainfall'])

            result = return_prediction(N, P, K, temp, humidity, ph, rainfall)
            
            if result['success']:
                predicted_crop = result['prediction']
                
                # Save to History
                with open(HISTORY_FILE, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([N, P, K, temp, humidity, ph, rainfall, predicted_crop])
                
                return render_template('result.html', prediction=predicted_crop)
            else:
                flash(f"Prediction Error: {result.get('error')}", "danger")
                return redirect(url_for('predict'))

        except ValueError:
            flash("Invalid input. Please ensure all fields contain numerical values.", "danger")
            return redirect(url_for('predict'))
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", "danger")
            return redirect(url_for('predict'))

    return render_template('predict.html')

@app.route('/history')
def history():
    records = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, mode='r') as f:
            reader = csv.reader(f)
            records = list(reader)[1:] # skip header
    return render_template('history.html', records=records)

@app.route('/download_csv')
def download_csv():
    return send_file(HISTORY_FILE, as_attachment=True)

@app.route('/download_pdf/<crop>')
def download_pdf(crop):
    from fpdf import FPDF
    import datetime
    
    class PDF(FPDF):
        def header(self):
            # Header Background (Dark Green)
            self.set_fill_color(46, 125, 50)
            self.rect(0, 0, 210, 40, 'F')
            # Header Text
            self.set_font('Helvetica', 'B', 24)
            self.set_text_color(255, 255, 255)
            self.set_y(15)
            self.cell(0, 10, text='OptiCrop AI Report', new_x="LMARGIN", new_y="NEXT", align='C')
            self.ln(20)
            
        def footer(self):
            # Footer timestamp
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(128, 128, 128)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cell(0, 10, text=f'Generated on {timestamp} | OptiCrop ML Engine', new_x="LMARGIN", new_y="NEXT", align='C')

    pdf = PDF()
    pdf.add_page()
    
    # Recommendation Box
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 15, text="Optimal Crop Recommendation", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)
    
    # Draw a colored box for the crop
    pdf.set_fill_color(232, 245, 233) # Light Green
    pdf.set_draw_color(76, 175, 80) # Outline Green
    pdf.set_line_width(1)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 30, text=crop.upper(), border=1, new_x="LMARGIN", new_y="NEXT", align='C', fill=True)
    pdf.ln(15)
    
    # Details text
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    
    summary = (
        f"Congratulations! Based on the soil composition and environmental metrics provided, "
        f"the OptiCrop Machine Learning engine (Random Forest Classifier) has identified "
        f"'{crop.capitalize()}' as the absolute optimal crop to cultivate for maximum yield and sustainability."
    )
    pdf.multi_cell(0, 8, text=summary, align='C')
    
    pdf.ln(15)
    
    # Important note
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 6, text="Note: This recommendation is generated via an AI predictive model with 99.5% accuracy on historical data. Environmental factors can change, so always monitor local weather updates.", align='C')
    
    # Save temporarily to static
    pdf_path = f"static/report_{crop}.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True)

@app.route('/dashboard')
def dashboard():
    import pandas as pd
    df = pd.read_csv('dataset/Crop_recommendation.csv')
    
    # 1. Crop Frequency
    crop_counts = df['label'].value_counts().to_dict()
    
    # 2. Averages per crop (N, P, K, Temp, Hum, Rain)
    # Exclude categorical columns for mean calculation
    numeric_df = df.drop(columns=['label'])
    numeric_df['label'] = df['label']
    grouped = numeric_df.groupby('label').mean().to_dict('index')
    
    return render_template('dashboard.html', crop_counts=crop_counts, grouped=grouped)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
