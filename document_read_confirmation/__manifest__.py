{
    'name': "Confirmación de Lectura de Documentos",
    'version': '1.0',
    'summary': "Permite rastrear y confirmar la lectura de documentos en Odoo.",
    'description': """
        Este módulo añade la funcionalidad de confirmar la lectura de documentos
        adjuntos en Odoo, proporcionando un historial y seguimiento de quién
        ha leído qué documento y cuándo.Tamnbien con resúmenes generados por IA
    """,
    'author': "César Collado",
    'website': "",
    'category': 'Productivity/Documents',
    'depends': ['base', 'mail'],
    'data': [
        "data/gemini.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/documento_interno_views.xml",
        'views/documento_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['google-generativeai']
    },
}