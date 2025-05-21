document.addEventListener("DOMContentLoaded", () => {
    // Log to confirm the script is running
    console.log("main.js loaded and DOM fully parsed.");

    // Check if Chart.js is loaded
    if (typeof Chart === "undefined") {
        console.error("Chart.js is not loaded. Please include it in your HTML.");
        const chartErrorDiv = document.getElementById("progress-charts");
        if (chartErrorDiv) {
            chartErrorDiv.innerHTML = "<p style=\"color: red;\">Error: Charting library (Chart.js) is missing. Cannot display charts.</p>";
        }
        return;
    }

    // Get the canvas element
    const ctx = document.getElementById("mainProgressChart");
    if (!ctx) {
        console.warn("Canvas element with ID \"mainProgressChart\" not found. Cannot render chart.");
        return;
    }

    // --- Progress Chart: Workout Duration Over Time ---
    // This assumes `workoutDataForChart` is made available globally by Flask in index.html,
    // e.g., <script>const workoutDataForChart = {{ workouts|tojson|safe }};</script>
    // `workouts` should be an array of objects, each with 'date' and 'duration'.
    
    let workoutData = [];
    if (typeof workoutDataForChart !== "undefined" && Array.isArray(workoutDataForChart)) {
        workoutData = workoutDataForChart;
    } else {
        console.warn("Global variable 'workoutDataForChart' not found or not an array. Chart will be empty or use placeholder data.");
        const chartContainer = ctx.parentElement;
        if (chartContainer && workoutData.length === 0) {
            const noDataMsg = document.createElement("p");
            noDataMsg.textContent = "No workout data available to display charts yet. Log some workouts!";
            noDataMsg.style.textAlign = "center";
            if (!chartContainer.querySelector(".no-chart-data-message")) {
                noDataMsg.className = "no-chart-data-message";
                chartContainer.appendChild(noDataMsg);
            }
        }
    }

    const sortedWorkouts = [...workoutData].sort((a, b) => new Date(a.date) - new Date(b.date));

    const labels = sortedWorkouts.map(workout => {
        const d = new Date(workout.date);
        return `${d.getFullYear()}-${("0" + (d.getMonth() + 1)).slice(-2)}-${("0" + d.getDate()).slice(-2)}`;
    });
    const durations = sortedWorkouts.map(workout => workout.duration);

    if (labels.length > 0 && durations.length > 0) {
        new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Workout Duration (minutes)",
                    data: durations,
                    borderColor: "rgba(75, 192, 192, 1)",
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    tension: 0.1,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Duration (minutes)"
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: "Date"
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: "top",
                    },
                    tooltip: {
                        mode: "index",
                        intersect: false,
                    }
                }
            }
        });
    } else {
        console.log("Not enough data to render the workout duration chart.");
    }
});
