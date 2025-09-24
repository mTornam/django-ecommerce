let cartCache = null
const container = document.getElementById('cart-items')
const sideCart = document.getElementById('side-cart')
const clearBtn = document.getElementById('clear-cart')
const clearBtnDiv = clearBtn.parentElement
const cartCount = document.getElementById('cart-count')

function toggleSideCart() {
  sideCart.classList.toggle('open')
  document.querySelector('body').classList.toggle('no-scroll', sideCart.classList.contains('open'))
}


async function getCart(refresh=false) {
    if (cartCache && !refresh) {
        return cartCache
    }

    const response = await fetch('http://127.0.0.1:8000/api/carts/')
    const data = await response.json()

    cartCache = data
    cartCount.textContent = cartCache.count
    renderCart()
    return cartCache
}

async function addToCart(product, quantity) {
    await fetch('http://127.0.0.1:8000/api/carts/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({product, quantity})
    });
    await getCart(true)
}

async function updateCartItem(product_id, quantity) {
    await fetch(`http://127.0.0.1:8000/api/carts/items/${product_id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({quantity})
    });
    await getCart(true)
}

async function removeCartItem(product_id) {
    await fetch(`http://127.0.0.1:8000/api/carts/items/${product_id}`, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'}
    });
    await getCart(true)
}

async function clearCart() {
    await fetch('http://127.0.0.1:8000/api/carts/', {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'}
    })
    await getCart(true)
}

function renderCart() {
    let template
    let clone
    const summaryTotal = document.querySelector('#cart-summary .total')
    const checkoutBtn = document.getElementById('checkout-btn')
    

    container.innerHTML = '' // clear container
    if (cartCache.items && cartCache.items.length > 0) {
        template = document.getElementById('cart-item-template')
        cartCache.items.forEach(item => {
            clone = template.content.cloneNode(true)            
            clone.querySelector('.p-name').textContent = item.product_name
            clone.querySelector('.p-qty').textContent = `x${item.quantity}`
            clone.querySelector('.p-price').textContent = `$${item.subtotal.toFixed(2)}`
            clone.querySelector('.bt-hr').setAttribute('data-id', item.id) 

            container.appendChild(clone)
        });

        clearBtnDiv.querySelector('#count').textContent = cartCache.count
        clearBtnDiv.classList.remove('d-none')
        summaryTotal.textContent = `$${cartCache.total.toFixed(2)}`
        checkoutBtn.classList.remove('disabled')
    } else {
        template = document.getElementById('empty-cart-template')
        clone = template.content.cloneNode(true)
        
        container.appendChild(clone)
        clearBtnDiv.classList.add('d-none')
        summaryTotal.textContent = '$0.00'
        checkoutBtn.classList.add('disabled')
    }
}

document.querySelectorAll('.add-to-cart').forEach(btn=> {
    btn.addEventListener("click", (e)=> {
        e.preventDefault()
        const product_id = parseInt(btn.getAttribute('data-product-id'))
        const qtyInput = btn.closest('div').querySelector('input[name="quantity"]')
        const qty = qtyInput ? parseInt(qtyInput.value) : 1

        addToCart(product_id, qty)
    })
})

container.addEventListener("click", (e)=> {
    if (e.target.classList.contains('delete-btn')) {
        const product_id = e.target.closest('.bt-hr').getAttribute('data-id')
        removeCartItem(product_id)
    }
})

clearBtn.addEventListener("click", (e)=> {
    e.preventDefault()
    clearCart()
})

getCart()