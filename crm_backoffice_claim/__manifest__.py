# Copyright 2015-2017 Odoo S.A.
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Cristina Martin R.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "BackOffice Claims Extends",
   # "version": "13.0.1.0.0",
    "category": "Customer Relationship Management",
    'author': "Mordant Business Solutions",
    'website': 'https://www.mordantbs.com',
    'category': 'CRM',
    'version': '13.0.0.2',
    "summary": "Track your customers/vendors claims and grievances.",
    "depends": ["crm_claim","base_geolocalize","sale_management","crm_claim_type"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/res_media_views.xml",
        "views/crm_claims_views.xml"
    ],
    "installable": True,
}
