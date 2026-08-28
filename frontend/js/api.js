const API_CONFIG = Object.freeze({
    BASE_URL: "http://localhost:8002",
    ACTION_ENDPOINT: "/api/action",
    DEMO_MODE: false
});

async function sendAction(action, data = {}) {

    const payload = {
        action: action,
        data: data,
        timestamp: new Date().toISOString()
    };

    console.log("Sending AICTE action:", payload);

    try {

        const response = await fetch(
            `${API_CONFIG.BASE_URL}${API_CONFIG.ACTION_ENDPOINT}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            }
        );

        const result = await response.json();

        console.log("AICTE backend response:", result);

        if (!response.ok) {

            const errorMessage =
                typeof result.detail === "string"
                    ? result.detail
                    : result.detail?.error || `HTTP ${response.status}`;

            throw new Error(errorMessage);
        }

        return result;

    } catch (error) {

        console.error("AICTE API error:", error);

        alert(
            "AICTE Action API Error:\n\n" +
            error.message
        );

        throw error;
    }
}