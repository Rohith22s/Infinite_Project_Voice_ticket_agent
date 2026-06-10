document.addEventListener('DOMContentLoaded', () => {
    const recordBtn = document.getElementById('recordButton');
    const recordRing = document.querySelector('.record-ring');
    const statusText = document.getElementById('statusText');
    const recordingTime = document.getElementById('recordingTime');
    const processingOverlay = document.getElementById('processingOverlay');
    const processingText = document.getElementById('processingText');
    const ticketsTableBody = document.getElementById('ticketsTableBody');
    const refreshBtn = document.getElementById('refreshBtn');
    const deptDropdownContainer = document.getElementById('deptDropdownContainer');
    const deptDropdownBtn = document.getElementById('deptDropdownBtn');
    const deptDropdownText = document.getElementById('deptDropdownText');
    const deptDropdownItems = document.querySelectorAll('.custom-dropdown-item');
    const uploadBtn = document.getElementById('uploadBtn');
    const audioUpload = document.getElementById('audioUpload');
    const ticketSearch = document.getElementById('ticketSearch');
    let currentFilterVal = 'All';

    if (ticketSearch) {
        ticketSearch.addEventListener('input', fetchRecords);
    }

    if (deptDropdownContainer) {
        deptDropdownBtn.addEventListener('click', () => {
            deptDropdownContainer.classList.toggle('open');
        });

        document.addEventListener('click', (e) => {
            if (!deptDropdownContainer.contains(e.target)) {
                deptDropdownContainer.classList.remove('open');
            }
        });

        deptDropdownItems.forEach(item => {
            item.addEventListener('click', () => {
                deptDropdownItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                deptDropdownText.textContent = item.textContent;
                currentFilterVal = item.getAttribute('data-value');
                deptDropdownContainer.classList.remove('open');
                fetchRecords();
            });
        });
    }

    let isRecording = false;
    let mediaRecorder;
    let audioChunks = [];
    let timerInterval;
    let startTime;

    if (ticketsTableBody) {
        fetchRecords();
        if (refreshBtn) refreshBtn.addEventListener('click', fetchRecords);
    }

    if (recordBtn) {
        recordBtn.addEventListener('click', async () => {
            if (!isRecording) {
                await startRecording();
            } else {
                stopRecording();
            }
        });
    }

    if (uploadBtn && audioUpload) {
        uploadBtn.addEventListener('click', () => {
            audioUpload.click();
        });

        audioUpload.addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (file) {
                await uploadAudioFile(file);
            }
            audioUpload.value = ''; // reset
        });
    }

    function setStepProgress(stepNumber) {
        const steps = [1, 2, 3, 4];
        steps.forEach(num => {
            const el = document.getElementById(`step${num}`);
            if (num < stepNumber) {
                el.className = 'step completed active';
            } else if (num === stepNumber) {
                el.className = 'step active';
            } else {
                el.className = 'step';
            }
        });
    }

    async function uploadAudioFile(file) {
        processingOverlay.classList.remove('hidden');
        setStepProgress(1);
        processingText.textContent = "Uploading file...";
        
        let msgIndex = 1;
        const msgInterval = setInterval(() => {
            msgIndex++;
            if(msgIndex > 4) msgIndex = 4;
            setStepProgress(msgIndex);
            if(msgIndex === 2) processingText.textContent = "Whisper is transcribing...";
            if(msgIndex === 3) processingText.textContent = "AI Agent analyzing sentiment...";
            if(msgIndex === 4) processingText.textContent = "Finalizing structured ticket...";
        }, 4000);

        const formData = new FormData();
        formData.append('audio', file, file.name);

        try {
            const response = await fetch('/api/process_audio', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            clearInterval(msgInterval);
            
            if (result.success) {
                setStepProgress(4);
                processingText.textContent = "Success!";
                setTimeout(() => {
                    processingOverlay.classList.add('hidden');
                    fetchRecords();
                }, 1500);
            } else {
                throw new Error(result.error || 'Unknown error');
            }
        } catch (error) {
            console.error("Upload error:", error);
            clearInterval(msgInterval);
            processingText.textContent = "Error occurred";
            setTimeout(() => {
                processingOverlay.classList.add('hidden');
                alert(`Error processing file: ${error.message}`);
            }, 2000);
        }
    }

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = handleAudioStop;

            mediaRecorder.start();
            isRecording = true;
            
            recordBtn.classList.add('recording');
            recordBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';
            recordRing.classList.add('recording');
            statusText.textContent = 'Recording...';
            statusText.classList.add('recording');
            
            startTime = Date.now();
            updateTimer();
            timerInterval = setInterval(updateTimer, 1000);

        } catch (err) {
            console.error("Error accessing microphone:", err);
            alert("Could not access microphone. Please ensure you have granted permissions.");
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            isRecording = false;
            clearInterval(timerInterval);
            
            recordBtn.classList.remove('recording');
            recordBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
            recordRing.classList.remove('recording');
            statusText.textContent = 'Processing...';
            statusText.classList.remove('recording');
        }
    }

    function updateTimer() {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
        const secs = String(elapsed % 60).padStart(2, '0');
        recordingTime.textContent = `${mins}:${secs}`;
    }

    async function handleAudioStop() {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        
        processingOverlay.classList.remove('hidden');
        setStepProgress(1);
        processingText.textContent = "Uploading audio...";
        
        let msgIndex = 1;
        const msgInterval = setInterval(() => {
            msgIndex++;
            if(msgIndex > 4) msgIndex = 4;
            setStepProgress(msgIndex);
            if(msgIndex === 2) processingText.textContent = "Whisper is transcribing...";
            if(msgIndex === 3) processingText.textContent = "AI Agent analyzing sentiment...";
            if(msgIndex === 4) processingText.textContent = "Finalizing structured ticket...";
        }, 4000);

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        try {
            const response = await fetch('/api/process_audio', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            clearInterval(msgInterval);
            
            if (result.success) {
                setStepProgress(4);
                processingText.textContent = "Success!";
                setTimeout(() => {
                    processingOverlay.classList.add('hidden');
                    statusText.textContent = "Ready to record";
                    recordingTime.textContent = "00:00";
                    fetchRecords();
                }, 1500);
            } else {
                throw new Error(result.error || 'Unknown error');
            }
        } catch (error) {
            console.error("Upload error:", error);
            clearInterval(msgInterval);
            processingText.textContent = "Error occurred";
            setTimeout(() => {
                processingOverlay.classList.add('hidden');
                statusText.textContent = "Ready to record";
                recordingTime.textContent = "00:00";
                alert(`Error processing audio: ${error.message}`);
            }, 2000);
        }
    }

    async function fetchRecords() {
        try {
            refreshBtn.classList.add('fa-spin');
            const response = await fetch('/api/records');
            const records = await response.json();
            
            ticketsTableBody.innerHTML = '';

            if (records.length === 0) {
                ticketsTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem; color: var(--text-secondary);">No tickets found.</td></tr>';
            } else {
                const filterVal = currentFilterVal;
                const searchVal = ticketSearch ? ticketSearch.value.toLowerCase() : '';
                const grouped = {};
                records.forEach(r => {
                    const dept = r.department || 'Unassigned';
                    
                    const searchMatch = !searchVal || 
                        (r.title && r.title.toLowerCase().includes(searchVal)) ||
                        (r.description && r.description.toLowerCase().includes(searchVal)) ||
                        (r.category && r.category.toLowerCase().includes(searchVal)) ||
                        (r.id && r.id.toString().includes(searchVal));

                    if ((filterVal === 'All' || dept === filterVal) && searchMatch) {
                        if (!grouped[dept]) grouped[dept] = [];
                        grouped[dept].push(r);
                    }
                });
                
                if (Object.keys(grouped).length === 0) {
                    ticketsTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem; color: var(--text-secondary);">No tickets found for this department.</td></tr>';
                }

                const pWeight = { 'High': 1, 'Medium': 2, 'Low': 3 };
                
                Object.keys(grouped).sort().forEach(dept => {
                    const headerTr = document.createElement('tr');
                    headerTr.innerHTML = `<td colspan="4" style="padding: 1rem; background: rgba(99, 102, 241, 0.05); color: var(--accent-color); font-weight: 800; text-transform: uppercase; letter-spacing: 1px; border-top: 2px solid var(--accent-color);"><i class="fa-solid fa-building" style="margin-right: 0.5rem;"></i> ${dept}</td>`;
                    ticketsTableBody.appendChild(headerTr);

                    grouped[dept].sort((a, b) => {
                        const wA = pWeight[a.priority] || 4;
                        const wB = pWeight[b.priority] || 4;
                        if (wA !== wB) return wA - wB;
                        return new Date(b.created_at) - new Date(a.created_at);
                    });

                    grouped[dept].forEach(record => {
                        const tr = document.createElement('tr');
                        tr.style.borderBottom = "1px solid rgba(0,0,0,0.05)";
                        
                        let titleHtml = record.title || 'No Title';
                        let priorityBadge = '';
                        if(record.priority) {
                            priorityBadge = `<span class="badge priority-${record.priority}">${record.priority}</span>`;
                        }
                        
                        let statusBadge = '';
                        if (record.status) {
                            const statusColor = record.status === 'Resolved' ? '#10b981' : 'var(--danger)';
                            statusBadge = `<span class="badge" style="background: rgba(0,0,0,0.05); color: ${statusColor}; border: 1px solid ${statusColor}; font-size: 0.75rem; padding: 0.2rem 0.5rem; margin-left: 0.5rem;">${record.status}</span>`;
                        }

                        let deptCode = record.department ? record.department.replace(/[^A-Za-z]/g, '').substring(0, 3).toUpperCase() : 'GEN';
                        let prioCode = record.priority ? record.priority.substring(0, 1).toUpperCase() : 'U';
                        let formattedId = `${deptCode}-${prioCode}-${record.id.toString().padStart(4, '0')}`;

                        tr.innerHTML = `
                            <td style="padding: 1rem; color: var(--text-secondary); font-weight: 700;">#${formattedId}</td>
                            <td style="padding: 1rem;">
                                <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem; display: flex; align-items: center;">
                                    ${titleHtml} ${statusBadge}
                                </div>
                                <div style="font-size: 0.85rem; color: var(--text-secondary);">${record.category || 'General'}</div>
                            </td>
                            <td style="padding: 1rem;">${priorityBadge}</td>
                            <td style="padding: 1rem; text-align: center;">
                                <a href="/ticket/${record.id}" class="secondary-btn" style="margin: 0; padding: 0.4rem 0.8rem; font-size: 0.85rem; text-decoration: none;">View</a>
                            </td>
                        `;
                        ticketsTableBody.appendChild(tr);
                    });
                });
            }
            
            setTimeout(() => refreshBtn.classList.remove('fa-spin'), 500);
            
        } catch (error) {
            console.error("Error fetching records:", error);
            ticketsTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem; color: var(--danger);">Failed to load tickets.</td></tr>';
            refreshBtn.classList.remove('fa-spin');
        }
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const supportDirBtn = document.getElementById('supportDirBtn');
    const supportDirDropdown = document.getElementById('supportDirDropdown');
    const supportDirContainer = document.getElementById('supportDirContainer');

    if (supportDirBtn && supportDirDropdown) {
        supportDirBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            supportDirDropdown.classList.toggle('hidden');
        });

        document.addEventListener('click', (e) => {
            if (supportDirContainer && !supportDirContainer.contains(e.target)) {
                supportDirDropdown.classList.add('hidden');
            }
        });
    }
});
