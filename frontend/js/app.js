document.addEventListener("DOMContentLoaded", () => {
  const loggedIn = sessionStorage.getItem("aicte_demo_authenticated_v2") === "true";
  const currentPage = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll("[data-public-nav]").forEach((item) => item.classList.toggle("d-none", loggedIn));
  document.querySelectorAll("[data-auth-nav]").forEach((item) => item.classList.toggle("d-none", !loggedIn));
  const result = document.getElementById("action-result");
  const resultAction = document.getElementById("result-action");
  const resultDetail = document.getElementById("result-detail");
  const form = document.getElementById("action-form");
  const DEMO_ACCOUNTS = { Student: { username: "student001", password: "Student@123" }, Faculty: { username: "teacher001", password: "Teacher@123" }, Admin: { username: "developer001", password: "Developer@123" } };

  if (currentPage === "login.html" && form) {
    const rolePanel = document.createElement("div");
    rolePanel.className = "demo-panel rounded p-3 mb-4";
    rolePanel.innerHTML = `<div class="fw-semibold mb-2">Choose login portal</div><div class="d-flex flex-wrap gap-2"><button id="btn-student-login" data-role="Student" class="btn btn-sm btn-outline-primary">Student Login</button><button id="btn-faculty-login" data-role="Faculty" class="btn btn-sm btn-outline-primary">Teacher Login</button><button id="btn-admin-login" data-role="Admin" class="btn btn-sm btn-outline-primary">Developer Login</button></div><div id="login-credentials-hint" class="small text-secondary mt-3">Select a portal to see its demo credentials.</div>`;
    form.before(rolePanel);
  }
  if (currentPage === "register.html" && form) {
    form.querySelector('option[value="Developer"]')?.remove();
  }

  function showResult(action, data = {}) {
    const currentResult = document.getElementById("action-result");
    const currentAction = document.getElementById("result-action");
    const currentDetail = document.getElementById("result-detail");
    if (!currentResult) return;
    currentAction.textContent = action;
    currentDetail.textContent = Object.keys(data).length ? `Demo action triggered with ${Object.keys(data).length} field(s).` : "Demo action triggered. Ready for backend integration.";
    currentResult.classList.remove("d-none");
    currentResult.scrollIntoView({ block: "nearest" });
  }

  async function runAction(action, data = {}) {
    const button = document.querySelector(`[data-action="${action}"]`);
    if (button) { button.disabled = true; setTimeout(() => { button.disabled = false; }, 500); }
    await sendAction(action, data);
    if (action === "login_success") {
      sessionStorage.setItem("aicte_demo_authenticated_v2", "true");
      sessionStorage.setItem("aicte_demo_role", data.role || "Student");
      window.location.href = "index.html";
      return;
    }
    if (action === "register" && currentPage === "login.html") {
      window.location.href = "register.html";
      return;
    }
    if (action === "logout") {
      sessionStorage.removeItem("aicte_demo_authenticated_v2");
      sessionStorage.removeItem("aicte_demo_role");
      window.location.href = "login.html";
      return;
    }
    showResult(action, data);
  }
  document.querySelectorAll(".action-btn").forEach((button) => {

  // Submit buttons are handled by the form submit handler below.
  if (button.type === "submit") {
    return;
  }

  if (button.dataset.bound === "true") {
    return;
  }

  button.dataset.bound = "true";

  button.addEventListener("click", async (event) => {
    event.preventDefault();

    const action = button.dataset.action;

    if (!action) {
      console.error("No data-action found on button:", button);
      return;
    }

    console.log("Demo button clicked:", action);

    try {
      await runAction(action, {
        source: button.id || "action-button"
      });
    } catch (error) {
      console.error("Demo action failed:", action, error);
    }
  });
});
  
  if (form) form.addEventListener("submit", (event) => {
    event.preventDefault();
    const action = form.dataset.action || form.querySelector("[data-action]")?.dataset.action;
    const data = Object.fromEntries(new FormData(form).entries());
    if (currentPage === "login.html" && (!data.username?.trim() || !data.password?.trim() || !data.role)) {
      form.classList.add("was-validated");
      form.querySelector("input:invalid, select:invalid")?.focus();
      return;
    }
    if (currentPage === "login.html" && action === "login_success") {
      const account = DEMO_ACCOUNTS[data.role];
      if (!account || data.username.trim() !== account.username || data.password !== account.password) {
        showResult("login_failure", { message: "Invalid demo credentials" });
        return;
      }
    }
    if (action) runAction(action, data);
  });
  document.querySelectorAll("[data-role]").forEach((button) => button.addEventListener("click", () => {
    const roleSelect = form?.querySelector("select[name=role]");
    if (roleSelect) roleSelect.value = button.dataset.role;
    const registerButton = document.getElementById("btn-register");
    if (registerButton) registerButton.classList.toggle("d-none", button.dataset.role === "Admin");
    const account = DEMO_ACCOUNTS[button.dataset.role];
    const hint = document.getElementById("login-credentials-hint");
    if (hint && account) hint.textContent = `Demo credentials — Username: ${account.username} · Password: ${account.password}`;
    document.querySelectorAll("[data-role]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    form?.querySelector("input[name=username]")?.focus();
  }));
  form?.querySelector('select[name="role"]')?.addEventListener("change", (event) => {
    const registerButton = document.getElementById("btn-register");
    if (registerButton) registerButton.classList.toggle("d-none", event.target.value === "Admin");
  });
  document.querySelectorAll("[data-prefill-action]").forEach((button) => button.addEventListener("click", () => runAction(button.dataset.prefillAction, { scenario: button.textContent.trim() })));

  if (loggedIn && currentPage === "index.html") {
    document.querySelectorAll("main > section.container").forEach((section) => section.classList.add("d-none"));
    const role = sessionStorage.getItem("aicte_demo_role") || "Student";
    const views = {
      Student: { title: "Student Portal", intro: "Your student services", cards: `<div class="col-md-6 col-lg-3"><div class="card service-card"><div class="card-body p-4"><i class="bi bi-file-earmark-plus text-primary fs-3 mb-3"></i><h2 class="h5">Apply for Course</h2><p class="small text-secondary">Start a course application.</p><button id="btn-apply-course-home" data-action="apply_course" class="btn btn-primary action-btn">Apply</button></div></div></div><div class="col-md-6 col-lg-3"><div class="card service-card"><div class="card-body p-4"><i class="bi bi-upload text-primary fs-3 mb-3"></i><h2 class="h5">Upload Document</h2><p class="small text-secondary">Submit a supporting document.</p><a id="btn-upload-document-home" data-action="document_upload" href="upload.html" class="btn btn-outline-primary action-btn">Upload</a></div></div></div><div class="col-md-6 col-lg-3"><div class="card service-card"><div class="card-body p-4"><i class="bi bi-award text-primary fs-3 mb-3"></i><h2 class="h5">Certificate</h2><p class="small text-secondary">Download your certificate.</p><button id="btn-download-certificate-home" data-action="download_certificate" class="btn btn-outline-primary action-btn">Download</button></div></div></div><div class="col-md-6 col-lg-3"><div class="card service-card"><div class="card-body p-4"><i class="bi bi-credit-card text-primary fs-3 mb-3"></i><h2 class="h5">Pay Fees</h2><p class="small text-secondary">Open simulated payment.</p><a id="btn-pay-fees-home" data-action="pay_fees" href="payment.html" class="btn btn-outline-primary action-btn">Pay Now</a></div></div></div>` },
      Faculty: { title: "Faculty Portal", intro: "Your faculty services", cards: `<div class="col-md-6 col-lg-3"><div class="card service-card"><div class="card-body p-4"><i class="bi bi-person-check text-primary fs-3 mb-3"></i><h2 class="h5">Verify Student</h2><p class="small text-secondary">Review student verification.</p><button id="btn-verify-student-home" data-action="verify_student" class="btn btn-primary action-btn">Verify</button></div></div></div><div class="col-md-6 col-lg-3"><div class="card service-card"><div class="card-body p-4"><i class="bi bi-check2-square text-success fs-3 mb-3"></i><h2 class="h5">Approve Request</h2><p class="small text-secondary">Approve a pending request.</p><button id="btn-approve-request-home" data-action="request_approved" class="btn btn-outline-success action-btn">Approve</button></div></div></div><div class="col-md-6 col-lg-3"><div class="card service-card"><div class="card-body p-4"><i class="bi bi-x-circle text-danger fs-3 mb-3"></i><h2 class="h5">Reject Request</h2><p class="small text-secondary">Reject a pending request.</p><button id="btn-reject-request-home" data-action="request_rejected" class="btn btn-outline-danger action-btn">Reject</button></div></div></div><div class="col-md-6 col-lg-3"><div class="card service-card"><div class="card-body p-4"><i class="bi bi-file-earmark-arrow-up text-primary fs-3 mb-3"></i><h2 class="h5">Upload Result</h2><p class="small text-secondary">Submit an examination result.</p><button id="btn-upload-result-home" data-action="upload_result" class="btn btn-outline-primary action-btn">Upload</button></div></div></div>` },
      Admin: { title: "Admin Portal", intro: "Your administration services", cards: `<div class="col-md-6 col-lg-4"><div class="card service-card"><div class="card-body p-4"><i class="bi bi-bar-chart-line text-primary fs-3 mb-3"></i><h2 class="h5">View Reports</h2><p class="small text-secondary">Review portal activity reports.</p><button id="btn-view-reports-home" data-action="view_reports" class="btn btn-primary action-btn">View Reports</button></div></div></div><div class="col-md-6 col-lg-4"><div class="card service-card"><div class="card-body p-4"><i class="bi bi-arrow-clockwise text-primary fs-3 mb-3"></i><h2 class="h5">Restart Service</h2><p class="small text-secondary">Trigger a service restart.</p><button id="btn-restart-service-home" data-action="restart_service" class="btn btn-outline-primary action-btn">Restart</button></div></div></div><div class="col-md-6 col-lg-4"><div class="card service-card"><div class="card-body p-4"><i class="bi bi-journal-check text-primary fs-3 mb-3"></i><h2 class="h5">Generate Audit</h2><p class="small text-secondary">Request an audit report.</p><button id="btn-generate-audit-home" data-action="generate_audit" class="btn btn-outline-primary action-btn">Generate Audit</button></div></div></div>` }
    };
    const view = views[role] || views.Student;
    const statusStrip = document.querySelector(".status-strip");
    if (statusStrip) statusStrip.insertAdjacentHTML("beforebegin", `<section class="container py-5 role-view"><div class="section-label">${view.title}</div><h1 class="h2 mb-1">Welcome back</h1><p class="text-secondary mb-4">${view.intro}. Only ${role.toLowerCase()} features are shown.</p><div class="row g-4">${view.cards}</div><div id="action-result" class="card result-card mt-4 d-none"><div class="card-body"><div class="result-icon"><i class="bi bi-check-circle-fill me-2"></i>Action Result</div><div class="mt-2 fw-semibold" id="result-action"></div><div class="small text-secondary" id="result-detail"></div></div></div></section>`);
    document.querySelectorAll(".action-btn").forEach((button) => {
      if (!button.dataset.bound) { button.dataset.bound = "true"; button.addEventListener("click", () => runAction(button.dataset.action, { source: button.id || "role-action" })); }
    });
  }
});
