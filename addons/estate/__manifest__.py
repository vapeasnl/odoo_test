{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "salim",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/res_users_views.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
      #  'demo/demo_data.xml',
    ],
    'application': True,

}