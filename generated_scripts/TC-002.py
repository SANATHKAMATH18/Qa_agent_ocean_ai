import sys
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# Test Case ID
TEST_CASE_ID = "TC-002"

# HTML content for the E-Shop Checkout page
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
        let shippingCost = 0; // Track shipping cost separately

        function updateDisplayTotal() {
            document.getElementById('total').innerText = (total + shippingCost).toFixed(2);
        }

        function addToCart(name, price) {
            const cart = document.getElementById('cart');
            cart.innerHTML += `<p>${name} - $${price}</p>`;
            total += price;
            updateDisplayTotal();
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
                total = total - (total * 0.15); // Apply discount only to product total
                updateDisplayTotal();
                messageEl.textContent = 'Discount applied!';
                messageEl.style.color = 'green';
                discountApplied = true;
            } else {
                messageEl.textContent = 'Invalid discount code';
                messageEl.style.color = 'red';
            }
        }

        // Add event listeners for shipping radio buttons
        document.addEventListener('DOMContentLoaded', () => {
            const standardShipping = document.getElementById('shipping-standard');
            const expressShipping = document.getElementById('shipping-express');

            standardShipping.addEventListener('change', () => {
                if (standardShipping.checked) {
                    shippingCost = 0;
                    updateDisplayTotal();
                }
            });

            expressShipping.addEventListener('change', () => {
                if (expressShipping.checked) {
                    shippingCost = 10;
                    updateDisplayTotal();
                }
            });
        });


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

# Setup temporary HTML file
temp_html_file = None
driver = None

