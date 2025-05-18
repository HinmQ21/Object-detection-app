document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const uploadBtn = document.getElementById('upload-btn');
    const loadingElement = document.getElementById('loading');
    const loadingStatus = document.getElementById('loading-status');
    const resultsElement = document.getElementById('results');
    const originalImage = document.getElementById('original-image');
    const processedImage = document.getElementById('processed-image');
    const statsContainer = document.getElementById('stats-container');
    const errorMessage = document.getElementById('error-message');
    const modelSelect = document.getElementById('model-select');
    const modelDescription = document.getElementById('model-description');
    const dropArea = document.getElementById('drop-area');
    const progressFill = document.querySelector('.progress-fill');

    // Variables for task polling
    let pollingInterval = null;
    const POLLING_INTERVAL_MS = 1000; // Poll every second

    // Fetch available models from the server
    fetchAvailableModels();

    // Xử lý sự kiện khi người dùng chọn file
    fileInput.addEventListener('change', function() {
        handleFileSelection(fileInput.files);
    });

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('drag-over');
    }

    function unhighlight() {
        dropArea.classList.remove('drag-over');
    }

    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFileSelection(files);
    }

    function handleFileSelection(files) {
        if (files.length > 0) {
            // Hiển thị tên file đã chọn
            fileName.textContent = files[0].name;
            // Kích hoạt nút upload
            uploadBtn.disabled = false;

            // Nếu là hình ảnh, hiển thị preview
            const file = files[0];
            if (file.type.match('image.*')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Hiển thị hình ảnh gốc ngay lập tức
                    originalImage.src = e.target.result;
                    resultsElement.style.display = 'block';
                    // Ẩn hình ảnh đã xử lý
                    processedImage.src = '';
                    // Xóa thống kê cũ
                    statsContainer.innerHTML = '';
                };
                reader.readAsDataURL(file);
            }
        } else {
            fileName.textContent = 'Chưa có file nào được chọn';
            uploadBtn.disabled = true;
        }
    }

    // Function to poll task status
    function pollTaskStatus(taskId) {
        // Clear any existing polling interval
        if (pollingInterval) {
            clearInterval(pollingInterval);
        }

        // Reset progress animation
        progressFill.style.animation = 'none';
        setTimeout(() => {
            progressFill.style.animation = 'progress 2s ease-in-out infinite';
        }, 10);

        // Show the original image immediately
        if (tasks[taskId] && tasks[taskId].original_image) {
            originalImage.src = '/' + tasks[taskId].original_image;
            resultsElement.style.display = 'block';
        }

        // Show loading element
        loadingElement.style.display = 'block';

        // Update loading status
        loadingStatus.textContent = 'Đang tải lên hình ảnh';

        // Start polling
        pollingInterval = setInterval(() => {
            fetch(`/task/${taskId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Lỗi khi kiểm tra trạng thái tác vụ');
                    }
                    return response.json();
                })
                .then(data => {
                    // Update task data
                    tasks[taskId] = data;

                    // Update loading status based on task status
                    if (data.status === 'pending') {
                        loadingStatus.textContent = 'Đang chuẩn bị xử lý...';
                        progressFill.style.width = '30%';
                    } else if (data.status === 'processing') {
                        loadingStatus.textContent = 'Đang phát hiện đối tượng...';
                        progressFill.style.width = '70%';
                        // Stop animation during processing
                        progressFill.style.animation = 'none';
                    }

                    if (data.status === 'completed') {
                        // Set progress to 100%
                        progressFill.style.width = '100%';
                        progressFill.style.animation = 'none';

                        // Add a small delay for visual feedback
                        setTimeout(() => {
                            // Task completed, hide loading
                            clearInterval(pollingInterval);
                            loadingElement.style.display = 'none';

                            // Display images with fade-in effect
                            originalImage.style.opacity = '0';
                            processedImage.style.opacity = '0';

                            originalImage.src = '/' + data.original_image;
                            processedImage.src = '/' + data.processed_image;

                            setTimeout(() => {
                                originalImage.style.transition = 'opacity 0.5s ease';
                                processedImage.style.transition = 'opacity 0.5s ease';
                                originalImage.style.opacity = '1';
                                processedImage.style.opacity = '1';
                            }, 100);

                            // Display statistics
                            displayStats(data.detections, data.model_used);

                            // Show results
                            resultsElement.style.display = 'block';

                            // Scroll to results
                            resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }, 500);
                    } else if (data.status === 'failed') {
                        // Task failed
                        clearInterval(pollingInterval);
                        loadingElement.style.display = 'none';
                        showError(data.error || 'Xử lý hình ảnh thất bại');
                    }
                    // For 'pending' or 'processing' status, continue polling
                })
                .catch(error => {
                    clearInterval(pollingInterval);
                    loadingElement.style.display = 'none';
                    showError(error.message);
                });
        }, POLLING_INTERVAL_MS);
    }

    // Store task data
    const tasks = {};

    // Xử lý sự kiện khi form được submit
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Kiểm tra xem đã chọn file chưa
        if (fileInput.files.length === 0) {
            showError('Vui lòng chọn một hình ảnh để tải lên');
            return;
        }

        // Kiểm tra loại file
        const file = fileInput.files[0];
        const fileType = file.type;
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];

        if (!validTypes.includes(fileType)) {
            showError('Chỉ chấp nhận file hình ảnh định dạng JPEG, JPG, PNG, GIF, BMP hoặc WEBP');
            return;
        }

        // Kiểm tra kích thước file (giới hạn 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showError('Kích thước file quá lớn. Vui lòng chọn file nhỏ hơn 10MB');
            return;
        }

        // Hiển thị loading và ẩn thông báo lỗi
        loadingElement.style.display = 'block';
        errorMessage.style.display = 'none';

        // Disable upload button to prevent multiple submissions
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';

        // Reset the progress bar
        progressFill.style.width = '0%';
        progressFill.style.animation = 'progress 2s ease-in-out infinite';

        // Tạo form data để gửi lên server
        const formData = new FormData();
        formData.append('file', file);

        // Add the selected model to the form data
        const selectedModel = modelSelect.value;
        formData.append('model', selectedModel);

        // Gửi request lên server
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Lỗi khi tải lên hình ảnh');
            }
            return response.json();
        })
        .then(data => {
            // Store task data
            const taskId = data.task_id;
            tasks[taskId] = data;

            // Start polling for task status
            pollTaskStatus(taskId);

            // Show original image immediately
            if (data.original_image) {
                originalImage.src = '/' + data.original_image;
                resultsElement.style.display = 'block';
                // Hide the processed image until it's ready
                processedImage.src = '';
            }

            // Reset upload button after successful upload
            setTimeout(() => {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = '<i class="fas fa-search"></i> Phát hiện đối tượng';
            }, 1000);
        })
        .catch(error => {
            // Ẩn loading
            loadingElement.style.display = 'none';

            // Hiển thị thông báo lỗi
            showError(error.message);

            // Reset upload button
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-search"></i> Phát hiện đối tượng';
        });
    });

    // Hàm hiển thị thống kê đối tượng đã phát hiện
    function displayStats(detections, modelUsed) {
        // Xóa nội dung cũ
        statsContainer.innerHTML = '';

        // Create a container for model info
        const modelInfo = document.createElement('div');
        modelInfo.className = 'model-info';

        // Format the model name for display
        const displayModelName = modelUsed ?
            modelUsed.replace('yolo11', 'YOLOv11-').toUpperCase() :
            'YOLOv11-M';

        modelInfo.innerHTML = `<p>Mô hình sử dụng: <strong>${displayModelName}</strong></p>`;
        statsContainer.appendChild(modelInfo);

        if (detections.length === 0) {
            const noDetection = document.createElement('div');
            noDetection.className = 'no-detection';
            noDetection.innerHTML = `
                <i class="fas fa-search"></i>
                <p>Không phát hiện đối tượng nào trong hình ảnh.</p>
            `;
            statsContainer.appendChild(noDetection);
            return;
        }

        // Đếm số lượng của mỗi loại đối tượng
        const counts = {};
        detections.forEach(detection => {
            const className = detection.class;
            counts[className] = (counts[className] || 0) + 1;
        });

        // Tạo danh sách thống kê
        const statsList = document.createElement('div');
        statsList.className = 'stats-list';

        // Thêm tổng số đối tượng
        const totalItem = document.createElement('div');
        totalItem.className = 'stats-item';
        totalItem.innerHTML = `
            <span class="stats-label"><i class="fas fa-hashtag"></i> Tổng số đối tượng phát hiện:</span>
            <span class="stats-value">${detections.length}</span>
        `;
        statsList.appendChild(totalItem);

        // Thêm chi tiết cho từng loại đối tượng
        for (const [className, count] of Object.entries(counts)) {
            const item = document.createElement('div');
            item.className = 'stats-item';

            // Choose an appropriate icon based on the class name
            let icon = 'fas fa-tag';
            if (className.toLowerCase().includes('person') || className.toLowerCase().includes('người')) {
                icon = 'fas fa-user';
            } else if (className.toLowerCase().includes('car') || className.toLowerCase().includes('xe')) {
                icon = 'fas fa-car';
            } else if (className.toLowerCase().includes('dog') || className.toLowerCase().includes('chó')) {
                icon = 'fas fa-dog';
            } else if (className.toLowerCase().includes('cat') || className.toLowerCase().includes('mèo')) {
                icon = 'fas fa-cat';
            } else if (className.toLowerCase().includes('bird') || className.toLowerCase().includes('chim')) {
                icon = 'fas fa-dove';
            }

            item.innerHTML = `
                <span class="stats-label"><i class="${icon}"></i> ${className}:</span>
                <span class="stats-value">${count}</span>
            `;
            statsList.appendChild(item);
        }

        statsContainer.appendChild(statsList);

        // Add animation to stats items
        const statsItems = statsList.querySelectorAll('.stats-item');
        statsItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            item.style.transition = `opacity 0.3s ease, transform 0.3s ease`;
            item.style.transitionDelay = `${index * 0.1}s`;

            setTimeout(() => {
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, 100);
        });
    }

    // Hàm hiển thị thông báo lỗi
    function showError(message) {
        errorMessage.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        errorMessage.style.display = 'block';

        // Scroll to error message
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Add shake animation
        errorMessage.classList.add('shake');
        setTimeout(() => {
            errorMessage.classList.remove('shake');
        }, 500);
    }

    // Hàm lấy danh sách các mô hình có sẵn từ server
    function fetchAvailableModels() {
        fetch('/models')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Không thể lấy danh sách mô hình');
                }
                return response.json();
            })
            .then(data => {
                populateModelSelect(data.models, data.default_model);
            })
            .catch(error => {
                console.error('Error fetching models:', error);
                // Add a default option if we can't fetch models
                const option = document.createElement('option');
                option.value = 'yolo11m';
                option.textContent = 'YOLOv11-M (Mặc định)';
                modelSelect.appendChild(option);
                modelDescription.textContent = 'Medium - Cân bằng giữa tốc độ và độ chính xác';
            });
    }

    // Hàm điền các tùy chọn mô hình vào dropdown
    function populateModelSelect(models, defaultModel) {
        // Clear existing options
        modelSelect.innerHTML = '';

        // Sort model names for consistent display
        const modelNames = Object.keys(models).sort();

        // Add options for each model
        modelNames.forEach(modelName => {
            const option = document.createElement('option');
            option.value = modelName;

            // Format the display name (e.g., "yolo11m" -> "YOLOv11-M")
            const displayName = modelName.replace('yolo11', 'YOLOv11-').toUpperCase();
            option.textContent = displayName;

            // Set the default model
            if (modelName === defaultModel) {
                option.selected = true;
                modelDescription.textContent = models[modelName].description;
            }

            modelSelect.appendChild(option);
        });

        // Add event listener to update description when selection changes
        modelSelect.addEventListener('change', function() {
            const selectedModel = modelSelect.value;
            if (models[selectedModel]) {
                modelDescription.textContent = models[selectedModel].description;
            }
        });
    }
});
