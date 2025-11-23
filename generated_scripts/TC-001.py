import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# Test Case Definition
TEST_CASE = {
    "id": "TC-001",
    "title": "Validate form validation error display",
    "description": "Test that all form validation errors are displayed in red text when required fields are left empty.",
    "expected_result": "Validation errors are displayed in red text for all empty required fields.",
    "source_document": "checkout.html"
}

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

def setup_html_file(filename, content):
    """Creates a local HTML file for testing."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created local HTML file: {filename}")
        return os.path.abspath(filename)
    except IOError as e:
        print(f"Error creating HTML file {filename}: {e}")
        sys.exit(1)

def take_screenshot(driver, test_id):
    """Takes a screenshot and saves it with the test ID."""
    screenshot_name = f"{test_id}_failure.png"
    try:
        driver.save_screenshot(screenshot_name)
        print(f"Screenshot saved: {screenshot_name}")
    except WebDriverException as e:
        print(f"Could not take screenshot: {e}")

def run_test():
    """Executes the Selenium test case."""
    driver = None
    html_file_path = None
    test_id = TEST_CASE["id"]

    try:
        # 1. Setup local HTML file
        html_file_path = setup_html_file(TEST_CASE["source_document"], TARGET_HTML_CONTENT)
        file_url = f"file:///{html_file_path}"

        # 2. Initialize WebDriver
        # Use ChromeDriverManager to automatically download and manage the ChromeDriver
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        
        # 3. Navigate to the local HTML file
        driver.get(file_url)
        print(f"Navigated to: {file_url}")

        # Initialize WebDriverWait for explicit waits
        wait = WebDriverWait(driver, 10)

        # 4. Locate the "Pay Now" button
        pay_button = wait.until(EC.element_to_be_clickable((By.ID, "payBtn")))
        print("Found 'Pay Now' button.")

        # 5. Leave required fields empty and click "Pay Now"
        # The fields are already empty by default on page load
        pay_button.click()
        print("Clicked 'Pay Now' button with empty required fields.")

        # 6. Verify validation errors are displayed and in red text
        error_elements_data = [
            {"id": "nameError", "expected_text": "Name is required"},
            {"id": "emailError", "expected_text": "Email is required"},
            {"id": "addressError", "expected_text": "Address is required"}
        ]
        
        expected_color_rgb = "rgba(255, 0, 0, 1)" # Red color in RGBA format

        all_errors_valid = True
        for error_data in error_elements_data:
            error_id = error_data["id"]
            expected_text = error_data["expected_text"]
            
            try:
                # Wait for the error message to be visible
                error_element = wait.until(EC.visibility_of_element_located((By.ID, error_id)))
                print(f"Found error element: {error_id}")

                # Get the displayed text
                actual_text = error_element.text.strip()
                print(f"Actual text for {error_id}: '{actual_text}'")

                # Assert text content
                assert actual_text == expected_text, \
                    f"FAIL: Error message for {error_id} is incorrect. Expected '{expected_text}', got '{actual_text}'."
                print(f"PASS: Error message for {error_id} is correct: '{actual_text}'.")

                # Get the CSS color property
                actual_color = error_element.value_of_css_property("color")
                print(f"Actual color for {error_id}: '{actual_color}'")

                # Assert color is red
                assert actual_color == expected_color_rgb, \
                    f"FAIL: Error message color for {error_id} is incorrect. Expected '{expected_color_rgb}', got '{actual_color}'."
                print(f"PASS: Error message color for {error_id} is red.")

            except (TimeoutException, NoSuchElementException) as e:
                print(f"FAIL: Error element {error_id} not found or not visible: {e}")
                all_errors_valid = False
                break
            except AssertionError as e:
                print(e)
                all_errors_valid = False
                break
            except Exception as e:
                print(f"An unexpected error occurred while checking {error_id}: {e}")
                all_errors_valid = False
                break

        # Final assertion for the test case
        if all_errors_valid:
            print(f"Test Case {test_id} PASSED")
            sys.exit(0)
        else:
            print(f"Test Case {test_id} FAILED")
            take_screenshot(driver, test_id)
            sys.exit(1)

    except TimeoutException as e:
        print(f"Test Case {test_id} FAILED: Element not found or not interactive within the given time. Error: {e}")
        take_screenshot(driver, test_id)
        sys.exit(1)
    except NoSuchElementException as e:
        print(f"Test Case {test_id} FAILED: An element was not found. Error: {e}")
        take_screenshot(driver, test_id)
        sys.exit(1)
    except WebDriverException as e:
        print(f"Test Case {test_id} FAILED: A WebDriver specific error occurred. Error: {e}")
        take_screenshot(driver, test_id)
        sys.exit(1)
    except AssertionError as e:
        print(f"Test Case {test_id} FAILED: Assertion failed. Error: {e}")
        take_screenshot(driver, test_id)
        sys.exit(1)
    except Exception as e:
        print(f"Test Case {test_id} FAILED: An unexpected error occurred. Error: {e}")
        take_screenshot(driver, test_id)
        sys.exit(1)
    finally:
        if driver:
            driver.quit()
            print("WebDriver closed.")
        if html_file_path and os.path.exists(html_file_path):
            # Optionally, clean up the created HTML file
            # os.remove(html_file_path)
            # print(f"Cleaned up local HTML file: {html_file_path}")
            pass # Keeping the file for post-run inspection if needed

if __name__ == "__main__":
    run_test()
