# Módulo: Confirmación de Lectura de Documentos Internos (document_read_confirmation)

Este módulo de Odoo 17 facilita la gestión y distribución de documentos internos importantes,
añadiendo un sistema de confirmación de lectura.
Permite asegurar que el personal clave ha revisado y acusado recibo
de la información,manteniendo un registro auditable. 
Además como punto extra para este proyecto,
integra la generación de resúmenes automáticos de documentos en esta primera version solo para documentos de texto utf-8
utilizando la inteligencia artificial de Google Gemini.

## Características Principales

- Gestión centralizada de documentos internos.
- Asignación de "Lectores Requeridos" para cada documento.
- Funcionalidad de "Confirmar Lectura" para los usuarios.
- Seguimiento visual de lectores pendientes y confirmados.
- Notificaciones automáticas y actividades programadas para los lectores asignados.
- Generación automática de resúmenes de documentos mediante la API de Google Gemini.
- Integración con el sistema de seguimiento de actividades de Odoo.

## Requisitos y Dependencias

- Odoo 17
- Librerías Python externas
    - google-generativeai` (para la integración Gemini)
    * Instalación: pip install google-generativeai

## Instalación
Se proporciona un Dockerfile configurado para construir una imagen Docker de Odoo 17 con este módulo y sus dependencias Python preinstaladas.

### Configuración de Google Gemini AI
Para que la funcionalidad de generación de resúmenes por inteligencia artificial funcione correctamente, es necesario configurar una clave API de Google Gemini:

#### Obtener Clave API:

Dirígete a Google AI Studio o a la Consola de Google Cloud.

#### Genera una nueva clave API.

Importante: Asegúrate de que la API Generative Language API (o Vertex AI API si esta la subsume) esté habilitada en tu proyecto de Google Cloud.

#### Configurar en Odoo:

En tu instancia de Odoo, navega a Configuración > Parámetros del Sistema.

Busca el parámetro clave documento.interno.gemini_api_key.

Pega tu clave API de Gemini en el campo de valor de este parámetro y guarda los cambios.