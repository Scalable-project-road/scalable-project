/* ==========================================================
   LUAS PASSENGER ANALYTICS DASHBOARD
   dashboard.js
========================================================== */
 
/* ==========================
   GLOBAL VARIABLES
========================== */
 
let batchChart = null;
let realtimeChart = null;
let comparisonChart = null;
 
let refreshSeconds = 10;
 
const REFRESH_INTERVAL = 10000;
 
/* ==========================
   NUMBER FORMATTER
========================== */
 
function formatNumber(value){
 
    if(value === undefined || value === null)
        return "0";
 
    return Number(value).toLocaleString();
 
}
 
/* ==========================
   ANIMATED COUNTER
========================== */
 
function animateValue(elementId,start,end,duration){
 
    const obj=document.getElementById(elementId);
 
    if(!obj) return;
 
    if(start===end){
 
        obj.innerHTML=formatNumber(end);
 
        return;
 
    }
 
    const range=end-start;
 
    const stepTime=Math.abs(Math.floor(duration/range));
 
    let current=start;
 
    const increment=end>start?1:-1;
 
    const timer=setInterval(()=>{
 
        current+=increment;
 
        obj.innerHTML=formatNumber(current);
 
        if(current===end){
 
            clearInterval(timer);
 
        }
 
    },Math.max(stepTime,1));
 
}
 
/* ==========================
   REFRESH COUNTDOWN
========================== */
 
function startCountdown(){
 
    refreshSeconds=10;
 
    const timer=setInterval(()=>{
 
        refreshSeconds--;
 
        const label=document.getElementById("refreshCountdown");
 
        if(label){
 
            label.innerHTML="Refreshing in "+refreshSeconds+"s";
 
        }
 
        if(refreshSeconds<=0){
 
            clearInterval(timer);
 
        }
 
    },1000);
 
}
 
/* ==========================
   LOAD DASHBOARD
========================== */
 
async function loadDashboard(){
 
    try{
 
        startCountdown();
 
        const batchResponse=
            await fetch("/api/batch");
 
        const realtimeResponse=
            await fetch("/api/realtime");
 
        const comparisonResponse=
            await fetch("/api/comparison");
 
        const batch=
            await batchResponse.json();
 
        const realtime=
            await realtimeResponse.json();
 
        const comparison=
            await comparisonResponse.json();
 
        updateKPIs(batch,realtime);
 
        updateStatistics(batch,realtime);
 
        drawBatchChart(batch);
 
        drawRealtimeChart(realtime);
 
        drawComparisonChart(comparison);
 
        updateTime();
 
    }
 
    catch(error){
 
        console.error(error);
 
        updateStatus(false);
 
    }
 
}
/* ==========================================================
   UPDATE KPI CARDS
========================================================== */
 
function updateKPIs(batch, realtime) {
 
    const batchRecords = batch.length;
 
    const realtimeRecords =
        (realtime.green_records || 0) +
        (realtime.red_records || 0);
 
    const batchTotal = batch.reduce((sum, item) => {
 
        return sum + (item.total_passengers || 0);
 
    }, 0);
 
    const realtimeTotal =
        (realtime.green_total || 0) +
        (realtime.red_total || 0);
 
    animateValue(
        "batchRecords",
        0,
        batchRecords,
        600
    );
 
    animateValue(
        "realtimeRecords",
        0,
        realtimeRecords,
        600
    );
 
    animateValue(
        "batchTotal",
        0,
        batchTotal,
        800
    );
 
    animateValue(
        "realtimeTotal",
        0,
        realtimeTotal,
        800
    );
 
    animateValue(
        "greenTotal",
        0,
        realtime.green_total || 0,
        800
    );
 
    animateValue(
        "redTotal",
        0,
        realtime.red_total || 0,
        800
    );
 
}
 
/* ==========================================================
   PROCESSING STATISTICS
========================================================== */
 
function updateStatistics(batch, realtime) {
 
    document.getElementById("batchRecords2").innerHTML =
        batch.length;
 
    document.getElementById("realtimeRecords2").innerHTML =
        (realtime.green_records || 0) +
        (realtime.red_records || 0);
 
    document.getElementById("greenTotal2").innerHTML =
        formatNumber(realtime.green_total || 0);
 
    document.getElementById("redTotal2").innerHTML =
        formatNumber(realtime.red_total || 0);
 
}
 
