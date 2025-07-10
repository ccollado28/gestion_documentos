FROM odoo:17.0

LABEL maintainer="Cesar Collado collado.cesar.uy@gmail.com"

WORKDIR /usr/lib/python3/dist-packages/odoo

RUN mkdir -p /opt/odoo/custom_addons/document_read_confirmation

COPY ./document_read_confirmation /opt/odoo/custom_addons/document_read_confirmation/

RUN pip install --no-cache-dir google-generativeai
ENV ODOO_ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,/opt/odoo/custom_addons"

USER odoo

CMD ["odoo"]