# 🚀 Supply Chain Risk Prediction System

[![Python](https://img.shields.io/badge/Python-3.10.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black.svg)](https://flask.palletsprojects.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Random_Forest-orange.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/Database-SQLite-blue.svg)](https://www.sqlite.org/)

A web application that predicts supply chain risk levels using the **Random Forest machine learning algorithm**. It allows administrators to enter supply chain data, upload CSV files, generate risk predictions, monitor insights through an interactive dashboard, view prediction history, and export reports.

## 📑 Table of Contents

- [Features](#-features)
- [Login Credentials](#-login-credentials)
- [Requirements](#-requirements)
- [Technologies Used](#️-technologies-used)
- [Project Structure](#-project-structure)
- [Installation](#️-installation)
- [Run the Application](#️-run-the-application)
- [Machine Learning](#-machine-learning)
- [Model Evaluation](#-model-evaluation)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)
- [License](#-license)

---

## ✨ Features

| Feature                   | Description                                                                       |
| ------------------------- | --------------------------------------------------------------------------------- |
| 🔐 Admin Login            | Login page for administrator access                                               |
| 🤖 Risk Prediction        | Predicts Low, Medium, and High supply chain risk levels                           |
| 📝 Manual Data Entry      | Enter supply chain information manually                                           |
| 📂 CSV Upload             | Upload supply chain data from CSV files                                           |
| 📊 Interactive Dashboard  | Visualize risk distribution and supply chain insights                             |
| 📜 Prediction History     | View stored prediction records                                                    |
| 🔍 Search and Filter      | Search records and filter by risk level                                           |
| 📥 Excel Export           | Export prediction records to Excel                                                |
| 🖼️ Dashboard Image Export | Save a dashboard snapshot as an image                                             |
| 💾 SQLite Storage         | Store prediction records in a local database                                      |
| 📈 Model Evaluation       | Generate classification reports, confusion matrices, and feature importance plots |

---

## 🔐 Login Credentials

| Username | Password   |
| -------- | ---------- |
| `admin`  | `admin123` |

---

## ✅ Requirements

| Requirement  | Version / Details            |
| ------------ | ---------------------------- |
| Python       | 3.10.11                      |
| pip          | Python package installer     |
| Web browser  | Modern browser               |
| Dependencies | Listed in `requirements.txt` |

Check your Python version:

```bash
python --version
```

---

## 🛠️ Technologies Used

### Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap, if used in the templates
- Chart.js
- html2canvas

### Backend

- Python
- Flask

### Machine Learning and Data Processing

- Scikit-learn
- Pandas
- NumPy
- Joblib

### Database

- SQLite

### Reporting and Visualization

- OpenPyXL
- Matplotlib
- Seaborn

---

## 📂 Project Structure

```text
Supply_Chain_Risk_Prediction_System/
│
├── app.py
├── config.py
├── requirements.txt
├── .python-version
├── .env
├── .gitignore
│
├── model/
│   ├── train_model.py
│   ├── risk_model.pkl
│   └── reports/
│
├── database/
│   ├── database.db
│   └── db_setup.py
│
├── data/
│   └── supply_chain_data.csv
│
├── uploads/
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│
└── utils/
    ├── excel_export.py
    └── predictor.py
```

- `app.py` — Flask application entry point.
- `model/train_model.py` — Trains the machine learning model.
- `model/risk_model.pkl` — Saved model used for predictions.
- `database/database.db` — SQLite database.
- `data/supply_chain_data.csv` — Training dataset.
- `templates/` — HTML templates.
- `static/` — CSS, JavaScript, and other static assets.
- `utils/` — Helper modules for prediction and report export.
- `uploads/` — Uploaded files, if file saving is enabled.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/CodeWithDeveeswar/Supply_Chain_Risk_Prediction_System.git
```

### 2. Navigate to the project directory

```bash
cd Supply_Chain_Risk_Prediction_System
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure environment variables

If your application loads the Flask secret key from `.env`, create a `.env` file in the project root:

```env
SECRET_KEY=replace_with_a_secure_random_secret
```

Generate a secure value with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Replace the example value with the generated secret and ensure your Flask application loads it correctly.

**Important:** Never commit `.env` or other files containing passwords or secrets to GitHub. Add them to `.gitignore`.

---

## ▶️ Run the Application

Run the following commands from the project root after activating the virtual environment.

### 1. Initialize the database

```bash
python database/db_setup.py
```

### 2. Train the machine learning model

```bash
python model/train_model.py
```

Ensure that the training dataset exists at the location configured in the training script.

### 3. Start the Flask server

```bash
python app.py
```

### 4. Open the application

Visit:

**http://127.0.0.1:5000**

Log in using the credentials configured in your application.

---

## 📊 Machine Learning

The system uses a Random Forest Classifier to predict supply chain risk categories.

| Detail             | Description                                                                                  |
| ------------------ | -------------------------------------------------------------------------------------------- |
| Algorithm          | Random Forest Classifier                                                                     |
| Input features     | Delay, traffic, weather, inventory, order value, and port delay                              |
| Prediction classes | Low, Medium, High                                                                            |
| ML library         | Scikit-learn                                                                                 |
| Model saving       | Joblib                                                                                       |
| Evaluation         | Accuracy, balanced accuracy, classification report, confusion matrix, and feature importance |

Predictions depend on the training dataset and the patterns learned by the model.

---

## 📈 Model Evaluation

One recorded evaluation run produced the following results:

| Metric            | Result |
| ----------------- | -----: |
| Accuracy          |  61.9% |
| Balanced Accuracy | 67.03% |

The training script also generates a classification report, confusion matrix, and feature importance visualization when configured to do so.

These metrics describe that particular evaluation run. Performance can vary with different datasets, train-test splits, and model configurations. The model should be validated with representative real-world data before being used for operational decisions.

---

## 🚀 Future Enhancements

- [ ] Multi-user authentication
- [ ] Role-based access control
- [ ] Mobile-responsive design
- [ ] Cloud database integration
- [ ] Live supply chain data integration
- [ ] REST API support
- [ ] Model optimization and performance improvement
- [ ] Email notifications for high-risk predictions
- [ ] Automated model retraining
- [ ] Advanced historical risk analytics

---

## 👨‍💻 Author

**DEVEESWAR K** ([CodeWithDeveeswar](https://github.com/CodeWithDeveeswar))

---

## 📄 License

This project is developed for **academic and educational purposes**.
