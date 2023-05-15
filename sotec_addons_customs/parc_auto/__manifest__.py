{
    'name': 'PARC AUTO - SOTEC',
    'version': '1.0',
    'website': '',
    'category': 'Logiciel Parc Auto',
    'summary': "Ce logiciel est conçu pour faciliter la gestion de parc automobile",
    'author': 'Songo Technonogies (SOTEC)',
    'depends': ['base', 'fleet', "mail"],
    'images': ['static/description/auto.jpg'],
    'data': [
        'views/vue_parc.xml',
        'views/vue_parametres_parc.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
