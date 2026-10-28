// Responsive defaults: keep chart text readable on phones and desktop.
// Individual chart configurations below can still override these defaults.
if (window.Chart) {
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;
    Chart.defaults.font.family = "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    Chart.defaults.font.size = window.matchMedia("(max-width: 760px)").matches ? 11 : 12;
    Chart.defaults.color = "#cbd5e1";
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
    Chart.defaults.plugins.legend.labels.boxHeight = 10;
    Chart.defaults.plugins.legend.labels.padding = window.matchMedia("(max-width: 760px)").matches ? 10 : 14;
}

const ctx = document.getElementById('regionChart').getContext('2d');

new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Asia', 'Europe', 'North America', 'South America', 'Africa'],
        datasets: [{
            label: 'Number of Orders',
            data: [
                regionData?.[0] || 0,
                regionData?.[1] || 0,
                regionData?.[2] || 0,
                regionData?.[3] || 0,
                regionData?.[4] || 0
            ],
            backgroundColor: [
                '#3b82f6',
                '#22c55e',
                '#f59e0b',
                '#ef4444',
                '#a855f7'
            ],
            borderRadius: 6
        }]
    },
    options: {
        indexAxis: 'y',
        responsive: true,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            }
        }
    }
});

const ctx2 = document.getElementById('transportChart').getContext('2d');

new Chart(ctx2, {
    type: 'doughnut',
    data: {
        labels: ['Truck', 'Rail', 'Ship', 'Air'],
        datasets: [{
            data: [
                transportData?.[0] || 0,
                transportData?.[1] || 0,
                transportData?.[2] || 0,
                transportData?.[3] || 0
            ],
            backgroundColor: [
                '#38bdf8',
                '#22c55e',
                '#f59e0b',
                '#ef4444'
            ],
            borderWidth: 0
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,

        cutout: '60%',
        radius: '85%',

        plugins: {
            legend: {
                position: 'top',
                labels: {
                    color: '#cbd5f5'
                }
            }
        }
    }
});

const ctx3 = document.getElementById('weatherChart').getContext('2d');

new Chart(ctx3, {
    type: 'bar',
    data: {
        labels: ['Clear', 'Rain', 'Storm', 'Fog'],
        datasets: [
            {
                label: 'Low Risk',
                data: [
                    weatherData?.[0]?.Low || 0,
                    weatherData?.[1]?.Low || 0,
                    weatherData?.[2]?.Low || 0,
                    weatherData?.[3]?.Low || 0
                ],
                backgroundColor: '#22c55e'
            },
            {
                label: 'Medium Risk',
                data: [
                    weatherData?.[0]?.Medium || 0,
                    weatherData?.[1]?.Medium || 0,
                    weatherData?.[2]?.Medium || 0,
                    weatherData?.[3]?.Medium || 0
                ],
                backgroundColor: '#f59e0b'
            },
            {
                label: 'High Risk',
                data: [
                    weatherData?.[0]?.High || 0,
                    weatherData?.[1]?.High || 0,
                    weatherData?.[2]?.High || 0,
                    weatherData?.[3]?.High || 0
                ],
                backgroundColor: '#ef4444'
            }
        ]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                labels: {
                    color: '#cbd5f5'
                }
            }
        },
        scales: {
            x: {
                stacked: true,
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            },
            y: {
                stacked: true,
                beginAtZero: true,
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            }
        }
    }
});

const ctx4 = document.getElementById('trafficChart').getContext('2d');

new Chart(ctx4, {
    type: 'line',
    data: {
        labels: ['Low Traffic', 'Medium Traffic', 'High Traffic'],
        datasets: [{
            label: 'Average Delay (Days)',
            data: [
                trafficData?.[0] || 0,
                trafficData?.[1] || 0,
                trafficData?.[2] || 0
            ],

            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.2)',

            fill: true,
            tension: 0.4,

            pointBackgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
            pointRadius: 6,
            pointHoverRadius: 8
        }]
    },
    options: {
        responsive: true,

        plugins: {
            legend: {
                labels: {
                    color: '#cbd5f5'
                }
            }
        },

        scales: {
            x: {
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                },
                title: {
                    display: true,
                    text: 'Delay (Days)',
                    color: '#cbd5f5'
                }
            }
        }
    }
});

const ctx5 = document.getElementById('demandChart').getContext('2d');

