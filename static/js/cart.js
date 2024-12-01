/**
 * Updates the cart count displayed in the navbar
 * @param {number} count - The updated cart item count
 */
function updateCartCount(count) {
    const cartCountElement = document.getElementById('cart');
    if (cartCountElement) {
        cartCountElement.textContent = count;
    } else {
        console.error("Navbar cart count element not found.");
    }
}

/**
 * Fetches the cart data from localStorage and updates the navbar cart count
 */
function fetchAndUpdateCartCount() {
    const cartDataRaw = localStorage.getItem('cart');
    console.log('Raw Cart Data:', cartDataRaw); // Debugging

    const cartData = JSON.parse(cartDataRaw || '[]');
    console.log('Parsed Cart Data:', cartData); // Debugging

    if (Array.isArray(cartData)) {
        const totalCount = cartData.reduce((count, item) => count + (item.quantity || 0), 0);
        console.log('Total Count:', totalCount); // Debugging
        updateCartCount(totalCount);
    } else {
        console.error('Cart data is not an array:', cartData);
        updateCartCount(); // Reset count if invalid data
    }
}

/**
 * Initializes the cart count update process
 */
function initCartCount() {
    fetchAndUpdateCartCount(); // Update on page load
}

updateCartCount();
// Call the initializer function on DOMContentLoaded
document.addEventListener("DOMContentLoaded", initCartCount);
