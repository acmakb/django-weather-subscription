/**
 * 订阅状态切换JavaScript
 */

function toggleSubscription(element, subscriptionId) {
    // 阻止默认链接行为
    event.preventDefault();
    
    // 显示加载状态
    const originalText = element.textContent;
    element.textContent = '处理中...';
    element.style.pointerEvents = 'none';
    
    // 获取CSRF token
    let csrfToken = '';
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        csrfToken = csrfInput.value;
    } else {
        // 从cookie中获取CSRF token
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                csrfToken = value;
                break;
            }
        }
    }
    
    // 发送AJAX请求
    fetch(element.href, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新按钮文本和样式
            const newText = data.is_active ? '停用' : '激活';
            const newColor = data.is_active ? 'red' : 'green';
            
            element.textContent = newText;
            element.style.color = newColor;
            element.style.borderColor = newColor;
            element.style.pointerEvents = 'auto';
            
            // 显示成功消息
            showMessage(data.message, 'success');
            
            // 更新页面中的状态显示
            updateStatusDisplay(subscriptionId, data.is_active);
        } else {
            // 恢复原始状态
            element.textContent = originalText;
            element.style.pointerEvents = 'auto';
            
            // 显示错误消息
            showMessage(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        
        // 恢复原始状态
        element.textContent = originalText;
        element.style.pointerEvents = 'auto';
        
        // 显示错误消息
        showMessage('网络错误，请重试', 'error');
    });
    
    return false;
}

function updateStatusDisplay(subscriptionId, isActive) {
    // 查找并更新状态列显示
    const rows = document.querySelectorAll('tr');
    rows.forEach(row => {
        const actionCell = row.querySelector('a[onclick*="' + subscriptionId + '"]');
        if (actionCell) {
            // 查找同一行的状态列
            const cells = row.querySelectorAll('td');
            cells.forEach(cell => {
                if (cell.textContent.includes('是') || cell.textContent.includes('否')) {
                    cell.innerHTML = isActive ? 
                        '<img src="/static/admin/img/icon-yes.svg" alt="True">' : 
                        '<img src="/static/admin/img/icon-no.svg" alt="False">';
                }
            });
        }
    });
}

function showMessage(message, type) {
    // 创建消息元素
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        z-index: 9999;
        max-width: 300px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ${type === 'success' ? 'background-color: #28a745;' : 'background-color: #dc3545;'}
    `;
    messageDiv.textContent = message;
    
    // 添加到页面
    document.body.appendChild(messageDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 3000);
    
    // 添加点击关闭功能
    messageDiv.addEventListener('click', () => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    });
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('订阅管理JavaScript已加载');
});
