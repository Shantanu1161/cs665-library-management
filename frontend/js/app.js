/* ════════════════════════════════════════════════════════
   Library Management System — Frontend Application
   CS665 Project 3
   ════════════════════════════════════════════════════════ */

const API = "http://localhost:8000";

/* ── State ─────────────────────────────────────────────── */
let editingBookId   = null;
let editingMemberId = null;

/* ── API helper ────────────────────────────────────────── */
async function api(method, path, body = null) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

/* ── Toast ─────────────────────────────────────────────── */
function toast(msg, type = "success") {
  const icons = {
    success: "bi-check-circle-fill",
    error:   "bi-x-circle-fill",
    info:    "bi-info-circle-fill",
  };
  const el = document.createElement("div");
  el.className = `toast-msg toast-${type}`;
  el.innerHTML = `<i class="bi ${icons[type]}"></i> ${msg}`;
  document.getElementById("toast-container").appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

/* ── Debounce ──────────────────────────────────────────── */
const _timers = {};
function debounce(fn, delay) {
  return function(...args) {
    clearTimeout(_timers[fn]);
    _timers[fn] = setTimeout(() => fn(...args), delay);
  };
}

/* ── Stars helper ──────────────────────────────────────── */
function stars(n) {
  return "★".repeat(n) + "☆".repeat(5 - n);
}

/* ── Modal helpers ─────────────────────────────────────── */
function closeModal(id) { document.getElementById(id).classList.remove("open"); }
function openModal(id)  { document.getElementById(id).classList.add("open"); }

/* ── XSS guard ─────────────────────────────────────────── */
function esc(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* ── Navigation ────────────────────────────────────────── */
const pageTitles = {
  dashboard: "Dashboard",
  books:     "Books · Library Catalog",
  members:   "Members",
  borrows:   "Borrows · Loan Records",
  reviews:   "Reviews",
};

function navigate(page) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-link").forEach(a => a.classList.remove("active"));
  document.getElementById("page-" + page).classList.add("active");
  document.querySelector(`.nav-link[data-page="${page}"]`).classList.add("active");
  document.getElementById("page-title").textContent = pageTitles[page];

  if (page === "dashboard") loadDashboard();
  if (page === "books")     { loadGenres(); loadBooks(); }
  if (page === "members")   loadMembers();
  if (page === "borrows")   loadBorrows();
  if (page === "reviews")   loadReviews();
}

/* ════════ DASHBOARD ════════ */
async function loadDashboard() {
  try {
    const d = await api("GET", "/dashboard");

    document.getElementById("stats-grid").innerHTML = `
      <div class="stat-card">
        <div class="icon icon-books"><i class="bi bi-journal-bookmark-fill"></i></div>
        <div class="label">Total Books</div>
        <div class="value">${d.total_books}</div>
      </div>
      <div class="stat-card">
        <div class="icon icon-members"><i class="bi bi-people-fill"></i></div>
        <div class="label">Active Members</div>
        <div class="value">${d.total_members}</div>
      </div>
      <div class="stat-card">
        <div class="icon icon-loans"><i class="bi bi-arrow-left-right"></i></div>
        <div class="label">Active Loans</div>
        <div class="value">${d.active_loans}</div>
        <div class="sub">${d.total_loans} total</div>
      </div>
      <div class="stat-card">
        <div class="icon icon-overdue"><i class="bi bi-exclamation-triangle-fill"></i></div>
        <div class="label">Overdue</div>
        <div class="value">${d.overdue_loans}</div>
        <div class="sub">loans past due</div>
      </div>
      <div class="stat-card">
        <div class="icon icon-reviews"><i class="bi bi-star-fill"></i></div>
        <div class="label">Reviews</div>
        <div class="value">${d.total_reviews}</div>
        <div class="sub">Avg: ${d.avg_rating} ★</div>
      </div>
      <div class="stat-card">
        <div class="icon icon-fines"><i class="bi bi-cash-coin"></i></div>
        <div class="label">Fines Collected</div>
        <div class="value">$${d.total_fines_collected}</div>
      </div>
    `;

    const tbody = document.getElementById("dash-borrows-body");
    if (d.active_borrows.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="empty-state"><i class="bi bi-check-circle"></i><p>No active borrows</p></td></tr>`;
    } else {
      tbody.innerHTML = d.active_borrows.map(b => `
        <tr>
          <td>${esc(b.member_name)}</td>
          <td>${esc(b.book_title)}</td>
          <td>${b.due_date}</td>
          <td><span class="pill ${b.overdue ? "badge-overdue" : "badge-borrowed"}">${b.overdue ? "Overdue" : "Active"}</span></td>
        </tr>
      `).join("");
    }

    const maxCount = Math.max(...d.books_by_genre.map(g => g.count), 1);
    document.getElementById("genre-chart").innerHTML = d.books_by_genre.map(g => `
      <div class="genre-bar">
        <div class="genre-bar-label">${esc(g.genre)}</div>
        <div class="genre-bar-track">
          <div class="genre-bar-fill" style="width:${(g.count / maxCount) * 100}%"></div>
        </div>
        <div class="genre-bar-count">${g.count}</div>
      </div>
    `).join("") || '<p style="color:var(--text-muted);font-size:.85rem;">No data</p>';

    document.getElementById("top-books-body").innerHTML = d.top_books.map((b, i) => `
      <tr>
        <td><span class="pill badge-loans">${i + 1}</span></td>
        <td>${esc(b.title)}</td>
        <td><strong>${b.borrow_count}</strong></td>
        <td><span class="stars">${b.avg_rating ? "★".repeat(Math.round(b.avg_rating)) : "—"}</span> ${b.avg_rating || "—"}</td>
      </tr>
    `).join("");

  } catch(e) {
    toast("Dashboard failed to load: " + e.message, "error");
  }
}

/* ════════ BOOKS ════════ */
async function loadGenres() {
  try {
    const genres = await api("GET", "/genres");
    const sel = document.getElementById("genre-filter");
    sel.innerHTML = `<option value="">All Genres</option>` +
      genres.map(g => `<option value="${esc(g)}">${esc(g)}</option>`).join("");
  } catch(e) {}
}

async function loadBooks() {
  const search = document.getElementById("book-search").value;
  const genre  = document.getElementById("genre-filter").value;
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (genre)  params.set("genre", genre);

  const tbody = document.getElementById("books-body");
  tbody.innerHTML = `<tr><td colspan="8" class="loading">Loading…</td></tr>`;

  try {
    const books = await api("GET", `/books?${params}`);
    if (books.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8">
        <div class="empty-state"><i class="bi bi-journal-x"></i><p>No books found</p></div>
      </td></tr>`;
      return;
    }
    tbody.innerHTML = books.map(b => {
      let availClass = b.available_copies === 0 ? "badge-unavail"
                     : b.available_copies <= 1   ? "badge-limited"
                     : "badge-avail";
      return `
      <tr>
        <td><strong>${esc(b.title)}</strong></td>
        <td>${esc(b.author)}</td>
        <td><span class="pill badge-standard">${esc(b.genre)}</span></td>
        <td>${b.year || "—"}</td>
        <td style="font-family:monospace;font-size:.8rem;">${b.isbn || "—"}</td>
        <td>${b.total_copies}</td>
        <td><span class="pill ${availClass}">${b.available_copies} / ${b.total_copies}</span></td>
        <td>
          <button class="btn-sm-icon" title="Edit" onclick="editBook(${b.book_id})"><i class="bi bi-pencil"></i></button>
          <button class="btn-sm-danger" title="Delete" onclick="deleteBook(${b.book_id}, '${esc(b.title).replace(/'/g, '&#39;')}')"><i class="bi bi-trash"></i></button>
        </td>
      </tr>`;
    }).join("");
  } catch(e) {
    tbody.innerHTML = `<tr><td colspan="8" style="color:var(--danger);padding:20px;">${e.message}</td></tr>`;
  }
}

function openBookModal(book = null) {
  editingBookId = book ? book.book_id : null;
  document.getElementById("book-modal-title").textContent = book ? "Edit Book" : "Add Book";
  document.getElementById("b-title").value  = book?.title  || "";
  document.getElementById("b-author").value = book?.author || "";
  document.getElementById("b-genre").value  = book?.genre  || "";
  document.getElementById("b-year").value   = book?.year   || "";
  document.getElementById("b-isbn").value   = book?.isbn   || "";
  document.getElementById("b-total").value  = book?.total_copies || 1;
  document.getElementById("b-avail").value  = book?.available_copies ?? 1;
  document.getElementById("book-error").textContent = "";
  openModal("modal-book");
}

async function editBook(id) {
  try {
    const book = await api("GET", `/books/${id}`);
    openBookModal(book);
  } catch(e) { toast(e.message, "error"); }
}

async function saveBook() {
  const body = {
    title:            document.getElementById("b-title").value.trim(),
    author:           document.getElementById("b-author").value.trim(),
    genre:            document.getElementById("b-genre").value.trim(),
    isbn:             document.getElementById("b-isbn").value.trim() || null,
    year:             parseInt(document.getElementById("b-year").value) || null,
    total_copies:     parseInt(document.getElementById("b-total").value) || 1,
    available_copies: parseInt(document.getElementById("b-avail").value) ?? 1,
  };

  const errEl = document.getElementById("book-error");
  if (!body.title || !body.author || !body.genre) {
    errEl.textContent = "Title, Author, and Genre are required."; return;
  }
  errEl.textContent = "";

  try {
    if (editingBookId) {
      await api("PUT", `/books/${editingBookId}`, body);
      toast("Book updated successfully");
    } else {
      await api("POST", "/books", body);
      toast("Book added successfully");
    }
    closeModal("modal-book");
    loadBooks();
    loadGenres();
  } catch(e) {
    errEl.textContent = e.message;
  }
}

async function deleteBook(id, title) {
  if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;
  try {
    await api("DELETE", `/books/${id}`);
    toast("Book deleted");
    loadBooks();
  } catch(e) { toast(e.message, "error"); }
}

/* ════════ MEMBERS ════════ */
async function loadMembers() {
  const search = document.getElementById("member-search").value;
  const tbody = document.getElementById("members-body");
  tbody.innerHTML = `<tr><td colspan="7" class="loading">Loading…</td></tr>`;

  try {
    const members = await api("GET", `/members?search=${encodeURIComponent(search)}`);
    if (members.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7">
        <div class="empty-state"><i class="bi bi-person-x"></i><p>No members found</p></div>
      </td></tr>`;
      return;
    }
    tbody.innerHTML = members.map(m => `
      <tr>
        <td><strong>${esc(m.name)}</strong></td>
        <td>${esc(m.email)}</td>
        <td>${m.phone || "—"}</td>
        <td><span class="pill ${m.membership_type === 'premium' ? 'badge-premium' : 'badge-standard'}">${esc(m.membership_type)}</span></td>
        <td><span class="pill ${m.active ? 'badge-active' : 'badge-inactive'}">${m.active ? 'Active' : 'Inactive'}</span></td>
        <td>${m.created_at}</td>
        <td>
          <button class="btn-sm-icon" title="Edit" onclick="editMember(${m.user_id})"><i class="bi bi-pencil"></i></button>
          <button class="btn-sm-danger" title="Delete" onclick="deleteMember(${m.user_id}, '${esc(m.name).replace(/'/g, '&#39;')}')"><i class="bi bi-trash"></i></button>
        </td>
      </tr>
    `).join("");
  } catch(e) {
    tbody.innerHTML = `<tr><td colspan="7" style="color:var(--danger);padding:20px;">${e.message}</td></tr>`;
  }
}

function openMemberModal(member = null) {
  editingMemberId = member ? member.user_id : null;
  document.getElementById("member-modal-title").textContent = member ? "Edit Member" : "Add Member";
  document.getElementById("m-name").value  = member?.name  || "";
  document.getElementById("m-email").value = member?.email || "";
  document.getElementById("m-phone").value = member?.phone || "";
  document.getElementById("m-type").value  = member?.membership_type || "standard";
  document.getElementById("m-active").value = String(member?.active ?? 1);
  document.getElementById("m-active-wrap").style.display = member ? "block" : "none";
  document.getElementById("member-error").textContent = "";
  openModal("modal-member");
}

async function editMember(id) {
  try {
    const m = await api("GET", `/members/${id}`);
    openMemberModal(m);
  } catch(e) { toast(e.message, "error"); }
}

async function saveMember() {
  const body = {
    name:            document.getElementById("m-name").value.trim(),
    email:           document.getElementById("m-email").value.trim(),
    phone:           document.getElementById("m-phone").value.trim() || null,
    membership_type: document.getElementById("m-type").value,
  };
  if (editingMemberId) {
    body.active = parseInt(document.getElementById("m-active").value);
  }

  const errEl = document.getElementById("member-error");
  if (!body.name || !body.email) { errEl.textContent = "Name and Email are required."; return; }
  errEl.textContent = "";

  try {
    if (editingMemberId) {
      await api("PUT", `/members/${editingMemberId}`, body);
      toast("Member updated");
    } else {
      await api("POST", "/members", body);
      toast("Member added");
    }
    closeModal("modal-member");
    loadMembers();
  } catch(e) { errEl.textContent = e.message; }
}

async function deleteMember(id, name) {
  if (!confirm(`Delete member "${name}"? This cannot be undone.`)) return;
  try {
    await api("DELETE", `/members/${id}`);
    toast("Member deleted");
    loadMembers();
  } catch(e) { toast(e.message, "error"); }
}

/* ════════ BORROWS ════════ */
async function loadBorrows() {
  const activeOnly = document.getElementById("active-only").checked;
  const tbody = document.getElementById("borrows-body");
  tbody.innerHTML = `<tr><td colspan="9" class="loading">Loading…</td></tr>`;

  try {
    const loans = await api("GET", `/borrows?active_only=${activeOnly}`);
    if (loans.length === 0) {
      tbody.innerHTML = `<tr><td colspan="9">
        <div class="empty-state"><i class="bi bi-inbox"></i><p>No loans found</p></div>
      </td></tr>`;
      return;
    }
    tbody.innerHTML = loans.map(l => {
      let statusBadge = l.status === "Returned" ? "badge-returned"
                      : l.overdue               ? "badge-overdue"
                      : "badge-borrowed";
      let statusText  = l.status === "Returned" ? "Returned"
                      : l.overdue               ? "Overdue"
                      : "Borrowed";
      return `
      <tr>
        <td>#${l.loan_id}</td>
        <td>${esc(l.member_name)}</td>
        <td>${esc(l.book_title)}</td>
        <td>${l.loan_date}</td>
        <td>${l.due_date}</td>
        <td>${l.return_date || "—"}</td>
        <td><span class="pill ${statusBadge}">${statusText}</span></td>
        <td>${l.fine_amount != null ? `<strong>$${l.fine_amount}</strong>` : "—"}</td>
        <td>
          ${l.status === "Borrowed"
            ? `<button class="btn-sm-success" onclick="returnBook(${l.loan_id})"><i class="bi bi-arrow-return-left"></i> Return</button>`
            : `<span class="pill badge-returned"><i class="bi bi-check"></i> Done</span>`
          }
        </td>
      </tr>`;
    }).join("");
  } catch(e) {
    tbody.innerHTML = `<tr><td colspan="9" style="color:var(--danger);padding:20px;">${e.message}</td></tr>`;
  }
}

async function openBorrowModal() {
  try {
    const [members, books] = await Promise.all([
      api("GET", "/members"),
      api("GET", "/books"),
    ]);

    document.getElementById("bw-member").innerHTML =
      `<option value="">— Select Member —</option>` +
      members.filter(m => m.active).map(m =>
        `<option value="${m.user_id}">${esc(m.name)} (${esc(m.membership_type)})</option>`
      ).join("");

    document.getElementById("bw-book").innerHTML =
      `<option value="">— Select Book —</option>` +
      books.filter(b => b.available_copies > 0).map(b =>
        `<option value="${b.book_id}">${esc(b.title)} — ${b.available_copies} available</option>`
      ).join("");

    document.getElementById("bw-days").value = 14;
    document.getElementById("borrow-error").textContent = "";
    openModal("modal-borrow");
  } catch(e) { toast(e.message, "error"); }
}

async function issueLoan() {
  const body = {
    user_id: parseInt(document.getElementById("bw-member").value),
    book_id: parseInt(document.getElementById("bw-book").value),
    days:    parseInt(document.getElementById("bw-days").value),
  };
  const errEl = document.getElementById("borrow-error");
  if (!body.user_id || !body.book_id) { errEl.textContent = "Select a member and a book."; return; }
  if (!body.days || body.days < 1)    { errEl.textContent = "Loan duration must be at least 1 day."; return; }
  errEl.textContent = "";

  try {
    await api("POST", "/borrows", body);
    toast("Loan issued successfully!");
    closeModal("modal-borrow");
    loadBorrows();
    loadDashboard();
  } catch(e) { errEl.textContent = e.message; }
}

async function returnBook(loanId) {
  if (!confirm("Mark this book as returned?")) return;
  try {
    const loan = await api("PUT", `/borrows/${loanId}/return`);
    const fineMsg = loan.fine_amount > 0 ? ` Fine: $${loan.fine_amount}` : "";
    toast(`Book returned.${fineMsg}`);
    loadBorrows();
    loadDashboard();
  } catch(e) { toast(e.message, "error"); }
}

/* ════════ REVIEWS ════════ */
async function loadReviews() {
  const tbody = document.getElementById("reviews-body");
  tbody.innerHTML = `<tr><td colspan="6" class="loading">Loading…</td></tr>`;

  try {
    const reviews = await api("GET", "/reviews");
    if (reviews.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6">
        <div class="empty-state"><i class="bi bi-star"></i><p>No reviews yet</p></div>
      </td></tr>`;
      return;
    }
    tbody.innerHTML = reviews.map(r => `
      <tr>
        <td>${esc(r.book_title)}</td>
        <td>${esc(r.reviewer_name)}</td>
        <td><span class="stars">${stars(r.rating)}</span> <small>${r.rating}/5</small></td>
        <td style="max-width:280px;white-space:normal;">${r.comment ? esc(r.comment) : '<em style="color:var(--text-muted)">No comment</em>'}</td>
        <td>${r.created_at}</td>
        <td>
          <button class="btn-sm-danger" onclick="deleteReview(${r.review_id})"><i class="bi bi-trash"></i></button>
        </td>
      </tr>
    `).join("");
  } catch(e) {
    tbody.innerHTML = `<tr><td colspan="6" style="color:var(--danger);padding:20px;">${e.message}</td></tr>`;
  }
}

async function openReviewModal() {
  try {
    const [members, books] = await Promise.all([
      api("GET", "/members"),
      api("GET", "/books"),
    ]);

    document.getElementById("rv-member").innerHTML =
      `<option value="">— Select Member —</option>` +
      members.filter(m => m.active).map(m =>
        `<option value="${m.user_id}">${esc(m.name)}</option>`
      ).join("");

    document.getElementById("rv-book").innerHTML =
      `<option value="">— Select Book —</option>` +
      books.map(b => `<option value="${b.book_id}">${esc(b.title)}</option>`).join("");

    document.getElementById("rv-comment").value = "";
    document.getElementById("review-error").textContent = "";
    openModal("modal-review");
  } catch(e) { toast(e.message, "error"); }
}

async function saveReview() {
  const body = {
    user_id: parseInt(document.getElementById("rv-member").value),
    book_id: parseInt(document.getElementById("rv-book").value),
    rating:  parseInt(document.getElementById("rv-rating").value),
    comment: document.getElementById("rv-comment").value.trim() || null,
  };
  const errEl = document.getElementById("review-error");
  if (!body.user_id || !body.book_id) { errEl.textContent = "Select a member and a book."; return; }
  errEl.textContent = "";

  try {
    await api("POST", "/reviews", body);
    toast("Review added!");
    closeModal("modal-review");
    loadReviews();
  } catch(e) { errEl.textContent = e.message; }
}

async function deleteReview(id) {
  if (!confirm("Delete this review?")) return;
  try {
    await api("DELETE", `/reviews/${id}`);
    toast("Review deleted");
    loadReviews();
  } catch(e) { toast(e.message, "error"); }
}

/* ── API health check ──────────────────────────────────── */
async function checkApi() {
  try {
    await fetch(API + "/dashboard");
    document.getElementById("api-status").textContent = "● API Connected";
    document.getElementById("api-status").className = "pill badge-active";
  } catch(e) {
    document.getElementById("api-status").textContent = "● API Offline";
    document.getElementById("api-status").className = "pill badge-overdue";
  }
}

/* ── Init ──────────────────────────────────────────────── */
checkApi();
loadDashboard();
