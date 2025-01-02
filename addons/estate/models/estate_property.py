from odoo import api, fields, models, _
from odoo.exceptions import UserError

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "A Realestate Property"
    _order = "id desc"

    name = fields.Char('Property Name', required=True)
    description = fields.Text('Description', required=True)
    postcode = fields.Char('Postcode', required=False)
    date_availability = fields.Date('Availability Date', required=True, default=lambda self: fields.Datetime.add(fields.Datetime.today(), months=3), copy=False)
    expected_price = fields.Float('Expected Price', required=False)
    selling_price = fields.Float('Selling Price', required=False, copy=False, readonly=True)
    bedrooms = fields.Integer('Bedrooms', required=True, default=2)
    living_area = fields.Integer('Living Area', required=True, default=0)
    facades = fields.Integer('Facades', required=True, default=0)
    garage = fields.Boolean('Garage', required=True, default=False)
    garden = fields.Boolean('Garden', required=True, default=False)
    garden_area = fields.Integer('Garden Area', required=True, default=0)
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('east', 'East'), ('south', 'South'), ('west', 'West')],
        help="Select garden orientation"
    )
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(
            string='State',
            selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
            default='new'
            )

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Float(compute="_compute_total_area")
    best_offer = fields.Float(compute="_compute_best_offer")    
    
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)', 'The expected price must be a positive number.'),
        ('check_selling_price', 'CHECK(selling_price >= 0 OR selling_price IS NULL)', 'The selling price must be a positive number or NULL.')
    ]
    
    @api.ondelete(at_uninstall=False)
    def _unlink_record(self):
        # Interdit la suppression d'un enregistrement si son état n'est pas 'new' ou 'canceled'.
        if self.state not in ('new', 'canceled'):
            raise UserError(_('Sorry you can\'t delete this, only a canceled or new property can be deleted.'))
    
    @api.depends("living_area", "garden_area", "garden")
    def _compute_total_area(self):
        for record in self:
            # Calcule la surface totale en fonction de l'aire habitable et de la présence d'un jardin.
            total_area = record.living_area
            if record.garden:
                total_area += record.garden_area
            record.total_area = total_area

    @api.depends("offer_ids")
    def _compute_best_offer(self):
        for record in self:
            # Définit le meilleur prix d'offre en sélectionnant le maximum dans `offer_ids`.
            record.best_offer = max(record.offer_ids.mapped("price"), default=0)
                
    @api.onchange("garden")
    def _onchange_partner_id(self):
        # Modifie automatiquement `garden_area` et `garden_orientation` quand `garden` est activé.
        self.garden_area = 10
        self.garden_orientation = "north"
        
    def action_cancel_property(self):
        # Annule la propriété seulement si son état est 'new' ou 'canceled'.
        if any(record.state != 'new' and record.state != 'canceled' for record in self):
            raise UserError(_('Only a canceled or new property can be deleted.'))
        return self.write({'state': 'canceled'})
    
    def action_sold_property(self):
        # Marque la propriété comme 'sold' sauf si son état est 'canceled'.
        if any(record.state == 'canceled' for record in self):
            raise UserError(_('A canceled property cannot be sold.'))
        return self.write({'state': 'sold'})
