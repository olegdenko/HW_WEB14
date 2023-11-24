import sys
import os
sys.path.append(os.path.abspath('..'))

project = 'Contacts book'
copyright = '2023, OlegDenko'
author = 'OlegDenko'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['__build', 'Thumbs.db', '.DS_Store']


html_theme = 'nature'
html_static_path = ['_static']
