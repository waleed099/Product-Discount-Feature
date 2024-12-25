# -*- coding: utf-8 -*-
{
    'name': "product_discount_feature",

    'summary': "Product Discount Feature",

    'description': """
        Implement a simple feature in Odoo's eCommerce module. The task is to
        create a Product Discount Feature where a percentage discount can be applied to
        specic products, and the discounted price should be reected in the product listings
        and on the product detail page in the eCommerce store.
    """,

    'author': "Waleed Saeed",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['website_sale' ,'sale', 'sale_management' , 'product', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'reports/report_sale.xml',
        'views/templates.xml',
    ],
   
    "installable": True,
    'license': 'LGPL-3',
    
    
}

