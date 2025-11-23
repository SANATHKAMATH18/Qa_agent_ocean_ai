import sys
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Test Case ID
TEST_CASE_ID = "TC-007"

# Target HTML content provided in the problem description
TARGET_HTML_CONTENT = """
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

driver = None
html_file_path = None
try:
    # Create a temporary HTML file to serve the content
    fd, html_file_path = tempfile.mkstemp(suffix=".html")
    with os.fdopen(fd, 'w') as f:
        f.write(TARGET_HTML_CONTENT)
    
    # Initialize Chrome WebDriver using ChromeDriverManager
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    
    # Navigate to the local HTML file
    driver.get(f"file:///{html_file_path}")

    print(f"Starting Test Case {TEST_CASE_ID}: Attempt to Apply Discount Code SAVE15 Multiple Times")

    # 1. Add a product to the cart to ensure there's a total to discount
    print("Step 1: Adding 'Product A' to the cart.")
    add_to_cart_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='item'][1]/button"))
    )
    add_to_cart_btn.click()
    
    # Wait for the total to update to $50.00
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "total"), "50.00")
    )
    initial_product_total = float(driver.find_element(By.ID, "total").text)
    print(f"Current cart total: ${initial_product_total:.2f}")
    assert initial_product_total == 50.00, "Failed to add product to cart or total is incorrect."

    # 2. Apply the discount code 'SAVE15' for the first time
    print("Step 2: Applying discount code 'SAVE15' for the first time.")
    discount_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "discountCode"))
    )
    discount_input.send_keys("SAVE15")

    apply_discount_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='discountCode']/following-sibling::button[1]"))
    )
    apply_discount_btn.click()

    # Verify the discount message indicates success
    discount_message_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "discountMessage"))
    )
    expected_first_message = "Discount applied!"
    assert expected_first_message in discount_message_element.text, \
        f"Expected message '{expected_first_message}' after first application, but got '{discount_message_element.text}'"
    
    # Verify the total has been updated (50 - 15% of 50 = 42.50)
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "total"), "42.50")
    )
    first_applied_total = float(driver.find_element(By.ID, "total").text)
    print(f"Total after first discount application: ${first_applied_total:.2f}")
    assert first_applied_total == 42.50, \
        f"Expected total to be $42.50 after first discount, but got ${first_applied_total:.2f}"
    print("First discount applied successfully.")

    # 3. Attempt to apply the discount code 'SAVE15' again
    print("Step 3: Attempting to apply discount code 'SAVE15' for the second time.")
    # The input field still contains "SAVE15", so just click the apply button again
    apply_discount_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='discountCode']/following-sibling::button[1]"))
    )
    apply_discount_btn.click()

    # Verify the discount message indicates that the discount is already applied
    discount_message_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "discountMessage"))
    )
    expected_second_message = "Discount already applied"
    assert expected_second_message in discount_message_element.text, \
        f"Expected message '{expected_second_message}' after second attempt, but got '{discount_message_element.text}'"
    
    # Verify the total has NOT changed from the first application
    second_attempt_total = float(driver.find_element(By.ID, "total").text)
    print(f"Total after second discount attempt: ${second_attempt_total:.2f}")
    assert second_attempt_total == first_applied_total, \
        f"Expected total to remain ${first_applied_total:.2f}, but it changed to ${second_attempt_total:.2f}"
    print("Second discount attempt correctly blocked, total remained unchanged as expected.")

    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except Exception as e:
    print(f"Test Case {TEST_CASE_ID} FAILED")
    print(f"An error occurred: {e}")
    if driver:
        # Take a screenshot for debugging purposes
        screenshot_path = f"failure_{TEST_CASE_ID}.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    sys.exit(1)

finally:
    # Clean up: close the browser and remove the temporary HTML file
    if driver:
        driver.quit()
    if html_file_path and os.path.exists(html_file_path):
        os.remove(html_file_path)
        print(f"Temporary HTML file removed: {html_file_path}")
