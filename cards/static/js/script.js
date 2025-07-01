// Mobile menu toggle


// Back to top button
const backToTopButton = document.getElementById('back-to-top');
window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
        backToTopButton.classList.add('show');
    } else {
        backToTopButton.classList.remove('show');
    }
});

backToTopButton.addEventListener('click', function(e) {
    e.preventDefault();
    window.scrollTo({top: 0, behavior: 'smooth'});
});

// Product image zoom
document.querySelectorAll('.product-image img').forEach(image => {
    image.addEventListener('click', function() {
        this.classList.toggle('zoomed');
    });
});

// Countdown timer for deals
function updateDealTimer() {
    const now = new Date();
    const endOfDay = new Date();
    endOfDay.setHours(23, 59, 59, 999);
    
    const diff = endOfDay - now;
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    document.getElementById('hours').textContent = hours.toString().padStart(2, '0');
    document.getElementById('minutes').textContent = minutes.toString().padStart(2, '0');
    document.getElementById('seconds').textContent = seconds.toString().padStart(2, '0');
}

setInterval(updateDealTimer, 1000);

// Image slider for deals
let currentSlide = 0;
const slides = document.querySelectorAll('.slider-container img');

function showSlide(n) {
    slides.forEach(slide => slide.classList.remove('active'));
    currentSlide = (n + slides.length) % slides.length;
    slides[currentSlide].classList.add('active');
}

function nextSlide() {
    showSlide(currentSlide + 1);
}

// Auto slide every 5 seconds
setInterval(nextSlide, 5000);

// Cart quantity adjustments
document.querySelectorAll('.quantity-btn').forEach(button => {
    button.addEventListener('click', function() {
        const input = this.parentElement.querySelector('.quantity-input');
        let value = parseInt(input.value);
        
        if (this.classList.contains('minus') && value > 1) {
            input.value = value - 1;
        } else if (this.classList.contains('plus')) {
            input.value = value + 1;
        }
    });
});

// Product rating stars
document.querySelectorAll('.rating i').forEach(star => {
    star.addEventListener('click', function() {
        const rating = this.getAttribute('data-value');
        const container = this.parentElement;
        
        container.querySelectorAll('i').forEach((s, index) => {
            if (index < rating) {
                s.classList.add('fas');
                s.classList.remove('far');
            } else {
                s.classList.add('far');
                s.classList.remove('fas');
            }
        });
        
        // In a real app, you would send this to the server
        console.log(`Rated ${rating} stars`);
    });
});

// Quick view functionality
document.querySelectorAll('.quick-view').forEach(button => {
    button.addEventListener('click', function() {
        const productId = this.dataset.productId;
        // Implement your quick view modal logic here
        console.log('Quick view for product:', productId);
    });
});


document.addEventListener('DOMContentLoaded', function() {
    // Add to Cart functionality
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const csrfToken = this.dataset.csrfToken;
            
            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update cart count in navbar or show success message
                    const cartCountElements = document.querySelectorAll('.cart-count');
                    cartCountElements.forEach(el => {
                        el.textContent = data.cart_count;
                    });
                    
                    // Show success notification
                    showNotification('Item added to cart!', 'success');
                }
            })
            .catch(error => {
                showNotification('Error adding item to cart', 'error');
                console.error('Error:', error);
            });
        });
    });

    // Buy Now functionality
    document.querySelectorAll('.buy-now').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const csrfToken = this.dataset.csrfToken;
            
            // First add to cart
            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Then redirect to checkout
                    window.location.href = '/checkout/';
                }
            })
            .catch(error => {
                showNotification('Error processing your request', 'error');
                console.error('Error:', error);
            });
        });
    });

    // Notification function
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
});

document.querySelector('.buy-now').addEventListener('click', function() {
    const productId = this.dataset.productId;
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/checkout/';
        }
    })
    .catch(error => console.error('Error:', error));
});