
function showSection(sectionId) {
  const sections = ["menuSection", "ordersSection", "createOrderSection"];

  sections.forEach((id) => {
    document.getElementById(id).classList.add("hidden");
  });

  document.getElementById(sectionId).classList.remove("hidden");

  if (sectionId === "menuSection") {
    loadMenu();
  }

  if (sectionId === "ordersSection") {
    loadOrders();
  }
}

async function loadMenu() {
  const menuContainer = document.getElementById("menu");
  menuContainer.innerHTML = "Chargement du menu...";

  try {
    const response = await fetch("/menu");

    if (!response.ok) {
      throw new Error("Erreur HTTP : " + response.status);
    }

    const data = await response.json();
    const menu = data.menu;

    menuContainer.innerHTML = "";

    Object.keys(menu).forEach((category) => {
      const card = document.createElement("div");
      card.className = "category-card";

      const title = document.createElement("h3");
      title.textContent = category;
      card.appendChild(title);

      menu[category].forEach((item) => {
        const row = document.createElement("div");
        row.className = "menu-item";

        row.innerHTML = `
          <span>${item.name}</span>
          <strong>${Number(item.price).toFixed(2)} €</strong>
        `;

        card.appendChild(row);
      });

      menuContainer.appendChild(card);
    });
  } catch (error) {
    menuContainer.innerHTML = "Erreur lors du chargement du menu.";
    console.error(error);
  }
}


async function loadOrders() {
  const ordersContainer = document.getElementById("orders");
  ordersContainer.innerHTML = "Chargement des commandes...";

  try {
    const response = await fetch("/orders");

    if (!response.ok) {
      throw new Error("Erreur HTTP : " + response.status);
    }

    const orders = await response.json();

    if (!orders || orders.length === 0) {
      ordersContainer.innerHTML = "Aucune commande pour le moment.";
      return;
    }

    ordersContainer.innerHTML = "";

    orders.forEach((order) => {
      const card = document.createElement("div");
      card.className = "order-card";

      card.innerHTML = `
        <h3>Commande #${order.id}</h3>
        <p><strong>Client numéro :</strong> ${order.customer_number}</p>
        <p><strong>Items :</strong> ${order.items.join(", ")}</p>
        <p><strong>Total :</strong> ${Number(order.total).toFixed(2)} €</p>
        <p><strong>Status :</strong> ${order.status}</p>
        <button onclick="deleteOrder(${order.id})">Supprimer</button>
      `;

      ordersContainer.appendChild(card);
    });
  } catch (error) {
    ordersContainer.innerHTML = "Erreur lors du chargement des commandes.";
    console.error(error);
  }
}


async function createOrder(event) {
  event.preventDefault();

  const customerNumberValue = document.getElementById("customerNumber").value;
  const itemsValue = document.getElementById("items").value;

  const customerNumber = Number(customerNumberValue);

  const items = itemsValue
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);

  if (!customerNumber || customerNumber <= 0) {
    alert("Veuillez entrer un numéro client valide.");
    return;
  }

  if (items.length === 0) {
    alert("Veuillez entrer au moins un plat.");
    return;
  }

  const order = {
    customer_number: customerNumber,
    items: items
  };

  try {
    const response = await fetch("/orders", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(order)
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      alert(data.message || "Erreur lors de la création de la commande.");
      return;
    }

    alert("Commande créée avec succès ! Total : " + Number(data.order.total).toFixed(2) + " €");

    document.getElementById("orderForm").reset();
    loadOrders();
  } catch (error) {
    alert("Erreur lors de la création de la commande.");
    console.error(error);
  }
}


async function deleteOrder(orderId) {
  const confirmation = confirm("Voulez-vous vraiment supprimer cette commande ?");

  if (!confirmation) {
    return;
  }

  try {
    const response = await fetch(`/orders/${orderId}`, {
      method: "DELETE"
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      alert(data.message || "Erreur lors de la suppression de la commande.");
      return;
    }

    alert("Commande supprimée avec succès.");
    loadOrders();
  } catch (error) {
    alert("Erreur lors de la suppression de la commande.");
    console.error(error);
  }
}


async function testCommunication() {
  const result = document.getElementById("communicationResult");
  result.textContent = "Test en cours...";

  try {
    const response = await fetch("/menu-from-service");

    if (!response.ok) {
      throw new Error("Erreur HTTP : " + response.status);
    }

    const data = await response.json();
    result.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    result.textContent = "Erreur lors du test de communication.";
    console.error(error);
  }
}


document.getElementById("orderForm").addEventListener("submit", createOrder);

loadMenu();
loadOrders();