let batchChart;
let realtimeChart;
let comparisonChart;
 
function animateValue(id, start, end, duration) {
 
    let obj = document.getElementById(id);
 
    let startTime = null;
 
    function animation(currentTime) {
 
        if (!startTime) startTime = currentTime;
 
        const progress = Math.min((currentTime - startTime) / duration, 1);
 
        obj.innerHTML = Math.floor(progress * (end - start) + start).toLocaleString();
 
        if (progress < 1) {
 
            requestAnimationFrame(animation);
 
        }
 
    }
 
    requestAnimationFrame(animation);
 
}
 
async function loadDashboard() {
 
    const batch = await fetch("/api/batch").then(r => r.json());
 
    const realtime = await fetch("/api/realtime").then(r => r.json());
 
    const comparison = await fetch("/api/comparison").then(r => r.json());
 
    document.getElementById("lastUpdated").innerHTML =
        "Last Updated: " + new Date().toLocaleString();
 
    animateValue("batchRecords", 0, batch.length, 1000);
 
    animateValue(
        "realtimeRecords",
        0,
        realtime.green_records + realtime.red_records,
        1000
    );
 
    animateValue(
        "batchTotal",
        0,
        batch[0].total_passengers + batch[1].total_passengers,
        1500
    );
 
    animateValue(
        "realtimeTotal",
        0,
        realtime.green_total + realtime.red_total,
        1500
    );
 
    animateValue("greenRealtime", 0, realtime.green_total, 1200);
 
    animateValue("redRealtime", 0, realtime.red_total, 1200);
 
    document.getElementById("batchData").innerHTML = `
<b>Green Line</b><br>
Total: ${batch[0].total_passengers.toLocaleString()}<br>
Average: ${batch[0].average_passengers.toFixed(2)}
<hr>
<b>Red Line</b><br>
Total: ${batch[1].total_passengers.toLocaleString()}<br>
Average: ${batch[1].average_passengers.toFixed(2)}
`;
 
    document.getElementById("realtimeData").innerHTML = `
Green Total: ${realtime.green_total.toLocaleString()}<br>
Green Avg: ${realtime.green_average.toFixed(2)}
<hr>
Red Total: ${realtime.red_total.toLocaleString()}<br>
Red Avg: ${realtime.red_average.toFixed(2)}
`;
 
    document.getElementById("comparisonData").innerHTML = `
Batch Records: ${comparison.batch.length}
<hr>
Realtime Green: ${realtime.green_total.toLocaleString()}<br>
Realtime Red: ${realtime.red_total.toLocaleString()}
`;
 
    if (batchChart) batchChart.destroy();
 
    batchChart = new Chart(
    document.getElementById("batchChart"),
    {
        type: "doughnut",
        data: {
            labels: ["Green Line", "Red Line"],
            datasets: [{
                data: [
                    batch[0].total_passengers,
                    batch[1].total_passengers
                ],
                backgroundColor: [
                    "#28a745",
                    "#dc3545"
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    }
);
 
    if (realtimeChart) realtimeChart.destroy();
 
    realtimeChart = new Chart(
    document.getElementById("realtimeChart"),
    {
        type: "doughnut",
        data: {
            labels: ["Green", "Red"],
            datasets: [{
                data: [
                    realtime.green_total,
                    realtime.red_total
                ],
                backgroundColor: [
                    "#28a745",
                    "#dc3545"
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    }
);
 
    if (comparisonChart) comparisonChart.destroy();
 
    comparisonChart = new Chart(
    document.getElementById("comparisonChart"),
    {
        type: "bar",
        data: {
            labels: ["Batch", "Realtime"],
            datasets: [{
                label: "Records",
                data: [
                    comparison.batch.length,
                    realtime.green_records + realtime.red_records
                ],
                backgroundColor: [
                    "#007bff",
                    "#ffc107"
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    }
);
 
}
 
loadDashboard();
 
setInterval(loadDashboard, 10000);
 
