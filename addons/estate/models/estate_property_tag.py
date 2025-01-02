# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Realestate Property Tags"
    _order = "name asc"
    
    name = fields.Char('Property Tags', required=True)
    color = fields.Integer('Tag Color')
    active = fields.Boolean('Active', default=True)
    
   
