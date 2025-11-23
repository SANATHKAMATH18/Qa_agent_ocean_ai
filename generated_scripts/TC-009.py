import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# Test Case Details
TEST_CASE_ID = "TC-009"
TEST_CASE_TITLE = "Select Standard Shipping Method"
TEST_CASE_DESCRIPTION = "As a user, I select 'Standard shipping' as my preferred shipping method during checkout."
EXPECTED_RESULT = "No additional cost is added to the total cart value for standard shipping (shipping cost remains $0)."

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

# File path for the temporary HTML file
HTML_FILE_NAME = "checkout_page.html"
SCREENSHOT_DIR = "screenshots"

def setup_driver():
    """Initializes and returns a Chrome WebDriver."""
    # Ensure the screenshot directory exists
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)

    # Setup Chrome options (optional, but good practice)
    chrome_options = webdriver.ChromeOptions()
    # Uncomment the line below to run in headless mode (without opening a browser UI)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080") # Set a default window size

    # Initialize Chrome driver using ChromeDriverManager
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def create_html_file(content, filename):
    """Creates a temporary HTML file."""
    with open(filename, "w") as f:
        f.write(content)
    return os.path.abspath(filename)

def cleanup_html_file(filename):
    """Deletes the temporary HTML file."""
    if os.path.exists(filename):
        os.remove(filename)

def take_screenshot(driver, test_id):
    """Takes a screenshot and saves it to the screenshots directory."""
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"{test_id}_failure.png")
    try:
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
    except Exception as e:
        print(f"Failed to take screenshot: {e}")

def run_test():
    driver = None
    html_file_path = None
    try:
        # 1. Create the HTML file
        html_file_path = create_html_file(TARGET_HTML_CONTENT, HTML_FILE_NAME)
        
        # 2. Setup WebDriver
        driver = setup_driver()
        # Explicit wait with a 10-second timeout
        wait = WebDriverWait(driver, 10) 

        # 3. Navigate to the local HTML file
        driver.get(f"file:///{html_file_path}")
        print(f"Navigated to: {driver.current_url}")

        # 4. Add a product to the cart to establish a base total
        print("Adding 'Product A' to cart...")
        add_to_cart_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='item']/span[contains(text(), 'Product A')]/following-sibling::button"))
        )
        add_to_cart_button.click()

        # 5. Get the initial total value after adding products
        total_element = wait.until(EC.visibility_of_element_located((By.ID, "total")))
        initial_total_str = total_element.text
        initial_total = float(initial_total_str)
        print(f"Initial cart total after adding Product A: ${initial_total:.2f}")

        # 6. Verify 'Standard shipping' radio button is selected by default
        standard_shipping_radio = wait.until(
            EC.presence_of_element_located((By.ID, "shipping-standard"))
        )
        
        if not standard_shipping_radio.is_selected():
            # If for some reason it's not selected, click it.
            # Based on HTML, it should be selected by default.
            print("Standard shipping not selected by default, clicking it now.")
            standard_shipping_radio.click()
            # Re-check if it's selected after clicking
            if not standard_shipping_radio.is_selected():
                raise AssertionError("Failed to select Standard shipping method after clicking.")
        else:
            print("Standard shipping method is selected by default.")

        # 7. Get the total value again after confirming shipping method
        # The JavaScript doesn't dynamically update the total based on shipping selection
        # unless express is chosen. For standard (free) shipping, the total should remain unchanged.
        final_total_str = total_element.text
        final_total = float(final_total_str)
        print(f"Final cart total after confirming standard shipping: ${final_total:.2f}")

        # 8. Assert that no additional cost is added for standard shipping
        assert final_total == initial_total, \
            f"Expected total to remain ${initial_total:.2f} for standard shipping, but got ${final_total:.2f}"
        print(f"Assertion Passed: Total remained ${final_total:.2f}, confirming standard shipping is free.")

        # Optional: Fill user details and attempt to pay to ensure full checkout flow
        # This is not strictly required by TC-009's assertion but validates page functionality.
        print("Filling user details for checkout completion...")
        wait.until(EC.presence_of_element_located((By.ID, "name"))).send_keys("John Doe")
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys("john.doe@example.com")
        wait.until(EC.presence_of_element_located((By.ID, "address"))).send_keys("123 Test St, Test City")

        pay_button = wait.until(EC.element_to_be_clickable((By.ID, "payBtn")))
        pay_button.click()

        # Verify payment success message appears
        success_message = wait.until(EC.visibility_of_element_located((By.ID, "success")))
        assert success_message.is_displayed(), "Payment success message did not appear."
        print("Payment successful message displayed.")

        print(f"Test Case {TEST_CASE_ID} PASSED")
        sys.exit(0)

    except Exception as e:
        print(f"Test Case {TEST_CASE_ID} FAILED")
        print(f"Error: {e}")
        if driver:
            take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)

    finally:
        # 9. Cleanup: Close the browser and delete the temporary HTML file
        if driver:
            driver.quit()
        if html_file_path:
            cleanup_html_file(HTML_FILE_NAME)

if __name__ == "__main__":
    run_test()
