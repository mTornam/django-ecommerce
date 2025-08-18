document.addEventListener('DOMContentLoaded', ()=> {
    const qtyForms = document.querySelectorAll('#qty-form')

    qtyForms.forEach(form => {
        const quantity = form.querySelector('input[name="quantity"]')
        const updateBtn = form.querySelector('button[type="submit"]')

        const initialValue = quantity.value

        quantity.addEventListener('input', ()=> {
            if (quantity.value !== initialValue) {
                updateBtn.style.visibility = 'visible'
            } else {
                updateBtn.style.display = 'hidden'
            }
        })

    })
})

document.addEventListener('DOMContentLoaded', initCart);

function initCart() {
    // Update cart
    const updateBtns = document.querySelectorAll('button[type=["submit"]');
    updateBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            handleCartUpdate(this, csrftoken);
        });
    }); 
}

function  handleCartUpdate(button, csrftoken) {
    const quantityInput = button.closest('input[name="quantity"]');
    const form = button.closest('form')
    let updateUrl;

    if (form) {
        updateUrl = form.action
    }
    const quantity = parseInt(quantityInput.value)
    cartUpdate(updateUrl, quantity, button, csrftoken)
}

function cartUpdate(url, qty, csrftoken) {
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