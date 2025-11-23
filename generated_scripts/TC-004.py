import sys
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Test Case ID
TEST_CASE_ID = "TC-004"

# HTML content provided as a raw string
HTML_CONTENT = r'''
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
'''

driver = None
temp_file_path = None

try:
    # 1. Setup Chrome WebDriver using ChromeDriverManager
    print(f"[{TEST_CASE_ID}] Setting up Chrome WebDriver...")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    # Initialize WebDriverWait for explicit waits
    wait = WebDriverWait(driver, 10) 

    # 2. Create a temporary HTML file to host the content
    print(f"[{TEST_CASE_ID}] Creating temporary HTML file...")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as temp_file:
        temp_file.write(HTML_CONTENT)
        temp_file_path = temp_file.name
    
    # Construct the file URL for the browser to open
    file_url = 'file:///' + os.path.abspath(temp_file_path).replace('\\', '/')
    
    # 3. Navigate to the local HTML file
    print(f"[{TEST_CASE_ID}] Navigating to {file_url}...")
    driver.get(file_url)

    # 4. Add items to the cart to establish a base total
    print(f"[{TEST_CASE_ID}] Adding Product A ($50) to cart...")
    add_product_a_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[span[contains(text(), 'Product A')]]/button[text()='Add to Cart']")))
    add_product_a_button.click()

    print(f"[{TEST_CASE_ID}] Adding Product B ($30) to cart...")
    add_product_b_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[span[contains(text(), 'Product B')]]/button[text()='Add to Cart']")))
    add_product_b_button.click()

    # Get initial total before applying discount
    total_element = wait.until(EC.visibility_of_element_located((By.ID, "total")))
    initial_total_str = total_element.text
    initial_total = float(initial_total_str)
    print(f"[{TEST_CASE_ID}] Initial cart total: ${initial_total:.2f}")
    assert initial_total == 80.00, f"Assertion Failed: Expected initial total $80.00, but got ${initial_total:.2f}"

    # 5. Locate the discount code input field and enter the valid code
    print(f"[{TEST_CASE_ID}] Entering discount code 'SAVE15' into the input field...")
    discount_code_input = wait.until(EC.visibility_of_element_located((By.ID, "discountCode")))
    discount_code_input.send_keys("SAVE15")

    # 6. Click the "Apply" button to apply the discount
    print(f"[{TEST_CASE_ID}] Clicking 'Apply' button...")
    apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Apply']")))
    apply_button.click()

    # 7. Verify the discount message indicates successful application
    print(f"[{TEST_CASE_ID}] Verifying discount message...")
    discount_message_element = wait.until(EC.visibility_of_element_located((By.ID, "discountMessage")))
    discount_message_text = discount_message_element.text
    assert discount_message_text == "Discount applied!", \
        f"Assertion Failed: Expected discount message 'Discount applied!', but got '{discount_message_text}'"
    
    # 8. Verify the updated total cart value reflects the 15% discount
    print(f"[{TEST_CASE_ID}] Verifying updated cart total after discount...")
    updated_total_element = wait.until(EC.visibility_of_element_located((By.ID, "total")))
    updated_total_str = updated_total_element.text
    updated_total = float(updated_total_str)
    
    expected_discount_amount = initial_total * 0.15
    expected_total_after_discount = initial_total - expected_discount_amount
    
    # Using a small delta for float comparison due to potential precision issues
    assert abs(updated_total - expected_total_after_discount) < 0.01, \
        f"Assertion Failed: Expected updated total ${expected_total_after_discount:.2f}, but got ${updated_total:.2f}"
    
    print(f"[{TEST_CASE_ID}] Discount successfully applied. New total: ${updated_total:.2f}")

    # If all assertions pass, the test case is successful
    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except Exception as e:
    # Handle any exceptions that occur during the test
    print(f"Test Case {TEST_CASE_ID} FAILED")
    print(f"Error: {e}")
    if driver:
        # Take a screenshot on failure for debugging
        screenshot_name = f"{TEST_CASE_ID}_FAILED.png"
        driver.save_screenshot(screenshot_name)
        print(f"Screenshot saved as {screenshot_name}")
    sys.exit(1)

finally:
    # 9. Clean up: Close the browser and delete the temporary HTML file
    if driver:
        print(f"[{TEST_CASE_ID}] Quitting WebDriver...")
        driver.quit()
    if temp_file_path and os.path.exists(temp_file_path):
        print(f"[{TEST_CASE_ID}] Deleting temporary HTML file: {temp_file_path}")
        os.remove(temp_file_path)
