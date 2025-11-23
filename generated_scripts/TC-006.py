import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# CRITICAL: HTML content as a raw string to avoid escape sequence warnings
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

TEST_CASE_ID = "TC-006"
SCREENSHOT_DIR = "screenshots"
# Ensure the screenshot directory exists
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

driver = None
html_file_path = "temp_checkout_page.html"

try:
    # 1. Setup: Create a temporary HTML file to serve the content
    with open(html_file_path, "w") as f:
        f.write(HTML_CONTENT)

    # Initialize Chrome WebDriver using ChromeDriverManager for automatic driver management
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window() # Maximize the browser window for better visibility
    
    # Initialize WebDriverWait for explicit waits
    wait = WebDriverWait(driver, 10)

    # 2. Navigate to the local HTML file
    driver.get(f"file:///{os.path.abspath(html_file_path)}")

    print(f"Starting Test Case {TEST_CASE_ID}: Verify Standard Shipping Cost")

    # Add items to the cart
    # Locate and click 'Add to Cart' button for Product A
    add_to_cart_btn_a = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='item'][1]/button")))
    add_to_cart_btn_a.click()
    print("Step: Added 'Product A' to cart.")

    # Locate and click 'Add to Cart' button for Product B
    add_to_cart_btn_b = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='item'][2]/button")))
    add_to_cart_btn_b.click()
    print("Step: Added 'Product B' to cart.")

    # Verify cart total updates (optional, but good practice to ensure items were added)
    cart_total_element = wait.until(EC.visibility_of_element_located((By.ID, "total")))
    current_total = float(cart_total_element.text)
    # Product A ($50) + Product B ($30) = $80
    assert current_total == 80.00, \
        f"Assertion Failed: Expected cart total to be $80.00 after adding products, but got ${current_total:.2f}."
    print(f"Verification: Cart total is correctly displayed as ${current_total:.2f}.")

    # Select 'Standard Shipping' option
    # The 'Standard Shipping' radio button is checked by default in the HTML,
    # but we explicitly click it to simulate user interaction and ensure its state.
    standard_shipping_radio = wait.until(EC.element_to_be_clickable((By.ID, "shipping-standard")))
    if not standard_shipping_radio.is_selected():
        standard_shipping_radio.click()
    print("Step: Selected 'Standard Shipping' option.")

    # Verify that 'Standard Shipping' is indeed selected
    assert standard_shipping_radio.is_selected(), \
        "Assertion Failed: 'Standard Shipping' radio button is not selected."
    print("Verification: 'Standard Shipping' radio button is confirmed as selected.")

    # Verify the shipping cost displayed for 'Standard Shipping'
    # According to the HTML, the shipping cost is indicated in the label text associated with the radio button.
    standard_shipping_label = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "label[for='shipping-standard']")))
    shipping_label_text = standard_shipping_label.text
    print(f"Info: Text of 'Standard Shipping' label is: '{shipping_label_text}'")

    # Expected result: "The shipping cost displayed in the cart summary or checkout total is $0.00."
    # Based on the provided HTML, the label explicitly states "Standard (Free)".
    expected_cost_indicator = "Free"
    assert expected_cost_indicator in shipping_label_text, \
        f"Assertion Failed: Expected shipping cost to be '{expected_cost_indicator}' in the label, " \
        f"but found '{shipping_label_text}'."
    print(f"Verification: Standard Shipping cost is correctly displayed as '{expected_cost_indicator}' " \
          f"in the associated label.")

    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except Exception as e:
    print(f"Test Case {TEST_CASE_ID} FAILED")
    print(f"Error: {e}")
    if driver:
        # Take a screenshot on failure
        screenshot_name = os.path.join(SCREENSHOT_DIR, f"{TEST_CASE_ID}_FAILED.png")
        driver.save_screenshot(screenshot_name)
        print(f"Screenshot saved to {screenshot_name}")
    sys.exit(1)

finally:
    # Teardown: Close the browser and remove the temporary HTML file
    if driver:
        driver.quit()
    if os.path.exists(html_file_path):
        os.remove(html_file_path)
    print("Cleanup: Browser closed and temporary HTML file removed.")
