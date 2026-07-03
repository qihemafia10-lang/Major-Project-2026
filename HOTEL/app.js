// app.js
// -------
// Frontend Controller for Grand Horizon Hotel Management System.
// Stores all data in localStorage for persistence.

// ───────────── CORE APP STATE ─────────────
const AppState = {
  rooms: [],
  customers: [],
  bookings: [],
  currentUser: null
};

// ───────────── SEED DATA ─────────────
const DefaultRooms = [
  { room_id: 1, room_number: "101", room_type: "Single", price: 1500, status: "Available" },
  { room_id: 2, room_number: "102", room_type: "Single", price: 1500, status: "Available" },
  { room_id: 3, room_number: "201", room_type: "Double", price: 2500, status: "Available" },
  { room_id: 4, room_number: "202", room_type: "Double", price: 2500, status: "Booked" },
  { room_id: 5, room_number: "301", room_type: "Suite", price: 5000, status: "Available" },
  { room_id: 6, room_number: "302", room_type: "Deluxe", price: 7500, status: "Available" },
  { room_id: 7, room_number: "401", room_type: "Penthouse", price: 15000, status: "Available" }
];

const DefaultCustomers = [
  { customer_id: 1, name: "Arjun Sharma", phone: "9876543210", email: "arjun@email.com", address: "Mumbai", id_proof: "Aadhar: 1234-5678-9012" },
  { customer_id: 2, name: "Priya Patel", phone: "8765432109", email: "priya@email.com", address: "Delhi", id_proof: "Passport: Z1234567" },
  { customer_id: 3, name: "Rahul Verma", phone: "7654321098", email: "rahul@email.com", address: "Bangalore", id_proof: "DL: KA-03-2022" }
];

const DefaultBookings = [
  { booking_id: 1, customer_id: 2, room_id: 4, check_in: "2026-07-01", check_out: "2026-07-05", total_days: 4, bill_amount: 10000, booking_status: "Checked-In" }
];

// ───────────── INITIALIZATION ─────────────
function initData() {
  if (!localStorage.getItem("hms_rooms")) {
    localStorage.setItem("hms_rooms", JSON.stringify(DefaultRooms));
  }
  if (!localStorage.getItem("hms_customers")) {
    localStorage.setItem("hms_customers", JSON.stringify(DefaultCustomers));
  }
  if (!localStorage.getItem("hms_bookings")) {
    localStorage.setItem("hms_bookings", JSON.stringify(DefaultBookings));
  }
  
  AppState.rooms = JSON.parse(localStorage.getItem("hms_rooms"));
  AppState.customers = JSON.parse(localStorage.getItem("hms_customers"));
  AppState.bookings = JSON.parse(localStorage.getItem("hms_bookings"));
  
  const user = sessionStorage.getItem("hms_user");
  if (user) {
    AppState.currentUser = user;
    showMainApp();
  }
}

function saveData(key) {
  localStorage.setItem(`hms_${key}`, JSON.stringify(AppState[key]));
}

// ───────────── TOAST NOTIFICATION ─────────────
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  toast.className = `toast toast-${type}`;
  toast.innerText = message;
  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.add("hidden");
  }, 3000);
}

// ───────────── LOGIN & NAVIGATION ─────────────
document.getElementById("login-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const user = document.getElementById("login-username").value.trim();
  const pass = document.getElementById("login-password").value;
  
  if (user === "admin" && pass === "admin123") {
    AppState.currentUser = user;
    sessionStorage.setItem("hms_user", user);
    document.getElementById("login-error").classList.add("hidden");
    showToast("Login successful!", "success");
    showMainApp();
  } else {
    document.getElementById("login-error").classList.remove("hidden");
    showToast("Invalid credentials", "error");
  }
});

