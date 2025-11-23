import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# Test Case ID
TEST_CASE_ID = "TC-012"

# Target HTML content
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

# Create a temporary HTML file
HTML_FILE_NAME = "checkout_test_page.html"
with open(HTML_FILE_NAME, "w") as f:
    f.write(TARGET_HTML_CONTENT)

# Construct the file URL
FILE_URL = "file://" + os.path.abspath(HTML_FILE_NAME)

driver = None
try:
    # Initialize Chrome WebDriver
    # Use ChromeDriverManager to automatically download and manage the ChromeDriver executable
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window() # Maximize window for better visibility
    
    # Navigate to the local HTML file
    driver.get(FILE_URL)

    # Explicit wait for elements to be present
    wait = WebDriverWait(driver, 10)

    # --- Test Steps ---

    # 1. Add a product to the cart to enable a realistic checkout scenario
    # Wait for the "Add to Cart" button for Product A and click it
    add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='item'][1]/button")))
    add_to_cart_btn.click()
    print("Added Product A to cart.")

    # 2. Fill in the Full Name field
    name_field = wait.until(EC.presence_of_element_located((By.ID, "name")))
    name_field.send_keys("John Doe")
    print("Filled 'Full Name' field.")

    # 3. Fill in the Email field with a valid email
    email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
    email_field.send_keys("john.doe@example.com")
    print("Filled 'Email' field.")

    # 4. Leave the Address field empty (this is the core of the test case)
    address_field = wait.until(EC.presence_of_element_located((By.ID, "address")))
    address_field.clear() # Ensure it's empty
    print("Left 'Address' field empty.")

    # 5. Click the "Pay Now" button
    pay_button = wait.until(EC.element_to_be_clickable((By.ID, "payBtn")))
    pay_button.click()
    print("Clicked 'Pay Now' button.")

    # --- Assertions/Verification ---

    # 6. Verify that the payment success message is NOT displayed
    # We expect the success message to be hidden
    success_message = wait.until(EC.presence_of_element_located((By.ID, "success")))
    if success_message.is_displayed():
        raise AssertionError("Payment success message was displayed, but payment should have failed due to missing address.")
    print("Verified: Payment success message is NOT displayed.")

    # 7. Verify that a form validation error message is displayed for the empty 'address' field
    # Wait for the address error message to be visible
    address_error_message = wait.until(EC.visibility_of_element_located((By.ID, "addressError")))
    
    # Assert the text content of the error message
    expected_error_text = "Address is required"
    actual_error_text = address_error_message.text.strip()
    assert actual_error_text == expected_error_text, \
        f"Expected address error message '{expected_error_text}', but got '{actual_error_text}'"
    print(f"Verified: Address error message '{actual_error_text}' is displayed.")

    # Assert that the error message is displayed in red text (by checking its class)
    # The style tag defines .error { color: red; }
    assert "error" in address_error_message.get_attribute("class"), \
        "Address error message does not have the 'error' class, indicating it might not be red."
    print("Verified: Address error message has 'error' class (red text).")

    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except (TimeoutException, NoSuchElementException) as e:
    print(f"Test Case {TEST_CASE_ID} FAILED: Element not found or timed out - {e}")
    if driver:
        driver.save_screenshot(f"{TEST_CASE_ID}_failure_screenshot.png")
    sys.exit(1)
except AssertionError as e:
    print(f"Test Case {TEST_CASE_ID} FAILED: Assertion failed - {e}")
    if driver:
        driver.save_screenshot(f"{TEST_CASE_ID}_failure_screenshot.png")
    sys.exit(1)
except WebDriverException as e:
    print(f"Test Case {TEST_CASE_ID} FAILED: WebDriver error - {e}")
    if driver:
        driver.save_screenshot(f"{TEST_CASE_ID}_failure_screenshot.png")
    sys.exit(1)
except Exception as e:
    print(f"Test Case {TEST_CASE_ID} FAILED: An unexpected error occurred - {e}")
    if driver:
        driver.save_screenshot(f"{TEST_CASE_ID}_failure_screenshot.png")
    sys.exit(1)
finally:
    # Clean up: close the browser and remove the temporary HTML file
    if driver:
        driver.quit()
    if os.path.exists(HTML_FILE_NAME):
        os.remove(HTML_FILE_NAME)
    print("Browser closed and temporary HTML file removed.")