/**
 * Google Ads 关键词分析工具
 * 前端JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const keywordForm = document.getElementById('keyword-form');
    const keywordInput = document.getElementById('keyword-input');
    const loadingElement = document.getElementById('loading');
    const errorElement = document.getElementById('error-message');
    const resultsElement = document.getElementById('results');
    
    // 结果显示元素
    const resultKeyword = document.getElementById('result-keyword');
    const volumeUs = document.getElementById('volume-us');
    const volumeGlobal = document.getElementById('volume-global');
    const kd = document.getElementById('kd');
    const cpc = document.getElementById('cpc');
    const type = document.getElementById('type');
    const competition = document.getElementById('competition');
    const competitionBar = document.getElementById('competition-bar');
    
    // 调试信息
    console.log('JavaScript已加载，表单元素:', keywordForm);
    
    // 监听表单提交
    keywordForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 获取关键词
        const keyword = keywordInput.value.trim();
        console.log('提交的关键词:', keyword);
        
        if (!keyword) {
            showError('请输入关键词');
            return;
        }
        
        // 显示加载状态
        showLoading();
        console.log('显示加载状态，准备发送请求');
        
        // 发送请求
        console.log('开始发送请求到 /analyze');
        fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `keyword=${encodeURIComponent(keyword)}`
        })
        .then(response => {
            console.log('收到响应:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // 隐藏加载状态
            hideLoading();
            console.log('解析的响应数据:', data);
            
            if (!data.success) {
                showError(data.error || '获取数据失败');
                return;
            }
            
            // 显示结果
            displayResults(data.data);
        })
        .catch(error => {
            hideLoading();
            console.error('请求出错:', error);
            showError('请求失败: ' + error.message);
        });
    });
    
    /**
     * 显示加载状态
     */
    function showLoading() {
        loadingElement.classList.remove('d-none');
        errorElement.classList.add('d-none');
        resultsElement.classList.add('d-none');
    }
    
    /**
     * 隐藏加载状态
     */
    function hideLoading() {
        loadingElement.classList.add('d-none');
    }
    
    /**
     * 显示错误信息
     */
    function showError(message) {
        console.log('显示错误:', message);
        errorElement.textContent = message;
        errorElement.classList.remove('d-none');
        resultsElement.classList.add('d-none');
    }
    
    /**
     * 显示结果
     */
    function displayResults(data) {
        console.log('显示结果:', data);
        // 设置关键词
        resultKeyword.textContent = data.keyword;
        
        // 设置搜索量
        volumeUs.textContent = formatNumber(data.volume_us || 0);
        volumeGlobal.textContent = formatNumber(data.volume_global || 0);
        
        // 设置KD
        const kdValue = data.kd || 0;
        kd.textContent = kdValue.toFixed(1);
        kd.className = 'card-text fs-3 ' + getKdClass(kdValue);
        
        // 设置CPC
        cpc.textContent = formatCurrency(data.cpc || 0);
        
        // 设置类型
        const typeValue = data.type || 'I';
        type.innerHTML = `<span class="type-badge type-${typeValue.toLowerCase()}">${getTypeLabel(typeValue)}</span>`;
        
        // 设置竞争度
        const competitionValue = data.competition_index || 0;
        competition.textContent = getCompetitionLabel(competitionValue);
        competitionBar.style.width = `${competitionValue}%`;
        competitionBar.className = 'progress-bar ' + getCompetitionClass(competitionValue);
        
        // 显示结果
        resultsElement.classList.remove('d-none');
    }
    
    /**
     * 格式化数字
     */
    function formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }
    
    /**
     * 格式化货币
     */
    function formatCurrency(num) {
        return '$' + num.toFixed(2);
    }
    
    /**
     * 获取KD类名
     */
    function getKdClass(kd) {
        if (kd < 30) return 'text-success';
        if (kd < 70) return 'text-warning';
        return 'text-danger';
    }
    
    /**
     * 获取类型标签
     */
    function getTypeLabel(type) {
        switch (type) {
            case 'I': return '信息型';
            case 'C': return '商业型';
            case 'T': return '交易型';
            default: return '信息型';
        }
    }
    
    /**
     * 获取竞争度标签
     */
    function getCompetitionLabel(value) {
        if (value < 33) return '低竞争度 (' + value + ')';
        if (value < 66) return '中等竞争度 (' + value + ')';
        return '高竞争度 (' + value + ')';
    }
    
    /**
     * 获取竞争度类名
     */
    function getCompetitionClass(value) {
        if (value < 33) return 'bg-success';
        if (value < 66) return 'bg-warning';
        return 'bg-danger';
    }
});
