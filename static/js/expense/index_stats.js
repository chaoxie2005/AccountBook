

function categoryStats(title, data) {
    var myChart = echarts.init(document.getElementById('categoryStats'));
    var option = {
        title: {
            text: title,
            left: 'center',
        },
        tooltip: {
            trigger: 'item'
        },
        legend: {
            orient: 'horizontal',
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
                        fontSize: 18,
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: false
                },
                data: data
            }
        ]
    };
    myChart.setOption(option);
}

function dateStats(title, data) {
    var myChart = echarts.init(document.getElementById('dateStats'));
    var option = {
        title: {
            text: title,
            left: 'center',
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '10%', // 默认底部边距
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                data: data.key,
                axisTick: {
                    alignWithLabel: true
                }
            }
        ],
        dataZoom: [
            {
                type: 'inside',
                xAxisIndex: [0],
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
                data: data.value,
                label: {
                    show: true,
                    position: 'top',
                    formatter: '{c} 元'
                }
            }
        ]
    };
    myChart.setOption(option);
}


function getDataSetStats() {
    fetch('/expense/index_stats/').then((res) => res.json())
        .then((data) => {
            categoryStats('支出比例【本年】', data.category)
            dateStats('每月支出【本年】', data.month)
        })
}

document.onload = getDataSetStats()