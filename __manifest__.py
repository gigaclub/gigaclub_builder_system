{
    'name': 'GigaClub Builder System',
    'version': '14.0.1.0.0',
    'summary': 'GigaClub Builder System Module',
    'category': 'GigaClub',
    'author': 'GigaClub.net',
    'website': 'https://GigaClub.net/',
    'license': 'GPL-3',
    'depends': ['gigaclub_translation', 'gigaclub_team'],
    'data': [
         'data/gc_builder_world_type_data.xml',
         'views/gc_builder_task_view.xml',
         'views/gc_team_view.xml',
         'views/gc_user_view.xml',
         'views/gc_builder_world_view.xml',
         'views/gc_builder_world_type_view.xml',
         'views/menu_views.xml',
         'security/ir.model.access.csv'
     ],
    'installable': True,
    'auto_install': False
}
