document.addEventListener('DOMContentLoaded', function() {
    console.log('Cart script initialized');
    setupCart();
});

function setupCart() {
    setupDeleteButtons();
    setupQuantityButtons();
    setupSaveButtons();
}

function setupDeleteButtons() {
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', handleDeleteClick);
    });
}

function setupQuantityButtons() {
    document.querySelectorAll('.qty-btn').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const isIncrease = this.classList.contains('increase');
            updateQuantity(productId, isIncrease);
        });
    });
}

function setupSaveButtons() {
    document.querySelectorAll('.save-btn').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            saveForLater(productId);
        });
    });
}

function handleDeleteClick(event) {
    event.preventDefault();
    const button = event.currentTarget;
    const productId = button.dataset.productId;
    
    if (!productId) {
        console.error('Delete button missing product ID');
        return;
    }

    if (confirm('Are you sure you want to remove this item from your cart?')) {
        removeCartItem(productId);
    }
}

function removeCartItem(productId) {
    const url = `/cart/remove/${productId}/`;
    const csrfToken = getCSRFToken();
    
    if (!csrfToken) {
        alert('Security error. Please refresh the page.');
        return;
    }

    showLoading(true);
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(handleResponse)
    .then(data => {
        if (data.success) {
            animateRemoval(productId, () => {
                updateCartDisplay(data);
                if (data.item_count === 0) {
                    showEmptyCart();
                }
            });
        } else {
            throw new Error(data.error || 'Failed to remove item');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.message);
    })
    .finally(() => {
        showLoading(false);
    });
}

function animateRemoval(productId, callback) {
    const itemElement = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
    
    if (!itemElement) {
        console.error('Item element not found');
        return;
    }

    // Start removal animation
    itemElement.style.transition = 'all 0.3s ease';
    itemElement.style.opacity = '0';
    itemElement.style.height = `${itemElement.offsetHeight}px`;
    
    // Force reflow
    void itemElement.offsetHeight;
    
    // Complete animation
    itemElement.style.height = '0';
    itemElement.style.padding = '0';
    itemElement.style.margin = '0';
    itemElement.style.border = 'none';
    itemElement.style.overflow = 'hidden';
    
    setTimeout(() => {
        itemElement.remove();
        if (callback) callback();
    }, 300);
}

function updateCartDisplay(data) {
    // Update counters
    document.querySelectorAll('.cart-count, #summary-count').forEach(el => {
        el.textContent = data.item_count;
    });
    
    // Update totals
    document.getElementById('subtotal').textContent = data.subtotal.toFixed(2);
    document.getElementById('tax').textContent = data.tax.toFixed(2);
    document.getElementById('total').textContent = data.total.toFixed(2);
}

function showEmptyCart() {
    document.querySelector('.cart-content').innerHTML = `
        <div class="empty-cart">
            <img src="https://m.media-amazon.com/images/G/31/cart/empty/kettle-desaturated._CB424694257_.svg" alt="Empty cart">
            <h2>Your Cart is empty</h2>
            <a href="{% url 'product_list' %}" class="shop-btn">Shop now</a>
        </div>
    `;
}

function updateQuantity(productId, isIncrease) {
    const url = `/cart/update/${productId}/`;
    const csrfToken = getCSRFToken();
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: isIncrease ? 'increase' : 'decrease'
        })
    })
    .then(handleResponse)
    .then(data => {
        if (data.success) {
            updateItemQuantity(productId, data.new_quantity, data.item_total);
            updateCartDisplay(data);
        } else {
            throw new Error(data.error || 'Failed to update quantity');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.message);
    });
}

function updateItemQuantity(productId, quantity, total) {
    const itemElement = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
    if (itemElement) {
        itemElement.querySelector('.quantity').textContent = quantity;
        itemElement.querySelector('.item-total').textContent = total.toFixed(2);
    }
}

function saveForLater(productId) {
    const url = `/cart/save/${productId}/`;
    const csrfToken = getCSRFToken();
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(handleResponse)
    .then(data => {
        if (data.success) {
            alert('Item saved for later!');
            removeCartItem(productId);
        } else {
            throw new Error(data.error || 'Failed to save item');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.message);
    });
}

// Utility functions
function handleResponse(response) {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

function getCSRFToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) return csrfInput.value;
    
    const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
    return cookieMatch ? cookieMatch[1] : '';
}

function showLoading(show) {
    const loader = document.getElementById('loading-overlay') || createLoader();
    loader.style.display = show ? 'flex' : 'none';
}

function createLoader() {
    const loader = document.createElement('div');
    loader.id = 'loading-overlay';
    loader.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: none;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;
    loader.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(loader);
    return loader;
}