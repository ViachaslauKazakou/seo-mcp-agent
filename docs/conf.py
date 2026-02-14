# Configuration file for Sphinx documentation builder

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath('..'))

project = 'SEO MCP Agent'
copyright = '2026, Viachaslau Kazakou'
author = 'Viachaslau Kazakou'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'myst_parser',
    'sphinx_autodoc_typehints',
]

# MyST configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

# Source file suffixes
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output options
html_theme = 'sphinx_book_theme'
html_static_path = []
html_logo = 'logo.svg'

# Theme options
html_theme_options = {
    "repository_url": "https://github.com/ViachaslauKazakou/seo-mcp-agent",
    "repository_branch": "main",
    "use_issues_button": True,
    "use_repository_button": True,
}

# Napoleon extension settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False

# Autodoc settings
autodoc_typehints = "description"
autodoc_member_order = "bysource"

# Intersphinx settings
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}

# LaTeX settings
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
}

latex_documents = [
    ('index', 'seo-mcp-agent.tex', 'SEO MCP Agent Documentation',
     'Viachaslau Kazakou', 'manual'),
]
