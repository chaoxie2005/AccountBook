function incomeTypePie(title, data) {
    var myChart = echarts.init(document.getElementById('s1'));
    var option = {
        tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
        legend: { bottom: '0', left: 'center', textStyle: { color: '#858796' } },
        series: [{
            name: '收入类型',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
            label: { show: false, position: 'center' },
            emphasis: { label: { show: true, fontSize: '18', fontWeight: 'bold' } },
            labelLine: { show: false },
            data: data,
            color: ['#1cc88a', '#4e73df', '#36b9cc', '#f6c23e', '#e74a3b', '#858796']
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

function incomeTypeBar(title, data) {
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
            name: '收入金额',
            type: 'bar',
            barWidth: '60%',
            data: data.values,
            itemStyle: { color: '#1cc88a', borderRadius: [4, 4, 0, 0] }
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

function monthlyIncome(title, data) {
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
            lineStyle: { color: '#1cc88a', width: 3 },
            itemStyle: { color: '#1cc88a' },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(28, 200, 138, 0.3)' },
                    { offset: 1, color: 'rgba(28, 200, 138, 0)' }
                ])
            }
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

function yearlyIncome(title, data) {
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
            lineStyle: { color: '#4e73df', width: 3 },
            itemStyle: { color: '#4e73df' }
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

fetch('/income/income_s1/')
    .then(response => response.json())
    .then(data => incomeTypePie('收入分类占比', data));

fetch('/income/income_s2/')
    .then(response => response.json())
    .then(data => incomeTypeBar('收入金额分布', data));

fetch('/income/income_s3/')
    .then(response => response.json())
    .then(data => monthlyIncome('每月收入趋势', data));

fetch(`/income/income_s4/${new Date().getFullYear()}/`)
    .then(response => response.json())
    .then(data => yearlyIncome('年度累计收入', data));
