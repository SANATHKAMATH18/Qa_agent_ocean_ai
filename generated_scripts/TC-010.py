import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Test Case ID
TEST_CASE_ID = "TC-010"

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
html_file_name = "checkout.html"
with open(html_file_name, "w") as f:
    f.write(html_content)

# Get the absolute path to the HTML file
html_file_path = os.path.abspath(html_file_name)

driver = None
try:
    # Initialize Chrome WebDriver using ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window() # Maximize window for better visibility
    
    # Navigate to the local HTML file
    driver.get(f"file:///{html_file_path}")

    # Initialize WebDriverWait
    wait = WebDriverWait(driver, 10)

    print(f"Starting Test Case {TEST_CASE_ID}: Cart Summary Updates Instantly on Item Addition")

    # 1. Verify initial cart state
    # Wait for the total element to be visible and get its text
    initial_total_element = wait.until(EC.visibility_of_element_located((By.ID, "total")))
    assert initial_total_element.text == "0", f"Initial total expected '0', but found '{initial_total_element.text}'"
    print("Initial total is $0.00 as expected.")

    # Wait for the cart element to be visible and get its innerHTML
    initial_cart_element = wait.until(EC.visibility_of_element_located((By.ID, "cart")))
    assert initial_cart_element.get_attribute('innerHTML').strip() == "", "Initial cart should be empty"
    print("Initial cart is empty as expected.")

    # 2. Add Product A to cart
    # Find and click the "Add to Cart" button for Product A
    product_a_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='item']/span[contains(text(), 'Product A')]/following-sibling::button")))
    product_a_button.click()
    print("Clicked 'Add to Cart' for Product A.")

    # Verify cart summary updates instantly for Product A
    # Wait for the total to update to "50.00"
    wait.until(EC.text_to_be_present_in_element((By.ID, "total"), "50.00"))
    current_total = driver.find_element(By.ID, "total").text
    assert current_total == "50.00", f"Total expected '50.00' after adding Product A, but found '{current_total}'"
    print(f"Total updated to ${current_total} for Product A.")

    # Verify Product A is in the cart summary
    cart_content = driver.find_element(By.ID, "cart").get_attribute('innerHTML')
    assert "Product A - $50" in cart_content, f"Cart content does not contain 'Product A - $50'. Content: {cart_content}"
    print("Cart summary contains 'Product A - $50'.")

    # 3. Add Product B to cart
    # Find and click the "Add to Cart" button for Product B
    product_b_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='item']/span[contains(text(), 'Product B')]/following-sibling::button")))
    product_b_button.click()
    print("Clicked 'Add to Cart' for Product B.")

    # Verify cart summary updates instantly for Product B
    # Wait for the total to update to "80.00" (50 + 30)
    wait.until(EC.text_to_be_present_in_element((By.ID, "total"), "80.00"))
    current_total = driver.find_element(By.ID, "total").text
    assert current_total == "80.00", f"Total expected '80.00' after adding Product B, but found '{current_total}'"
    print(f"Total updated to ${current_total} for Product B.")

    # Verify Product B is also in the cart summary
    cart_content = driver.find_element(By.ID, "cart").get_attribute('innerHTML')
    assert "Product A - $50" in cart_content and "Product B - $30" in cart_content, \
        f"Cart content does not contain both 'Product A - $50' and 'Product B - $30'. Content: {cart_content}"
    print("Cart summary contains 'Product A - $50' and 'Product B - $30'.")

    # 4. Add Product C to cart
    # Find and click the "Add to Cart" button for Product C
    product_c_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='item']/span[contains(text(), 'Product C')]/following-sibling::button")))
    product_c_button.click()
    print("Clicked 'Add to Cart' for Product C.")

    # Verify cart summary updates instantly for Product C
    # Wait for the total to update to "100.00" (50 + 30 + 20)
    wait.until(EC.text_to_be_present_in_element((By.ID, "total"), "100.00"))
    current_total = driver.find_element(By.ID, "total").text
    assert current_total == "100.00", f"Total expected '100.00' after adding Product C, but found '{current_total}'"
    print(f"Total updated to ${current_total} for Product C.")

    # Verify Product C is also in the cart summary
    cart_content = driver.find_element(By.ID, "cart").get_attribute('innerHTML')
    assert "Product A - $50" in cart_content and "Product B - $30" in cart_content and "Product C - $20" in cart_content, \
        f"Cart content does not contain all products. Content: {cart_content}"
    print("Cart summary contains 'Product A - $50', 'Product B - $30', and 'Product C - $20'.")

    print(f"Test Case {TEST_CASE_ID} PASSED")
    sys.exit(0)

except Exception as e:
    print(f"Test Case {TEST_CASE_ID} FAILED")
    print(f"An error occurred: {e}")
    if driver:
        # Take a screenshot on failure
        screenshot_path = f"{TEST_CASE_ID}_FAILED.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    sys.exit(1)

finally:
    # Close the browser
    if driver:
        driver.quit()
    # Clean up the temporary HTML file
    if os.path.exists(html_file_name):
        os.remove(html_file_name)
