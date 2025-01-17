function newDocument() {
    document.getElementById('doc-content').value = '';
}

document.addEventListener('DOMContentLoaded', function() {
    const list = document.getElementById('document-list');
    list.querySelectorAll('li').forEach(li => {
        li.addEventListener('click', function() {
            const title = this.getAttribute('data-title');
            loadDocument(title);
        });
    });
});

function loadDocument(title) {
    fetch(`/get_document?title=${encodeURIComponent(title)}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('doc-content').value = data.content;
        } else {
            alert('Error loading document.');
        }
    });
}


function saveDocument() {
    const content = document.getElementById('doc-content').value;
    const title = prompt("Enter document title:");
    if (title && content) {
        fetch('/add_document', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: title, content: content })
        }).then(response => response.json())
          .then(data => {
            if (data.success) {
                alert('Document saved successfully.');
                location.reload();  // Reload to update the document list
            } else {
                alert('Error saving document.');
            }
        });
    } else {
        alert("You must provide a title and content for the document.");
    }
}


function saveAndDownloadPDF() {
    let content = document.getElementById('doc-content').value;
    let title = prompt("Enter document title:");
    if (title && content) {
        fetch('/save_pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: title, content: content })
        }).then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('Network response was not ok.');
        }).then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `${title}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        }).catch(error => console.error('Error:', error));
    } else {
        alert("You must provide a title and content for the document.");
    }
}
function loadDocument(title) {
    fetch(`/get_document?title=${encodeURIComponent(title)}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('doc-content').value = data.content;
        } else {
            alert('Error loading document.');
        }
    });
}
