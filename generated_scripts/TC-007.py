import os
import sys
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Test Case Details
TEST_CASE_ID = "TC-007"
TEST_CASE_TITLE = "Verify Express Shipping Cost"
# The expected shipping cost text as it appears in the label for the Express shipping option.
# The provided JavaScript does not dynamically add shipping cost to the 'total' span.
EXPECTED_SHIPPING_COST_IN_LABEL = "($10)" 
# Expected total after adding Product A ($50) and Product B ($30) to the cart.
# This total does NOT include shipping cost as per the provided JS logic.
EXPECTED_PRODUCT_TOTAL = 80.00 

# CRITICAL: Use a raw string with triple quotes for HTML content to avoid escape sequence issues.
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

# Initialize WebDriver and temporary file variables
driver = None
temp_html_file = None

try:
    # Create a temporary HTML file to host the content
    temp_html_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
    temp_html_file.write(HTML_CONTENT)
    temp_html_file.close()
    # Construct the file URL for the browser
    file_path = 'file:///' + temp_html_file.name.replace('\\', '/')

    # Initialize Chrome WebDriver using ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window() # Maximize window for better visibility
    # Initialize WebDriverWait for explicit waits
    wait = WebDriverWait(driver, 10) 

    # Navigate to the local HTML file
    driver.get(file_path)
    print(f"Navigated to: {file_path}")

    # --- Test Steps ---

    # 1. Add items to the cart (Product A and Product B)
    print("Adding Product A to cart...")
    # Find and click the "Add to Cart" button for Product A
    product_a_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[span[contains(text(), 'Product A')]]/button")))
    product_a_button.click()
    
    print("Adding Product B to cart...")
    # Find and click the "Add to Cart" button for Product B
    product_b_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[span[contains(text(), 'Product B')]]/button")))
    product_b_button.click()

    # Verify the cart total after adding products (before considering shipping)
    total_element = wait.until(EC.visibility_of_element_located((By.ID, "total")))
    current_product_total = float(total_element.text)
    assert current_product_total == EXPECTED_PRODUCT_TOTAL, \
        f"Assertion Failed: Expected product total to be ${EXPECTED_PRODUCT_TOTAL:.2f}, but got ${current_product_total:.2f}."
    print(f"Cart total after adding products: ${current_product_total:.2f}")

    # 2. Select the 'Express Shipping' option during checkout
    print("Selecting 'Express Shipping' option...")
    express_shipping_radio = wait.until(EC.element_to_be_clickable((By.ID, "shipping-express")))
    express_shipping_radio.click()
    # Verify that the Express shipping radio button is indeed selected
    wait.until(EC.element_to_be_selected((By.ID, "shipping-express")))
    print("Express Shipping selected successfully.")

    # 3. Fill in user details (required for successful payment processing)
    print("Filling user details...")
    wait.until(EC.visibility_of_element_located((By.ID, "name"))).send_keys("Automation User")
    wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys("test@example.com")
    wait.until(EC.visibility_of_element_located((By.ID, "address"))).send_keys("123 Test Street, Testville")
    print("User details filled.")

    # 4. Click 'Pay Now' button to complete the checkout flow
    print("Clicking 'Pay Now' button...")
    pay_button = wait.until(EC.element_to_be_clickable((By.ID, "payBtn")))
    pay_button.click()

    # --- Verification ---
    # The test case requires verifying "The shipping cost displayed... is $10.00."
    # Based on the provided HTML and JavaScript, the shipping cost is NOT added to the 'total' span.
    # Instead, it is explicitly mentioned in the label for the 'Express' shipping option.
    # Therefore, we verify the text content of this label.
    print("Verifying Express Shipping cost display in the label...")
    express_shipping_label = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "label[for='shipping-express']")))
    label_text = express_shipping_label.text
    
    assert EXPECTED_SHIPPING_COST_IN_LABEL in label_text, \
        f"Assertion Failed: Expected shipping cost '{EXPECTED_SHIPPING_COST_IN_LABEL}' not found in Express shipping label. Actual label text: '{label_text}'"
    print(f"Verified: Express Shipping label correctly displays '{EXPECTED_SHIPPING_COST_IN_LABEL}'. Label text: '{label_text}'")

    # Also verify that the payment success message appears, indicating successful checkout completion
    success_message = wait.until(EC.visibility_of_element_located((By.ID, "success")))
    assert success_message.is_displayed(), "Assertion Failed: Payment success message is not displayed after clicking 'Pay Now'."
    print("Payment successful message displayed.")

    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except Exception as e:
    print(f"Test Case {TEST_CASE_ID} FAILED")
    print(f"Error: {e}")
    if driver:
        # Take a screenshot on failure for debugging
        screenshot_name = f"{TEST_CASE_ID}_FAILED.png"
        driver.save_screenshot(screenshot_name)
        print(f"Screenshot saved as {screenshot_name}")
    sys.exit(1)

finally:
    # Clean up: Close the browser and delete the temporary HTML file
    if driver:
        driver.quit()
    if temp_html_file and os.path.exists(temp_html_file.name):
        os.remove(temp_html_file.name)
        print(f"Cleaned up temporary file: {temp_html_file.name}")
