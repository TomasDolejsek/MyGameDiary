// Global variables
let elements = [];
let selectedElement = null;
let draggedElement = null;
let offsetX = 0;
let offsetY = 0;
let currentFormName = '';
let currentDescription = '';
let templateId = '';


// Counter object to keep track of element counts
let elementCounts = {
    text: 0,
    textarea: 0,
    number: 0,
    select: 0,
    picture: 0,
};

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    templateId = document.getElementById('templateId').value;
    initializeFormNameButton();
    initializeDescription();
    loadConfiguration(); // Load initial configuration

    document.addEventListener('mousemove', (e) => {
        if (draggedElement) {
            const pdfPreview = document.getElementById('pdfPreview');
            const rect = pdfPreview.getBoundingClientRect();

            // Calculate new position
            let newX = e.clientX - rect.left - offsetX;
            let newY = e.clientY - rect.top - offsetY;

            // Constrain to PDF preview boundaries
            newX = Math.max(0, Math.min(newX, rect.width - draggedElement.width));
            newY = Math.max(0, Math.min(newY, rect.height - draggedElement.height));

            // Update element position
            draggedElement.x = newX;
            draggedElement.y = newY;

            renderElements();
        }
    });

    document.addEventListener('mouseup', () => {
        if (draggedElement) {
            const draggedDiv = document.querySelector('.dragging');
            if (draggedDiv) {
                draggedDiv.classList.remove('dragging');
            }
            draggedElement = null;
        }
    });
});

function initializeFormNameButton() {
    const formNameContainer = document.getElementById('formNameContainer'); // Assuming the container for the form name
    const formNameBtn = document.createElement('span'); // Create a span for the form name
    formNameBtn.id = 'formNameBtn';
    formNameBtn.textContent = currentFormName;
    formNameBtn.style.cursor = 'pointer';

    // Add the edit icon
    const editIcon = document.createElement('i');
    editIcon.className = 'bi bi-pencil ms-2';
    editIcon.style.cursor = 'pointer';

    // Add click event to the edit icon
    editIcon.addEventListener('click', makeFormNameEditable);

    // Add the form name and edit icon to the container
    formNameContainer.innerHTML = ''; // Clear any existing content
    formNameContainer.appendChild(formNameBtn);
    formNameContainer.appendChild(editIcon);

    // Add click event to the form name itself
    formNameBtn.addEventListener('click', makeFormNameEditable);
}

function initializeDescription() {
    const descriptionField = document.getElementById('descriptionField');
    descriptionField.addEventListener('blur', () => {
        saveDescription(descriptionField)
    })
}

function makeFormNameEditable() {
    const formNameContainer = document.getElementById('formNameContainer');
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentFormName;
    input.className = 'form-control form-control-sm';
    input.style.width = '200px';

    // Replace the form name and edit icon with the input field
    formNameContainer.innerHTML = '';
    formNameContainer.appendChild(input);
    input.focus();

    // Save the form name on blur or Enter key press
    input.addEventListener('blur', () => saveFormName(input));
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            saveFormName(input);
        }
    });
}

function saveFormName(input) {
    currentFormName = input.value.trim() || 'Nepojmenovaný template';
    initializeFormNameButton(); // Reinitialize the form name with the updated value
}

function saveDescription(input) {
    currentDescription = input.value.trim() || '';
    initializeDescription();
}

function updateFormNameButton() {
    const formNameBtn = document.getElementById('formNameBtn');
    formNameBtn.textContent = currentFormName;
}

function updateFormDescription() {
    const descriptionField = document.getElementById('descriptionField');
    descriptionField.value = currentDescription;
}

function generateElementName(type) {
    elementCounts[type]++;
    const typeNames = {
        text: 'TextField',
        textarea: 'TextArea',
        number: 'NumberField',
        select: 'Dropdown',
        picture: 'Picture',
    };
    return `${typeNames[type]}${elementCounts[type]}`;
}

function addElement(type) {
    const element = {
        id: Date.now(),
        type,
        name: generateElementName(type),
        placeholder: type === 'select' ? '' : (type === 'picture' ? 'No picture uploaded' : `Enter ${type} here`),
        x: 20,
        y: 20,
        width: 200,
        height: type === 'picture' ? 150 : 40,  // Default height for pictures
        options: type === 'select' ? ['Option 1', 'Option 2'] : [],
        pictureUrl: ''  // Add this for picture elements
    };
    elements.push(element);
    renderElements();
}

