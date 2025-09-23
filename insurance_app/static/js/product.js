
let currentView = 'grid';
let compareList = [];

function setView(view) {
    currentView = view;
    const container = document.getElementById('productsContainer');
    const gridBtn = document.getElementById('gridView');
    const listBtn = document.getElementById('listView');

    if (view === 'grid') {
        container.className = 'grid md:grid-cols-2 xl:grid-cols-3 gap-6';
        gridBtn.className = 'p-2 bg-blue-600 text-white rounded-l-lg';
        listBtn.className = 'p-2 text-gray-600 hover:bg-gray-100 rounded-r-lg';
    } else {
        container.className = 'space-y-6';
        gridBtn.className = 'p-2 text-gray-600 hover:bg-gray-100 rounded-l-lg';
        listBtn.className = 'p-2 bg-blue-600 text-white rounded-r-lg';

        // Modify cards for list view
        document.querySelectorAll('.product-card').forEach(card => {
            if (view === 'list') {
                card.classList.add('flex', 'flex-row');
                const img = card.querySelector('.h-48');
                if (img) img.className = 'w-48 h-48 bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center flex-shrink-0';
            } else {
                card.classList.remove('flex', 'flex-row');
            }
        });
    }
}

// Đóng modal
document.getElementById("closeCompare").addEventListener("click", function () {
    document.getElementById("compareModal").style.display = "none";
    compareProducts = [];
});
