document.addEventListener('DOMContentLoaded', init);

function init() {
    const updateCartForms = document.querySelectorAll('update-form');
    updateCartForms.forEach(form => {
        const inputQuantity = form.querySelector('input[name="quantity"]');
        const submitBtn = form.querySelector('button[type="submit"]');
        const productId = form.dataset.productId;

        const initialvalue = inputQuantity.value;
        submitBtn.style.visibility = 'hidden';

        inputQuantity.addEventListener('input', function() {
            submitBtn.style.visibility = (inputQuantity.value !== initialvalue) ? 'visible' : 'hidden';
        });

        form.addEventListener('submit', function(e) {
            e.preventDefault()
            handleUpdateCart(this, productId, csrftoken)
        });
    });
}

function handleUpdateCart(form, id, csrftoken) {
    const formData = new FormData(form);
    const quantity = formData.get('quantity');
    const updateUrl = form.action;

    updateCart(updateUrl, formData, csrftoken);
}

function updateCart(url, form, csrftoken) {
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest' 
        },
        body: formData
    })
    .then(handleResponse)
    .then(data => {
        if (data.success) {
            updateCartCount(data.cart_count);
            updateCartTotal(data.cart_total);
            
            // Reset the form state
            const quantityInput = form.querySelector('input[name="quantity"]');
            const updateBtn = form.querySelector('button[type="submit"]');
            quantityInput.dataset.initialValue = quantityInput.value;
            updateBtn.style.visibility = 'hidden';
        } else {
        }
    })
    .catch(handleError);
}
