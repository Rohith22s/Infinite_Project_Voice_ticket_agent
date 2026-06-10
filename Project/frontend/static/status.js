document.addEventListener('DOMContentLoaded', () => {
    const pill = document.getElementById('systemStatusPill');
    const dropdown = document.getElementById('systemStatusDropdown');
    const statusList = document.getElementById('statusList');
    
    if(!pill || !dropdown || !statusList) return;

    // Toggle dropdown
    pill.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', () => {
        dropdown.classList.add('hidden');
    });

    dropdown.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    async function checkHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            let allOnline = true;
            statusList.innerHTML = '';
            
            for (const [service, status] of Object.entries(data)) {
                const isOnline = status === 'Online';
                if (!isOnline) allOnline = false;
                
                const dotClass = isOnline ? 'green' : 'red';
                statusList.innerHTML += `
                    <li style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; font-size: 0.9rem; color: var(--text-secondary);">
                        <div class="status-dot ${dotClass}"></div>
                        <span style="flex-grow: 1;">${service}</span>
                        <span style="font-weight: 600; font-size: 0.8rem; color: ${isOnline ? '#10b981' : 'var(--danger)'};">${status}</span>
                    </li>
                `;
            }
            
            // Remove the last margin bottom
            if(statusList.lastElementChild) {
                statusList.lastElementChild.style.marginBottom = '0';
            }
            
            const mainDot = pill.querySelector('.status-dot');
            if(allOnline) {
                mainDot.className = 'status-dot green';
            } else {
                mainDot.className = 'status-dot red';
            }
            
        } catch(e) {
            console.error('Health check failed', e);
            const mainDot = pill.querySelector('.status-dot');
            mainDot.className = 'status-dot red';
            statusList.innerHTML = '<li style="color: var(--danger); font-size: 0.9rem; text-align: center;">Cannot reach server.</li>';
        }
    }

    // Initial check
    checkHealth();
    
    // Poll every 15 seconds
    setInterval(checkHealth, 15000);
});
