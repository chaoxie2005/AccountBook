function expensetypePie(title, data) {
    var myChart = echarts.init(document.getElementById('s1'));
    var option = {
        tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
        legend: { bottom: '0', left: 'center', textStyle: { color: '#858796' } },
        series: [{
            name: '支出分类',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
            label: { show: false, position: 'center' },
            emphasis: { label: { show: true, fontSize: '18', fontWeight: 'bold' } },
            labelLine: { show: false },
            data: data,
            color: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796']
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

function expensetypeBar(title, data) {
    var myChart = echarts.init(document.getElementById('s2'));
    var option = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: [{ 
            type: 'category', 
            data: data.captions, 
            axisTick: { alignWithLabel: true },
            axisLine: { lineStyle: { color: '#e3e6f0' } },
            axisLabel: { color: '#858796' }
        }],
        yAxis: [{ 
            type: 'value',
            splitLine: { lineStyle: { color: '#e3e6f0', type: 'dashed' } },
            axisLabel: { color: '#858796' }
        }],
        series: [{
            name: '支出金额',
            type: 'bar',
            barWidth: '60%',
            data: data.values,
            itemStyle: { color: '#4e73df', borderRadius: [4, 4, 0, 0] }
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

function monthlyexpense(title, data) {
    var myChart = echarts.init(document.getElementById('s3'));
    const option = {
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { 
            type: 'category', 
            data: data.captions,
            axisLine: { lineStyle: { color: '#e3e6f0' } },
            axisLabel: { color: '#858796' }
        },
        yAxis: { 
            type: 'value',
            splitLine: { lineStyle: { color: '#e3e6f0', type: 'dashed' } },
            axisLabel: { color: '#858796' }
        },
        series: [{
            data: data.values,
            type: 'line',
            smooth: true,
            lineStyle: { color: '#4e73df', width: 3 },
            itemStyle: { color: '#4e73df' },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(78, 115, 223, 0.3)' },
                    { offset: 1, color: 'rgba(78, 115, 223, 0)' }
                ])
            }
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

function yearlyexpense(title, data) {
    var myChart = echarts.init(document.getElementById('s4'));
    const option = {
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { 
            type: 'category', 
            data: data.captions,
            axisLine: { lineStyle: { color: '#e3e6f0' } },
            axisLabel: { color: '#858796' }
        },
        yAxis: { 
            type: 'value',
            splitLine: { lineStyle: { color: '#e3e6f0', type: 'dashed' } },
            axisLabel: { color: '#858796' }
        },
        series: [{
            data: data.values,
            type: 'line',
            step: 'start',
            lineStyle: { color: '#1cc88a', width: 3 },
            itemStyle: { color: '#1cc88a' }
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

fetch('/expense/expense_s1/')
    .then(response => response.json())
    .then(data => expensetypePie('支出分类占比', data));

fetch('/expense/expense_s2/')
    .then(response => response.json())
    .then(data => expensetypeBar('支出金额分布', data));

fetch('/expense/expense_s3/')
    .then(response => response.json())
    .then(data => monthlyexpense('每月支出趋势', data));

fetch(`/expense/expense_s4/${new Date().getFullYear()}/`)
    .then(response => response.json())
    .then(data => yearlyexpense('年度累计支出', data));
