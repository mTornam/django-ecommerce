document.addEventListener("DOMContentLoaded", function () {
  //init
  const csrftoken = getCookie("csrftoken");
  const cartCount = document.getElementById("cart-count");
  const addToCartBtns = document.querySelectorAll(".add-to-cart"); //add to cart btns
  const updateCartBtns = document.querySelectorAll(".updateCartBtn"); //update cart btns
  const cartTotal = document.getElementById("cart-total") //cart Total
  const removeBtns = document.querySelectorAll(".remove-btn");

  //add to cart
  addToCartBtns.forEach((button) => {
    const productId = button.dataset.productId;
    let quantity, addUrl;

    // check if product detail view form situation
    if (button.name === "update") {
      const form = button.closest("form");
      quantity = parseInt(form.querySelector('input[name="quantity"]').value);
      addUrl = form.action;
    } else {
      quantity = 1;
      addUrl = button.dataset.url;
    }

    button.addEventListener("click", function (e) {
      fetch(addUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
          product_id: productId,
          quantity: quantity,
        }),
      })
        .then(handleResponse)
        .then((data) => {
          if (data.success) {
            let msgData = {
              type: data.type,
              msg: data.message
            }
            updateMessages(msgData)
            console.log(msgData);
            
            cartCount.textContent = data.cart_count;
          } else {
            console.error("Error: ", data.message);
          }
        })
        .catch((error) => {
          console.error(error.message);
        });
    });
  });
  //update cart
  updateCartBtns.forEach((button) => {
    const updateForm = button.closest(".update-form");
    const productId = updateForm.dataset.productId;
    const updateUrl = updateForm.action;
    const inputQuantity = updateForm.querySelector('input[name="quantity"]');
    const productTotal = updateForm.closest("tr").querySelector(".total-price");
    let initialValue = inputQuantity.value;

    button.style.visibility = "hidden";

    inputQuantity.addEventListener("input", function () {
      button.style.visibility =
        initialValue !== inputQuantity.value ? "visible" : "hidden";
    });

    updateForm.addEventListener("submit", function (e) {
      e.preventDefault();
      fetch(updateUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
          product_id: productId,
          quantity: parseInt(inputQuantity.value),
        }),
      })
        .then(handleResponse)
        .then((data) => {
          if (data.success) {
            cartCount.textContent = data.cart_count;
            initialValue = inputQuantity.value;
            button.style.visibility = "hidden";
            productTotal.textContent = formatted(data.product_total);
            cartTotal.textContent = formatted(data.cart_total);
            console.log(cartTotal.textContent);

          } else {
            console.error("Error: ", data.message);
          }
        })
        .catch((error) => {
          console.error(error.message);
        });
    });
  });
  //remove from cart
  removeBtns.forEach(button => {
    const tableRow = button.closest('tr');
    const productId = button.dataset.productId;
    const removeUrl = button.dataset.url;

    button.addEventListener('click', function (e) {
      e.preventDefault();
      fetch(removeUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
          product_id: productId,
        }),
      })
        .then(handleResponse)
        .then((data) => {
          if (data.success) {
            cartCount.textContent = data.cart_count;
            cartTotal.textContent = formatted(data.cart_total);
            if (data.cart_total <= 0) location.reload();
            else tableRow.remove()
          } else {
            console.error("Error: ", data.message);
          }
        })
        .catch((error) => {
          console.error(error.message);
        });

    })
  });
});

function handleResponse(response) {
  if (!response.ok) {
    throw new Error(`${response.status}: ${response.statusText}`);
  }
  return response.json();
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function formatted(amount) {
  return amount.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

function updateMessages(msgData) {
  const messages = document.getElementById('messages')
  console.log(messages);
  
  if (msgData.type) {
    let alert = `
      <div class="alert alert-${msgData.type} alert-dismissible fade show rounded-0" role="alert">
      ${msgData.msg}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `;
    messages.insertAdjacentHTML("afterbegin", alert)
    
  }
}