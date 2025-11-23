import sys
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# Test Case ID
TEST_CASE_ID = "TC-010"

# Target HTML content
HTML_CONTENT = r'''<!DOCTYPE html>
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
</html>'''

driver = None
temp_html_file = None

try:
    # Create a temporary HTML file
    fd, path = tempfile.mkstemp(suffix=".html")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(HTML_CONTENT)
    temp_html_file = path

    # Initialize Chrome WebDriver
    # Use ChromeDriverManager to automatically download and manage the ChromeDriver executable
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # Navigate to the local HTML file
    driver.get(f"file:///{temp_html_file}")

    # --- Test Steps for TC-010: Successful Payment Message Visibility ---

    # 1. Add a product to the cart to enable checkout
    print("Adding 'Product A' to cart...")
    add_to_cart_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='item'][1]/button"))
    )
    add_to_cart_btn.click()
    print("Product A added.")

    # 2. Fill in user details (Name, Email, Address)
    print("Filling user details...")
    name_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "name"))
    )
    name_input.send_keys("John Doe")

    email_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    email_input.send_keys("john.doe@example.com")

    address_textarea = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "address"))
    )
    address_textarea.send_keys("123 Main St, Anytown, USA")
    print("User details filled.")

    # 3. Click the "Pay Now" button
    print("Clicking 'Pay Now' button...")
    pay_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "payBtn"))
    )
    pay_button.click()
    print("'Pay Now' button clicked.")

    # 4. Verify that the success message is displayed
    print("Verifying payment success message visibility...")
    success_message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "success"))
    )

    # Assert the text content of the success message
    expected_message = "Payment Successful!"
    actual_message = success_message.text
    assert actual_message == expected_message, \
        f"Expected success message '{expected_message}' but got '{actual_message}'"

    print(f"Success message found: '{actual_message}'")
    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except Exception as e:
    print(f"Test Case {TEST_CASE_ID} FAILED")
    print(f"An error occurred: {e}")
    if driver:
        # Take a screenshot on failure
        screenshot_name = f"{TEST_CASE_ID}_FAILED_screenshot.png"
        driver.save_screenshot(screenshot_name)
        print(f"Screenshot saved as {screenshot_name}")
    sys.exit(1)

finally:
    # Close the browser
    if driver:
        driver.quit()
    # Clean up the temporary HTML file
    if temp_html_file and os.path.exists(temp_html_file):
        os.remove(temp_html_file)
        print(f"Cleaned up temporary file: {temp_html_file}")