new Chart(ctx5, {
    type: 'bar',
    data: {
        labels: ['Low', 'Medium', 'High'],
        datasets: [{
            label: 'Demand Distribution',
            data: [
                demandData?.[0] || 0,
                demandData?.[1] || 0,
                demandData?.[2] || 0
            ],
            backgroundColor: [
                '#22c55e',
                '#f59e0b',
                '#ef4444'
            ],
            borderRadius: 6,
            barThickness: 50
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            }
        }
    }
});

const ctx6 = document.getElementById('stockChart').getContext('2d');

new Chart(ctx6, {
    type: 'bar',
    data: {
        labels: ['Sufficient', 'Low', 'Out of Stock'],
        datasets: [
            {
                label: 'Low Risk',
                data: [
                    stockData?.Sufficient?.Low || 0,
                    stockData?.Low?.Low || 0,
                    stockData?.Out?.Low || 0
                ],
                backgroundColor: '#22c55e'
            },
            {
                label: 'Medium Risk',
                data: [
                    stockData?.Sufficient?.Medium || 0,
                    stockData?.Low?.Medium || 0,
                    stockData?.Out?.Medium || 0
                ],
                backgroundColor: '#f59e0b'
            },
            {
                label: 'High Risk',
                data: [
                    stockData?.Sufficient?.High || 0,
                    stockData?.Low?.High || 0,
                    stockData?.Out?.High || 0
                ],
                backgroundColor: '#ef4444'
            }
        ]
    },
    options: {
        indexAxis: 'y',
        responsive: true,
        plugins: {
            legend: {
                labels: {
                    color: '#cbd5f5'
                }
            }
        },
        scales: {
            x: {
                stacked: true,
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            },
            y: {
                stacked: true,
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            }
        }
    }
});

const ctx8 = document.getElementById('valueChart').getContext('2d');

new Chart(ctx8, {
    type: 'line',
    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Order Value ($)',
            data: [
                valueData?.[1] || 0,
                valueData?.[2] || 0,
                valueData?.[3] || 0,
                valueData?.[4] || 0,
                valueData?.[5] || 0,
                valueData?.[6] || 0,
                valueData?.[0] || 0
            ],

            borderColor: '#22c55e',
            backgroundColor: 'rgba(34, 197, 94, 0.2)',

            fill: true,
            tension: 0.4,

            pointBackgroundColor: [
                '#22c55e',
                '#3b82f6',
                '#f59e0b',
                '#ef4444',
                '#a855f7',
                '#06b6d4',
                '#eab308'
            ],
            pointRadius: 6,
            pointHoverRadius: 8
        }]
    },
    options: {
        responsive: true,

        plugins: {
            legend: {
                labels: {
                    color: '#cbd5f5'
                }
            }
        },

        scales: {
            x: {
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                },
                title: {
                    display: true,
                    text: 'Order Value ($)',
                    color: '#cbd5f5'
                }
            }
        }
    }
});

const ctx7 = document.getElementById('fuelChart').getContext('2d');
const lowRisk = [];
const mediumRisk = [];
const highRisk = [];

(fuelData || []).forEach(d => {
    const delay = d[0] || 0;
    const fuel = d[1] || 0;
    const risk = (d[2] || "").toLowerCase();

    const point = { x: fuel, y: delay };

    if (risk === "low") lowRisk.push(point);
    else if (risk === "medium") mediumRisk.push(point);
    else if (risk === "high") highRisk.push(point);
});

new Chart(ctx7, {
    type: 'scatter',
    data: {
        datasets: [
            {
                label: 'Low Risk',
                data: lowRisk,
                backgroundColor: '#22c55e'
            },
            {
                label: 'Medium Risk',
                data: mediumRisk,
                backgroundColor: '#f59e0b'
            },
            {
                label: 'High Risk',
                data: highRisk,
                backgroundColor: '#ef4444'
            }
        ]
    },
    options: {
        responsive: true,

        interaction: {
            mode: 'nearest',
            intersect: true
        },

        plugins: {
            legend: {
                labels: {
                    color: '#cbd5f5'
                }
            },
            tooltip: {
                mode: 'nearest',
                intersect: true,
                callbacks: {
                    label: function(context) {
                        const x = context.raw.x;
                        const y = context.raw.y;
                        const label = context.dataset.label;
                        return `${label} → Fuel: ${x}, Delay: ${y}`;
                    }
                }
            }
        },

        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Fuel Cost ($/unit)',
                    color: '#cbd5f5'
                },
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Delay (Days)',
                    color: '#cbd5f5'
                },
                ticks: {
                    color: '#cbd5f5'
                },
                grid: {
                    color: '#1e293b'
                }
            }
        }
    }
});