/* ==========================================================
   LAST UPDATED
========================================================== */
 
function updateTime() {
 
    const now = new Date();
 
    const formatted =
        now.toLocaleDateString() +
        " " +
        now.toLocaleTimeString();
 
    document.getElementById("lastUpdated").innerHTML =
        "Last Updated : " + formatted;
 
}
 
/* ==========================================================
   STATUS PANEL
========================================================== */
 
function updateStatus(isOnline = true) {
 
    const statusCards = document.querySelectorAll(".status-card");
 
    statusCards.forEach(card => {
 
        if (isOnline) {
 
            card.style.borderLeft = "6px solid #27ae60";
 
            if (!card.innerHTML.startsWith("🟢")) {
 
                card.innerHTML =
                    "🟢 " +
                    card.innerHTML.replace("🔴", "").trim();
 
            }
 
        } else {
 
            card.style.borderLeft = "6px solid #e74c3c";
 
            card.innerHTML =
                "🔴 Offline";
 
        }
 
    });
 
}
 
/* ==========================================================
   DESTROY OLD CHARTS
========================================================== */
 
function destroyCharts() {
 
    if (batchChart) {
 
        batchChart.destroy();
 
    }
 
    if (realtimeChart) {
 
        realtimeChart.destroy();
 
    }
 
    if (comparisonChart) {
 
        comparisonChart.destroy();
 
    }
 
}
/* ==========================================================
   BATCH CHART
========================================================== */
 
function drawBatchChart(batch){
 
    if(batchChart){
 
        batchChart.destroy();
 
    }
 
    const labels = batch.map(item => item.line);
 
    const totals = batch.map(item => item.total_passengers);
 
    const averages = batch.map(item => item.average_passengers);
 
    const ctx =
        document
            .getElementById("batchChart")
            .getContext("2d");
 
    batchChart = new Chart(ctx,{
 
        type:"bar",
 
        data:{
 
            labels:labels,
 
            datasets:[
 
                {
 
                    label:"Total Passengers",
 
                    data:totals,
 
                    backgroundColor:[
                        "#1565c0",
                        "#2ecc71"
                    ],
 
                    borderRadius:8
 
                },
 
                {
 
                    label:"Average Passengers",
 
                    data:averages,
 
                    backgroundColor:[
                        "#42a5f5",
                        "#81c784"
                    ],
 
                    borderRadius:8
 
                }
 
            ]
 
        },
 
        options:{
 
            responsive:true,
 
            maintainAspectRatio:false,
 
            plugins:{
 
                legend:{
                    position:"top"
                }
 
            },
 
            animation:{
                duration:1200
            }
 
        }
 
    });
 
    document.getElementById("batchText").innerHTML =
        "<strong>Historical Batch Processing Results</strong>";
 
}
 
/* ==========================================================
   REALTIME CHART
========================================================== */
 
function drawRealtimeChart(realtime){
 
    if(realtimeChart){
 
        realtimeChart.destroy();
 
    }
 
    const ctx =
        document
            .getElementById("realtimeChart")
            .getContext("2d");
 
    realtimeChart = new Chart(ctx,{
 
        type:"doughnut",
 
        data:{
 
            labels:[
 
                "Green Line",
 
                "Red Line"
 
            ],
 
            datasets:[{
 
                data:[
 
                    realtime.green_total,
 
                    realtime.red_total
 
                ],
 
                backgroundColor:[
 
                    "#2ecc71",
 
                    "#e74c3c"
 
                ]
 
            }]
 
        },
 
        options:{
 
            responsive:true,
 
            maintainAspectRatio:false,
 
            plugins:{
 
                legend:{
                    position:"bottom"
                }
 
            },
 
            animation:{
                animateRotate:true,
 
                duration:1400
 
            }
 
        }
 
    });
 
    document.getElementById("realtimeText").innerHTML =
 
        "<strong>Current Streaming Window</strong><br><br>" +
 
        "Green Records : <b>" +
        realtime.green_records +
        "</b><br>" +
 
        "Red Records : <b>" +
        realtime.red_records +
        "</b>";
 
}
 
