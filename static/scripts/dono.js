// Banco de dados de produtos (simulado)
const productsDatabase = [
    { id: 'P001', name: 'Pelúcia', category: 'Brinquedos', price: 29.90, stock: 15, available: true },
    { id: 'P002', name: 'Ração Premium', category: 'Alimentos', price: 89.90, stock: 42, available: true },
    { id: 'P003', name: 'Coleira Antipulgas', category: 'Acessórios', price: 45.50, stock: 0, available: false },
    { id: 'P004', name: 'Camiseta Estampada', category: 'Vestuário', price: 59.90, stock: 8, available: true },
    { id: 'P005', name: 'Caneca Personalizada', category: 'Casa e Cozinha', price: 32.90, stock: 20, available: true },
    { id: 'P006', name: 'Adesivo para Carro', category: 'Automotivo', price: 14.90, stock: 0, available: false },
    { id: 'P007', name: 'Poster Decorativo', category: 'Decoração', price: 24.90, stock: 12, available: true },
    { id: 'P008', name: 'Chaveiro de Metal', category: 'Acessórios', price: 19.90, stock: 25, available: true },
    { id: 'P009', name: 'Livro de Treinamento', category: 'Livros', price: 49.90, stock: 7, available: true },
    { id: 'P010', name: 'Kit de Cuidados', category: 'Cuidados Pessoais', price: 79.90, stock: 0, available: false },
    { id: 'P011', name: 'Brinquedo Interativo', category: 'Brinquedos', price: 39.90, stock: 18, available: true },
    { id: 'P012', name: 'Snack Natural', category: 'Alimentos', price: 22.90, stock: 0, available: false },
    { id: 'P013', name: 'Guia para Passeio', category: 'Acessórios', price: 65.90, stock: 5, available: true },
    { id: 'P014', name: 'Moletom', category: 'Vestuário', price: 99.90, stock: 3, available: true }
];

// Dados de vendas para cálculo de lucro (simulado)
const monthlySales = [
    { productId: 'P001', unitsSold: 12, revenue: 358.80 },
    { productId: 'P002', unitsSold: 25, revenue: 2247.50 },
    { productId: 'P004', unitsSold: 8, revenue: 479.20 },
    { productId: 'P005', unitsSold: 15, revenue: 493.50 },
    { productId: 'P007', unitsSold: 10, revenue: 249.00 },
    { productId: 'P008', unitsSold: 18, revenue: 358.20 },
    { productId: 'P009', unitsSold: 5, revenue: 249.50 },
    { productId: 'P011', unitsSold: 14, revenue: 558.60 },
    { productId: 'P013', unitsSold: 7, revenue: 461.30 },
    { productId: 'P014', unitsSold: 3, revenue: 299.70 }
];

// Estado da aplicação
let currentView = 'categorized';
let isOwnerView = false;

// Função para calcular o lucro total
function calculateTotalProfit() {
    return monthlySales.reduce((total, sale) => total + sale.revenue, 0);
}

// Função para agrupar produtos por categoria
function groupByCategory(products) {
    return products.reduce((acc, product) => {
        if (!acc[product.category]) {
            acc[product.category] = [];
        }
        acc[product.category].push(product);
        return acc;
    }, {});
}

// Função para ordenar produtos
function sortProducts(products, sortBy) {
    switch(sortBy) {
        case 'name':
            return products.sort((a, b) => a.name.localeCompare(b.name));
        case 'category':
            return products.sort((a, b) => a.category.localeCompare(b.category));
        case 'price-asc':
            return products.sort((a, b) => a.price - b.price);
        case 'price-desc':
            return products.sort((a, b) => b.price - a.price);
        default:
            return products;
    }
}

// Função para filtrar produtos
function filterProducts(products, category, availability) {
    return products.filter(product => {
        const categoryMatch = category === 'all' || product.category === category;
        const availabilityMatch = availability === 'all' || 
                                (availability === 'available' && product.available) ||
                                (availability === 'unavailable' && !product.available);
        return categoryMatch && availabilityMatch;
    });
}
// Função para renderizar os produtos na tela (visão por categoria) - ATUALIZADA
function renderCategorizedView(products) {
    const container = document.getElementById('products-container');
    container.innerHTML = '';
    
    if (products.length === 0) {
        container.innerHTML = '<div class="no-results">Nenhum produto encontrado</div>';
        return;
    }
    
    // Atualizar estatísticas
    updateStats(products);
    
    // Agrupar por categoria
    const groupedProducts = groupByCategory(products);
    
    // Ordenar categorias alfabeticamente
    const sortedCategories = Object.keys(groupedProducts).sort();
    
    // Obter o tipo de ordenação selecionado
    const sortBy = document.getElementById('sort-select').value;
    
    // Para cada categoria, criar uma seção
    sortedCategories.forEach(category => {
        const categorySection = document.createElement('div');
        categorySection.className = 'category-section';
        
        const categoryHeader = document.createElement('div');
        categoryHeader.className = 'category-header';
        categoryHeader.textContent = `${category} (${groupedProducts[category].length} produtos)`;
        
        categorySection.appendChild(categoryHeader);
        
        // Ordenar produtos da categoria conforme a seleção do usuário
        const sortedProducts = sortProducts([...groupedProducts[category]], sortBy);
        
        // Adicionar cada produto da categoria
        sortedProducts.forEach(product => {
            const productElement = document.createElement('div');
            productElement.className = 'product';
            
            productElement.innerHTML = `
                <div class="product-code">#${product.id}</div>
                <div class="product-info">
                    <div class="product-name">${product.name}</div>
                    <div class="product-category" style="display: none;">${product.category}</div>
                </div>
                <div class="product-price">R$ ${product.price.toFixed(2)}</div>
                <div class="product-stock">${product.stock} un</div>
                <div class="product-availability ${product.available ? 'available' : 'unavailable'}">
                    ${product.available ? 'Disponível' : 'Esgotado'}
                </div>
            `;
            
            categorySection.appendChild(productElement);
        });
        
        container.appendChild(categorySection);
    });
}

