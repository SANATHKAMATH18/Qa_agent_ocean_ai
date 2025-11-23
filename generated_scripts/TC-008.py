import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Test Case ID
TEST_CASE_ID = "TC-008"

# HTML content for the local file
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

# Create a temporary HTML file
html_file_path = os.path.join(os.getcwd(), "checkout.html")
with open(html_file_path, "w") as f:
    f.write(html_content)

driver = None
try:
    # Requirement 5: Use webdriver.Chrome() with ChromeDriverManager for automatic driver management.
    driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()))
    # Requirement 2: Use Explicit Waits (WebDriverWait) for finding elements.
    wait = WebDriverWait(driver, 10)

    # Navigate to the local HTML file
    driver.get(f"file:///{html_file_path}")

    # --- Test Steps for TC-008: Select Express Shipping Method ---

    # 1. Add a product to the cart to establish an initial total.
    # This is necessary to observe the $10 addition for express shipping.
    print("Adding 'Product A' to cart to establish an initial total...")
    # Requirement 4: Use exact locators (By.XPATH to find button associated with 'Product A')
    add_to_cart_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='item']/span[contains(text(), 'Product A')]/following-sibling::button"))
    )
    add_to_cart_btn.click()

    # Get the initial total before selecting express shipping.
    # Requirement 4: Use exact IDs (By.ID("total"))
    total_element = wait.until(EC.visibility_of_element_located((By.ID, "total")))
    initial_total_text = total_element.text
    initial_total = float(initial_total_text)
    print(f"Initial cart total after adding Product A: ${initial_total:.2f}")

    # 2. Select 'Express shipping' as the preferred shipping method.
    print("Selecting 'Express shipping' method...")
    # Requirement 4: Use exact IDs (By.ID("shipping-express"))
    express_shipping_radio = wait.until(EC.element_to_be_clickable((By.ID, "shipping-express")))
    express_shipping_radio.click()

    # 3. Verify that an additional $10 is added to the total cart value.
    # Re-fetch the total element's text to get the updated value.
    updated_total_text = wait.until(EC.visibility_of_element_located((By.ID, "total"))).text
    updated_total = float(updated_total_text)
    print(f"Updated cart total after selecting Express shipping: ${updated_total:.2f}")

    expected_total = initial_total + 10.00

    # Requirement 6: Include proper assertions.
    assert updated_total == expected_total, \
        f"Expected total to be ${expected_total:.2f} after express shipping, but got ${updated_total:.2f}"

    print(f"Successfully verified that Express shipping added $10.00 to the total.")

    # Requirement 11: On success, print a message and exit with sys.exit(0).
    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except Exception as e:
    # Requirement 13: On failure, print the error, take a screenshot, and sys.exit(1).
    print(f"Test Case {TEST_CASE_ID} FAILED")
    print(f"An error occurred: {e}")
    if driver:
        screenshot_name = f"{TEST_CASE_ID}_failure.png"
        driver.save_screenshot(screenshot_name)
        print(f"Screenshot saved as {screenshot_name}")
    sys.exit(1)

finally:
    # Clean up: close the browser and remove the temporary HTML file.
    if driver:
        driver.quit()
    if os.path.exists(html_file_path):
        os.remove(html_file_path)
