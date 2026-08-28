const ACTIONS = Object.freeze({
  LOGIN_SUCCESS: "login_success", LOGIN_FAILURE: "login_failure", INVALID_TOKEN: "invalid_token", SESSION_TIMEOUT: "session_timeout", UNAUTHORIZED_ACCESS: "unauthorized_access", LOGOUT: "logout", REGISTER: "register", FORGOT_PASSWORD: "forgot_password",
  APPLY_COURSE: "apply_course", UPLOAD_DOCUMENT: "upload_document", DOWNLOAD_CERTIFICATE: "download_certificate", PAY_FEES: "pay_fees",
  PAYMENT_SUCCESS: "payment_success", PAYMENT_FAILURE: "payment_failure", PAYMENT_TIMEOUT: "payment_timeout", REFUND: "refund", DUPLICATE_TRANSACTION: "duplicate_transaction",
  VERIFY_STUDENT: "verify_student", REJECT_STUDENT: "reject_student", UPLOAD_RESULT: "upload_result", VIEW_APPLICATION: "view_application", VIEW_REPORTS: "view_reports", RESTART_SERVICE: "restart_service", GENERATE_AUDIT: "generate_audit",
  REQUEST_SUBMITTED: "request_submitted", REQUEST_PENDING: "request_pending", REQUEST_APPROVED: "request_approved", REQUEST_REJECTED: "request_rejected",
  DOCUMENT_UPLOAD: "document_upload", DOCUMENT_DOWNLOAD: "document_download", DOCUMENT_DELETE: "document_delete", DOCUMENT_INVALID: "document_invalid"
});
