import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Test Case Details ---
TEST_CASE_ID = "TC-003"
TEST_CASE_TITLE = "Verify Form Validation Error Display Color"
# Expected color for red in RGB format. Selenium often returns rgba(255, 0, 0, 1) for 'red'.
EXPECTED_COLOR_RGB = "rgb(255, 0, 0)"
EXPECTED_COLOR_RGBA = "rgba(255, 0, 0, 1)"

# --- Create a temporary HTML file ---
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Shop Checkout</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
        }
        .item {
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            padding: 8px 16px;
            margin: 5px;
            cursor: pointer;
        }
        #payBtn {
            background-color: green;
            color: white;
            padding: 12px 24px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
        }
        .error {
            color: red;
            font-size: 12px;
        }
        #success {
            display: none;
            color: green;
            font-weight: bold;
            margin-top: 10px;
        }
        input[type="text"], input[type="email"], textarea {
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            box-sizing: border-box;
        }
        h3 {
            margin-top: 20px;
            color: #333;
        }
    </style>
</head>
<body>
    <h1>E-Shop Checkout</h1>

    <h3>Products</h3>
    <div class="item">
        <span>Product A - $50</span>
        <button onclick="addToCart('Product A', 50)">Add to Cart</button>
    </div>
    <div class="item">
        <span>Product B - $30</span>
        <button onclick="addToCart('Product B', 30)">Add to Cart</button>
    </div>
    <div class="item">
        <span>Product C - $20</span>
        <button onclick="addToCart('Product C', 20)">Add to Cart</button>
    </div>

    <h3>Cart Summary</h3>
    <div id="cart"></div>
    <p>Total: $<span id="total">0</span></p>

    <h3>Discount Code</h3>
    <input type="text" id="discountCode" placeholder="Enter discount code">
    <button onclick="applyDiscount()">Apply</button>
    <span id="discountMessage"></span>

    <h3>User Details</h3>
    <input type="text" id="name" placeholder="Full Name" required><br><br>
    <input type="email" id="email" placeholder="Email" required><br>
    <span id="emailError" class="error"></span><br>
    <textarea id="address" placeholder="Address" required></textarea><br>
    <span id="nameError" class="error"></span>
    <span id="addressError" class="error"></span>

    <h3>Shipping Method</h3>
    <input type="radio" name="shipping" id="shipping-standard" value="standard" checked> 
    <label for="shipping-standard">Standard (Free)</label><br>
    <input type="radio" name="shipping" id="shipping-express" value="express"> 
    <label for="shipping-express">Express ($10)</label>

    <h3>Payment Method</h3>
    <input type="radio" name="payment" id="payment-card" value="card" checked> 
    <label for="payment-card">Credit Card</label><br>
    <input type="radio" name="payment" id="payment-paypal" value="paypal"> 
    <label for="payment-paypal">PayPal</label>

    <br><br>
    <button id="payBtn" onclick="processPayment()">Pay Now</button>
    <p id="success">Payment Successful!</p>

    <script>
        let total = 0;
        let discountApplied = false;

        function addToCart(name, price) {
            const cart = document.getElementById('cart');
            cart.innerHTML += `<p>${name} - $${price}</p>`;
            total += price;
            document.getElementById('total').innerText = total.toFixed(2);
        }

        function applyDiscount() {
            const code = document.getElementById('discountCode').value;
            const messageEl = document.getElementById('discountMessage');
            
            if (discountApplied) {
                messageEl.textContent = 'Discount already applied';
                messageEl.style.color = 'red';
                return;
            }
            
            if (code === 'SAVE15') {
                total = total - (total * 0.15);
                document.getElementById('total').innerText = total.toFixed(2);
                messageEl.textContent = 'Discount applied!';
                messageEl.style.color = 'green';
                discountApplied = true;
            } else {
                messageEl.textContent = 'Invalid discount code';
                messageEl.style.color = 'red';
            }
        }

        function validateEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        }

        function processPayment() {
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const address = document.getElementById('address').value.trim();
            
            // Clear previous errors
            document.getElementById('emailError').textContent = '';
            document.getElementById('nameError').textContent = '';
            document.getElementById('addressError').textContent = '';
            
            let isValid = true;
            
            // Validate name
            if (!name) {
                document.getElementById('nameError').textContent = 'Name is required';
                isValid = false;
            }
            
            // Validate email
            if (!email) {
                document.getElementById('emailError').textContent = 'Email is required';
                isValid = false;
            } else if (!validateEmail(email)) {
                document.getElementById('emailError').textContent = 'Invalid email format';
                isValid = false;
            }
            
            // Validate address
            if (!address) {
                document.getElementById('addressError').textContent = 'Address is required';
                isValid = false;
            }
            
            if (isValid) {
                document.getElementById('success').style.display = 'block';
            } else {
                document.getElementById('success').style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

# Define the path for the temporary HTML file
HTML_FILE_NAME = "checkout_form_validation.html"
HTML_FILE_PATH = os.path.abspath(HTML_FILE_NAME)

# Write the HTML content to the file
with open(HTML_FILE_PATH, "w") as f:
    f.write(html_content)

driver = None # Initialize driver to None for proper cleanup in finally block
try:
    # Initialize Chrome WebDriver using ChromeDriverManager
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window() # Maximize window for better visibility

    # Open the local HTML file
    driver.get(f"file://{HTML_FILE_PATH}")
    print(f"Navigated to: {driver.current_url}")

    # --- Test Steps ---

    # 1. Trigger a form validation error by clicking 'Pay Now' without filling required fields.
    # This will cause validation errors for 'name', 'email', and 'address' fields.
    pay_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "payBtn"))
    )
    pay_button.click()
    print("Clicked 'Pay Now' button to trigger form validation.")

    # 2. Wait for the email error message element to be visible and contain text.
    # We choose 'emailError' as a representative validation error to check its color.
    email_error_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "emailError"))
    )
    
    # Assert that the error message is displayed and not empty
    assert email_error_element.is_displayed(), "Email error message is not displayed."
    assert email_error_element.text.strip() != "", "Email error message is empty."
    print(f"Email error message displayed: '{email_error_element.text}'")

    # 3. Get the computed color style of the error message element.
    actual_color = email_error_element.value_of_css_property("color")
    print(f"Actual color of email error message: {actual_color}")

    # 4. Verify that the displayed form validation error message is in red text.
    # Selenium returns color in rgba() or rgb() format. We compare it to the expected red.
    if actual_color == EXPECTED_COLOR_RGB or actual_color == EXPECTED_COLOR_RGBA:
        print(f"Assertion Passed: Error message color is '{actual_color}', which is red.")
    else:
        raise AssertionError(
            f"Assertion Failed: Expected error message color to be red ({EXPECTED_COLOR_RGB} or {EXPECTED_COLOR_RGBA}), "
            f"but got '{actual_color}'."
        )

    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except Exception as e:
    print(f"Test Case {TEST_CASE_ID} FAILED")
    print(f"Error: {e}")
    if driver:
        # Take a screenshot on failure for debugging
        screenshot_path = f"{TEST_CASE_ID}_FAILURE.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    sys.exit(1)

finally:
    # Close the browser if it was opened
    if driver:
        driver.quit()
    # Clean up the temporary HTML file
    if os.path.exists(HTML_FILE_PATH):
        os.remove(HTML_FILE_PATH)
        print(f"Cleaned up temporary file: {HTML_FILE_PATH}")