function removeElement(id) {
    const element = elements.find(el => el.id === id);
    if (element) {
        elementCounts[element.type]--;
    }
    elements = elements.filter(el => el.id !== id);
    if (selectedElement?.id === id) {
        selectedElement = null;
    }
    renderElements();
}

function createFormElement(element) {
    const div = document.createElement('div');
    div.className = `mb-3 position-relative form-element-container ${selectedElement?.id === element.id ? 'selected' : ''}`;
    div.id = `form-${element.id}`;

    // Add click handler for selection to the main container
    const handleSelection = (e) => {
        // Remove selected class from all elements
        document.querySelectorAll('.element').forEach(el => {
            el.classList.remove('selected');
        });
        document.querySelectorAll('.form-element-container').forEach(el => {
            el.classList.remove('selected');
        });

        // Add selected class to clicked element and corresponding PDF element
        div.classList.add('selected');
        const pdfElement = document.getElementById(`element-${element.id}`);
        if (pdfElement) {
            pdfElement.classList.add('selected');
        }

        selectedElement = element;
    };

    div.addEventListener('click', handleSelection);

    // Add a small note to identify the type of the element
    const typeBadge = document.createElement('span');
    typeBadge.className = 'badge bg-secondary mb-2'; // Bootstrap badge styling
    typeBadge.textContent = getElementTypeName(element.type); // Get the type name
    div.appendChild(typeBadge);

    // Remove button
    const removeBtn = document.createElement('button');
    removeBtn.className = 'btn btn-danger remove-btn';
    removeBtn.innerHTML = 'X';
    removeBtn.onclick = (e) => {
        e.stopPropagation();
        removeElement(element.id);
    };
    div.appendChild(removeBtn);

    // Editable name with edit button
    const nameContainer = document.createElement('div');
    nameContainer.className = 'editable-container';
    nameContainer.addEventListener('click', handleSelection); // Add click handler

    const nameSpan = document.createElement('span');
    nameSpan.className = 'field-name';
    nameSpan.textContent = element.name;
    nameSpan.addEventListener('click', handleSelection); // Add click handler

    const editNameBtn = document.createElement('button');
    editNameBtn.className = 'edit-btn';
    editNameBtn.innerHTML = '✎';
    editNameBtn.onclick = (e) => {
        handleSelection(e); // Add selection handling
        e.stopPropagation();
        makeEditable(nameSpan, element, 'name');
    };

    nameContainer.appendChild(nameSpan);
    nameContainer.appendChild(editNameBtn);
    div.appendChild(nameContainer);
    if (element.type === 'picture') {
        const pictureContainer = document.createElement('div');
        pictureContainer.className = 'picture-container mt-2';

        // URL input
        const urlContainer = document.createElement('div');
        urlContainer.className = 'input-group mb-2';

        const urlInput = document.createElement('input');
        urlInput.type = 'text';
        urlInput.className = 'form-control';
        urlInput.placeholder = 'Enter picture URL';
        urlInput.value = element.pictureUrl || '';

        const urlButton = document.createElement('button');
        urlButton.className = 'btn btn-outline-secondary';
        urlButton.textContent = 'Set URL';
        urlButton.onclick = (e) => {
            e.stopPropagation();
            element.pictureUrl = urlInput.value;
            renderElements();
        };

        urlContainer.appendChild(urlInput);
        urlContainer.appendChild(urlButton);

        // File upload
        const fileContainer = document.createElement('div');
        fileContainer.className = 'input-group';

        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.className = 'form-control';
        fileInput.accept = 'image/*';

        const uploadButton = document.createElement('button');
        uploadButton.className = 'btn btn-outline-secondary';
        uploadButton.textContent = 'Upload';
        uploadButton.onclick = (e) => {
            e.stopPropagation();
            if (fileInput.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    element.pictureUrl = e.target.result;
                    renderElements();
                };
                reader.readAsDataURL(fileInput.files[0]);
            }
        };

        fileContainer.appendChild(fileInput);
        fileContainer.appendChild(uploadButton);

        pictureContainer.appendChild(urlContainer);
        pictureContainer.appendChild(fileContainer);
        div.appendChild(pictureContainer);

    } else if (element.type === 'select') {
        const optionsContainer = document.createElement('div');
        optionsContainer.className = 'options-container mt-2';

        // Options list
        const optionsList = document.createElement('div');
        optionsList.className = 'options-list';

        element.options.forEach((option, index) => {
            const optionRow = document.createElement('div');
            optionRow.className = 'option-row d-flex align-items-center mb-1';

            // Option text
            const optionText = document.createElement('input');
            optionText.type = 'text';
            optionText.className = 'form-control form-control-sm me-2';
            optionText.value = option;
            optionText.onchange = (e) => {
                element.options[index] = e.target.value;
                renderElements();
            };

            // Remove option button
            const removeOptionBtn = document.createElement('button');
            removeOptionBtn.className = 'btn btn-sm btn-danger';
            removeOptionBtn.innerHTML = 'X';
            removeOptionBtn.onclick = (e) => {
                e.stopPropagation();
                element.options.splice(index, 1);
                renderElements();
            };

            optionRow.appendChild(optionText);
            optionRow.appendChild(removeOptionBtn);
            optionsList.appendChild(optionRow);
        });

        // Add option button
        const addOptionBtn = document.createElement('button');
        addOptionBtn.className = 'btn btn-sm btn-outline-primary mt-1';
        addOptionBtn.innerHTML = '+ Add Option';
        addOptionBtn.onclick = (e) => {
            e.stopPropagation();
            element.options.push(`Option ${element.options.length + 1}`);
            renderElements();
        };

        optionsContainer.appendChild(optionsList);
        optionsContainer.appendChild(addOptionBtn);
        div.appendChild(optionsContainer);

    } else {
        // Editable placeholder with edit button
        const placeholderContainer = document.createElement('div');
        placeholderContainer.className = 'editable-container';
        placeholderContainer.addEventListener('click', handleSelection); // Add click handler

        const placeholderSpan = document.createElement('span');
        placeholderSpan.className = 'field-placeholder';
        placeholderSpan.textContent = element.placeholder;
        placeholderSpan.addEventListener('click', handleSelection); // Add click handler

        const editPlaceholderBtn = document.createElement('button');
        editPlaceholderBtn.className = 'edit-btn';
        editPlaceholderBtn.innerHTML = '✎';
        editPlaceholderBtn.onclick = (e) => {
            handleSelection(e); // Add selection handling
            e.stopPropagation();
            makeEditable(placeholderSpan, element, 'placeholder');
        };

        placeholderContainer.appendChild(placeholderSpan);
        placeholderContainer.appendChild(editPlaceholderBtn);
        div.appendChild(placeholderContainer);
    }

    return div;
}