/* ==========================================================
   COMPARISON CHART
========================================================== */
 
function drawComparisonChart(comparison){
 
    if(comparisonChart){
 
        comparisonChart.destroy();
 
    }
 
    const batchRecords =
        comparison.batch.length;
 
    const realtimeRecords =
        comparison.realtime.green_records +
        comparison.realtime.red_records;
 
    const ctx =
        document
            .getElementById("comparisonChart")
            .getContext("2d");
 
    comparisonChart = new Chart(ctx,{
 
        type:"bar",
 
        data:{
 
            labels:[
 
                "Batch",
 
                "Realtime"
 
            ],
 
            datasets:[{
 
                label:"Records",
 
                data:[
 
                    batchRecords,
 
                    realtimeRecords
 
                ],
 
                backgroundColor:[
 
                    "#1565c0",
 
                    "#f39c12"
 
                ],
 
                borderRadius:8
 
            }]
 
        },
 
        options:{
 
            indexAxis:"y",
 
            responsive:true,
 
            maintainAspectRatio:false,
 
            plugins:{
 
                legend:{
 
                    display:true
 
                }
 
            },
 
            animation:{
 
                duration:1200
 
            }
 
        }
 
    });
 
    document.getElementById("comparisonText").innerHTML =
 
        "<strong>Lambda Architecture Comparison</strong><br><br>" +
 
        "Batch Records : <b>" +
        batchRecords +
        "</b><br>" +
 
        "Realtime Records : <b>" +
        realtimeRecords +
        "</b>";
 
}
/* ==========================================================
   DASHBOARD HEALTH CHECK
========================================================== */
 
function dashboardHealth(batch, realtime) {
 
    const batchOK = batch && batch.length > 0;
 
    const realtimeOK =
        (realtime.green_records || 0) +
        (realtime.red_records || 0) > 0;
 
    if (batchOK && realtimeOK) {
 
        updateStatus(true);
 
    } else {
 
        updateStatus(false);
 
    }
 
}
 
/* ==========================================================
   WINDOW INFORMATION
========================================================== */
 
function updateWindowInformation(realtime) {
 
    if (!document.getElementById("comparisonText"))
        return;
 
    let text = "";
 
    if (realtime.window_start) {
 
        text +=
            "<br><b>Window Start:</b> " +
            realtime.window_start;
 
    }
 
    if (realtime.window_end) {
 
        text +=
            "<br><b>Window End:</b> " +
            realtime.window_end;
 
    }
 
    if (text !== "") {
 
        document.getElementById("comparisonText").innerHTML += text;
 
    }
 
}
 
/* ==========================================================
   API RESPONSE TIMER
========================================================== */
 
async function timedFetch(url) {
 
    const start = performance.now();
 
    const response = await fetch(url);
 
    const data = await response.json();
 
    const end = performance.now();
 
    return {
 
        data: data,
 
        time: Math.round(end - start)
 
    };
 
}
 
/* ==========================================================
   REFRESH NOTIFICATION
========================================================== */
 
function showRefreshMessage() {
 
    console.log(
 
        "Dashboard refreshed at",
 
        new Date().toLocaleTimeString()
 
    );
 
}
 
/* ==========================================================
   LOADING EFFECT
========================================================== */
 
function showLoading() {
 
    document.querySelectorAll(".card").forEach(card => {
 
        card.style.opacity = ".6";
 
    });
 
}
 
function hideLoading() {
 
    document.querySelectorAll(".card").forEach(card => {
 
        card.style.opacity = "1";
 
    });
 
}
 
/* ==========================================================
   REFRESH DASHBOARD
========================================================== */
 
