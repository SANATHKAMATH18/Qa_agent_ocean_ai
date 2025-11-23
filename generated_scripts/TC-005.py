import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Define test case details
TEST_CASE_ID = "TC-005"
TEST_CASE_TITLE = "Verify Success Message Visibility After Payment"
EXPECTED_SUCCESS_MESSAGE = "Payment Successful!"

# --- Create a temporary HTML file for the test ---
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

HTML_FILE_NAME = "checkout.html"
SCREENSHOT_DIR = "screenshots"

def setup_driver():
    """Initializes and returns a Chrome WebDriver."""
    try:
        # Setup Chrome options (optional, but good for headless or specific settings)
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless") # Uncomment to run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Install and get the path to the ChromeDriver executable
        driver_path = ChromeDriverManager().install()
        
        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
        driver.maximize_window()
        return driver
    except WebDriverException as e:
        print(f"Error setting up WebDriver: {e}")
        sys.exit(1)

def create_html_file(content, filename):
    """Creates a local HTML file."""
    try:
        with open(filename, "w") as f:
            f.write(content)
        return os.path.abspath(filename)
    except IOError as e:
        print(f"Error creating HTML file {filename}: {e}")
        sys.exit(1)

def take_screenshot(driver, test_id):
    """Takes a screenshot and saves it to the screenshots directory."""
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"{test_id}_failure.png")
    try:
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    except Exception as e:
        print(f"Failed to take screenshot: {e}")

def run_test():
    """Executes the Selenium test case."""
    driver = None
    html_file_path = None
    try:
        # 1. Create the local HTML file
        html_file_path = create_html_file(HTML_CONTENT, HTML_FILE_NAME)
        
        # 2. Initialize WebDriver
        driver = setup_driver()
        
        # 3. Navigate to the local HTML file
        driver.get(f"file:///{html_file_path}")
        print(f"Navigated to: {driver.current_url}")

        # Set up WebDriverWait for explicit waits
        wait = WebDriverWait(driver, 10)

        # --- Test Case TC-005: Verify Success Message Visibility After Payment ---

        # Step 1: Add a product to the cart to ensure a non-zero total
        print("Adding 'Product A' to cart...")
        add_to_cart_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='item'][1]/button")),
            "Timed out waiting for 'Add to Cart' button for Product A"
        )
        add_to_cart_button.click()
        print("Product A added to cart.")

        # Step 2: Fill in user details
        print("Filling user details...")
        name_input = wait.until(EC.visibility_of_element_located((By.ID, "name")), "Timed out waiting for 'name' input")
        name_input.send_keys("John Doe")

        email_input = wait.until(EC.visibility_of_element_located((By.ID, "email")), "Timed out waiting for 'email' input")
        email_input.send_keys("john.doe@example.com")

        address_textarea = wait.until(EC.visibility_of_element_located((By.ID, "address")), "Timed out waiting for 'address' textarea")
        address_textarea.send_keys("123 Main St, Anytown, USA")
        print("User details filled.")

        # Step 3: Click the "Pay Now" button
        print("Clicking 'Pay Now' button...")
        pay_button = wait.until(
            EC.element_to_be_clickable((By.ID, "payBtn")),
            "Timed out waiting for 'Pay Now' button"
        )
        pay_button.click()
        print("'Pay Now' button clicked.")

        # Step 4: Verify the success message appears
        print(f"Waiting for success message: '{EXPECTED_SUCCESS_MESSAGE}'...")
        success_message_element = wait.until(
            EC.visibility_of_element_located((By.ID, "success")),
            f"Timed out waiting for success message with ID 'success' to be visible."
        )
        
        actual_success_message = success_message_element.text.strip()
        
        # Assertion
        assert actual_success_message == EXPECTED_SUCCESS_MESSAGE, \
            f"Expected success message '{EXPECTED_SUCCESS_MESSAGE}' but got '{actual_success_message}'"
        
        print(f"Success message found: '{actual_success_message}'")
        print(f"Test Case {TEST_CASE_ID} PASSED")
        sys.exit(0)

    except TimeoutException as e:
        print(f"Test Case {TEST_CASE_ID} FAILED: Element not found or not visible within the given time.")
        print(f"Error: {e}")
        if driver:
            take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    except NoSuchElementException as e:
        print(f"Test Case {TEST_CASE_ID} FAILED: An element was not found on the page.")
        print(f"Error: {e}")
        if driver:
            take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    except AssertionError as e:
        print(f"Test Case {TEST_CASE_ID} FAILED: Assertion failed.")
        print(f"Error: {e}")
        if driver:
            take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    except Exception as e:
        print(f"Test Case {TEST_CASE_ID} FAILED: An unexpected error occurred.")
        print(f"Error: {e}")
        if driver:
            take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    finally:
        # Clean up: close the browser and remove the temporary HTML file
        if driver:
            driver.quit()
            print("WebDriver closed.")
        if html_file_path and os.path.exists(html_file_path):
            os.remove(html_file_path)
            print(f"Temporary HTML file '{HTML_FILE_NAME}' removed.")

if __name__ == "__main__":
    run_test()
