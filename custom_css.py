"""
Custom CSS styling for professional UI/UX.
"""

CUSTOM_CSS = """
<style>
    /* Global Styles */
    :root {
        --primary-color: #0f766e;
        --primary-light: #14b8a6;
        --primary-dark: #0d3d3c;
        --accent-color: #f59e0b;
        --danger-color: #ef4444;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --bg-light: #f8fafc;
        --bg-card: #ffffff;
        --text-dark: #1e293b;
        --text-light: #64748b;
        --border-color: #e2e8f0;
    }
    
    /* Main Container */
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d3d3c 0%, #0f766e 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ffffff;
    }
    
    /* Sidebar Navigation - Extra Large & Prominent */
    [data-testid="stSidebar"] a {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        padding: 1rem !important;
        display: block !important;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stSidebar"] button {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        padding: 1.2rem 1.5rem !important;
        width: 100%;
        min-height: 60px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    [data-testid="stSidebar"] label {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--text-dark);
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: #0f766e;
    }
    
    h2 {
        font-size: 1.875rem;
        margin-top: 1.5rem;
        border-bottom: 3px solid var(--primary-light);
        padding-bottom: 0.5rem;
    }
    
    /* Card Styles */
    [data-testid="stContainer"] {
        background: var(--bg-card);
        border-radius: 12px;
        border: 1px solid var(--border-color);
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    [data-testid="stContainer"]:hover {
        border-color: var(--primary-light);
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.15);
    }
    
    /* Buttons */
    button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(15, 118, 110, 0.2);
    }
    
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3);
    }
    
    button:active {
        transform: translateY(0);
    }
    
    /* Input Fields */
    input[type="text"],
    input[type="email"],
    input[type="search"],
    textarea,
    select {
        border: 2px solid #2d3748 !important;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: #1a202c !important;
        color: #ffffff !important;
    }
    
    input[type="text"]:focus,
    input[type="email"]:focus,
    input[type="search"]:focus,
    textarea:focus,
    select:focus {
        outline: none;
        border-color: #2d3748 !important;
        box-shadow: none;
        background: #1a202c !important;
        color: #ffffff !important;
    }
    
    input[type="text"]::placeholder,
    input[type="email"]::placeholder,
    input[type="search"]::placeholder,
    textarea::placeholder {
        color: #a0aec0 !important;
    }
    
    /* Info/Success/Warning/Error Messages */
    [data-testid="stAlert"] {
        border-radius: 8px;
        border: 2px solid;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stSuccess {
        border-color: var(--success-color);
        background: rgba(16, 185, 129, 0.1);
        color: var(--success-color);
    }
    
    .stError {
        border-color: var(--danger-color);
        background: rgba(239, 68, 68, 0.1);
        color: var(--danger-color);
    }
    
    .stWarning {
        border-color: var(--warning-color);
        background: rgba(245, 158, 11, 0.1);
        color: var(--warning-color);
    }
    
    .stInfo {
        border-color: var(--primary-light);
        background: rgba(20, 184, 166, 0.1);
        color: var(--primary-dark);
    }
    
    /* Tab Styles */
    [data-testid="stTabs"] [aria-selected="true"] {
        border-bottom: 3px solid var(--primary-light);
        color: var(--primary-dark);
    }
    
    /* Metric Cards */
    [data-testid="metric-container"] {
        background: var(--bg-card);
        border: 2px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    /* Expander/Collapsible */
    [data-testid="stExpander"] {
        border: 2px solid var(--border-color);
        border-radius: 8px;
        background: var(--bg-card);
    }
    
    /* Links */
    a {
        color: var(--primary-light);
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
        border-bottom: 2px solid transparent;
    }
    
    a:hover {
        color: var(--primary-color);
        border-bottom-color: var(--primary-light);
    }
    
    /* Code Blocks */
    code {
        background: var(--bg-light);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 0.25rem 0.5rem;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        color: var(--text-dark);
    }
    
    /* Spinner */
    [data-testid="stSpinner"] {
        color: var(--primary-light);
    }
    
    /* News Article Card */
    .news-card {
        background: var(--bg-card);
        border: 2px solid var(--border-color);
        border-left: 4px solid var(--primary-light);
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .news-card:hover {
        border-left-color: var(--primary-color);
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.15);
        transform: translateX(4px);
    }
    
    .news-title {
        font-size: 1.125rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.75rem;
        line-height: 1.4;
    }
    
    .news-meta {
        display: flex;
        gap: 1rem;
        margin: 0.75rem 0;
        flex-wrap: wrap;
        font-size: 0.875rem;
        color: var(--text-light);
    }
    
    .news-meta-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .news-snippet {
        color: var(--text-dark);
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 0.75rem 0;
    }
    
    /* Source Badge */
    .source-badge {
        display: inline-block;
        background: linear-gradient(135deg, #14b8a6 0%, #0f766e 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .rss-badge {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }
    
    .twitter-badge {
        background: linear-gradient(135deg, #1da1f2 0%, #1a91da 100%);
    }
    
    /* Search Box */
    .search-container {
        background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0 1rem 0;
        color: white;
    }
    
    .search-container h3 {
        color: white;
        margin-bottom: 1rem;
    }
    
    /* Columns Layout - Vertical Alignment Fix */
    [data-testid="column"] {
        padding: 0;
        margin: 0;
        display: flex;
        align-items: flex-start;
        justify-content: flex-start;
        padding-top: 8px;
    }
    
    /* Input and Button Height Match */
    [data-testid="column"] input[type="text"],
    [data-testid="column"] input[type="search"],
    [data-testid="column"] button {
        height: 48px;
        display: flex;
        align-items: center;
    }
    
    [data-testid="column"] button {
        margin-top: 12px !important;
    }
    
    /* Remove Extra Spacing */
    [data-testid="stVerticalBlock"] > [data-testid="column"] {
        padding: 0.25rem 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-light);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-light);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-color);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        .news-card {
            padding: 1rem;
        }
        
        .news-meta {
            flex-direction: column;
            gap: 0.5rem;
        }
    }
</style>
"""


def inject_css():
    """Inject custom CSS into Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
