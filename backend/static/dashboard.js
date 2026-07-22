let batchChart = null;

let realtimeChart = null;

let comparisonChart = null;
 
async function loadDashboard() {
 
    try {
 
        // -----------------------------

        // Fetch APIs

        // -----------------------------

        const batch = await fetch("/api/batch").then(r => r.json());

        const realtime = await fetch("/api/realtime").then(r => r.json());

        const comparison = await fetch("/api/comparison").then(r => r.json());
 
        // -----------------------------

        // Last Updated

        // -----------------------------

        document.getElementById("lastUpdated").innerHTML =

            "Last Updated: " + new Date().toLocaleString();
 
        // -----------------------------

        // KPI Cards

        // -----------------------------

        document.getElementById("batchRecords").innerHTML =

            batch.length;
 
        document.getElementById("realtimeRecords").innerHTML =

            realtime.green_records + realtime.red_records;
 
        document.getElementById("batchTotal").innerHTML =

            (

                batch[0].total_passengers +

                batch[1].total_passengers

            ).toLocaleString();
 
        document.getElementById("realtimeTotal").innerHTML =

            (

                realtime.green_total +

                realtime.red_total

            ).toLocaleString();
 
        document.getElementById("greenTotal").innerHTML =

            realtime.green_total.toLocaleString();
 
        document.getElementById("redTotal").innerHTML =

            realtime.red_total.toLocaleString();
 
        // -----------------------------

        // Batch Details

        // -----------------------------

        document.getElementById("batchText").innerHTML = `
<h3>Green Line</h3>
<p><b>Total:</b> ${batch[0].total_passengers.toLocaleString()}</p>
<p><b>Average:</b> ${batch[0].average_passengers.toFixed(2)}</p>
 
            <hr>
 
            <h3>Red Line</h3>
<p><b>Total:</b> ${batch[1].total_passengers.toLocaleString()}</p>
<p><b>Average:</b> ${batch[1].average_passengers.toFixed(2)}</p>

        `;
 
        // -----------------------------

        // Realtime Details

        // -----------------------------

        document.getElementById("realtimeText").innerHTML = `
<h3>Green</h3>
<p><b>Total:</b> ${realtime.green_total.toLocaleString()}</p>
<p><b>Average:</b> ${realtime.green_average.toFixed(2)}</p>
 
            <hr>
 
            <h3>Red</h3>
<p><b>Total:</b> ${realtime.red_total.toLocaleString()}</p>
<p><b>Average:</b> ${realtime.red_average.toFixed(2)}</p>

        `;
 
        // -----------------------------

        // Comparison Details

        // -----------------------------

        document.getElementById("comparisonText").innerHTML = `
<div style="text-align:center">
 
                <h3>Batch Records: ${batch.length}</h3>
 
                <h3>Realtime Records:

                ${realtime.green_records + realtime.red_records}</h3>
 
            </div>

        `;
 
        // -----------------------------

        // Destroy old charts

        // -----------------------------

        if (batchChart) batchChart.destroy();

        if (realtimeChart) realtimeChart.destroy();

        if (comparisonChart) comparisonChart.destroy();
 
        // -----------------------------

        // Batch Chart

        // -----------------------------

        batchChart = new Chart(

            document.getElementById("batchChart"),

            {

                type: "doughnut",
 
                data: {

                    labels: ["Green", "Red"],
 
                    datasets: [{

                        label: "Batch Passengers",
 
                        data: [

                            batch[0].total_passengers,

                            batch[1].total_passengers

                        ],
 
                        backgroundColor: [

                            "#2ecc71",

                            "#e74c3c"

                        ]

                    }]

                },
 
                options: {

                    responsive: true,

                    plugins: {

                        legend: {

                            position: "top"

                        }

                    }

                }

            }

        );
 
        // -----------------------------

        // Realtime Chart

        // -----------------------------

        realtimeChart = new Chart(

            document.getElementById("realtimeChart"),

            {

                type: "doughnut",
 
                data: {

                    labels: ["Green", "Red"],
 
                    datasets: [{

                        label: "Realtime Passengers",
 
                        data: [

                            realtime.green_total,

                            realtime.red_total

                        ],
 
                        backgroundColor: [

                            "#2ecc71",

                            "#e74c3c"

                        ]

                    }]

                },
 
                options: {

                    responsive: true,

                    plugins: {

                        legend: {

                            position: "top"

                        }

                    }

                }

            }

        );
 
        // -----------------------------

        // Comparison Chart

        // -----------------------------

        comparisonChart = new Chart(

            document.getElementById("comparisonChart"),

            {

                type: "bar",
 
                data: {
 
                    labels: ["Batch", "Realtime"],
 
                    datasets: [{
 
                        label: "Records",
 
                        data: [

                            batch.length,

                            realtime.green_records +

                            realtime.red_records

                        ],
 
                        backgroundColor: [

                            "#1976d2",

                            "#ff9800"

                        ]

                    }]

                },
 
                options: {
 
                    responsive: true,
 
                    plugins: {
 
                        legend: {

                            display: true

                        }

                    },
 
                    scales: {
 
                        y: {

                            beginAtZero: true

                        }

                    }

                }

            }

        );
 
    } catch (error) {
 
        console.error(error);
 
        document.getElementById("lastUpdated").innerHTML =

            "Error loading dashboard";
 
    }

}
 
// -----------------------------

// Initial Load

// -----------------------------

loadDashboard();
 
// -----------------------------

// Auto Refresh Every 10 Seconds

// -----------------------------

setInterval(loadDashboard, 10000);
 
