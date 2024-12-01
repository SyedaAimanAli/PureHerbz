<script>
console.log('Cart script is active');

// Load cart data from localStorage or initialize an empty cart
let cart = JSON.parse(localStorage.getItem('cart')) || {};

// Asynchronous function to fetch product details
async function getProductById(productId) {
  try {
    const response = await fetch(`/getproductname/?id=${productId}`);
    if (!response.ok) throw new Error(`Error: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch product data:', error);
    return null;
  }
}

// Save cart data back to localStorage
function saveCartData() {
  localStorage.setItem('cart', JSON.stringify(cart));
}

// Update cart count on the UI
function updateCartCount() {
  const totalCount = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
  const cartCountElement = document.getElementById('cart-count');
  if (cartCountElement) cartCountElement.innerText = totalCount;
}

// Render cart items in the cart table
async function renderCartItems() {
  const cartTableBody = document.querySelector('table.table tbody');
  if (!cartTableBody) return;

  cartTableBody.innerHTML = ''; // Clear table
  let grandTotal = 0;

  for (const [productId, item] of Object.entries(cart)) {
    const productData = await getProductById(productId);
    if (!productData) continue;

    const { productName, price, imageUrl } = productData;
    const quantity = item.quantity;
    const total = price * quantity;
    grandTotal += total;

    // Create a row for the item
    const row = document.createElement('tr');
    row.className = 'text-center';
    row.innerHTML = `
      <td class="product-remove">
        <a href="#" data-id="${productId}" class="remove-item"><span class="ion-ios-close"></span></a>
      </td>
      <td class="image-prod">
        <div class="img" style="background-image: url(${imageUrl});"></div>
      </td>
      <td class="product-name"><h3>${productName}</h3></td>
      <td class="price">$${price.toFixed(2)}</td>
      <td class="quantity">
        <div class="input-group mb-3">
          <button class="btn minus" data-id="${productId}" style="width: 30px;">-</button>
          <input type="text" class="form-control input-number" value="${quantity}" readonly>
          <button class="btn plus" data-id="${productId}" style="width: 30px;">+</button>
        </div>
      </td>
      <td class="total">$${total.toFixed(2)}</td>
    `;
    cartTableBody.appendChild(row);
  }

  // Update grand total in the UI
  const totalPriceElement = document.querySelector('.total-price span:last-child');
  if (totalPriceElement) totalPriceElement.innerText = `$${grandTotal.toFixed(2)}`;

  attachEventListeners();
}

// Attach event listeners for cart actions
function attachEventListeners() {
  const cartTable = document.querySelector('table.table');

  if (cartTable) {
    cartTable.addEventListener('click', (event) => {
      const target = event.target.closest('button, a');
      if (!target) return;

      const productId = target.dataset.id;

      if (target.classList.contains('plus')) {
        cart[productId].quantity += 1;
      } else if (target.classList.contains('minus')) {
        cart[productId].quantity = Math.max(0, cart[productId].quantity - 1);
        if (cart[productId].quantity === 0) delete cart[productId];
      } else if (target.classList.contains('remove-item')) {
        event.preventDefault();
        delete cart[productId];
      }

      saveCartData();
      renderCartItems();
      updateCartCount();
    });
  }
}

// Initialize the cart on page load
updateCartCount();
renderCartItems();

</script>







{% comment %} <script>
	
  console.log('Cart script is working');

// Load the cart data from localStorage or initialize an empty cart
var cart = JSON.parse(localStorage.getItem('cart')) || {};

// Function to fetch product details by ID (using AJAX)
function getProductById(productId) {
  var productData = {};
  $.ajax({
    url: '/get-cart-items/',
    method: 'GET',
    data: { id: productId },
    async: false,
    success: function (data) {
      console.log('Product data:', data); // Debugging
      productData = data;
    },
    error: function (xhr, status, error) {
      console.error('Error fetching product data:', error);
    }
  });
  return productData;
}

updateCartCount();


// Function to render cart items in the table
function renderCartItems() {
  var cartTableBody = document.querySelector('table.table tbody');
  var grandTotal = 0;
  cartTableBody.innerHTML = ''; // Clear existing rows

  for (var item in cart) {
    var productId = item.replace('pr', '');
    var productData = getProductById(productId);
    var productName = productData.productName;
    var price = productData.price;
    var quantity = cart[item];
    var imageUrl = productData.imageUrl;
    var total = price * quantity;
    grandTotal += total;

    // Create a new row for the cart item
    var row = document.createElement('tr');
    row.className = 'text-center';
    row.innerHTML = `
      <td class="product-remove">
        <a href="#" data-id="${productId}" class="remove-item"><span class="ion-ios-close"></span></a>
      </td>
      <td class="image-prod">
        <div class="img" style="background-image:url(${imageUrl});"></div>
      </td>
      <td class="product-name">
        <h3>${productName}</h3>
      </td>
      <td class="price">$${price}</td>
      <td class="quantity">
		<div class="input-group mb-3">
			<button class="btn minus " data-id="${productId}" style="width: 30px; border: 1px solid #349a35">-</button>
			<input type="text" class="quantity form-control input-number" value="${quantity}" readonly>
			<button class="btn plus " data-id="${productId}" style="width: 30px;">+</button>
		</div>
		</td>
      <td class="total">$${total.toFixed(2)}</td>
    `;

    cartTableBody.appendChild(row);
  }

  // Update the grand total
  document.querySelector('.total-price span:last-child').innerText = `$${grandTotal.toFixed(2)}`;

  // Attach event listeners to quantity buttons and remove buttons
  attachEventListeners();
}

// Function to attach event listeners to dynamically created elements
function attachEventListeners() {
  // Quantity increment buttons
  document.querySelectorAll('.plus').forEach(button => {
    button.addEventListener('click', function () {
      var productId = this.dataset.id;
      cart['pr' + productId] = (cart['pr' + productId] || 0) + 1;
	  updateCartCount();
      saveCartData();
      renderCartItems();
    });
  });

  // Quantity decrement buttons
  document.querySelectorAll('.minus').forEach(button => {
    button.addEventListener('click', function () {
      var productId = this.dataset.id;
      cart['pr' + productId] = Math.max(0, (cart['pr' + productId] || 0) - 1);
      if (cart['pr' + productId] === 0) delete cart['pr' + productId];
	  updateCartCount();
      saveCartData();
      renderCartItems();
    });
  });

  // Remove item buttons
  document.querySelectorAll('.remove-item').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      var productId = this.dataset.id;
      delete cart['pr' + productId];
	  updateCartCount();
      saveCartData();
      renderCartItems();
    });
  });
}

function updateCartCount() {
  var totalCount = 0;
  for (var item in cart) {
    totalCount += cart[item];
  }
  document.getElementById('cart').innerHTML = totalCount;
}

// Function to save cart data to localStorage
function saveCartData() {
  localStorage.setItem('cart', JSON.stringify(cart));
}

// Initial rendering of cart items
renderCartItems();

</script> {% endcomment %}
