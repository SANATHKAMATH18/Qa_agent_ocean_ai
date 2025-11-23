import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# --- Test Case Details ---
TEST_CASE_ID = "TC-004"
# The expected RGBA value for 'green' as rendered by browsers.
# This is derived from the CSS 'background-color: green;' in the target HTML.
EXPECTED_BUTTON_COLOR_RGBA = "rgba(0, 128, 0, 1)"

# --- Create a temporary HTML file for the test ---
HTML_FILE_NAME = "checkout_page_tc004.html"
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

def create_html_file(filename, content):
    """Creates a temporary HTML file with the given content."""
    with open(filename, "w") as f:
        f.write(content)
    # Return the absolute path to the file
    return os.path.abspath(filename)

def cleanup_html_file(filename):
    """Removes the temporary HTML file."""
    if os.path.exists(filename):
        os.remove(filename)

# Initialize driver and html_file_path to None for finally block
driver = None
html_file_path = None

try:
    # Create the temporary HTML file for the test
    html_file_path = create_html_file(HTML_FILE_NAME, HTML_CONTENT)
    
    # Initialize Chrome WebDriver using ChromeDriverManager for automatic driver management
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    # Set up WebDriverWait for explicit waits with a timeout of 10 seconds
    wait = WebDriverWait(driver, 10)

    # Navigate to the local HTML file
    # Using 'file:///' prefix to open a local file
    driver.get(f"file:///{html_file_path}")
    print(f"Navigated to local file: {html_file_path}")

    # --- Test Case TC-004: Verify 'Pay Now' Button Color ---
    print(f"\n--- Executing Test Case {TEST_CASE_ID}: Verify 'Pay Now' Button Color ---")

    # 1. Locate the 'Pay Now' button using its ID
    # Use an explicit wait to ensure the button is visible before interacting
    pay_now_button = wait.until(
        EC.visibility_of_element_located((By.ID, "payBtn")),
        message="Timed out waiting for 'Pay Now' button to be visible."
    )
    print("Successfully located the 'Pay Now' button.")

    # 2. Get the computed 'background-color' CSS property of the button
    actual_color = pay_now_button.value_of_css_property("background-color")
    print(f"Actual 'Pay Now' button background color: {actual_color}")

    # 3. Assert that the actual color matches the expected green RGBA value
    if actual_color == EXPECTED_BUTTON_COLOR_RGBA:
        print(f"Test Case {TEST_CASE_ID} PASSED: The 'Pay Now' button has the expected green color ({actual_color}).")
        sys.exit(0) # Exit with success code
    else:
        # If the color does not match, raise an AssertionError
        raise AssertionError(
            f"Test Case {TEST_CASE_ID} FAILED: 'Pay Now' button color is '{actual_color}', "
            f"but expected '{EXPECTED_BUTTON_COLOR_RGBA}' (green)."
        )

except Exception as e:
    # Catch any exceptions that occur during the test execution
    print(f"Test Case {TEST_CASE_ID} FAILED due to an error: {e}")
    if driver:
        # If the driver was initialized, take a screenshot for debugging
        screenshot_name = f"{TEST_CASE_ID}_FAILED_screenshot.png"
        driver.save_screenshot(screenshot_name)
        print(f"Screenshot saved as {screenshot_name}")
    sys.exit(1) # Exit with failure code

finally:
    # Ensure the browser is closed and the temporary HTML file is cleaned up
    if driver:
        driver.quit()
        print("Browser closed.")
    if html_file_path:
        cleanup_html_file(HTML_FILE_NAME)
        print(f"Temporary HTML file '{HTML_FILE_NAME}' cleaned up.")

