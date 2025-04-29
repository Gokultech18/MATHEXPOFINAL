from flask import Flask, request, jsonify, render_template_string
import sympy as sp

app = Flask(__name__)

# HTML served as string
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Double Integral Calculator</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet" />
  <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Poppins', sans-serif;
    }
    body {
      background: linear-gradient(270deg, #2c3e50, #4ca1af, #6a11cb, #2575fc);
      background-size: 800% 800%;
      animation: gradientShift 15s ease infinite;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }

    @keyframes gradientShift {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    .container {
      background: #fff;
      padding: 30px;
      border-radius: 15px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
      max-width: 650px;
      width: 100%;
      animation: fadeIn 1s ease-in-out;
    }
    h1 {
      text-align: center;
      margin-bottom: 25px;
      color: #333;
    }
    label {
      font-weight: 600;
      display: block;
      margin: 15px 0 5px;
      color: #333;
    }
    input[type="text"] {
      width: 100%;
      padding: 12px;
      margin-top: 5px;
      border: 2px solid #ddd;
      border-radius: 10px;
      transition: all 0.4s ease;
    }
    input[type="text"]:focus {
      border-color: #4CAF50;
      box-shadow: 0 0 8px #4CAF50;
      outline: none;
      transform: scale(1.02);
    }
    button {
      margin-top: 20px;
      width: 100%;
      padding: 15px;
      background: linear-gradient(90deg, #4CAF50, #45a049);
      border: none;
      color: #fff;
      font-size: 18px;
      font-weight: 600;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.3s ease;
    }
    button:hover {
      background: linear-gradient(90deg, #45a049, #4CAF50);
      transform: scale(1.05);
      box-shadow: 0 0 12px #4CAF50;
    }

    .result-box {
      background: linear-gradient(135deg, #e3ffe7, #d9e7ff);
      padding: 20px;
      margin-top: 30px;
      border-radius: 15px;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1), 0 0 25px rgba(80, 250, 123, 0.2);
      position: relative;
      overflow: hidden;
      transition: all 0.4s ease-in-out;
    }
    .result-box:hover {
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2), 0 0 40px rgba(80, 250, 123, 0.4);
    }

    .result-box::before {
      content: "";
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
      animation: shine 5s linear infinite;
      z-index: 0;
    }

    @keyframes shine {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .result-box h2 {
      margin-bottom: 15px;
      color: #2c3e50;
      z-index: 1;
      position: relative;
    }

    .latex-container, pre {
      background-color: rgba(255, 255, 255, 0.95);
      padding: 15px;
      border-radius: 10px;
      font-size: 16px;
      white-space: pre-wrap;
      word-wrap: break-word;
      box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.05);
      transition: all 0.3s;
      z-index: 1;
      position: relative;
    }

    .latex-container:hover, pre:hover {
      background-color: #eef9f1;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>💖Double Integral Calculator💖</h1>
    <form id="integralForm">
      <label for="function">Function (example: x*2 + y*2 or sin,cos,log):</label>
      <input type="text" id="function" placeholder="Enter function..." required />
      <label for="lower_limit_x">Lower Limit (outer variable x):</label>
      <input type="text" id="lower_limit_x" value="0" />
      <label for="upper_limit_x">Upper Limit (outer variable x):</label>
      <input type="text" id="upper_limit_x" value="1" />
      <label for="lower_limit_y">Lower Limit (inner variable y):</label>
      <input type="text" id="lower_limit_y" value="0" />
      <label for="upper_limit_y">Upper Limit (inner variable y):</label>
      <input type="text" id="upper_limit_y" value="1" />
      <button type="submit">Calculate ❤😊</button>
    </form>

    <div class="result-box">
      <h2>✨ Integral Expression:</h2>
      <div id="latex-output" class="latex-container"></div>
    </div>

    <div class="result-box">
      <h2>🎉 Numerical Result:</h2>
      <pre id="result"></pre>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
  <script>
    document.getElementById('integralForm').onsubmit = async function (event) {
      event.preventDefault();
      const functionText = document.getElementById('function').value;
      const lower_limit_x = document.getElementById('lower_limit_x').value;
      const upper_limit_x = document.getElementById('upper_limit_x').value;
      const lower_limit_y = document.getElementById('lower_limit_y').value;
      const upper_limit_y = document.getElementById('upper_limit_y').value;

      const response = await fetch('/double_integral', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          function: functionText,
          lower_limit_x,
          upper_limit_x,
          lower_limit_y,
          upper_limit_y
        })
      });

      const result = await response.json();
      document.getElementById('result').innerText = result.result || result.error;
      if (result.latex) {
        document.getElementById('latex-output').innerHTML = `\\[ ${result.latex} \\]`;
        MathJax.typeset();
      }
      if (result.result) {
        confetti({
          particleCount: 150,
          spread: 70,
          origin: { y: 0.6 }
        });
      }
    };
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/double_integral', methods=['POST'])
def double_integral():
    data = request.get_json()
    function_expr = data.get('function')
    lower_limit_x = data.get('lower_limit_x', 0)
    upper_limit_x = data.get('upper_limit_x', 1)
    lower_limit_y = data.get('lower_limit_y', 0)
    upper_limit_y = data.get('upper_limit_y', 1)

    if not function_expr:
        return jsonify({"error": "Function is required"}), 400

    try:
        lower_limit_x = int(float(lower_limit_x))
        upper_limit_x = int(float(upper_limit_x))
        lower_limit_y = int(float(lower_limit_y))
        upper_limit_y = int(float(upper_limit_y))

        f = sp.sympify(function_expr)
        variables = sorted(list(f.free_symbols), key=lambda x: str(x))
        if len(variables) != 2:
            return jsonify({"error": "Function must have exactly 2 variables."}), 400

        var1, var2 = variables
        integral_result = sp.integrate(f, (var2, lower_limit_y, upper_limit_y), (var1, lower_limit_x, upper_limit_x))
        evaluated_result = int(integral_result.evalf())

        latex_expr = r"\int_{{{}}}^{{{}}} \int_{{{}}}^{{{}}} {} \, d{} \, d{}".format(
            lower_limit_x, upper_limit_x,
            lower_limit_y, upper_limit_y,
            sp.latex(f),
            sp.latex(var2),
            sp.latex(var1)
        )

        return jsonify({
            "result": str(evaluated_result),
            "latex": latex_expr
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
