// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.dashboard')) {
        loadDashboardData();
    }
});

/**
 * 加载仪表板数据
 */
function loadDashboardData() {
    // 加载数据摘要
    fetchDataSummary();
    // 加载行政区统计
    loadDistrictStats();
}

/**
 * 获取数据摘要
 */
function fetchDataSummary() {
    fetch('/api/data/summary')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('获取数据摘要失败:', data.error);
                return;
            }

            document.getElementById('total-records').textContent =
                data.total_records.toLocaleString();
            document.getElementById('total-districts').textContent =
                data.total_districts;
            document.getElementById('avg-price').textContent =
                data.avg_price.toFixed(2) + ' 万元';
            document.getElementById('avg-unit-price').textContent =
                data.avg_unit_price.toFixed(0) + ' 元/㎡';
        })
        .catch(error => console.error('错误:', error));
}

/**
 * 加载行政区统计表格
 */
function loadDistrictStats() {
    fetch('/api/data/district-stats')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('获取行政区统计失败:', data.error);
                return;
            }

            // 填充表头
            const headerRow = document.getElementById('table-header');
            headerRow.innerHTML = '<th>行政区</th>';
            data.columns.forEach(col => {
                const th = document.createElement('th');
                th.textContent = col;
                headerRow.appendChild(th);
            });

            // 填充数据行
            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';
            data.index.forEach((district, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = '<td><strong>' + district + '</strong></td>';
                data.data[idx].forEach(value => {
                    const td = document.createElement('td');
                    td.textContent = typeof value === 'number' ?
                        value.toFixed(2) : value;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error('错误:', error));
}

/**
 * 生成图表
 */
function generateCharts() {
    fetch('/api/charts/generate', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('图表生成成功:', data.charts);
                // 重新加载页面以显示新图表
                location.reload();
            } else {
                alert('生成图表失败: ' + data.error);
            }
        })
        .catch(error => {
            console.error('错误:', error);
            alert('生成图表出错');
        });
}
