/* MoneyMap - Interactive JavaScript */

// ==================== GLOBAL VARIABLES ====================

let expenseChart = null;
let incomeChart = null;
let categoryChart = null;

// ==================== DOCUMENT READY ====================

document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    initializeModals();
    initializeFileUpload();
    initializeChatbot();
    loadTransactionData();
});

// ==================== CHART INITIALIZATION ====================

function initializeCharts() {
    // Category Pie Chart
    const categoryCanvas = document.getElementById('categoryChart');
    if (categoryCanvas) {
        const ctx = categoryCanvas.getContext('2d');
        const categoryData = categoryCanvas.getAttribute('data-categories');
        
        if (categoryData) {
            const categories = JSON.parse(categoryData);
            const labels = Object.keys(categories);
            const values = Object.values(categories);
            const colors = generateColors(labels.length);
            
            categoryChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: colors,
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ₹${value.toLocaleString()} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Monthly Trends Chart
    const trendsCanvas = document.getElementById('trendsChart');
    if (trendsCanvas) {
        const ctx = trendsCanvas.getContext('2d');
        
        incomeChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Income',
                        data: [],
                        backgroundColor: 'rgba(16, 185, 129, 0.8)',
                        borderColor: 'rgba(16, 185, 129, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Expenses',
                        data: [],
                        backgroundColor: 'rgba(239, 68, 68, 0.8)',
                        borderColor: 'rgba(239, 68, 68, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ₹' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
}

function generateColors(count) {
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#9966FF'
    ];
    
    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    
    return result;
}

function loadTransactionData() {
    fetch('/api/transactions')
        .then(response => response.json())
        .then(data => {
            updateTrendsChart(data.income_trends, data.expense_trends);
        })
        .catch(error => console.error('Error loading transaction data:', error));
}

function updateTrendsChart(incomeData, expenseData) {
    const trendsCanvas = document.getElementById('trendsChart');
    if (!trendsCanvas || !incomeChart) return;
    
    const allMonths = new Set([
        ...Object.keys(incomeData),
        ...Object.keys(expenseData)
    ]);
    
    const sortedMonths = Array.from(allMonths).sort();
    
    incomeChart.data.labels = sortedMonths.map(month => {
        const date = new Date(month + '-01');
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    });
    
    incomeChart.data.datasets[0].data = sortedMonths.map(month => incomeData[month] || 0);
    incomeChart.data.datasets[1].data = sortedMonths.map(month => expenseData[month] || 0);
    
    incomeChart.update();
}

// ==================== MODAL FUNCTIONS ====================

function initializeModals() {
    // Add Income Modal
    const addIncomeBtn = document.getElementById('addIncomeBtn');
    const incomeModal = document.getElementById('incomeModal');
    
    if (addIncomeBtn && incomeModal) {
        addIncomeBtn.addEventListener('click', function() {
            incomeModal.classList.add('active');
        });
    }
    
    // Add Expense Modal
    const addExpenseBtn = document.getElementById('addExpenseBtn');
    const expenseModal = document.getElementById('expenseModal');
    
    if (addExpenseBtn && expenseModal) {
        addExpenseBtn.addEventListener('click', function() {
            expenseModal.classList.add('active');
        });
    }
    
    // Add Goal Modal
    const addGoalBtn = document.getElementById('addGoalBtn');
    const goalModal = document.getElementById('goalModal');
    
    if (addGoalBtn && goalModal) {
        addGoalBtn.addEventListener('click', function() {
            goalModal.classList.add('active');
        });
    }
    
    // Close modals
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.modal').classList.remove('active');
        });
    });
    
    // Close modal on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('active');
            }
        });
    });
}

function openEditModal(type, id) {
    const modal = document.getElementById(`${type}Modal`);
    const form = document.getElementById(`${type}Form`);
    
    if (!modal || !form) return;
    
    // Fetch data
    fetch(`/api/${type}/${id}`)
        .then(response => response.json())
        .then(data => {
            // Populate form
            for (const key in data) {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            }
            
            modal.classList.add('active');
        })
        .catch(error => console.error('Error loading data:', error));
}

// ==================== FILE UPLOAD ====================

function initializeFileUpload() {
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.getElementById('receiptInput');
    
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });
        
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function() {
            this.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleReceiptUpload(files[0]);
            }
        });
        
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleReceiptUpload(this.files[0]);
            }
        });
    }
}

