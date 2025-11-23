import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# --- Test Case Details ---
TEST_CASE_ID = "TC-001"
TEST_CASE_TITLE = "Successful Payment with All Required Details"
EXPECTED_RESULT = "Payment succeeds, and a clearly visible success message is displayed."

# --- HTML Content for the local file ---
HTML_CONTENT = """
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

# --- Setup for local HTML file ---
HTML_FILE_NAME = "checkout_page.html"
FILE_PATH = os.path.abspath(HTML_FILE_NAME)
FILE_URL = f"file://{FILE_PATH}"

driver = None
try:
    # Create the HTML file
    with open(HTML_FILE_NAME, "w") as f:
        f.write(HTML_CONTENT)

    # Initialize WebDriver
    # Use ChromeDriverManager to automatically download and manage chromedriver
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    # Navigate to the local HTML file
    driver.get(FILE_URL)

    # Initialize WebDriverWait for explicit waits
    wait = WebDriverWait(driver, 10)

    print(f"--- Running Test Case: {TEST_CASE_ID} - {TEST_CASE_TITLE} ---")

    # Step 1: Add items to cart
    # Find and click 'Add to Cart' for Product A
    product_a_add_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(., 'Product A - $50')]/button"))
    )
    product_a_add_button.click()
    print("Added Product A to cart.")

    # Find and click 'Add to Cart' for Product B
    product_b_add_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(., 'Product B - $30')]/button"))
    )
    product_b_add_button.click()
    print("Added Product B to cart.")

    # Optional: Verify cart total updates (e.g., wait for total to be > 0)
    wait.until(EC.text_to_be_present_in_element((By.ID, "total"), "80.00"))
    print(f"Cart total updated to: ${driver.find_element(By.ID, 'total').text}")

    # Step 2: Provide user details
    # Fill Full Name
    name_input = wait.until(EC.visibility_of_element_located((By.ID, "name")))
    name_input.send_keys("John Doe")
    print("Entered Full Name.")

    # Fill Email
    email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")))
    email_input.send_keys("john.doe@example.com")
    print("Entered Email.")

    # Fill Address
    address_textarea = wait.until(EC.visibility_of_element_located((By.ID, "address")))
    address_textarea.send_keys("123 Automation Street, Test City, 12345")
    print("Entered Address.")

    # Step 3: Select a shipping method (Express)
    shipping_express_radio = wait.until(
        EC.element_to_be_clickable((By.ID, "shipping-express"))
    )
    shipping_express_radio.click()
    print("Selected Express shipping method.")

    # Step 4: Select a payment method (Credit Card - already default, but clicking ensures interaction)
    payment_card_radio = wait.until(
        EC.element_to_be_clickable((By.ID, "payment-card"))
    )
    payment_card_radio.click()
    print("Selected Credit Card payment method.")

    # Step 5: Proceed to complete the payment
    pay_button = wait.until(EC.element_to_be_clickable((By.ID, "payBtn")))
    pay_button.click()
    print("Clicked 'Pay Now' button.")

    # Step 6: Verify payment success message
    success_message_element = wait.until(
        EC.visibility_of_element_located((By.ID, "success"))
    )

    # Assert the text content
    assert success_message_element.text == "Payment Successful!", \
        f"Expected success message 'Payment Successful!' but got '{success_message_element.text}'"

    # Assert the display style (it should be 'block' when visible)
    assert success_message_element.value_of_css_property("display") == "block", \
        "Success message is not displayed as 'block'."

    print(f"Verification successful: '{success_message_element.text}' is displayed.")

    print(f"\nTest Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except (TimeoutException, NoSuchElementException) as e:
    print(f"\nTest Case {TEST_CASE_ID} FAILED: Element not found or timed out - {e}")
    if driver:
        screenshot_path = f"{TEST_CASE_ID}_FAILED_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    sys.exit(1)
except AssertionError as e:
    print(f"\nTest Case {TEST_CASE_ID} FAILED: Assertion failed - {e}")
    if driver:
        screenshot_path = f"{TEST_CASE_ID}_FAILED_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    sys.exit(1)
except WebDriverException as e:
    print(f"\nTest Case {TEST_CASE_ID} FAILED: WebDriver error - {e}")
    if driver:
        screenshot_path = f"{TEST_CASE_ID}_FAILED_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    sys.exit(1)
except Exception as e:
    print(f"\nTest Case {TEST_CASE_ID} FAILED: An unexpected error occurred - {e}")
    if driver:
        screenshot_path = f"{TEST_CASE_ID}_FAILED_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    sys.exit(1)
finally:
    # Clean up: Close the browser and remove the temporary HTML file
    if driver:
        driver.quit()
    if os.path.exists(HTML_FILE_NAME):
        os.remove(HTML_FILE_NAME)