document.getElementById("logout-btn").addEventListener("click", () => {
  AppState.currentUser = null;
  sessionStorage.removeItem("hms_user");
  document.getElementById("app").classList.add("hidden");
  document.getElementById("login-screen").classList.remove("hidden");
  document.getElementById("login-screen").classList.add("active");
  document.getElementById("login-form").reset();
  showToast("Logged out successfully");
});

function showMainApp() {
  document.getElementById("login-screen").classList.remove("active");
  document.getElementById("login-screen").classList.add("hidden");
  document.getElementById("app").classList.remove("hidden");
  App.refreshDashboard();
  App.setupNav();
  App.startClock();
}

// Sidebar responsive toggle
document.getElementById("sidebar-toggle").addEventListener("click", () => {
  document.getElementById("sidebar").classList.toggle("collapsed");
});

document.getElementById("mobile-menu-btn").addEventListener("click", () => {
  document.getElementById("sidebar").classList.toggle("mobile-open");
});

// Close mobile sidebar when clicking main content
document.getElementById("main-content").addEventListener("click", () => {
  document.getElementById("sidebar").classList.remove("mobile-open");
});

// ───────────── MAIN APP MODULE ─────────────
const App = {
  startClock() {
    const updateTime = () => {
      const now = new Date();
      document.getElementById("topbar-time").innerText = now.toLocaleString("en-US", {
        weekday: "short", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit"
      });
    };
    updateTime();
    setInterval(updateTime, 1000);
  },

  setupNav() {
    document.querySelectorAll(".nav-item").forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const section = item.dataset.section;
        App.navigate(section);
      });
    });
  },

  navigate(section) {
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    document.querySelectorAll(".section").forEach(s => s.classList.add("hidden"));
    
    const activeNav = document.querySelector(`.nav-item[data-section="${section}"]`);
    if (activeNav) activeNav.classList.add("active");
    
    const activeSection = document.getElementById(`section-${section}`);
    if (activeSection) activeSection.classList.remove("hidden");
    
    // Breadcrumb Update
    document.getElementById("breadcrumb").innerText = section.charAt(0).toUpperCase() + section.slice(1);
    
    // Trigger module refreshes
    if (section === "dashboard") App.refreshDashboard();
    else if (section === "rooms") Rooms.render();
    else if (section === "customers") Customers.render();
    else if (section === "bookings") Bookings.render();
    else if (section === "billing") Billing.render();
    else if (section === "reports") Reports.render();
  },

  refreshDashboard() {
    const totalRooms = AppState.rooms.length;
    const available = AppState.rooms.filter(r => r.status === "Available").length;
    const booked = totalRooms - available;
    const totalCusts = AppState.customers.length;
    const activeBookings = AppState.bookings.filter(b => ["Confirmed", "Checked-In"].includes(b.booking_status)).length;
    const totalRevenue = AppState.bookings.filter(b => b.booking_status === "Completed")
      .reduce((sum, b) => sum + b.bill_amount, 0);

    document.getElementById("stat-total-rooms").innerText = totalRooms;
    document.getElementById("stat-available").innerText = available;
    document.getElementById("stat-booked").innerText = booked;
    document.getElementById("stat-customers").innerText = totalCusts;
    document.getElementById("stat-active-bookings").innerText = activeBookings;
    document.getElementById("stat-revenue").innerText = `₹${totalRevenue.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    // Update Sidebar Badges
    document.getElementById("badge-rooms").innerText = available;
    document.getElementById("badge-customers").innerText = totalCusts;
    document.getElementById("badge-bookings").innerText = activeBookings;

    // Occupancy chart calculation
    const pct = totalRooms > 0 ? Math.round((booked / totalRooms) * 100) : 0;
    const chart = document.getElementById("occupancy-chart");
    chart.innerHTML = `
      <div class="occ-row">
        <div class="occ-label">Occupied</div>
        <div class="occ-bar-wrap">
          <div class="occ-bar" style="width: ${pct}%; background: var(--orange);"></div>
        </div>
        <div class="occ-pct">${pct}%</div>
      </div>
      <div class="occ-row">
        <div class="occ-label">Available</div>
        <div class="occ-bar-wrap">
          <div class="occ-bar" style="width: ${100 - pct}%; background: var(--green);"></div>
        </div>
        <div class="occ-pct">${100 - pct}%</div>
      </div>
    `;

    // Render Recent Bookings list
    const recent = AppState.bookings.slice(-4).reverse();
    const recentList = document.getElementById("recent-bookings-list");
    if (recent.length === 0) {
      recentList.innerHTML = `<div style="color:var(--text2);text-align:center;padding:1rem;">No recent bookings</div>`;
      return;
    }
    
    recentList.innerHTML = recent.map(b => {
      const cust = AppState.customers.find(c => c.customer_id === b.customer_id)?.name || "Unknown";
      const room = AppState.rooms.find(r => r.room_id === b.room_id)?.room_number || "—";
      const stClass = b.booking_status.toLowerCase().replace("-", "");
      return `
        <div class="recent-item">
          <div class="recent-dot" style="background: ${b.booking_status === 'Completed' ? 'var(--purple)' : b.booking_status === 'Checked-In' ? 'var(--green)' : 'var(--blue)'}"></div>
          <div class="recent-name">${cust} (Room ${room})</div>
          <div class="recent-amount">₹${b.bill_amount.toLocaleString("en-IN")}</div>
          <span class="recent-status status-${stClass}">${b.booking_status}</span>
        </div>
      `;
    }).join("");
  }
};

// ───────────── ROOMS MODULE ─────────────
const Rooms = {
  render() {
    const q = document.getElementById("room-search").value.toLowerCase();
    const status = document.getElementById("room-filter-status").value;
    const type = document.getElementById("room-filter-type").value;
    
    const tbody = document.getElementById("rooms-tbody");
    tbody.innerHTML = "";
    
    const filtered = AppState.rooms.filter(r => {
      const matchesSearch = r.room_number.includes(q) || r.room_type.toLowerCase().includes(q);
      const matchesStatus = status === "" || r.status === status;
      const matchesType = type === "" || r.room_type === type;
      return matchesSearch && matchesStatus && matchesType;
    });

    if (filtered.length === 0) {
      document.getElementById("rooms-empty").classList.remove("hidden");
      document.getElementById("rooms-table").classList.add("hidden");
      return;
    }
    document.getElementById("rooms-empty").classList.add("hidden");
    document.getElementById("rooms-table").classList.remove("hidden");

    tbody.innerHTML = filtered.map(r => `
      <tr>
        <td>${r.room_id}</td>
        <td style="font-weight: 700;">${r.room_number}</td>
        <td>${r.room_type}</td>
        <td>₹${r.price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
        <td><span class="badge ${r.status === 'Available' ? 'badge-available' : 'badge-booked'}">${r.status}</span></td>
        <td>
          <div class="action-btns">
            <button class="btn-icon" onclick="Rooms.openModal(${r.room_id})" title="Edit">✏️</button>
            <button class="btn-icon del" onclick="Rooms.delete(${r.room_id})" title="Delete">🗑️</button>
          </div>
        </td>
      </tr>
    `).join("");
  },

  openModal(id = null) {
    const modal = document.getElementById("room-modal");
    const form = document.getElementById("room-form");
    form.reset();
    
    if (id) {
      const room = AppState.rooms.find(r => r.room_id === id);
      document.getElementById("room-modal-title").innerText = "Edit Room";
      document.getElementById("room-id").value = room.room_id;
      document.getElementById("room-number").value = room.room_number;
      document.getElementById("room-type").value = room.room_type;
      document.getElementById("room-price").value = room.price;
    } else {
      document.getElementById("room-modal-title").innerText = "Add Room";
      document.getElementById("room-id").value = "";
    }
    modal.classList.remove("hidden");
  },

  closeModal() {
    document.getElementById("room-modal").classList.add("hidden");
  },

  save(e) {
    e.preventDefault();
    const id = document.getElementById("room-id").value;
    const num = document.getElementById("room-number").value.trim().toUpperCase();
    const type = document.getElementById("room-type").value;
    const price = parseFloat(document.getElementById("room-price").value);

    if (!num || !type || isNaN(price) || price <= 0) {
      showToast("Please fill in all required fields with valid values", "error");
      return;
    }

    // Check unique number
    const dup = AppState.rooms.find(r => r.room_number === num && r.room_id != id);
    if (dup) {
      showToast(`Room number ${num} already exists!`, "error");
      return;
    }

    if (id) {
      // Edit
      const roomIndex = AppState.rooms.findIndex(r => r.room_id == id);
      AppState.rooms[roomIndex] = { ...AppState.rooms[roomIndex], room_number: num, room_type: type, price };
      showToast("Room updated successfully", "success");
    } else {
      // Add
      const nextId = AppState.rooms.length > 0 ? Math.max(...AppState.rooms.map(r => r.room_id)) + 1 : 1;
      AppState.rooms.push({ room_id: nextId, room_number: num, room_type: type, price, status: "Available" });
      showToast("New Room added successfully", "success");
    }

    saveData("rooms");
    Rooms.closeModal();
    Rooms.render();
  },

  delete(id) {
    const room = AppState.rooms.find(r => r.room_id === id);
    if (room.status === "Booked") {
      showToast("Cannot delete a booked room!", "error");
      return;
    }
    if (confirm(`Are you sure you want to delete Room ${room.room_number}?`)) {
      AppState.rooms = AppState.rooms.filter(r => r.room_id !== id);
      saveData("rooms");
      showToast("Room deleted successfully");
      Rooms.render();
    }
  }
};

// ───────────── CUSTOMERS MODULE ─────────────
const Customers = {
  render() {
    const q = document.getElementById("customer-search").value.toLowerCase();
    const tbody = document.getElementById("customers-tbody");
    tbody.innerHTML = "";
    
    const filtered = AppState.customers.filter(c => 
      c.name.toLowerCase().includes(q) || c.phone.includes(q)
    );

    if (filtered.length === 0) {
      document.getElementById("customers-empty").classList.remove("hidden");
      document.getElementById("customers-table").classList.add("hidden");
      return;
    }
    document.getElementById("customers-empty").classList.add("hidden");
    document.getElementById("customers-table").classList.remove("hidden");

    tbody.innerHTML = filtered.map(c => `
      <tr>
        <td>${c.customer_id}</td>
        <td style="font-weight:600;">${c.name}</td>
        <td>${c.phone}</td>
        <td>${c.email}</td>
        <td>${c.id_proof || '—'}</td>
        <td>
          <div class="action-btns">
            <button class="btn-icon" onclick="Customers.openModal(${c.customer_id})" title="Edit">✏️</button>
            <button class="btn-icon del" onclick="Customers.delete(${c.customer_id})" title="Delete">🗑️</button>
          </div>
        </td>
      </tr>
    `).join("");
  },

  openModal(id = null) {
    const modal = document.getElementById("customer-modal");
    const form = document.getElementById("customer-form");
    form.reset();

    if (id) {
      const c = AppState.customers.find(x => x.customer_id === id);
      document.getElementById("customer-modal-title").innerText = "Edit Customer";
      document.getElementById("customer-id").value = c.customer_id;
      document.getElementById("customer-name").value = c.name;
      document.getElementById("customer-phone").value = c.phone;
      document.getElementById("customer-email").value = c.email;
      document.getElementById("customer-address").value = c.address;
      document.getElementById("customer-idproof").value = c.id_proof;
    } else {
      document.getElementById("customer-modal-title").innerText = "Add Customer";
      document.getElementById("customer-id").value = "";
    }
    modal.classList.remove("hidden");
  },

  closeModal() {
    document.getElementById("customer-modal").classList.add("hidden");
  },

  save(e) {
    e.preventDefault();
    const id = document.getElementById("customer-id").value;
    const name = document.getElementById("customer-name").value.trim();
    const phone = document.getElementById("customer-phone").value.trim();
    const email = document.getElementById("customer-email").value.trim();
    const address = document.getElementById("customer-address").value.trim();
    const id_proof = document.getElementById("customer-idproof").value.trim();

    if (!name || !phone || !email) {
      showToast("Please fill in Name, Phone, and Email", "error");
      return;
    }

    if (id) {
      const idx = AppState.customers.findIndex(c => c.customer_id == id);
      AppState.customers[idx] = { ...AppState.customers[idx], name, phone, email, address, id_proof };
      showToast("Customer details updated", "success");
    } else {
      const nextId = AppState.customers.length > 0 ? Math.max(...AppState.customers.map(c => c.customer_id)) + 1 : 1;
      AppState.customers.push({ customer_id: nextId, name, phone, email, address, id_proof });
      showToast("Customer registered successfully", "success");
    }

    saveData("customers");
    Customers.closeModal();
    Customers.render();
  },

  delete(id) {
    // Check if customer has active booking
    const active = AppState.bookings.find(b => b.customer_id === id && ["Confirmed", "Checked-In"].includes(b.booking_status));
    if (active) {
      showToast("Cannot delete guest with active bookings!", "error");
      return;
    }
    if (confirm("Are you sure you want to delete this customer?")) {
      AppState.customers = AppState.customers.filter(c => c.customer_id !== id);
      saveData("customers");
      showToast("Customer deleted");
      Customers.render();
    }
  }
};

// ───────────── BOOKINGS MODULE ─────────────
const Bookings = {
  render() {
    const q = document.getElementById("booking-search").value.toLowerCase();
    const status = document.getElementById("booking-filter-status").value;
    const tbody = document.getElementById("bookings-tbody");
    tbody.innerHTML = "";

    const filtered = AppState.bookings.filter(b => {
      const cust = AppState.customers.find(c => c.customer_id === b.customer_id)?.name.toLowerCase() || "";
      const room = AppState.rooms.find(r => r.room_id === b.room_id)?.room_number || "";
      const matchesSearch = cust.includes(q) || room.includes(q);
      const matchesStatus = status === "" || b.booking_status === status;
      return matchesSearch && matchesStatus;
    });

    const bookingsTableWrap = tbody.closest('.table-wrap');
    if (filtered.length === 0) {
      document.getElementById("bookings-empty").classList.remove("hidden");
      bookingsTableWrap.style.display = "none";
      return;
    }
    document.getElementById("bookings-empty").classList.add("hidden");
    bookingsTableWrap.style.display = "";

    tbody.innerHTML = filtered.slice().reverse().map(b => {
      const cust = AppState.customers.find(c => c.customer_id === b.customer_id)?.name || "Unknown";
      const room = AppState.rooms.find(r => r.room_id === b.room_id)?.room_number || "—";
      
      let actionBtn = "";
      if (b.booking_status === "Confirmed") {
        actionBtn = `<button class="btn btn-sm btn-ghost" onclick="Bookings.checkIn(${b.booking_id})">📥 Check In</button>`;
      } else if (b.booking_status === "Checked-In") {
        actionBtn = `<button class="btn btn-sm btn-primary" onclick="Bookings.checkOut(${b.booking_id})">📤 Check Out</button>`;
      } else if (b.booking_status === "Completed") {
        actionBtn = `<button class="btn btn-sm btn-ghost" onclick="Billing.preview(${b.booking_id})">🧾 Invoice</button>`;
      }

      return `
        <tr>
          <td>${b.booking_id}</td>
          <td style="font-weight:500;">${cust}</td>
          <td>Room ${room}</td>
          <td>${b.check_in}</td>
          <td>${b.check_out}</td>
          <td>${b.total_days}</td>
          <td style="font-weight:700;color:var(--gold);">₹${b.bill_amount.toLocaleString("en-IN")}</td>
          <td><span class="badge badge-${b.booking_status.toLowerCase().replace("-", "")}">${b.booking_status}</span></td>
          <td>
            <div style="display:flex;gap:.5rem;align-items:center;">
              ${actionBtn}
              ${["Confirmed"].includes(b.booking_status) ? `<button class="btn-icon del" onclick="Bookings.cancel(${b.booking_id})">✕</button>` : ''}
            </div>
          </td>
        </tr>
      `;
    }).join("");
  },

  openModal() {
    const modal = document.getElementById("booking-modal");
    const custSel = document.getElementById("booking-customer");
    const roomSel = document.getElementById("booking-room");
    
    // Fill customer dropdown
    custSel.innerHTML = '<option value="">Select Guest</option>' + 
      AppState.customers.map(c => `<option value="${c.customer_id}">${c.name} (${c.phone})</option>`).join("");
      
    // Fill room dropdown (available rooms only)
    roomSel.innerHTML = '<option value="">Select Room</option>' + 
      AppState.rooms.filter(r => r.status === "Available").map(r => `<option value="${r.room_id}">Room ${r.room_number} (${r.room_type} - ₹${r.price})</option>`).join("");
      
    document.getElementById("booking-form").reset();
    document.getElementById("booking-summary").style.display = "none";
    modal.classList.remove("hidden");
  },

  closeModal() {
    document.getElementById("booking-modal").classList.add("hidden");
  },

  calcBill() {
    const roomId = document.getElementById("booking-room").value;
    const ci = document.getElementById("booking-checkin").value;
    const co = document.getElementById("booking-checkout").value;
    const sumDiv = document.getElementById("booking-summary");

    if (!roomId || !ci || !co) {
      sumDiv.style.display = "none";
      return;
    }

    const room = AppState.rooms.find(r => r.room_id == roomId);
    const date1 = new Date(ci);
    const date2 = new Date(co);
    const diff = date2 - date1;
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));

    if (isNaN(days) || days <= 0) {
      sumDiv.style.display = "none";
      return;
    }

    const base = room.price * days;
    const tax = Math.round(base * 0.10);
    const total = base + tax;

    document.getElementById("sum-days").innerText = `${days} Night(s)`;
    document.getElementById("sum-price").innerText = `₹${room.price.toLocaleString("en-IN")}`;
    document.getElementById("sum-base").innerText = `₹${base.toLocaleString("en-IN")}`;
    document.getElementById("sum-tax").innerText = `₹${tax.toLocaleString("en-IN")} (10%)`;
    document.getElementById("sum-total").innerText = `₹${total.toLocaleString("en-IN")}`;
    sumDiv.style.display = "block";
  },

  save(e) {
    e.preventDefault();
    const custId = parseInt(document.getElementById("booking-customer").value);
    const roomId = parseInt(document.getElementById("booking-room").value);
    const ci = document.getElementById("booking-checkin").value;
    const co = document.getElementById("booking-checkout").value;

    if (!custId || !roomId || !ci || !co) {
      showToast("Please fill all required booking parameters", "error");
      return;
    }

    const date1 = new Date(ci);
    const date2 = new Date(co);
    if (date2 <= date1) {
      showToast("Check-out date must be after check-in date", "error");
      return;
    }

    const days = Math.ceil((date2 - date1) / (1000 * 60 * 60 * 24));
    const room = AppState.rooms.find(r => r.room_id === roomId);
    const totalBill = room.price * days;

    const nextId = AppState.bookings.length > 0 ? Math.max(...AppState.bookings.map(b => b.booking_id)) + 1 : 1;
    AppState.bookings.push({
      booking_id: nextId,
      customer_id: custId,
      room_id: roomId,
      check_in: ci,
      check_out: co,
      total_days: days,
      bill_amount: totalBill,
      booking_status: "Confirmed"
    });

    // Mark room booked
    room.status = "Booked";

    saveData("bookings");
    saveData("rooms");
    showToast("Booking Confirmed successfully", "success");
    Bookings.closeModal();
    Bookings.render();
  },

  checkIn(id) {
    const booking = AppState.bookings.find(b => b.booking_id === id);
    booking.booking_status = "Checked-In";
    saveData("bookings");
    showToast("Guest successfully Checked In!", "success");
    Bookings.render();
  },

  checkOut(id) {
    const booking = AppState.bookings.find(b => b.booking_id === id);
    booking.booking_status = "Completed";
    
    // Free the room
    const room = AppState.rooms.find(r => r.room_id === booking.room_id);
    room.status = "Available";

    saveData("bookings");
    saveData("rooms");
    showToast("Check-out processed and Room is now Available", "success");
    Bookings.render();
  },

  cancel(id) {
    if (confirm("Are you sure you want to cancel this booking?")) {
      const booking = AppState.bookings.find(b => b.booking_id === id);
      booking.booking_status = "Cancelled";
      
      const room = AppState.rooms.find(r => r.room_id === booking.room_id);
      room.status = "Available";

      saveData("bookings");
      saveData("rooms");
      showToast("Booking Cancelled");
      Bookings.render();
    }
  }
};

// ───────────── BILLING / INVOICES MODULE ─────────────
const Billing = {
  render() {
    const q = document.getElementById("invoice-search").value.toLowerCase();
    const grid = document.getElementById("invoices-grid");
    grid.innerHTML = "";

    const completed = AppState.bookings.filter(b => b.booking_status === "Completed");
    const filtered = completed.filter(b => {
      const name = AppState.customers.find(c => c.customer_id === b.customer_id)?.name.toLowerCase() || "";
      return name.includes(q) || String(b.booking_id).includes(q);
    });

    if (filtered.length === 0) {
      document.getElementById("invoices-empty").classList.remove("hidden");
      return;
    }
    document.getElementById("invoices-empty").classList.add("hidden");

    grid.innerHTML = filtered.slice().reverse().map(b => {
      const cust = AppState.customers.find(c => c.customer_id === b.customer_id);
      const room = AppState.rooms.find(r => r.room_id === b.room_id);
      const tax = Math.round(b.bill_amount * 0.10);
      const grandTotal = b.bill_amount + tax;
      
      return `
        <div class="invoice-card glass" onclick="Billing.preview(${b.booking_id})">
          <div class="inv-no">INV-${String(b.booking_id).padStart(4, '0')}</div>
          <div class="inv-name">${cust?.name || 'Unknown'}</div>
          <div class="inv-room">Room ${room?.room_number || '—'} (${room?.room_type}) • ${b.total_days} Day(s)</div>
          <div class="inv-total">₹${grandTotal.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</div>
          <div class="inv-date">Checked Out: ${b.check_out}</div>
        </div>
      `;
    }).join("");
  },

  preview(id) {
    const b = AppState.bookings.find(x => x.booking_id === id);
    const cust = AppState.customers.find(c => c.customer_id === b.customer_id);
    const room = AppState.rooms.find(r => r.room_id === b.room_id);

    const base = b.bill_amount;
    const tax = Math.round(base * 0.10);
    const total = base + tax;
    const invoiceNo = `INV-${String(b.booking_id).padStart(4, '0')}`;
    const dateIssued = new Date().toLocaleString();

    const separator = "=".repeat(52);
    const line = "-".repeat(52);

    const invoiceText = `
${separator}
           Grand Horizon Hotel
        OFFICIAL INVOICE / RECEIPT
${separator}
 Invoice No  : ${invoiceNo}
 Date Issued : ${dateIssued}
${line}
 GUEST INFORMATION
${line}
 Customer ID  : ${b.customer_id}
 Name         : ${cust?.name || 'N/A'}
 Phone        : ${cust?.phone || 'N/A'}
 Email        : ${cust?.email || 'N/A'}
${line}
 ROOM INFORMATION
${line}
 Room Number  : ${room?.room_number || 'N/A'}
 Room Type    : ${room?.room_type || 'N/A'}
 Check-In     : ${b.check_in}
 Check-Out    : ${b.check_out}
 Total Days   : ${b.total_days}
${line}
 BILLING SUMMARY
${line}
 Price / Day  : ₹${room?.price.toFixed(2).padStart(10)}
 Base Amount  : ₹${base.toFixed(2).padStart(10)}
 Tax (10 %)   : ₹${tax.toFixed(2).padStart(10)}
 GRAND TOTAL  : ₹${total.toFixed(2).padStart(10)}
${separator}
 Status       : Paid / Settled
${separator}
      Thank you for staying at Grand Horizon!
          We hope to see you again soon.
${separator}
`;

    document.getElementById("invoice-content").innerText = invoiceText.trim();
    document.getElementById("invoice-modal").classList.remove("hidden");
  },

  closeModal() {
    document.getElementById("invoice-modal").classList.add("hidden");
  },

  print() {
    const paper = document.getElementById("invoice-content").innerText;
    const printWin = window.open("", "_blank");
    printWin.document.write(`<pre style="font-family:monospace;padding:2rem;">${paper}</pre>`);
    printWin.document.close();
    printWin.print();
  }
};

// ───────────── REPORTS MODULE ─────────────
const Reports = {
  render() {
    const dateInput = document.getElementById("report-date");
    if (!dateInput.value) {
      const today = new Date().toISOString().split("T")[0];
      dateInput.value = today;
    }
    this.renderRevenueChart();
  },

  daily() {
    const d = document.getElementById("report-date").value;
    if (!d) return;

    const rev = AppState.bookings
      .filter(b => b.check_out === d && b.booking_status === "Completed")
      .reduce((sum, b) => sum + b.bill_amount, 0);

    const res = document.getElementById("report-daily-result");
    res.innerHTML = `
      <div class="result-amount">₹${rev.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</div>
      <div class="result-label">Total Revenue generated on Check-out Date: ${d}</div>
    `;
    res.classList.remove("hidden");
  },

  monthly() {
    const yr = parseInt(document.getElementById("report-year").value);
    const mo = parseInt(document.getElementById("report-month").value);
    if (isNaN(yr) || isNaN(mo)) return;

    const pattern = `${yr}-${String(mo).padStart(2, '0')}`;
    const rev = AppState.bookings
      .filter(b => b.check_out.startsWith(pattern) && b.booking_status === "Completed")
      .reduce((sum, b) => sum + b.bill_amount, 0);

    const res = document.getElementById("report-monthly-result");
    res.innerHTML = `
      <div class="result-amount">₹${rev.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</div>
      <div class="result-label">Total Revenue generated in Month: ${pattern}</div>
    `;
    res.classList.remove("hidden");
  },

  renderRevenueChart() {
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const currentYear = new Date().getFullYear();
    const monthlyRev = Array(12).fill(0);

    AppState.bookings.forEach(b => {
      if (b.booking_status === "Completed") {
        const d = new Date(b.check_out);
        if (d.getFullYear() === currentYear) {
          monthlyRev[d.getMonth()] += b.bill_amount;
        }
      }
    });

    const maxRev = Math.max(...monthlyRev, 1);
    const breakdown = document.getElementById("revenue-breakdown");
    breakdown.innerHTML = monthlyRev.map((rev, index) => {
      const pct = (rev / maxRev) * 100;
      return `
        <div class="rev-row">
          <div class="rev-month">${monthNames[index]} ${currentYear}</div>
          <div class="rev-bar-wrap">
            <div class="rev-bar" style="width: ${pct}%"></div>
          </div>
          <div class="rev-amount">₹${rev.toLocaleString("en-IN")}</div>
        </div>
      `;
    }).join("");
  }
};

// Start HMS
window.addEventListener("DOMContentLoaded", initData);
