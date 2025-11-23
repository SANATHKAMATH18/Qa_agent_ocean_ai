import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, AssertionError, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# CRITICAL: HTML content as a raw string with triple quotes
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

TEST_CASE_ID = "TC-005"
TEMP_HTML_FILE = "temp_checkout_page.html"
SCREENSHOT_DIR = "screenshots"

def take_screenshot(driver, filename):
    """Takes a screenshot and saves it to the screenshots directory."""
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    try:
        driver.save_screenshot(filepath)
        print(f"Screenshot saved to {filepath}")
    except Exception as e:
        print(f"Failed to take screenshot: {e}")

def run_test():
    driver = None
    temp_html_file_path = os.path.abspath(TEMP_HTML_FILE)

    try:
        # Create a temporary HTML file to load in the browser
        with open(TEMP_HTML_FILE, "w") as f:
            f.write(HTML_CONTENT)

        # Initialize Chrome WebDriver using ChromeDriverManager
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.maximize_window()

        # Navigate to the local HTML file
        driver.get(f"file://{temp_html_file_path}")

        print(f"Starting Test Case {TEST_CASE_ID}: Attempt to Apply Discount Code Multiple Times")

        # 1. Add items to the cart
        # Find all "Add to Cart" buttons using XPath
        add_to_cart_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(), 'Add to Cart')]"))
        )
        
        # Click the first two items (Product A and Product B) to add them to the cart
        if len(add_to_cart_buttons) < 2:
            raise AssertionError("Not enough 'Add to Cart' buttons found to add multiple items.")
        
        add_to_cart_buttons[0].click() # Add Product A ($50)
        add_to_cart_buttons[1].click() # Add Product B ($30)
        print("Added Product A and Product B to cart.")

        # Get the initial total before any discount application
        total_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "total"))
        )
        initial_cart_total = float(total_element.text)
        print(f"Initial cart total: ${initial_cart_total:.2f}")
        
        # Assert the initial total is correct (50 + 30 = 80)
        expected_initial_total = 80.0
        assert abs(initial_cart_total - expected_initial_total) < 0.01, \
            f"Assertion Failed: Expected initial total ${expected_initial_total:.2f}, but got ${initial_cart_total:.2f}"
        print(f"Verified initial cart total is ${initial_cart_total:.2f}.")

        # Locate discount code input, apply button, and message span
        discount_code_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "discountCode"))
        )
        apply_discount_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Apply']"))
        )
        discount_message_span = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "discountMessage"))
        )

        # 2. Successfully apply the 'SAVE15' discount for the first time
        print("Attempting to apply 'SAVE15' discount for the first time...")
        discount_code_input.send_keys("SAVE15")
        apply_discount_button.click()

        # Wait for the success message to appear
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "discountMessage"), "Discount applied!")
        )
        # Assert the discount success message
        assert discount_message_span.text == "Discount applied!", \
            f"Assertion Failed: Expected 'Discount applied!' message, but got '{discount_message_span.text}'"
        print("First discount 'SAVE15' applied successfully.")

        # Verify the total amount after the first discount (80 * 0.85 = 68.0)
        first_discounted_total = float(total_element.text)
        expected_first_discounted_total = initial_cart_total * 0.85 
        assert abs(first_discounted_total - expected_first_discounted_total) < 0.01, \
            f"Assertion Failed: Expected total after first discount ${expected_first_discounted_total:.2f}, but got ${first_discounted_total:.2f}"
        print(f"Verified total after first discount: ${first_discounted_total:.2f}")

        # 3. Attempt to apply the same discount code 'SAVE15' again
        print("Attempting to apply 'SAVE15' discount for the second time...")
        # Clear the input field before re-entering the code (good practice)
        discount_code_input.clear()
        discount_code_input.send_keys("SAVE15")
        apply_discount_button.click()

        # Wait for the message indicating the discount cannot be applied again
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "discountMessage"), "Discount already applied")
        )
        expected_message_second_attempt = "Discount already applied"
        # Assert the message for the second attempt
        assert discount_message_span.text == expected_message_second_attempt, \
            f"Assertion Failed: Expected message '{expected_message_second_attempt}', but got '{discount_message_span.text}'"
        print(f"Verified message for second attempt: '{discount_message_span.text}'")

        # Verify that the total amount has NOT changed after the second attempt
        second_attempt_total = float(total_element.text)
        assert abs(second_attempt_total - first_discounted_total) < 0.01, \
            f"Assertion Failed: Total changed after second discount attempt. Expected ${first_discounted_total:.2f}, but got ${second_attempt_total:.2f}"
        print(f"Verified total remained unchanged after second discount attempt: ${second_attempt_total:.2f}")

        print(f"Test Case {TEST_CASE_ID} PASSED")
        sys.exit(0)

    except (TimeoutException, NoSuchElementException, AssertionError, WebDriverException) as e:
        print(f"Test Case {TEST_CASE_ID} FAILED")
        print(f"Error: {e}")
        if driver:
            take_screenshot(driver, f"{TEST_CASE_ID}_FAILED.png")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during Test Case {TEST_CASE_ID}")
        print(f"Error: {e}")
        if driver:
            take_screenshot(driver, f"{TEST_CASE_ID}_UNEXPECTED_ERROR.png")
        sys.exit(1)
    finally:
        # Ensure the browser is closed
        if driver:
            driver.quit()
        # Clean up the temporary HTML file
        if os.path.exists(temp_html_file_path):
            os.remove(temp_html_file_path)
            print(f"Cleaned up temporary file: {TEMP_HTML_FILE}")

if __name__ == "__main__":
    run_test()