// Helper function to get the type name
function getElementTypeName(type) {
    const typeNames = {
        text: 'TextField',
        textarea: 'TextArea',
        number: 'NumberField',
        select: 'Dropdown',
        picture: 'Picture',
    };
    return typeNames[type] || 'Unknown';
}

function makeEditable(span, element, property) {
    const input = document.createElement('input');
    input.type = 'text';
    input.value = element[property];
    input.className = 'form-control form-control-sm';

    const saveChanges = () => {
        const newValue = input.value.trim();
        if (newValue) {
            element[property] = newValue;
            renderElements();
        } else {
            span.textContent = element[property];
            input.replaceWith(span);
        }
    };

    input.onblur = saveChanges;
    input.onkeydown = (e) => {
        if (e.key === 'Enter') {
            saveChanges();
        } else if (e.key === 'Escape') {
            input.replaceWith(span);
        }
    };

    span.replaceWith(input);
    input.focus();
    input.select();
}

function createDraggableElement(element) {
    const div = document.createElement('div');
    div.className = `element draggable ${selectedElement?.id === element.id ? 'selected' : ''}`;
    div.id = `element-${element.id}`;
    div.style.left = `${element.x}px`;
    div.style.top = `${element.y}px`;
    div.style.width = `${element.width}px`;
    div.style.minHeight = `${element.height}px`;

    // Remove button
    const removeBtn = document.createElement('button');
    removeBtn.className = 'btn btn-danger remove-btn';
    removeBtn.innerHTML = 'X';
    removeBtn.onclick = (e) => {
        e.stopPropagation();
        removeElement(element.id);
    };
    div.appendChild(removeBtn);

    // Name display
    const nameDiv = document.createElement('div');
    nameDiv.className = 'pdf-field-name';
    nameDiv.textContent = element.name;
    div.appendChild(nameDiv);

    // Input preview
    let input, pictureContainer;
    switch (element.type) {
        case 'text':
            input = document.createElement('input');
            input.type = 'text';
            break;
        case 'textarea':
            input = document.createElement('textarea');
            break;
        case 'number':
            input = document.createElement('input');
            input.type = 'number';
            break;
        case 'select':
            input = document.createElement('div'); // Change to div instead of select
            input.className = 'form-control mt-1';
            input.textContent = 'Vybraná možnost';
            input.style.color = '#6c757d'; // Optional: makes the text appear muted
            break;
        case 'picture':
            pictureContainer = document.createElement('div');
            pictureContainer.className = 'picture-preview';
            pictureContainer.style.display = 'flex';
            pictureContainer.style.alignItems = 'center';
            pictureContainer.style.justifyContent = 'center';
            pictureContainer.style.overflow = 'hidden';


            const img = document.createElement('img');
            img.src = PICTURE_PLACEHOLDER_URL;
            img.style.width = '100%'; // Fill the width of the container
            img.style.height = '100%'; // Fill the height of the container
            img.style.objectFit = 'cover'; // Ensure the image scales proportionally to cover the container

            pictureContainer.appendChild(img);
            break;
    }

    if (input) {
        input.className = 'form-control mt-1';
        input.placeholder = element.placeholder;
        input.disabled = true;
        div.appendChild(input);
    }

    if (pictureContainer) {
        div.appendChild(pictureContainer)
    }

    // Add click handler for selection
    div.addEventListener('click', (e) => {
        if (e.target === removeBtn) return;

        document.querySelectorAll('.element').forEach(el => {
            el.classList.remove('selected');
        });
        document.querySelectorAll('.form-element-container').forEach(el => {
            el.classList.remove('selected');
        });

        div.classList.add('selected');
        const formElement = document.getElementById(`form-${element.id}`);
        if (formElement) {
            formElement.classList.add('selected');
        }

        selectedElement = element;
    });

    // Add drag functionality
    div.addEventListener('mousedown', (e) => {
        if (e.target === removeBtn || e.target.classList.contains('resize-handle')) return;

        const pdfPreview = document.getElementById('pdfPreview');
        const rect = pdfPreview.getBoundingClientRect();
        const elementRect = div.getBoundingClientRect();

        offsetX = e.clientX - elementRect.left;
        offsetY = e.clientY - elementRect.top;

        draggedElement = element;
        selectedElement = element;

        div.classList.add('dragging');

        renderElements();
    });

    // Add resize handles
    const handles = ['nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w'].map(direction => {
        const handle = document.createElement('div');
        handle.className = `resize-handle ${direction}`;
        return handle;
    });

    handles.forEach(handle => {
        div.appendChild(handle);

        handle.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            const startX = e.clientX;
            const startY = e.clientY;
            const startWidth = element.width;
            const startHeight = element.height;
            const startLeft = element.x;
            const startTop = element.y;
            const direction = handle.className.split(' ')[1];

            const pdfPreview = document.getElementById('pdfPreview');
            const pdfRect = pdfPreview.getBoundingClientRect();
            const maxWidth = pdfRect.width;
            const maxHeight = pdfRect.height;

            const onMouseMove = (e) => {
                const deltaX = e.clientX - startX;
                const deltaY = e.clientY - startY;

                // Helper function to constrain dimensions
                const constrainDimensions = (x, y, w, h) => {
                    // Ensure element stays within PDF preview bounds
                    const newX = Math.max(0, Math.min(x, maxWidth - w));
                    const newY = Math.max(0, Math.min(y, maxHeight - h));
                    const newWidth = Math.max(50, Math.min(w, maxWidth - newX));
                    const newHeight = Math.max(30, Math.min(h, maxHeight - newY));
                    return { x: newX, y: newY, width: newWidth, height: newHeight };
                };

                let newDimensions;

                switch(direction) {
                    case 'se':
                        newDimensions = constrainDimensions(
                            startLeft,
                            startTop,
                            startWidth + deltaX,
                            startHeight + deltaY
                        );
                        break;
                    case 'sw':
                        newDimensions = constrainDimensions(
                            startLeft + deltaX,
                            startTop,
                            startWidth - deltaX,
                            startHeight + deltaY
                        );
                        break;
                    case 'ne':
                        newDimensions = constrainDimensions(
                            startLeft,
                            startTop + deltaY,
                            startWidth + deltaX,
                            startHeight - deltaY
                        );
                        break;
                    case 'nw':
                        newDimensions = constrainDimensions(
                            startLeft + deltaX,
                            startTop + deltaY,
                            startWidth - deltaX,
                            startHeight - deltaY
                        );
                        break;
                    case 'n':
                        newDimensions = constrainDimensions(
                            startLeft,
                            startTop + deltaY,
                            startWidth,
                            startHeight - deltaY
                        );
                        break;
                    case 's':
                        newDimensions = constrainDimensions(
                            startLeft,
                            startTop,
                            startWidth,
                            startHeight + deltaY
                        );
                        break;
                    case 'e':
                        newDimensions = constrainDimensions(
                            startLeft,
                            startTop,
                            startWidth + deltaX,
                            startHeight
                        );
                        break;
                    case 'w':
                        newDimensions = constrainDimensions(
                            startLeft + deltaX,
                            startTop,
                            startWidth - deltaX,
                            startHeight
                        );
                        break;
                }

                // Apply the constrained dimensions
                element.x = newDimensions.x;
                element.y = newDimensions.y;
                element.width = newDimensions.width;
                element.height = newDimensions.height;

                renderElements();
            };

            const onMouseUp = () => {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            };

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });
    });

    return div;
}

