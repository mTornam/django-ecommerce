document.addEventListener('DOMContentLoaded', function() {
    initCart();
});

function initCart() {
    const csrftoken = getCookie('csrftoken');
    // Add to cart buttons
    const addToCartBtns = document.querySelectorAll('button.add-to-cart, #add-to-cart-btn');
    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            handleAddToCart(this, csrftoken)
        });
    });
    // remove from cart buttons
    const removeBtns = document.querySelectorAll('.remove-btn');
    removeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            handleRemoveFromCart(this, csrftoken)
        })
    });
    // update cart forms
    document.querySelectorAll('.update-form').forEach(form => {
        const input = form.querySelector('input[name="quantity"]');
        const button = form.querySelector('button');
        const productId = form.dataset.productId;
        const initialValue = input.value;

        button.style.visibility = 'hidden';

        input.addEventListener('input', () => {
            button.style.visibility = (input.value !== initialValue) ? 'visible' : 'hidden';
        });

        form.addEventListener('submit', e => {
            e.preventDefault();
            handleUpdateCart(form, productId, csrftoken);
        });
    });
}

function handleAddToCart(button, csrftoken) {
    const form = button.closest('form');
    const productId = button.dataset.productId;
    let quantity = 1;
    let addUrl;

    if (form) {
        const inputQuantity = form.querySelector('input[name="quantity"]');

        if (inputQuantity) {
            quantity = parseInt(inputQuantity.value) || 1;
        } 
        addUrl = form.action

    } else {
        addUrl = button.dataset.url
    }

    addToCart(addUrl, productId, quantity, csrftoken);
}

function handleRemoveFromCart(button, csrftoken) {
    const removeUrl = button.dataset.url;
    const productId = button.dataset.productId;
    removeFromCart(removeUrl, productId, button, csrftoken)
}

function handleUpdateCart(form, productId, csrftoken) {
    const formData = new FormData(form);
    const quantity = formData.get('quantity');
    const url = form.url;

    updateCart(url, productId, quantity, csrftoken);
}


function addToCart(url, id, qty, csrftoken) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            'product_id': id,
            'quantity': qty
        })
    })
    .then(handleResponse)
    .then(data => {
        if (data.success) {
            updateCartCount(data.cart_count);
            console.log(data.message);
        } else {
            console.error('Failed to add item to cart');
        }
    })
    .catch(handleError);
}

function removeFromCart(url, id, btn, csrftoken) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            'product_id': id,
        })
    })
    .then(handleResponse)
    .then(data => {
        if (data.success) {
            updateCartCount(data.cart_count);
            updateCartList(btn, data.cart_total)
            console.log(data.message);
        } else {
            console.error('Failed to add item to cart');
        }
    })
    .catch(handleError);
}


function updateCart(url, productId, quantity, csrftoken) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ product_id: productId, quantity })
    })
    .then(handleResponse)
    .then(data => {
        if (data.success) {
            updateCartCount(data.cart_count);
            updateCartList(btn, data.cart_total)
            console.log(data.message);
        } else {
            console.error('Failed to add item to cart');
        }
    })
    .catch(handleError);
}




function updateCartCount(count) {
    const cartCount = document.getElementById('cart-count');
    if (cartCount) cartCount.textContent = count;
}

function updateCartList(btn, total) {
    const tableRow = btn.closest('tr');
    const cartTotal = document.getElementById('cart-total');

    if (total <= 0) {
        location.reload()
        return;
    }

    if (tableRow) tableRow.remove();
    if (cartTotal) cartTotal.textContent = total;
}

function handleResponse(response) {
    if (!response.ok) {
        throw new Error(`${response.status}: ${response.statusText}`);
    }
    return response.json();
}

function handleError(error) {
    console.error('Error: ', error.message )
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}