import sys
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# CRITICAL: HTML content must be a raw string with triple quotes to avoid escape sequence warnings
HTML_CONTENT = r'''<!DOCTYPE html>
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
</html>'''

TEST_CASE_ID = "TC-011"
SCREENSHOT_DIR = "screenshots"

def take_screenshot(driver, test_id):
    """Takes a screenshot and saves it to the specified directory."""
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"{test_id}_failure.png")
    try:
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    except Exception as e:
        print(f"Failed to take screenshot: {e}")

def run_test():
    driver = None
    temp_html_file = None
    try:
        # 1. Setup temporary HTML file
        # Create a temporary file to host the HTML content for the browser
        temp_html_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
        temp_html_file.write(HTML_CONTENT)
        temp_html_file.close()
        file_path = 'file://' + os.path.abspath(temp_html_file.name)
        print(f"Temporary HTML file created at: {file_path}")

        # 2. Initialize WebDriver
        # Use ChromeDriverManager to automatically download and manage the ChromeDriver executable
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.maximize_window()
        print("WebDriver initialized.")

        # 3. Navigate to the local HTML file
        driver.get(file_path)
        print(f"Navigated to: {file_path}")

        # 4. Get initial cart total
        # Wait for the 'total' element to be visible and retrieve its initial text value
        total_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "total"))
        )
        initial_total_text = total_element.text
        initial_total = float(initial_total_text)
        print(f"Initial cart total: ${initial_total:.2f}")

        # Define the product to add and its expected price
        product_name_to_add = "Product A"
        product_price = 50.00
        expected_new_total = initial_total + product_price

        # 5. Locate and click the "Add to Cart" button for the specified product
        # Using XPath to find the button that is a sibling to the span containing the product name
        add_to_cart_button_xpath = f"//div[@class='item']/span[contains(text(), '{product_name_to_add}')]/following-sibling::button[contains(text(), 'Add to Cart')]"
        add_to_cart_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, add_to_cart_button_xpath))
        )
        print(f"Clicking 'Add to Cart' for {product_name_to_add}...")
        add_to_cart_button.click()

        # 6. Verify the cart summary updates instantly without a full page refresh
        # The JavaScript updates the total with toFixed(2), so we expect a string like "50.00"
        expected_total_string = f"{expected_new_total:.2f}"
        print(f"Waiting for cart total to update to: ${expected_total_string}")

        # Use explicit wait to ensure the text of the 'total' element changes to the expected value
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "total"), expected_total_string)
        )

        # Retrieve the updated total text and convert to float for assertion
        updated_total_text = total_element.text
        updated_total = float(updated_total_text)
        print(f"Updated cart total: ${updated_total:.2f}")

        # Assert that the updated total matches the expected value
        assert updated_total == expected_new_total, \
            f"Cart total did not update correctly. Expected ${expected_new_total:.2f}, but got ${updated_total:.2f}"

        print(f"Test Case {TEST_CASE_ID} PASSED: Cart summary updated instantly to ${updated_total:.2f} as expected.")
        sys.exit(0)

    except TimeoutException as e:
        print(f"Test Case {TEST_CASE_ID} FAILED: Timeout occurred while waiting for an element or condition - {e}")
        take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    except NoSuchElementException as e:
        print(f"Test Case {TEST_CASE_ID} FAILED: An expected element was not found on the page - {e}")
        take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    except AssertionError as e:
        print(f"Test Case {TEST_CASE_ID} FAILED: Assertion failed - {e}")
        take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    except WebDriverException as e:
        print(f"Test Case {TEST_CASE_ID} FAILED: A WebDriver specific error occurred (e.g., browser crash, connection issue) - {e}")
        take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    except Exception as e:
        print(f"Test Case {TEST_CASE_ID} FAILED: An unexpected error occurred - {e}")
        take_screenshot(driver, TEST_CASE_ID)
        sys.exit(1)
    finally:
        # 7. Cleanup
        # Close the browser if it was opened
        if driver:
            driver.quit()
            print("WebDriver closed.")
        # Remove the temporary HTML file
        if temp_html_file and os.path.exists(temp_html_file.name):
            os.remove(temp_html_file.name)
            print(f"Temporary HTML file removed: {temp_html_file.name}")

if __name__ == "__main__":
    run_test()