async function refreshDashboard() {
 
    try {
 
        showLoading();
 
        const batchResult =
            await timedFetch("/api/batch");
 
        const realtimeResult =
            await timedFetch("/api/realtime");
 
        const comparisonResult =
            await timedFetch("/api/comparison");
 
        const batch =
            batchResult.data;
 
        const realtime =
            realtimeResult.data;
 
        const comparison =
            comparisonResult.data;
 
        updateKPIs(batch, realtime);
 
        updateStatistics(batch, realtime);
 
        destroyCharts();
 
        drawBatchChart(batch);
 
        drawRealtimeChart(realtime);
 
        drawComparisonChart(comparison);
 
        updateWindowInformation(realtime);
 
        dashboardHealth(batch, realtime);
 
        updateTime();
 
        hideLoading();
 
        showRefreshMessage();
 
        console.log(
 
            "Batch API:",
 
            batchResult.time + " ms"
 
        );
 
        console.log(
 
            "Realtime API:",
 
            realtimeResult.time + " ms"
 
        );
 
        console.log(
 
            "Comparison API:",
 
            comparisonResult.time + " ms"
 
        );
 
    }
 
    catch (error) {
 
        console.error(error);
 
        updateStatus(false);
 
        hideLoading();
 
    }
 
}
 
/* ==========================================================
   RESET DASHBOARD
========================================================== */
 
function resetDashboard() {
 
    destroyCharts();
 
    document.querySelectorAll(".kpi-card h1").forEach(item => {
 
        item.innerHTML = "0";
 
    });
 
}
/* ==========================================================
   AUTO REFRESH
========================================================== */
 
function startAutoRefresh() {
 
    refreshDashboard();
 
    setInterval(() => {
 
        refreshDashboard();
 
        startCountdown();
 
    }, REFRESH_INTERVAL);
 
}
 
/* ==========================================================
   PAGE INITIALIZATION
========================================================== */
 
function initializeDashboard() {
 
    console.log("==========================================");
    console.log("Luas Passenger Analytics Dashboard");
    console.log("Cloud Computing Project");
    console.log("==========================================");
 
    resetDashboard();
 
    startCountdown();
 
    startAutoRefresh();
 
}
 
/* ==========================================================
   WINDOW EVENTS
========================================================== */
 
window.addEventListener("load", () => {
 
    initializeDashboard();
 
});
 
/* Refresh dashboard when browser tab becomes active */
 
window.addEventListener("focus", () => {
 
    console.log("Window Active");
 
    refreshDashboard();
 
});
 
/* ==========================================================
   KEYBOARD SHORTCUTS
========================================================== */
 
document.addEventListener("keydown", (event) => {
 
    switch (event.key.toLowerCase()) {
 
        case "r":
 
            console.log("Manual Refresh");
 
            refreshDashboard();
 
            break;
 
        case "h":
 
            console.log("Dashboard Health Check");
 
            break;
 
        case "c":
 
            console.clear();
 
            console.log("Console Cleared");
 
            break;
 
    }
 
});
 
/* ==========================================================
   WINDOW RESIZE
========================================================== */
 
window.addEventListener("resize", () => {
 
    if (batchChart) {
 
        batchChart.resize();
 
    }
 
    if (realtimeChart) {
 
        realtimeChart.resize();
 
    }
 
    if (comparisonChart) {
 
        comparisonChart.resize();
 
    }
 
});
 
/* ==========================================================
   CONNECTION CHECK
========================================================== */
 
async function checkConnection() {
 
    try {
 
        const response = await fetch("/api/batch");
 
        if (response.ok) {
 
            updateStatus(true);
 
        } else {
 
            updateStatus(false);
 
        }
 
    }
 
    catch (err) {
 
        updateStatus(false);
 
    }
 
}
 
/* ==========================================================
   PERIODIC HEALTH CHECK
========================================================== */
 
setInterval(() => {
 
    checkConnection();
 
}, 30000);
 
/* ==========================================================
   EXPORT DASHBOARD DATA
========================================================== */
 
async function exportDashboardData() {
 
    try {
 
        const batch = await fetch("/api/batch").then(r => r.json());
 
        const realtime = await fetch("/api/realtime").then(r => r.json());
 
        const exportObject = {
 
            exported_at: new Date().toISOString(),
 
            batch: batch,
 
            realtime: realtime
 
        };
 
        console.log("Dashboard Export");
 
        console.log(exportObject);
 
    }
 
    catch (error) {
 
        console.error(error);
 
    }
 
}
 
/* ==========================================================
   APPLICATION READY
========================================================== */
 
console.log("Dashboard JavaScript Loaded Successfully");
 
console.log("Waiting for page initialization...");
 
/* ==========================================================
   END OF FILE
========================================================== */
 
