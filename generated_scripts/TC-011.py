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
TEST_CASE_ID = "TC-011"
TEST_CASE_TITLE = "Verify Presence and Basic Interactivity of Input Fields"
HTML_FILE_NAME = "checkout_page.html"
SCREENSHOT_DIR = "screenshots"

# --- Target HTML File Content ---
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
    """Creates a local HTML file for testing."""
    with open(filename, "w") as f:
        f.write(content)
    return os.path.abspath(filename)

def setup_driver():
    """Initializes and returns a Chrome WebDriver."""
    # Set up Chrome options (optional, e.g., headless mode)
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless") # Uncomment to run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Use ChromeDriverManager to automatically download and manage the ChromeDriver
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    return driver

def take_screenshot(driver, test_id):
    """Takes a screenshot and saves it to the screenshots directory."""
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"{test_id}_failure.png")
    try:
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
    except WebDriverException as e:
        print(f"Failed to take screenshot: {e}")

def run_test():
    driver = None
    html_file_path = None
    try:
        # 1. Create the local HTML file
        html_file_path = create_html_file(HTML_FILE_NAME, HTML_CONTENT)
        print(f"Local HTML file created at: {html_file_path}")

        # 2. Initialize the WebDriver
        driver = setup_driver()
        
        # 3. Navigate to the local HTML file
        driver.get(f"file:///{html_file_path}")
        print(f"Navigated to: file:///{html_file_path}")

        # Set up WebDriverWait for explicit waits
        wait = WebDriverWait(driver, 10)

        print(f"\n--- Running Test Case: {TEST_CASE_ID} - {TEST_CASE_TITLE} ---")

        # --- Verify User Details Input Fields ---
        print("Verifying 'User Details' input fields:")
        
        # Full Name input (ID: name)
        name_input_locator = (By.ID, "name")
        name_input = wait.until(EC.visibility_of_element_located(name_input_locator),
                                f"'{name_input_locator[1]}' input field not visible.")
        assert name_input.is_enabled(), f"'{name_input_locator[1]}' input field is not enabled."
        test_name = "John Doe"
        name_input.send_keys(test_name)
        assert name_input.get_attribute("value") == test_name, f"Failed to enter text into '{name_input_locator[1]}'."
        print(f"  - Full Name input (ID: {name_input_locator[1]}) is present, enabled, and accepts input.")

        # Email input (ID: email)
        email_input_locator = (By.ID, "email")
        email_input = wait.until(EC.visibility_of_element_located(email_input_locator),
                                 f"'{email_input_locator[1]}' input field not visible.")
        assert email_input.is_enabled(), f"'{email_input_locator[1]}' input field is not enabled."
        test_email = "john.doe@example.com"
        email_input.send_keys(test_email)
        assert email_input.get_attribute("value") == test_email, f"Failed to enter text into '{email_input_locator[1]}'."
        print(f"  - Email input (ID: {email_input_locator[1]}) is present, enabled, and accepts input.")

        # Address textarea (ID: address)
        address_textarea_locator = (By.ID, "address")
        address_textarea = wait.until(EC.visibility_of_element_located(address_textarea_locator),
                                      f"'{address_textarea_locator[1]}' textarea not visible.")
        assert address_textarea.is_enabled(), f"'{address_textarea_locator[1]}' textarea is not enabled."
        test_address = "123 Main St, Anytown, USA"
        address_textarea.send_keys(test_address)
        assert address_textarea.get_attribute("value") == test_address, f"Failed to enter text into '{address_textarea_locator[1]}'."
        print(f"  - Address textarea (ID: {address_textarea_locator[1]}) is present, enabled, and accepts input.")

        # --- Verify Shipping Method Radio Buttons ---
        print("\nVerifying 'Shipping Method' radio buttons:")

        # Standard Shipping radio button (ID: shipping-standard)
        shipping_standard_locator = (By.ID, "shipping-standard")
        shipping_standard = wait.until(EC.visibility_of_element_located(shipping_standard_locator),
                                        f"'{shipping_standard_locator[1]}' radio button not visible.")
        assert shipping_standard.is_enabled(), f"'{shipping_standard_locator[1]}' radio button is not enabled."
        assert shipping_standard.is_selected(), f"'{shipping_standard_locator[1]}' radio button is not selected by default."
        print(f"  - Standard Shipping radio (ID: {shipping_standard_locator[1]}) is present, enabled, and selected by default.")

        # Express Shipping radio button (ID: shipping-express)
        shipping_express_locator = (By.ID, "shipping-express")
        shipping_express = wait.until(EC.visibility_of_element_located(shipping_express_locator),
                                      f"'{shipping_express_locator[1]}' radio button not visible.")
        assert shipping_express.is_enabled(), f"'{shipping_express_locator[1]}' radio button is not enabled."
        assert not shipping_express.is_selected(), f"'{shipping_express_locator[1]}' radio button is selected unexpectedly."
        
        # Click Express Shipping and verify selection change
        shipping_express.click()
        assert shipping_express.is_selected(), f"Failed to select '{shipping_express_locator[1]}' radio button."
        assert not shipping_standard.is_selected(), f"'{shipping_standard_locator[1]}' radio button is still selected after selecting Express."
        print(f"  - Express Shipping radio (ID: {shipping_express_locator[1]}) is present, enabled, and can be selected.")

        # --- Verify Payment Method Radio Buttons ---
        print("\nVerifying 'Payment Method' radio buttons:")

        # Credit Card radio button (ID: payment-card)
        payment_card_locator = (By.ID, "payment-card")
        payment_card = wait.until(EC.visibility_of_element_located(payment_card_locator),
                                  f"'{payment_card_locator[1]}' radio button not visible.")
        assert payment_card.is_enabled(), f"'{payment_card_locator[1]}' radio button is not enabled."
        assert payment_card.is_selected(), f"'{payment_card_locator[1]}' radio button is not selected by default."
        print(f"  - Credit Card radio (ID: {payment_card_locator[1]}) is present, enabled, and selected by default.")

        # PayPal radio button (ID: payment-paypal)
        payment_paypal_locator = (By.ID, "payment-paypal")
        payment_paypal = wait.until(EC.visibility_of_element_located(payment_paypal_locator),
                                    f"'{payment_paypal_locator[1]}' radio button not visible.")
        assert payment_paypal.is_enabled(), f"'{payment_paypal_locator[1]}' radio button is not enabled."
        assert not payment_paypal.is_selected(), f"'{payment_paypal_locator[1]}' radio button is selected unexpectedly."

        # Click PayPal and verify selection change
        payment_paypal.click()
        assert payment_paypal.is_selected(), f"Failed to select '{payment_paypal_locator[1]}' radio button."
        assert not payment_card.is_selected(), f"'{payment_card_locator[1]}' radio button is still selected after selecting PayPal."
        print(f"  - PayPal radio (ID: {payment_paypal_locator[1]}) is present, enabled, and can be selected.")

        # --- Verify Discount Code Input Field (as an example of another input field) ---
        print("\nVerifying 'Discount Code' input field:")
        discount_code_locator = (By.ID, "discountCode")
        discount_code_input = wait.until(EC.visibility_of_element_located(discount_code_locator),
                                         f"'{discount_code_locator[1]}' input field not visible.")
        assert discount_code_input.is_enabled(), f"'{discount_code_locator[1]}' input field is not enabled."
        test_discount = "TESTCODE"
        discount_code_input.send_keys(test_discount)
        assert discount_code_input.get_attribute("value") == test_discount, f"Failed to enter text into '{discount_code_locator[1]}'."
        print(f"  - Discount Code input (ID: {discount_code_locator[1]}) is present, enabled, and accepts input.")

        print(f"\nAll necessary input fields are present, clearly labeled, and allow user input/selection as expected.")
        print(f"Test Case {TEST_CASE_ID} PASSED")
        sys.exit(0)

    except (TimeoutException, NoSuchElementException, AssertionError) as e:
        print(f"\nTest Case {TEST_CASE_ID} FAILED: {e}")
        if driver:
            take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    except WebDriverException as e:
        print(f"\nTest Case {TEST_CASE_ID} FAILED due to WebDriver error: {e}")
        if driver:
            take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    except Exception as e:
        print(f"\nTest Case {TEST_CASE_ID} FAILED due to unexpected error: {e}")
        if driver:
            take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    finally:
        # Cleanup: Quit the driver and remove the temporary HTML file
        if driver:
            driver.quit()
            print("WebDriver quit.")
        if html_file_path and os.path.exists(html_file_path):
            os.remove(html_file_path)
            print(f"Removed temporary HTML file: {html_file_path}")

if __name__ == "__main__":
    run_test()