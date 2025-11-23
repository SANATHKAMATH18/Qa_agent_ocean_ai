import sys
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Test Case Details
TC_ID = "TC-006"
TC_TITLE = "Apply Discount Code SAVE15 Successfully"
DISCOUNT_CODE = "SAVE15"
EXPECTED_DISCOUNT_PERCENTAGE = 0.15 # 15% discount

# Target HTML content
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

driver = None
temp_file = None

try:
    # 1. Create a temporary HTML file to serve as the target page
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".html", encoding='utf-8')
    temp_file.write(html_content)
    temp_file.close()
    file_path = 'file://' + os.path.abspath(temp_file.name)

    # 2. Initialize WebDriver using ChromeDriverManager for automatic driver management
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    # Set up explicit wait with a 10-second timeout
    wait = WebDriverWait(driver, 10) 

    # 3. Navigate to the local HTML file
    driver.get(file_path)
    print(f"Navigated to: {file_path}")

    # 4. Add items to the cart to establish a total value for discount application
    # Find and click "Add to Cart" button for Product A ($50)
    product_a_add_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='item'][span[contains(text(), 'Product A')]]/button"))
    )
    product_a_add_button.click()
    print("Added Product A to cart.")

    # Find and click "Add to Cart" button for Product B ($30)
    product_b_add_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='item'][span[contains(text(), 'Product B')]]/button"))
    )
    product_b_add_button.click()
    print("Added Product B to cart.")

    # 5. Get the initial total before applying the discount
    total_element = wait.until(EC.visibility_of_element_located((By.ID, "total")))
    initial_total_text = total_element.text
    initial_total = float(initial_total_text)
    print(f"Initial cart total: ${initial_total:.2f}")

    # Calculate the expected total after applying the 15% discount
    expected_total_after_discount = initial_total * (1 - EXPECTED_DISCOUNT_PERCENTAGE)
    print(f"Expected total after '{DISCOUNT_CODE}' ({EXPECTED_DISCOUNT_PERCENTAGE*100}% off): ${expected_total_after_discount:.2f}")

    # 6. Locate the discount code input field and enter the discount code
    discount_code_input = wait.until(EC.visibility_of_element_located((By.ID, "discountCode")))
    discount_code_input.send_keys(DISCOUNT_CODE)
    print(f"Entered discount code: '{DISCOUNT_CODE}'")

    # 7. Locate and click the "Apply" button next to the discount code input
    apply_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@id='discountCode']/following-sibling::button[text()='Apply']"))
    )
    apply_button.click()
    print("Clicked 'Apply' button.")

    # 8. Verify the discount message displayed
    discount_message_element = wait.until(EC.visibility_of_element_located((By.ID, "discountMessage")))
    actual_discount_message = discount_message_element.text
    expected_discount_message = "Discount applied!"
    assert actual_discount_message == expected_discount_message, \
        f"Assertion Failed: Expected discount message '{expected_discount_message}', but got '{actual_discount_message}'"
    print(f"Verified discount message: '{actual_discount_message}'")

    # 9. Verify the total cart value has been updated correctly
    # Wait for the total element's text to change from the initial total, indicating an update
    wait.until(lambda driver: float(driver.find_element(By.ID("total")).text) != initial_total)
    
    final_total_text = total_element.text
    final_total = float(final_total_text)
    print(f"Final cart total after discount: ${final_total:.2f}")

    # Assert that the final total matches the calculated expected discounted total
    # Rounding to 2 decimal places for accurate currency comparison
    assert round(final_total, 2) == round(expected_total_after_discount, 2), \
        f"Assertion Failed: Expected final total to be ${expected_total_after_discount:.2f}, but got ${final_total:.2f}"
    
    print(f"Test Case {TC_ID} PASSED")
    sys.exit(0)

except Exception as e:
    print(f"Test Case {TC_ID} FAILED")
    print(f"An error occurred: {e}")
    if driver:
        # Take a screenshot on failure
        screenshot_name = f"{TC_ID}_FAILED_screenshot.png"
        driver.save_screenshot(screenshot_name)
        print(f"Screenshot saved as {screenshot_name}")
    sys.exit(1)

finally:
    # 10. Clean up: Close the browser and delete the temporary HTML file
    if driver:
        driver.quit()
    if temp_file and os.path.exists(temp_file.name):
        os.remove(temp_file.name)
        print(f"Cleaned up temporary file: {temp_file.name}")
