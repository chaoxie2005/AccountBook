function expensetypePie(title, data) {
    var myChart = echarts.init(document.getElementById('s1'));
    var option = {
        title: {
            text: title,
        },
        tooltip: {
            trigger: 'item'
        },
        legend: {
            bottom: '5%',
            left: 'center'
        },
        series: [
            {
                name: 'Access From',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: false,
                    position: 'center'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 40,
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: false
                },
                data: data,
            }
        ]
    };
    // 使用刚指定的配置项和数据显示图表。
    myChart.setOption(option);
}

function expensetypeBar(title, data) {
    var myChart = echarts.init(document.getElementById('s2'));
    var option = {
        title: {
            text: title
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        grid: {
            left: '10%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                data: data.captions,
                axisTick: {
                    alignWithLabel: true
                }
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: [
            {
                name: 'Direct',
                type: 'bar',
                barWidth: '60%',
                data: data.values,
            }
        ]
    };
    // 使用刚指定的配置项和数据显示图表。
    myChart.setOption(option);
}


function monthlyexpense(title, data) {
    var myChart = echarts.init(document.getElementById('s3'));
    const option = {
        title: {
            text: title
        },
        grid: {
            left: '15%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: data.captions,
        },
        yAxis: {
            type: 'value'
        },
        series: [
            {
                data: data.values,
                type: 'bar'
            }
        ]
    };
    // 使用刚指定的配置项和数据显示图表。
    myChart.setOption(option);
}

function Annualcumulativexpenditure(title, data) {
    var myChart = echarts.init(document.getElementById('s4'));
    const option = {
        title: {
            text: title
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['今年', '去年'],
            right: '10%'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        toolbox: {
            feature: {
                saveAsImage: {}
            }
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: data.month,
        },
        yAxis: {
            type: 'value'
        },
        series: [
            {
                name: '今年',
                type: 'line',
                data: data.this_year_values,
                smooth: true
            },
            {
                name: '去年',
                type: 'line',
                data: data.last_year_values,
                smooth: true
            }
        ]
    };
    // 使用刚指定的配置项和数据显示图表。
    myChart.setOption(option);
}

function getDataSetEcharts() {
    fetch('/expense/expense_s1/').then(res => res.json()).then((data) => {
        expensetypePie('支出类型【今年】', data);
    });
    fetch('/expense/expense_s2/').then(res => res.json()).then((data) => {
        expensetypeBar('支出类型【今年】', data);
    });
    fetch('/expense/expense_s3/').then(res => res.json()).then((data) => {
        values = data.values;
        mvi = data.max_value_index
        values[mvi] = {
            value: values[mvi],
            itemStyle: { color: '#a90000' }
        }
        newData = {
            captions: data.captions,
            values: values
        }
        monthlyexpense('每月支出【今年】', newData);
    });

    const currentDate = new Date();
    const thisYear = currentDate.getFullYear()
    fetch(`/expense/expense_s4/${thisYear}`).then((res) => res.json()).then((data) => {
        let s4_data = {}
        s4_data.month = data.captions;
        s4_data.this_year_values = data.values;
        fetch(`/expense/expense_s4/${thisYear - 1}`).then((res) => res.json()).then((data) => {
            s4_data.last_year_values = data.values;
            console.log(s4_data);
            Annualcumulativexpenditure('年度累计支出', s4_data)
        })
    })
}

document.onload = getDataSetEcharts()