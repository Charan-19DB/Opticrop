# 🌾 OptiCrop – Smart Agricultural Production Optimization Engine

OptiCrop is an AI-powered agricultural recommendation system that predicts the most suitable crop to plant based on soil nutrients and environmental conditions. 

By utilizing a highly tuned Machine Learning algorithm (Random Forest, 99.5% accuracy), OptiCrop helps farmers maximize their yield, minimize fertilizer waste, and make data-driven, sustainable decisions.

---

## 🚀 Features
- **Real-Time Predictions:** Input soil and weather metrics to get instant crop recommendations.
- **Interactive Dashboard:** Beautiful Chart.js visualizations explaining dataset statistics.
- **Export to PDF:** Instantly download a professional PDF report of your crop recommendation.
- **Prediction History:** All queries are securely logged into a CSV database.
- **Dark Mode:** Seamless UI theme toggling utilizing LocalStorage.
- **Fully Responsive UI:** Built with Bootstrap 5, optimized for mobile and desktop.

## 🛠️ Tech Stack
- **Backend:** Python 3, Flask, Jinja2
- **Machine Learning:** Scikit-Learn, Pandas, NumPy
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
- **Utilities:** fpdf2 (PDF Generation), Pickle (Model Serialization)

---

## 📁 Directory Structure
```text
OptiCrop/
│
├── dataset/
│   ├── Crop_recommendation.csv     # Raw Kaggle dataset
│   └── prediction_history.csv      # Logged user queries
│
├── model/
│   ├── crop_model.pkl              # Pickled Random Forest classifier
│   ├── encoder.pkl                 # Pickled LabelEncoder
│   └── scaler.pkl                  # Pickled StandardScaler
│
├── notebooks/
│   └── EDA.ipynb                   # Jupyter notebook containing Exploratory Data Analysis
│
├── static/
│   ├── css/style.css               # Custom CSS styles (gradients, animations, dark mode)
│   └── js/main.js                  # Frontend Javascript logic
│
├── templates/
│   ├── base.html                   # Master layout with Navbar and Footer
│   ├── index.html                  # Home page
│   ├── predict.html                # Prediction form
│   ├── result.html                 # Prediction results & PDF trigger
│   ├── dashboard.html              # Chart.js visualization dashboard
│   ├── history.html                # Prediction logs table
│   └── 404.html                    # Error handling page
│
├── tests/
│   ├── test_app.py                 # Flask integration tests
│   └── test_predict.py             # ML pipeline unit tests
│
├── utils/
│   ├── predict.py                  # Functions to handle scaling, predicting, and returning values
│   └── preprocess.py               # ML training preprocessing pipeline
│
├── app.py                          # Main Flask server entrypoint
├── train_model.py                  # Script to train 7 ML algorithms and save the best one
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

---

## ⚙️ Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/OptiCrop.git
   cd OptiCrop
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   
   # Activate on Windows:
   .\.venv\Scripts\activate
   # Activate on macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Machine Learning Pipeline (Optional):**
   *Note: Pre-trained models are already provided in the `/model` directory. If you wish to retrain them, run:*
   ```bash
   python train_model.py
   ```

---

## 💻 Usage Guide

1. **Start the Flask Server:**
   ```bash
   python app.py
   ```
2. **Access the Web App:**
   Open your browser and navigate to `http://127.0.0.1:5000`
3. **Make a Prediction:**
   Click on the "Recommendation" tab, fill out the environmental metrics, and hit submit to view your AI-generated crop recommendation!
4. **Run Automated Tests:**
   ```bash
   python -m pytest tests/ -v
   ```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