// Função para renderizar os produtos na tela (visão em lista) - ATUALIZADA
function renderListView(products) {
    const container = document.getElementById('products-container');
    container.innerHTML = '';
    
    if (products.length === 0) {
        container.innerHTML = '<div class="no-results">Nenhum produto encontrado</div>';
        return;
    }
    
    // Atualizar estatísticas
    updateStats(products);
    
    // Ordenar produtos conforme a seleção do usuário
    const sortBy = document.getElementById('sort-select').value;
    const sortedProducts = sortProducts(products, sortBy);
    
    // Adicionar cada produto
    sortedProducts.forEach(product => {
        const productElement = document.createElement('div');
        productElement.className = 'product';
        
        productElement.innerHTML = `
            <div class="product-code">#${product.id}</div>
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-category">${product.category}</div>
            </div>
            <div class="product-price">R$ ${product.price.toFixed(2)}</div>
            <div class="product-stock">${product.stock} un</div>
            <div class="product-availability ${product.available ? 'available' : 'unavailable'}">
                ${product.available ? 'Disponível' : 'Esgotado'}
            </div>
        `;
        
        container.appendChild(productElement);
    });
}

// Função para pesquisar produtos (ATUALIZADA)
function searchProducts() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const categoryFilter = document.getElementById('category-filter').value;
    const availabilityFilter = document.getElementById('availability-filter').value;
    
    let filteredProducts = filterProducts(productsDatabase, categoryFilter, availabilityFilter);
    
    if (searchTerm) {
        filteredProducts = filteredProducts.filter(product => 
            product.name.toLowerCase().includes(searchTerm) || 
            product.category.toLowerCase().includes(searchTerm)
        );
    }
    
    // Aplicar a visualização atual (agora a ordenação é aplicada dentro de cada função de render)
    if (currentView === 'categorized') {
        renderCategorizedView(filteredProducts);
    } else {
        renderListView(filteredProducts);
    }
}

// Função para alternar entre visualizações (ATUALIZADA)
function toggleView(viewType) {
    currentView = viewType;
    
    // Atualizar botões
    document.getElementById('categorized-view').classList.toggle('active', viewType === 'categorized');
    document.getElementById('list-view').classList.toggle('active', viewType === 'list');
    
    // Mostrar/ocultar elementos conforme a visualização
    const categoryElements = document.querySelectorAll('.product-category');
    categoryElements.forEach(el => {
        el.style.display = viewType === 'list' ? 'block' : 'none';
    });
    
    // Renderizar a visualização atual
    searchProducts();
}

// Event listeners (ATUALIZADOS)
document.getElementById('sort-select').addEventListener('change', searchProducts);

// Função para atualizar as estatísticas
function updateStats(products) {
    const totalProducts = products.length;
    const availableProducts = products.filter(p => p.available).length;
    const unavailableProducts = totalProducts - availableProducts;
    
    // Agrupar para contar categorias únicas
    const categories = [...new Set(products.map(p => p.category))];
    
    document.getElementById('total-products').textContent = totalProducts;
    document.getElementById('available-products').textContent = availableProducts;
    document.getElementById('unavailable-products').textContent = unavailableProducts;
    document.getElementById('total-categories').textContent = categories.length;
}

// Função para preencher o filtro de categorias
function populateCategoryFilter() {
    const categoryFilter = document.getElementById('category-filter');
    const categories = [...new Set(productsDatabase.map(p => p.category))].sort();
    
    // Limpar opções existentes (exceto a primeira)
    while (categoryFilter.options.length > 1) {
        categoryFilter.remove(1);
    }
    
    // Adicionar categorias
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });
}


// Event listeners
document.getElementById('search-button').addEventListener('click', searchProducts);
document.getElementById('search-input').addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
        searchProducts();
    }
});

document.getElementById('sort-select').addEventListener('change', searchProducts);
document.getElementById('category-filter').addEventListener('change', searchProducts);
document.getElementById('availability-filter').addEventListener('change', searchProducts);

document.getElementById('categorized-view').addEventListener('click', () => toggleView('categorized'));
document.getElementById('list-view').addEventListener('click', () => toggleView('list'));

// Inicializar a aplicação
document.addEventListener('DOMContentLoaded', () => {
    populateCategoryFilter();
    renderCategorizedView(productsDatabase);
});