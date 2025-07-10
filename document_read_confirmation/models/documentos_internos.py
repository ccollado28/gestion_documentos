import base64

import google.generativeai as genai

from odoo import models, fields, api
from odoo.exceptions import UserError


class DocumentInterno(models.Model):
    _name = 'documento.interno'
    _description = 'Documento Interno para Confirmación de Lectura'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Título", required=True)
    description = fields.Text("Descripción")
    archivo = fields.Binary("Archivo", attachment=True, help="Sube el documento interno aquí.")
    filename = fields.Char("Nombre del Archivo")

    fecha_publicacion = fields.Datetime(
        string="Fecha de Publicación",
        default=lambda self: fields.Datetime.now(),
        readonly=True
    )

    required_reader_ids = fields.Many2many(
        'res.users',
        'documento_required_users_rel',
        'document_id',
        'user_id',
        string="Lectores Requeridos"
    )

    confirmed_reader_ids = fields.Many2many(
        'res.users',
        'documento_confirmed_users_rel',
        'document_id',
        'user_id',
        string="Usuarios que han leído"
    )

    pending_reader_ids = fields.Many2many(
        'res.users',
        compute='_compute_pending_readers',
        string="Lectores Pendientes",
        store=False,
    )

    tiene_lectores_pendientes = fields.Boolean(
        string="Tiene Lectores Pendientes?",
        compute="_compute_tiene_lectores_pendientes",
        store=True
    )

    @api.depends('required_reader_ids', 'confirmed_reader_ids')
    def _compute_tiene_lectores_pendientes(self):
        for record in self:
            record.tiene_lectores_pendientes = bool(
                set(record.required_reader_ids.ids) - set(record.confirmed_reader_ids.ids)
            )

    is_read_by_current_user = fields.Boolean(
        string="Leído por mí",
        compute='_compute_is_read_by_current_user',
        store=False
    )

    summary_gemini = fields.Text("Resumen Generado por IA")

    @api.depends('required_reader_ids', 'confirmed_reader_ids')
    def _compute_pending_readers(self):
        for record in self:
            record.pending_reader_ids = record.required_reader_ids - record.confirmed_reader_ids

    @api.depends('confirmed_reader_ids')
    def _compute_is_read_by_current_user(self):
        for record in self:
            record.is_read_by_current_user = self.env.user in record.confirmed_reader_ids

    def confirmar_lectura(self):
        self.ensure_one()

        if self.env.user in self.confirmed_reader_ids:
            raise UserError("¡Atención! Ya confirmaste la lectura de este documento previamente.")

        self.sudo().write({'confirmed_reader_ids': [(4, self.env.uid)]})

        self.message_post(
            body=f"El usuario **{self.env.user.name}** ha confirmado la lectura de este documento.",
            subtype_xmlid='mail.mt_note'
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '¡Confirmación Exitosa!',
                'message': 'Has confirmado correctamente la lectura de este documento.',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.required_reader_ids:
                subject = f"Nuevo Documento Interno: {record.name}"
                body = f"Se ha publicado un nuevo documento interno que requiere tu lectura y confirmación: <b>{record.name}</b>.<br/><br/>" \
                       f"Por favor, revisa el documento y confirma tu lectura. " \
                       f"<a href='/web#id={record.id}&model=documento.interno&view_type=form' style='font-weight: bold;'>Haz clic aquí para ir al documento.</a>"

                for user in record.required_reader_ids:
                    record.activity_schedule(
                        'mail.mail_activity_data_todo',
                        note=body,
                        user_id=user.id,
                        summary=subject,
                        date_deadline=fields.Date.today()
                    )

                if record.archivo:
                    # se genera el resumen
                    record.sudo().generate_gemini_summary()
        return records

    def _get_gemini_api_key(self):
        """ Obtiene la clave API de Gemini de los parámetros de configuración de Odoo. """
        ICPSudo = self.env['ir.config_parameter'].sudo()
        api_key = ICPSudo.get_param('documento.interno.gemini_api_key')
        if not api_key:
            raise UserError("La clave API de Gemini no está configurada. Contacta al administrador.")
        return api_key

    def generate_gemini_summary(self):
        self.ensure_one()
        if not self.archivo:
            self.message_post(
                body="No se pudo generar un resumen automático: No hay archivo adjunto.",
                subtype_xmlid='mail.mt_note'
            )
            self.write({'summary_gemini': "No hay archivo adjunto para resumir."})
            return

            self.message_post(
                body="El resumen ya ha sido generado para este documento. No se regenerará.",
                subtype_xmlid='mail.mt_note'
            )
            return

        try:
            # Intenta decodificar el archivo. Asumimos texto UTF-8.
            file_content = base64.b64decode(self.archivo).decode('utf-8')
        except Exception as e:
            self.message_post(
                body=f"Error al decodificar el archivo para el resumen: {e}. Asegúrate de que es un archivo de texto válido o sin formato especial.",
                subtype_xmlid='mail.mt_note'
            )
            self.write({'summary_gemini': "Error al procesar el archivo para el resumen."})
            return

        try:
            gemini_api_key = self._get_gemini_api_key()
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            # Define la "prompt" para Gemini.
            prompt = f"Por favor, genera un resumen conciso y objetivo del siguiente documento, enfocándote en los puntos clave y la información más relevante. El resumen debe tener un máximo de 200 palabras. Si el documento es muy corto o carece de contenido sustancial, indica que no se puede generar un resumen significativo.\n\nContenido del documento:\n{file_content}"
            response = model.generate_content(prompt, request_options={'timeout': 60})


            if response and response.text:
                self.write({'summary_gemini': response.text})
                self.message_post(
                    body=f"Se ha generado un resumen automático del documento por IA.",
                    subtype_xmlid='mail.mt_note'
                )
            else:
                self.write({'summary_gemini': "No se pudo generar un resumen automático para este documento."})
                self.message_post(
                    body=f"Falló la generación del resumen automático por IA.",
                    subtype_xmlid='mail.mt_note'
                )

        except UserError as e:  # Captura UserError si la API Key no está configurada
            self.message_post(
                body=f"Error de configuración para generar el resumen: {e}",
                subtype_xmlid='mail.mt_note'
            )
            self.write({'summary_gemini': "Error de configuración de la API."})

        except Exception as e:  # Captura cualquier otro error de la API
            error_message = f"Error inesperado al comunicarse con Gemini o generar el resumen: {e}"
            self.message_post(
                body=error_message,
                subtype_xmlid='mail.mt_note'
            )
            self.write({'summary_gemini': f"Error en la generación del resumen por IA: {e}"})



    def message_post(self, body, subtype_xmlid):
        pass
