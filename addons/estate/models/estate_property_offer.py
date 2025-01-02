# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta

from odoo.exceptions import UserError, ValidationError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Realestate Property Offer"
    _order = "price desc"
    
    price = fields.Float('Offer Amount', required=True)
    
    status = fields.Selection(
        string='Offer Status',
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        help="Select status")
    
    partner_id = fields.Many2one("res.partner", string="Partner", copy=False)
    property_id = fields.Many2one("estate.property", string="Property")
    validity = fields.Integer("Offer Validity", default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    
    _sql_constraints = [
        ('check_offer_price', 'CHECK(price > 0)', 'The offer price must a positive number.'),
    ]
        
        
        
    @api.model
    def create(self, vals):
        # Récupère l'offre ayant le prix le plus élevé pour la propriété spécifiée par 'property_id' dans `vals`.
        max_offer = self.env['estate.property.offer'].search(
            [('property_id', '=', vals['property_id'])], order='price desc', limit=1
        )

        # Vérifie si le prix de la nouvelle offre est supérieur à l'offre maximale existante.
        if int(vals['price']) <= int(max_offer['price']):
            # Si le prix de la nouvelle offre est inférieur ou égal au prix maximum existant, lève une erreur de validation.
            raise ValidationError("The offer [%d] should be higher than [%d]" % (
                int(vals['price']), int(max_offer['price'])
            ))

        # Met à jour l'état de la propriété à 'offer_received' pour indiquer qu'une nouvelle offre a été reçue.
        self.env['estate.property'].browse(vals['property_id']).state = 'offer_received'

        # Appelle la méthode `create` d'Odoo pour insérer le nouvel enregistrement.
        return super().create(vals)

    
    
        
    @api.constrains('price')
    def _check_offer_price(self):
        # Cette contrainte vérifie que le prix de l'offre (price) est au moins 90% du prix attendu (expected_price).
        for record in self:
            # Calcule le pourcentage du prix de l'offre par rapport au prix attendu.
            if (100 * float(record.price) / float(record.property_id.expected_price)) < 90:
                # Si le prix est inférieur à 90% du prix attendu, une erreur est levée.
                raise ValidationError("The offer price should be at least 90% of the expected price.")

    
    @api.depends("validity")
    def _compute_date_deadline(self):
        # Calcule automatiquement la date d'échéance (date_deadline) en fonction de la validité de l'offre.
        for record in self:
            if record.create_date:
                # Ajoute le nombre de jours de validité à la date de création pour définir la date d'échéance.
                record.date_deadline = record.create_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        # Calcule la validité en fonction de la différence entre la date d'échéance et la date de création.
        for record in self:
            if record.date_deadline:
                # La validité est la différence en jours entre la date d'échéance et la date de création.
                record.validity = (record.date_deadline - record.create_date.date()).days
                
                
    def action_accept_offer(self):
        # Accepte une offre pour la propriété, en modifiant son état et en assignant le prix et l'acheteur.
        for record in self:
            if record.property_id.state == 'offer_accepted':
                # Si une offre est déjà acceptée pour cette propriété, lève une erreur.
                raise UserError("Already accepted an offer for this property")

            if record.property_id.state not in ('sold', 'canceled'):
                # Si la propriété n'est ni vendue ni annulée, accepte l'offre.
                record.property_id.selling_price = record.price  # Met à jour le prix de vente.
                record.property_id.state = 'offer_accepted'      # Change l'état à 'offer_accepted'.
                record.property_id.buyer = record.partner_id     # Assigne l'acheteur de l'offre comme propriétaire.
            else:
                # Si la propriété est vendue ou annulée, lève une erreur.
                raise UserError("Cannot accept an offer for a Sold/Canceled Property")
        # Change le statut de l'offre à 'accepted'.
        return self.write({'status': 'accepted'})
    
    def action_refuse_offer(self):
        # Refuse une offre pour la propriété, sauf si la propriété est vendue ou annulée.
        for record in self:
            if record.property_id.state in ('sold', 'canceled'):
                # Lève une erreur si la propriété est déjà vendue ou annulée.
                raise UserError("Cannot refuse an offer for a Sold/Canceled Property")
        # Change le statut de l'offre à 'refused'.
        return self.write({'status': 'refused'})
