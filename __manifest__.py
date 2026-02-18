{
    'name': "l10n_cl_hr_payroll_community",

    'summary': """
        Chilean Payroll Localization Community Edition""",

    'description': """
        Chilean Payroll Localization including:
        - Economic Indicators (UF, UTM, UTA, IMM)
        - Impuesto Único
        - LRE Export Wizard
        - Contract Extensions
        - Salary Rule Extensions
    """,

    'author': "Bentamar",
    'website': "http://www.bentamar.cl",

    'category': 'Human Resources/Payroll',
    'version': '18.0.1.0.0',

    'depends': ['base', 'hr', 'hr_contract', 'om_hr_payroll'],

    'data': [
        'security/ir.model.access.csv',
        'views/indicators_view.xml',
        'views/afp_parameter_view.xml',
        'views/family_parameter_view.xml',
        'views/res_company_view.xml',
        'views/iu_views.xml',
        'views/hr_contract_view.xml',
        'views/hr_salary_rule_view.xml',
        'wizard/lre_export_wizard_views.xml',
        'wizard/previred_export_wizard_views.xml',
        'views/menu.xml',
    ],
    "application": False,
}