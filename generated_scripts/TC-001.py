from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sys
import os
import tempfile

# Test Case ID for reporting
TEST_CASE_ID = "TC-001"

# CRITICAL: HTML content embedded as a raw string with triple quotes
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
temp_file = None
try:
    # Create a temporary HTML file to load in the browser
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
    temp_file.write(HTML_CONTENT)
    temp_file.close()
    file_path = 'file:///' + temp_file.name.replace('\\', '/')

    # Initialize the Chrome driver using ChromeDriverManager
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()  # Maximize window for better visibility
    # Initialize WebDriverWait for explicit waits
    wait = WebDriverWait(driver, 10)

    # Navigate to the temporary HTML file
    driver.get(file_path)
    print(f"Navigated to: {file_path}")

    # --- Test Steps: Successful Order with Standard Shipping and Discount ---

    # 1. Add items to the cart
    print("Adding Product A, B, and C to the cart...")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[span='Product A - $50']/button[text()='Add to Cart']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[span='Product B - $30']/button[text()='Add to Cart']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[span='Product C - $20']/button[text()='Add to Cart']"))).click()
    
    # Verify initial total (50 + 30 + 20 = 100)
    total_element = wait.until(EC.visibility_of_element_located((By.ID, "total")))
    assert total_element.text == "100.00", f"Assertion Failed: Expected initial total '100.00', but got '{total_element.text}'"
    print(f"Items added. Current total: ${total_element.text}")

    # 2. Apply the 'SAVE15' discount
    print("Applying discount code 'SAVE15'...")
    discount_code_input = wait.until(EC.visibility_of_element_located((By.ID, "discountCode")))
    discount_code_input.send_keys("SAVE15")
    
    apply_discount_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//h3[text()='Discount Code']/following-sibling::button[text()='Apply']")))
    apply_discount_button.click()
    
    # Verify discount message and its color
    discount_message_element = wait.until(EC.visibility_of_element_located((By.ID, "discountMessage")))
    assert discount_message_element.text == "Discount applied!", f"Assertion Failed: Expected discount message 'Discount applied!', but got '{discount_message_element.text}'"
    # Check for green color (rgb(0, 128, 0) is the computed style for 'green')
    assert discount_message_element.value_of_css_property('color') == 'rgb(0, 128, 0)', \
        f"Assertion Failed: Expected discount message color 'rgb(0, 128, 0)', but got '{discount_message_element.value_of_css_property('color')}'"
    
    # Verify discounted total (100 * 0.85 = 85)
    total_element = wait.until(EC.visibility_of_element_located((By.ID, "total")))
    assert total_element.text == "85.00", f"Assertion Failed: Expected discounted total '85.00', but got '{total_element.text}'"
    print(f"Discount 'SAVE15' applied. New total: ${total_element.text}")

    # 3. Provide all required user details
    print("Entering user details (Name, Email, Address)...")
    wait.until(EC.visibility_of_element_located((By.ID, "name"))).send_keys("Automation User")
    wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys("automation.user@example.com")
    wait.until(EC.visibility_of_element_located((By.ID, "address"))).send_keys("123 Test Street, Test City, 12345")
    print("User details entered.")

    # 4. Select standard shipping
    print("Selecting Standard Shipping method...")
    standard_shipping_radio = wait.until(EC.element_to_be_clickable((By.ID, "shipping-standard")))
    # Standard shipping is checked by default in HTML, but explicitly clicking ensures interaction
    if not standard_shipping_radio.is_selected():
        standard_shipping_radio.click()
    assert standard_shipping_radio.is_selected(), "Assertion Failed: Standard shipping radio button is not selected."
    # The HTML states "Standard (Free)", so the cost is implicitly $0.00.
    print("Standard Shipping selected (Cost: $0.00).")

    # 5. Select payment method (Credit Card is checked by default)
    print("Selecting Credit Card payment method...")
    credit_card_radio = wait.until(EC.element_to_be_clickable((By.ID, "payment-card")))
    # Credit Card is checked by default in HTML, but explicitly clicking ensures interaction
    if not credit_card_radio.is_selected():
        credit_card_radio.click()
    assert credit_card_radio.is_selected(), "Assertion Failed: Credit Card payment radio button is not selected."
    print("Credit Card payment method selected.")

    # 6. Verify 'Pay Now' button is green and submit the order
    print("Verifying 'Pay Now' button color and submitting the order...")
    pay_button = wait.until(EC.element_to_be_clickable((By.ID, "payBtn")))
    pay_button_color = pay_button.value_of_css_property('background-color')
    # The CSS specifies 'green', which typically resolves to rgba(0, 128, 0, 1) or rgb(0, 128, 0)
    assert pay_button_color in ['rgba(0, 128, 0, 1)', 'rgb(0, 128, 0)'], \
        f"Assertion Failed: Expected Pay Now button background color to be green, but got '{pay_button_color}'"
    print("Pay Now button color verified as green.")
    
    pay_button.click()
    print("Clicked 'Pay Now' button to process payment.")

    # 7. Verify the success message is displayed
    success_message_element = wait.until(EC.visibility_of_element_located((By.ID, "success")))
    assert success_message_element.is_displayed(), "Assertion Failed: Success message is not displayed after payment."
    assert success_message_element.text == "Payment Successful!", \
        f"Assertion Failed: Expected success message 'Payment Successful!', but got '{success_message_element.text}'"
    print("Order successfully placed. Success message 'Payment Successful!' displayed and verified.")

    # If all assertions pass, the test case is successful
    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except Exception as e:
    # Handle any exceptions that occur during the test
    print(f"Test Case {TEST_CASE_ID} FAILED")
    print(f"An error occurred: {e}")
    if driver:
        # Take a screenshot on failure
        screenshot_name = f"{TEST_CASE_ID}_FAILED.png"
        driver.save_screenshot(screenshot_name)
        print(f"Screenshot saved as {screenshot_name}")
    sys.exit(1)
finally:
    # Ensure the browser is closed and temporary file is removed
    if driver:
        driver.quit()
        print("Browser closed.")
    if temp_file and os.path.exists(temp_file.name):
        os.remove(temp_file.name)
        print(f"Temporary file {temp_file.name} removed.")