function handleReceiptUpload(file) {
    const formData = new FormData();
    formData.append('receipt', file);
    
    const uploadStatus = document.getElementById('uploadStatus');
    if (uploadStatus) {
        uploadStatus.innerHTML = '<div class="spinner"></div><p>Scanning receipt...</p>';
    }
    
    fetch('/upload_receipt', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (uploadStatus) {
            if (result.success) {
                uploadStatus.innerHTML = `
                    <div class="alert alert-success">
                        <strong>Receipt Scanned Successfully!</strong><br>
                        Amount: ₹${result.data.amount}<br>
                        Date: ${result.data.date}<br>
                        Merchant: ${result.data.merchant}
                    </div>
                `;
                
                // Auto-fill expense form
                autoFillExpenseForm(result.data);
            } else {
                uploadStatus.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
            }
        }
    })
    .catch(error => {
        if (uploadStatus) {
            uploadStatus.innerHTML = `<div class="alert alert-danger">Upload failed: ${error.message}</div>`;
        }
    });
}

function autoFillExpenseForm(receiptData) {
    const titleInput = document.querySelector('#expenseModal [name="title"]');
    const amountInput = document.querySelector('#expenseModal [name="amount"]');
    const dateInput = document.querySelector('#expenseModal [name="date"]');
    
    if (titleInput) titleInput.value = receiptData.merchant;
    if (amountInput) amountInput.value = receiptData.amount;
    if (dateInput) dateInput.value = receiptData.date;
}

// ==================== CHATBOT ====================

function initializeChatbot() {
    const chatForm = document.getElementById('chatForm');
    const chatMessages = document.querySelector('.chat-messages');
    
    if (chatForm && chatMessages) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const messageInput = document.getElementById('chatMessage');
            const message = messageInput.value.trim();
            
            if (!message) return;
            
            // Add user message
            addChatMessage(message, 'user');
            messageInput.value = '';
            
            // Send to server
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(result => {
                if (result.success || result.response) {
                    addChatMessage(result.response, 'bot');
                } else {
                    addChatMessage('Sorry, I encountered an error.', 'bot');
                }
            })
            .catch(error => {
                addChatMessage('Sorry, I could not process your request.', 'bot');
            });
        });
    }
}

function addChatMessage(text, sender) {
    const chatMessages = document.querySelector('.chat-messages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    messageDiv.textContent = text;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ==================== FORM VALIDATION ====================

function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });
    
    return isValid;
}

// ==================== BUDGET PROGRESS ====================

function updateBudgetProgress(spent, limit) {
    const progressBar = document.querySelector('.budget-progress .progress-fill');
    const progressText = document.querySelector('.budget-percentage');
    
    if (progressBar && progressText) {
        const percentage = Math.min((spent / limit) * 100, 100);
        progressBar.style.width = percentage + '%';
        progressText.textContent = percentage.toFixed(1) + '%';
        
        if (percentage > 90) {
            progressBar.style.background = 'var(--gradient-danger)';
        } else if (percentage > 70) {
            progressBar.style.background = 'var(--warning-color)';
        }
    }
}

// ==================== GOAL PROGRESS ====================

function updateGoalProgress(current, target) {
    const percentage = (current / target) * 100;
    return Math.min(percentage, 100);
}

// ==================== NOTIFICATIONS ====================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transition = 'opacity 0.3s ease';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ==================== CONFIRMATION DIALOGS ====================

function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// ==================== DATE FORMAT UTILITIES ====================

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// ==================== FILTER AND SORT ====================

function filterTable(tableId, filterValue) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const category = row.querySelector('.category-cell');
        if (category) {
            if (filterValue === 'all' || category.textContent.trim() === filterValue) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex]?.textContent.trim() || '';
        const bValue = b.cells[columnIndex]?.textContent.trim() || '';
        
        const aNum = parseFloat(aValue.replace(/[^0-9.-]+/g, ''));
        const bNum = parseFloat(bValue.replace(/[^0-9.-]+/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return bNum - aNum;
        }
        
        return aValue.localeCompare(bValue);
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

// ==================== EXPORT FUNCTIONS ====================

function exportToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(col => {
            rowData.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
        });
        csv.push(rowData.join(','));
    });
    
    downloadFile(csv.join('\n'), filename, 'text/csv');
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

// ==================== AUTO DISMISS ALERTS ====================

setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.transition = 'opacity 0.3s ease';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    });
}, 5000);

// ==================== PERFORMANCE OPTIMIZATION ====================

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== MOBILE MENU TOGGLE ====================

function toggleMobileMenu() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
}

console.log('MoneyMap initialized successfully!');