try:
    # Create a temporary HTML file
    fd, path = tempfile.mkstemp(suffix=".html")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(HTML_CONTENT)
    temp_html_file = f'file:///{path}'

    # Initialize Chrome WebDriver
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window() # Maximize window for better visibility
    
    # Set up explicit wait
    wait = WebDriverWait(driver, 10)

    # Navigate to the local HTML file
    driver.get(temp_html_file)

    print(f"--- Starting Test Case {TEST_CASE_ID}: Successful Order with Express Shipping and Discount ---")

    # 1. Add items to the cart
    print("Adding items to cart...")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[span[contains(text(), 'Product A')]]/button"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[span[contains(text(), 'Product B')]]/button"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[span[contains(text(), 'Product C')]]/button"))).click()

    # Verify initial total
    total_element = wait.until(EC.visibility_of_element_located(By.ID("total")))
    initial_total = float(total_element.text)
    expected_initial_total = 50.00 + 30.00 + 20.00
    assert initial_total == expected_initial_total, \
        f"Expected initial total {expected_initial_total}, but got {initial_total}"
    print(f"Initial cart total verified: ${initial_total:.2f}")

    # 2. Apply the 'SAVE15' discount
    print("Applying 'SAVE15' discount...")
    discount_code_input = wait.until(EC.visibility_of_element_located(By.ID("discountCode")))
    discount_code_input.send_keys("SAVE15")
    
    apply_discount_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Apply']")))
    apply_discount_button.click()

    # Verify discount message
    discount_message = wait.until(EC.visibility_of_element_located(By.ID("discountMessage")))
    wait.until(EC.text_to_be_present_in_element((By.ID("discountMessage")), "Discount applied!"))
    assert discount_message.text == "Discount applied!", \
        f"Expected discount message 'Discount applied!', but got '{discount_message.text}'"
    
    # Verify total after discount
    total_after_discount = float(total_element.text)
    expected_total_after_discount = expected_initial_total * 0.85 # 15% discount
    assert abs(total_after_discount - expected_total_after_discount) < 0.01, \
        f"Expected total after discount {expected_total_after_discount:.2f}, but got {total_after_discount:.2f}"
    print(f"Discount applied and total verified: ${total_after_discount:.2f}")

    # 3. Select express shipping
    print("Selecting Express Shipping...")
    express_shipping_radio = wait.until(EC.element_to_be_clickable(By.ID("shipping-express")))
    express_shipping_radio.click()

    # Verify total after express shipping
    total_after_shipping = float(total_element.text)
    expected_total_after_shipping = expected_total_after_discount + 10.00 # Express shipping cost is $10
    assert abs(total_after_shipping - expected_total_after_shipping) < 0.01, \
        f"Expected total after shipping {expected_total_after_shipping:.2f}, but got {total_after_shipping:.2f}"
    print(f"Express shipping selected and total verified: ${total_after_shipping:.2f}")

    # 4. Provide all required user details
    print("Entering user details...")
    wait.until(EC.visibility_of_element_located(By.ID("name"))).send_keys("John Doe")
    wait.until(EC.visibility_of_element_located(By.ID("email"))).send_keys("john.doe@example.com")
    wait.until(EC.visibility_of_element_located(By.ID("address"))).send_keys("123 Automation St, Test City, 12345")
    print("User details entered.")

    # 5. Select payment method (Credit Card is default, no action needed)
    print("Payment method 'Credit Card' is selected by default.")
    payment_card_radio = wait.until(EC.visibility_of_element_located(By.ID("payment-card")))
    assert payment_card_radio.is_selected(), "Credit Card payment method not selected by default."

    # 6. Successfully submit the order
    print("Submitting order...")
    pay_button = wait.until(EC.element_to_be_clickable(By.ID("payBtn")))
    
    # Verify 'Pay Now' button is green
    pay_button_color = pay_button.value_of_css_property("background-color")
    # Selenium returns RGBA, check for green color (e.g., rgba(0, 128, 0, 1) or similar)
    assert "rgb(0, 128, 0)" in pay_button_color or "rgba(0, 128, 0, 1)" in pay_button_color, \
        f"Expected 'Pay Now' button to be green, but got color: {pay_button_color}"
    print("Pay Now button color verified as green.")

    pay_button.click()

    # Verify success message is displayed
    success_message = wait.until(EC.visibility_of_element_located(By.ID("success")))
    assert success_message.is_displayed(), "Success message is not displayed after payment."
    assert success_message.text == "Payment Successful!", \
        f"Expected success message 'Payment Successful!', but got '{success_message.text}'"
    print("Success message 'Payment Successful!' displayed.")

    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except (TimeoutException, NoSuchElementException) as e:
    print(f"Test Case {TEST_CASE_ID} FAILED: Element not found or timed out - {e}")
    if driver:
        driver.save_screenshot(f"{TEST_CASE_ID}_failure_screenshot.png")
        print(f"Screenshot saved as {TEST_CASE_ID}_failure_screenshot.png")
    sys.exit(1)
except AssertionError as e:
    print(f"Test Case {TEST_CASE_ID} FAILED: Assertion failed - {e}")
    if driver:
        driver.save_screenshot(f"{TEST_CASE_ID}_failure_screenshot.png")
        print(f"Screenshot saved as {TEST_CASE_ID}_failure_screenshot.png")
    sys.exit(1)
except WebDriverException as e:
    print(f"Test Case {TEST_CASE_ID} FAILED: WebDriver error - {e}")
    if driver:
        driver.save_screenshot(f"{TEST_CASE_ID}_failure_screenshot.png")
        print(f"Screenshot saved as {TEST_CASE_ID}_failure_screenshot.png")
    sys.exit(1)
except Exception as e:
    print(f"Test Case {TEST_CASE_ID} FAILED: An unexpected error occurred - {e}")
    if driver:
        driver.save_screenshot(f"{TEST_CASE_ID}_failure_screenshot.png")
        print(f"Screenshot saved as {TEST_CASE_ID}_failure_screenshot.png")
    sys.exit(1)
finally:
    if driver:
        driver.quit()
    if temp_html_file and os.path.exists(temp_html_file.replace('file:///', '')):
        os.remove(temp_html_file.replace('file:///', ''))
        print(f"Cleaned up temporary HTML file: {temp_html_file.replace('file:///', '')}")

