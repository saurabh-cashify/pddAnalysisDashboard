// Handle folder selection for analysis folder upload
document.addEventListener('DOMContentLoaded', function() {
    console.log('📁 Folder upload script loaded');
    
    // Wait for the upload area to be rendered
    setTimeout(function() {
        const uploadArea = document.getElementById('eval-folder-upload-area');
        
        if (!uploadArea) {
            console.log('⚠️  Upload area not found, retrying...');
            return;
        }
        
        console.log('✅ Upload area found');
        
        // Add click handler to the upload area
        uploadArea.addEventListener('click', function(e) {
            console.log('🖱️  Upload area clicked');
            e.preventDefault();
            e.stopPropagation();
            
            // Create a temporary file input for folder selection
            const input = document.createElement('input');
            input.type = 'file';
            input.webkitdirectory = true;
            input.directory = true;
            input.multiple = true;
            
            // Handle file selection
            input.addEventListener('change', function(event) {
                const files = event.target.files;
                console.log(`📂 Selected ${files.length} files from folder`);
                
                if (files.length > 0) {
                    // Get folder name from first file path
                    const firstPath = files[0].webkitRelativePath || files[0].name;
                    const folderName = firstPath.split('/')[0];
                    
                    // Show filename indicator
                    const filenameDiv = document.getElementById('eval-folder-filename');
                    if (filenameDiv) {
                        filenameDiv.innerHTML = `
                            <div style="color: #10b981; font-weight: 500;">
                                <i class="fas fa-check-circle text-success me-2"></i>
                                Folder selected: ${folderName} (${files.length} files)
                            </div>
                        `;
                    }
                    
                    // Trigger the hidden Dash upload component
                    const dashUpload = document.querySelector('#eval-folder-upload input[type="file"]');
                    if (dashUpload) {
                        // Create a new FileList-like object
                        const dataTransfer = new DataTransfer();
                        for (let i = 0; i < files.length; i++) {
                            dataTransfer.items.add(files[i]);
                        }
                        
                        // Set the files to the Dash upload input
                        dashUpload.files = dataTransfer.files;
                        
                        // Trigger change event on Dash upload
                        const event = new Event('change', { bubbles: true });
                        dashUpload.dispatchEvent(event);
                        
                        console.log('✅ Files transferred to Dash upload component');
                    } else {
                        console.log('⚠️  Dash upload input not found');
                    }
                }
            });
            
            // Trigger the file picker
            input.click();
        });
        
        console.log('✅ Click handler attached');
    }, 500);
});

