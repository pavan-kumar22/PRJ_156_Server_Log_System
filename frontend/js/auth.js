(function guardHomePage() {
  const page = window.location.pathname.split("/").pop() || "index.html";
  const isProfile = page === "profile.html";
  if (isProfile && sessionStorage.getItem("aicte_demo_authenticated_v2") !== "true") {
    window.location.replace("login.html");
  }
})();
