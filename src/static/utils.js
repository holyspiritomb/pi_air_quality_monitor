function xAxisHours(labelarray, n) {
    // show n hours of data on the chart
    const lastmeasindex = labelarray.length - 1;
    const lastmeas = Date.parse(labelarray[lastmeasindex]);
    const hoursAgo = dateFns.subHours(lastmeas, n);
    return hoursAgo
}

const chartPlugins = {
    zoom: {
        events: ['touchstart', 'touchmove'],
        pan: {
            enabled: true,
            mode: 'x'
        },
        zoom: {
            wheel: {
                enabled: true
            },
            pinch: {
                enabled: true
            },
            mode: 'x',
            limits : {
                y: {min: 0, max: 'original'}
            }
        }
    },
}

const chartElements = {
    line: {
        borderwidth: 1
    }
}

function chartOptions(labelarray, n) {
    const xHours = xAxisHours(labelarray, n);
    return {
        elements: chartElements,
        scales: {
            y: {
                beginAtZero: true
            },
            x: {
                type: 'time',
                min: xHours,
            }
        },
        plugins: chartPlugins,
    }
}
