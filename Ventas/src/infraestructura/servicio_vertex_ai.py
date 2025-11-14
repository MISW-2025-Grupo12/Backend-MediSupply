"""Servicio para generar sugerencias usando Vertex AI (modo API Key REST)"""
import os
import logging
from typing import Optional, Dict
import requests

logger = logging.getLogger(__name__)


class ServicioVertexAI:
    """Servicio para interactuar con Vertex AI vía API REST usando API Key"""

    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_CLOUD_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "GOOGLE_CLOUD_API_KEY no está configurada. Define la API key en tu entorno "
                "para poder invocar Vertex AI."
            )

        # Modelo por defecto
        self.base_model = os.environ.get(
            "VERTEX_MODEL_NAME", "gemini-2.5-flash-lite"
        )
        self.endpoint = (
            "https://aiplatform.googleapis.com/v1/publishers/google/models/"
            f"{self.base_model}:generateContent"
        )
        logger.info("Servicio Vertex AI inicializado en modo API Key.")
    
    def obtener_mime_type(self, formato: str) -> str:
        """
        Obtiene el MIME type basado en el formato del archivo
        
        Args:
            formato: Extensión del archivo (jpg, png, mp4, etc.)
        
        Returns:
            MIME type correspondiente
        """
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'mp4': 'video/mp4',
            'mov': 'video/quicktime',
            'avi': 'video/x-msvideo',
            'webm': 'video/webm'
        }
        
        formato_lower = formato.lower()
        return mime_types.get(formato_lower, 'application/octet-stream')
    
    def generar_sugerencias(
        self,
        datos_cliente: Dict,
        historial_pedidos: Dict,
        archivo_url: Optional[str] = None,
        mime_type: Optional[str] = None,
        comentarios_evidencia: Optional[str] = None
    ) -> str:
        """
        Genera sugerencias usando Vertex AI
        
        Args:
            datos_cliente: Diccionario con datos del cliente (nombre, dirección, teléfono, etc.)
            historial_pedidos: Diccionario con resumen del historial de pedidos
            archivo_url: URL pública de GCS del archivo (imagen/video) - opcional
            mime_type: MIME type del archivo - opcional
            comentarios_evidencia: Comentarios asociados a la evidencia - opcional
        
        Returns:
            Texto con las sugerencias generadas
        """
        try:
            # System instruction - Instrucciones estándar que no cambian entre llamadas
            system_instruction_text = """Usted es un asistente experto en ventas para Medisupply, una empresa distribuidora de productos farmacéuticos. 

Proporcione respuestas CONCISAS y DIRECTAS. Use un lenguaje claro y profesional, evitando explicaciones extensas.

FORMATO DE RESPUESTA REQUERIDO:

**3 PRODUCTOS RECOMENDADOS:**
1. [Nombre del producto 1] - [Breve razón de recomendación]
2. [Nombre del producto 2] - [Breve razón de recomendación]
3. [Nombre del producto 3] - [Breve razón de recomendación]

**COMENTARIOS:**
[2-3 comentarios breves y prácticos sobre oportunidades de venta, estrategias comerciales o recomendaciones generales para este cliente]

**ANÁLISIS DE LA EVIDENCIA VISUAL:** (si se proporciona)
[Describa brevemente qué observa en la imagen o video y proporcione una sugerencia específica basada en lo que ve. Sea conciso y directo.]

IMPORTANTE: Mantenga la respuesta total en menos de 300 palabras. Sea directo y evite explicaciones extensas."""
            
            # Construir prompt solo con datos específicos del cliente
            prompt_parts = []
            
            # Información del cliente
            prompt_parts.append("=== INFORMACIÓN DEL CLIENTE ===")
            prompt_parts.append(f"Nombre: {datos_cliente.get('nombre', 'No disponible')}")
            prompt_parts.append(f"Dirección: {datos_cliente.get('direccion', 'No disponible')}")
            prompt_parts.append(f"Teléfono: {datos_cliente.get('telefono', 'No disponible')}")
            if 'email' in datos_cliente:
                prompt_parts.append(f"Email: {datos_cliente.get('email', 'No disponible')}")
            prompt_parts.append("")
            
            # Historial de pedidos
            prompt_parts.append("=== HISTORIAL DE COMPRAS ===")
            prompt_parts.append(f"Total de pedidos: {historial_pedidos.get('total_pedidos', 0)}")
            prompt_parts.append(f"Frecuencia de compra: {historial_pedidos.get('frecuencia_compra', 'No disponible')}")
            prompt_parts.append("")
            
            # Últimos pedidos
            ultimos_pedidos = historial_pedidos.get('ultimos_pedidos', [])
            if ultimos_pedidos:
                prompt_parts.append("Últimos pedidos:")
                for pedido in ultimos_pedidos[:5]:  # Mostrar últimos 5
                    prompt_parts.append(f"- Fecha: {pedido.get('fecha', 'N/A')}, Total: ${pedido.get('total', 0):.2f}, Estado: {pedido.get('estado', 'N/A')}")
                    items = pedido.get('items', [])
                    if items:
                        productos = ", ".join([f"{item.get('nombre', 'N/A')} (x{item.get('cantidad', 0)})" for item in items[:3]])
                        prompt_parts.append(f"  Productos: {productos}")
                prompt_parts.append("")
            
            # Productos más comprados
            productos_mas_comprados = historial_pedidos.get('productos_mas_comprados', [])
            if productos_mas_comprados:
                prompt_parts.append("Productos más comprados:")
                for producto in productos_mas_comprados[:5]:  # Top 5
                    prompt_parts.append(
                        f"- {producto.get('nombre', 'N/A')}: "
                        f"{producto.get('cantidad_total', 0)} unidades en "
                        f"{producto.get('veces_comprado', 0)} compras"
                    )
                prompt_parts.append("")
            
            # Comentarios de evidencia si existen
            if comentarios_evidencia:
                prompt_parts.append("=== COMENTARIOS DE LA VISITA ===")
                prompt_parts.append(comentarios_evidencia)
                prompt_parts.append("")
            
            # Solicitud simple - sin repetir el formato
            prompt_parts.append("Basándose en la información anterior, proporcione las sugerencias en el formato requerido.")
            
            if not archivo_url:
                prompt_parts.append("NOTA: No se proporcionó evidencia visual para analizar.")

            prompt_text = "\n".join(prompt_parts)

            return self._generar_con_api_key(
                prompt_text=prompt_text,
                system_instruction=system_instruction_text,
                archivo_url=archivo_url,
                mime_type=mime_type,
            )

        except Exception as e:
            logger.error(f"Error generando sugerencias con Vertex AI: {e}")
            raise

    def _generar_con_api_key(
        self,
        prompt_text: str,
        system_instruction: str,
        archivo_url: Optional[str],
        mime_type: Optional[str],
    ) -> str:
        """
        Genera sugerencias usando la API REST de Generative Language con API Key
        """
        # Construir las partes del mensaje del usuario
        parts = [{"text": prompt_text}]

        # Agregar archivo multimedia si existe
        parte_multimedia = self._construir_parte_archivo(
            archivo_url=archivo_url,
            mime_type=mime_type,
        )
        if parte_multimedia:
            parts.append(parte_multimedia)

        # Construir payload con systemInstruction separado (más eficiente)
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts,
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            }
        }

        url = f"{self.endpoint}?key={self.api_key}"

        logger.info("Generando sugerencias con Vertex AI (REST + API Key)...")
        respuesta = requests.post(url, json=payload, timeout=90)

        if not respuesta.ok:
            logger.error("Error REST Vertex AI: %s", respuesta.text)
            respuesta.raise_for_status()

        data = respuesta.json()
        texto = ""
        for candidato in data.get("candidates", []):
            contenido = candidato.get("content", {})
            for parte in contenido.get("parts", []):
                if "text" in parte:
                    texto += parte["text"]

        if not texto:
            logger.warning("La respuesta de Vertex AI no contiene texto utilizable.")
            texto = "No se recibieron sugerencias del modelo."

        return texto

    def _construir_parte_archivo(
        self,
        archivo_url: Optional[str],
        mime_type: Optional[str],
    ) -> Optional[Dict]:
        """
        Construye la parte del archivo para el payload de Vertex AI.
        Solo acepta URLs públicas de GCS (https://storage.googleapis.com/... o gs://...)
        
        Args:
            archivo_url: URL pública de GCS del archivo
            mime_type: MIME type del archivo
        
        Returns:
            Diccionario con file_data o None si no se proporciona URL válida
        """
        if not archivo_url or not mime_type:
            return None
        
        # Validar que sea una URL de GCS
        if not (archivo_url.startswith('https://storage.googleapis.com/') or archivo_url.startswith('gs://')):
            logger.warning(
                "La URL proporcionada no es de GCS: %s. Solo se aceptan URLs públicas de GCS.",
                archivo_url
            )
            return None
        
        # Usar la URL/URI directamente (Vertex AI acepta ambas)
        return {
            "file_data": {
                "mime_type": mime_type,
                "file_uri": archivo_url,
            }
        }

