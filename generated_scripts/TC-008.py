import sys
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

TEST_CASE_ID = "TC-008"
SCREENSHOT_DIR = "screenshots"

def run_test():
    driver = None
    temp_file = None
    try:
        # Create a directory for screenshots if it doesn't exist
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

        # Create a temporary HTML file to host the content
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
        temp_file.write(HTML_CONTENT)
        temp_file.close()
        # Get the file path in a format suitable for browser navigation
        file_path = 'file:///' + os.path.abspath(temp_file.name).replace('\\', '/')

        # Initialize Chrome WebDriver using ChromeDriverManager
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()

        # Navigate to the local HTML file
        driver.get(file_path)

        print(f"Starting Test Case {TEST_CASE_ID}: Form Validation Error Display in Red Text")

        # --- Test Steps ---
        # 1. Trigger form validation errors by leaving required fields empty
        #    and providing an invalid email format.

        # Leave 'name' field empty
        # Fill 'email' with an invalid format
        email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID("email"))))
        email_field.send_keys("invalid-email")
        # Leave 'address' field empty

        # Click the 'Pay Now' button to submit the form and trigger validation
        pay_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID("payBtn"))))
        pay_button.click()

        # 2. Verify that the validation error messages are displayed in red text.
        # Define the error elements and their expected messages
        error_elements_to_check = {
            "nameError": "Name is required",
            "emailError": "Invalid email format",
            "addressError": "Address is required"
        }
        
        all_errors_valid = True
        for error_id, expected_message in error_elements_to_check.items():
            try:
                # Wait for the error element to be visible
                error_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID(error_id))))
                
                # Assert that the error message is displayed
                assert error_element.is_displayed(), f"Error message for '{error_id}' is not displayed."
                
                # Assert that the error message text is correct
                actual_message = error_element.text.strip()
                assert actual_message == expected_message, \
                    f"Expected error message for '{error_id}' to be '{expected_message}', but got '{actual_message}'."
                
                # Assert that the error message is displayed in red text
                # The CSS defines .error { color: red; }, which typically resolves to rgba(255, 0, 0, 1) or rgb(255, 0, 0)
                color = error_element.value_of_css_property("color")
                expected_red_rgb = "rgb(255, 0, 0)"
                expected_red_rgba = "rgba(255, 0, 0, 1)"

                assert color == expected_red_rgb or color == expected_red_rgba, \
                    f"Error message for '{error_id}' is not red. Actual color: {color}"
                
                print(f"Validation for '{error_id}' PASSED: Message '{actual_message}' displayed in red.")

            except AssertionError as e:
                print(f"Validation for '{error_id}' FAILED: {e}")
                all_errors_valid = False
                break # Exit loop on first failure
            except Exception as e:
                print(f"An unexpected error occurred while checking '{error_id}': {e}")
                all_errors_valid = False
                break

        # Final check for overall test success
        if all_errors_valid:
            print(f"Test Case {TEST_CASE_ID} PASSED")
            sys.exit(0)
        else:
            # If any error validation failed, raise an assertion error to trigger the FAILED path
            raise AssertionError("One or more validation errors did not meet expectations.")

    except Exception as e:
        print(f"Test Case {TEST_CASE_ID} FAILED")
        print(f"Error: {e}")
        # Take a screenshot on failure
        if driver:
            screenshot_name = os.path.join(SCREENSHOT_DIR, f"{TEST_CASE_ID}_FAILED.png")
            driver.save_screenshot(screenshot_name)
            print(f"Screenshot saved to {screenshot_name}")
        sys.exit(1)
    finally:
        # Clean up: close the browser and delete the temporary HTML file
        if driver:
            driver.quit()
        if temp_file and os.path.exists(temp_file.name):
            os.remove(temp_file.name)
            print(f"Cleaned up temporary file: {temp_file.name}")

if __name__ == "__main__":
    run_test()
