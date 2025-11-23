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
TEST_CASE_ID = "TC-003"

# HTML content as a raw string
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

# Setup WebDriver
driver = None
temp_html_file = None

try:
    # Create a temporary HTML file to load in the browser
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
        f.write(HTML_CONTENT)
        temp_html_file = f.name
    
    # Initialize Chrome WebDriver using ChromeDriverManager for automatic driver management
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    # Navigate to the local HTML file
    driver.get(f"file:///{temp_html_file}")
    print(f"Navigated to {driver.current_url}")

    # Add a product to the cart to ensure a non-zero total, which might be a prerequisite for payment
    # Use explicit wait for the "Add to Cart" button for Product A to be clickable
    add_to_cart_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='item']/span[contains(text(), 'Product A')]/following-sibling::button"))
    )
    add_to_cart_btn.click()
    print("Action: Added 'Product A' to cart.")

    # Verify cart total is updated to reflect the added product
    total_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "total"))
    )
    assert total_element.text == "50.00", f"Assertion Failed: Expected total to be '50.00', but got '{total_element.text}'"
    print(f"Verification: Cart total is ${total_element.text}.")

    # For this test case, we intentionally leave required user details (name, email, address) blank.
    # No interaction with these input fields is needed as their default state is blank.
    print("Action: Intentionally leaving 'Full Name', 'Email', and 'Address' fields blank.")

    # Click the "Pay Now" button to attempt payment with missing details
    pay_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "payBtn"))
    )
    pay_button.click()
    print("Action: Clicked 'Pay Now' button.")

    # --- Assertions for Payment Failure and Error Messages ---

    # 1. Verify that the "Payment Successful!" message is NOT displayed
    success_message_element = driver.find_element(By.ID, "success")
    # Use EC.invisibility_of_element_located to ensure it's not visible
    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, "success")))
    assert success_message_element.is_displayed() is False, \
        "Assertion Failed: Payment success message should NOT be displayed when details are missing."
    print("Verification: Payment success message is NOT displayed.")

    # 2. Verify specific validation error messages are displayed for each missing field
    # Expected error messages and their corresponding IDs
    expected_errors = {
        "nameError": "Name is required",
        "emailError": "Email is required",
        "addressError": "Address is required"
    }

    for error_id, expected_text in expected_errors.items():
        # Use explicit wait for the error message element to be visible
        error_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, error_id))
        )
        
        # Verify error message text
        actual_text = error_element.text
        assert actual_text == expected_text, \
            f"Assertion Failed: Expected error for '{error_id}' to be '{expected_text}', but got '{actual_text}'"
        print(f"Verification: Error message for '{error_id}' is '{actual_text}'.")

        # Verify error message is displayed in red text
        # Get the computed style property 'color'. 'red' typically translates to 'rgb(255, 0, 0)'.
        color = error_element.value_of_css_property("color")
        assert color == "rgb(255, 0, 0)", \
            f"Assertion Failed: Expected error text color for '{error_id}' to be red (rgb(255, 0, 0)), but got '{color}'"
        print(f"Verification: Error message color for '{error_id}' is red.")

    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except Exception as e:
    print(f"Test Case {TEST_CASE_ID} FAILED")
    print(f"An error occurred: {e}")
    if driver:
        # Take a screenshot on failure for debugging
        screenshot_path = f"{TEST_CASE_ID}_failure_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    sys.exit(1)

finally:
    # Clean up: close the browser and delete the temporary HTML file
    if driver:
        driver.quit()
    if temp_html_file and os.path.exists(temp_html_file):
        os.remove(temp_html_file)
        print(f"Cleaned up temporary file: {temp_html_file}")
