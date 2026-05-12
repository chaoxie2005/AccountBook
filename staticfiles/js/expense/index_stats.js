

function categoryStats(title, data) {
    var myChart = echarts.init(document.getElementById('categoryStats'));
    var option = {
        tooltip: {
            trigger: 'item',
            formatter: '{b}: ¥{c} ({d}%)'
        },
        legend: {
            orient: 'horizontal',
            bottom: '0',
            left: 'center',
            textStyle: { color: '#858796' }
        },
        series: [
            {
                name: '支出分类',
                type: 'pie',
                radius: ['50%', '70%'],
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
                        fontSize: '18',
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: false
                },
                data: data,
                color: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796']
            }
        ]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

function dateStats(title, data) {
    var myChart = echarts.init(document.getElementById('dateStats'));
    var option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '10%',
            top: '10%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                data: data.key,
                axisTick: { alignWithLabel: true },
                axisLine: { lineStyle: { color: '#e3e6f0' } },
                axisLabel: { color: '#858796' }
            }
        ],
        yAxis: [
            {
                type: 'value',
                axisLine: { show: false },
                splitLine: { lineStyle: { color: '#e3e6f0', type: 'dashed' } },
                axisLabel: { color: '#858796' }
            }
        ],
        series: [
            {
                name: '支出金额',
                type: 'bar',
                barWidth: '60%',
                data: data.value,
                itemStyle: {
                    color: '#4e73df',
                    borderRadius: [4, 4, 0, 0]
                },
                label: {
                    show: true,
                    position: 'top',
                    formatter: '¥{c}',
                    color: '#4e73df'
                }
            }
        ]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

fetch('/expense/index_stats/')
    .then((response) => response.json())
    .then((data) => {
        categoryStats('支出分类占比', data.category);
        dateStats('月度支出趋势', data.month);
    });