function renderElements() {
    const pdfPreview = document.getElementById('pdfPreview');
    const formPreview = document.getElementById('formPreview');

    // Clear existing elements
    pdfPreview.innerHTML = '';
    formPreview.innerHTML = '';

    elements.forEach(element => {
        // Render the element in the PDF preview
        const pdfElement = createDraggableElement(element);
        pdfPreview.appendChild(pdfElement);

        // Render the element in the Form preview
        const formElement = createFormElement(element);
        formPreview.appendChild(formElement);

        // Maintain selection state
        if (selectedElement?.id === element.id) {
            pdfElement.classList.add('selected');
            formElement.classList.add('selected');
        }
    });
}

async function saveConfiguration() {
    const configToSave = {
        name: currentFormName,
        description: currentDescription,
        elements: elements,
        elementCounts: elementCounts
    };

    try {
        const url = templateId
            ? `/editor/save-template/${templateId}/`
            : `/editor/save-template/`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify(configToSave)
        });

        const data = await response.json();
        if (data.status === 'success') {
            if (!templateId) {
                templateId = data.templateId;
                window.history.pushState({}, '', `/editor/${templateId}/`);
            }
            alert('Template saved successfully!');
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        alert('Error saving template: ' + error.message);
    }
}

async function resetChanges() {
    if (confirm('Are you sure you want to reset all changes?')) {
        await loadConfiguration();
    }
}

async function loadConfiguration() {
    if (!templateId) {
        elements = [];
        elementCounts = {
            text: 0,
            textarea: 0,
            number: 0,
            select: 0,
            picture: 0,
        };
        currentFormName = 'Nepojmenovaný template';
        updateFormNameButton();
        updateFormDescription();
        renderElements();
        return;
    }

    try {
        const response = await fetch(`/editor/load-template/${templateId}/`);
        if (!response.ok) {
            throw new Error('Failed to load template');
        }
        const config = await response.json();

        elements = [];
        elementCounts = {
            text: 0,
            textarea: 0,
            number: 0,
            select: 0,
            picture: 0,
        };

        elements = config.elements || [];
        elements.forEach(element => {
            elementCounts[element.type] = (elementCounts[element.type] || 0) + 1;
        });

        currentFormName = config.name;
        currentDescription = config.description;
        updateFormNameButton();
        updateFormDescription();

        renderElements();
    } catch (error) {
        alert('Error loading template: ' + error.message);
    }
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!token) {
        console.error('CSRF token not found in the document');
        return '';
    }
    return token.value;
}