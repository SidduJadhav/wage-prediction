"""
HTML Templates for Frontend
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Labour Wage Prediction</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 { color: #667eea; margin-bottom: 10px; }
        p { color: #666; margin-bottom: 30px; }
        .sector-buttons {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        button {
            padding: 12px 25px;
            border: 2px solid #ddd;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        button:hover { border-color: #667eea; }
        button.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
        }
        input, select {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .submit-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }
        .submit-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }
        .result {
            margin-top: 30px;
            padding: 25px;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            border-radius: 10px;
            color: white;
            text-align: center;
        }
        .wage { font-size: 2.5em; font-weight: bold; margin: 15px 0; }
        .error {
            background: #ffebee;
            border: 1px solid #ef5350;
            border-radius: 8px;
            padding: 15px;
            color: #c62828;
            margin-top: 20px;
        }
        .loading { text-align: center; padding: 20px; }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>💼 Labour Wage Prediction System</h1>
        <p>Quick Test Frontend - Select a sector and fill in the details</p>
        
        <div class="sector-buttons">
            <button class="active" onclick="setSector('agriculture')">🌾 Agriculture</button>
            <button onclick="setSector('construction')">🏗️ Construction</button>
        </div>

        <form onsubmit="predict(event)">
            <div class="form-grid" id="formFields"></div>
            <button type="submit" class="submit-btn">🎯 Calculate Fair Wage</button>
        </form>

        <div id="result"></div>
    </div>

    <script>
        let currentSector = 'agriculture';
        let config = {};

        async function loadConfig() {
            try {
                const response = await fetch('/api/config');
                config = await response.json();
                renderForm();
            } catch (error) {
                document.getElementById('result').innerHTML = '<div class="error">Error loading config: ' + error.message + '</div>';
            }
        }

        function setSector(sector) {
            currentSector = sector;
            document.querySelectorAll('button').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            renderForm();
            document.getElementById('result').innerHTML = '';
        }

        function renderForm() {
            const sectorConfig = config[currentSector];
            if (!sectorConfig) return;

            const validValues = sectorConfig.valid_values || {};
            let html = '';

            Object.entries(validValues).forEach(([field, options]) => {
                html += `
                    <div>
                        <label>${field.replace(/_/g, ' ').toUpperCase()}</label>
                        <select name="${field}" required>
                            <option value="">Select ${field}</option>
                            ${options.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                        </select>
                    </div>
                `;
            });

            html += `
                <div>
                    <label>AGE</label>
                    <input type="number" name="age" min="18" max="70" value="35" required>
                </div>
                <div>
                    <label>EXPERIENCE (YEARS)</label>
                    <input type="number" name="experience_years" min="0" max="50" value="10" required>
                </div>
                <div>
                    <label>SKILL LEVEL</label>
                    <input type="number" name="skill_level" min="1" max="4" value="2" required>
                </div>
                <div>
                    <label>WORKING HOURS</label>
                    <input type="number" name="working_hours" min="6" max="10" value="8" required>
                </div>
            `;

            document.getElementById('formFields').innerHTML = html;
        }

        async function predict(e) {
            e.preventDefault();

            const form = document.querySelector('form');
            const data = new FormData(form);
            const payload = { sector: currentSector, data: {} };

            data.forEach((value, key) => {
                if (['age', 'experience_years', 'skill_level', 'working_hours'].includes(key)) {
                    payload.data[key] = parseInt(value);
                } else {
                    payload.data[key] = value;
                }
            });

            document.getElementById('result').innerHTML = '<div class="loading"><div class="spinner"></div><p>Calculating...</p></div>';

            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();

                if (result.success) {
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                            <h2>📊 Predicted Fair Wage</h2>
                            <div class="wage">₹${result.predicted_wage.toLocaleString()}</div>
                            <p>Per Day</p>
                            <p style="margin-top: 15px;">
                                <strong>Monthly (26 days):</strong> ₹${result.monthly_estimate.toLocaleString()}<br>
                                <strong>Annual (312 days):</strong> ₹${result.annual_estimate.toLocaleString()}
                            </p>
                        </div>
                    `;
                } else {
                    document.getElementById('result').innerHTML = '<div class="error"><strong>Error:</strong> ' + result.error + '</div>';
                }
            } catch (error) {
                document.getElementById('result').innerHTML = '<div class="error"><strong>Error:</strong> ' + error.message + '</div>';
            }
        }

        loadConfig();
    </script>
</body>
</html>
"""