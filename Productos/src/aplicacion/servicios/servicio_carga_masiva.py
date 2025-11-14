import csv
import io
import logging
import re
from typing import List, Dict, Tuple, Any
from aplicacion.comandos.crear_producto_con_inventario import CrearProductoConInventario
from aplicacion.comandos.actualizar_producto_con_inventario import ActualizarProductoConInventario
from aplicacion.comandos.crear_categoria import CrearCategoria
from seedwork.aplicacion.comandos import ejecutar_comando
from infraestructura.repositorios import RepositorioProductoSQLite, RepositorioCategoriaSQLite
from infraestructura.servicio_proveedores import ServicioProveedores

logger = logging.getLogger(__name__)

class ServicioCargaMasiva:
    """Servicio para procesar carga masiva de productos desde CSV"""
    
    REQUIRED_COLUMNS = ['nombre', 'descripcion', 'precio', 'stock', 'fecha_vencimiento', 'categoria', 'proveedor']
    
    def __init__(self, repositorio_producto=None, repositorio_categoria=None, servicio_proveedores=None):
        self.repositorio_producto = repositorio_producto or RepositorioProductoSQLite()
        self.repositorio_categoria = repositorio_categoria or RepositorioCategoriaSQLite()
        self.servicio_proveedores = servicio_proveedores or ServicioProveedores()
    
    def validar_archivo_csv(self, filename: str, content: bytes) -> Tuple[bool, str]:
        """Valida que el archivo sea CSV"""
        if not filename.lower().endswith('.csv'):
            return False, "El archivo debe tener extensión .csv"
        
        try:
            # Intentar parsear el CSV
            content_str = content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(content_str))
            headers = reader.fieldnames
            
            if not headers:
                return False, "El archivo CSV está vacío o no tiene headers"
            
            # Validar que tenga las columnas requeridas
            headers_lower = [h.lower().strip() for h in headers]
            for col in self.REQUIRED_COLUMNS:
                if col not in headers_lower:
                    return False, f"Falta la columna requerida: {col}"
            
            return True, "Archivo CSV válido"
        except Exception as e:
            return False, f"Error validando CSV: {str(e)}"
    
    def parsear_csv(self, content: bytes) -> Tuple[List[Dict[str, str]], List[str], Dict[str, str]]:
        """
        Parsea el contenido CSV y retorna:
        - Lista de diccionarios con keys normalizadas
        - Lista de headers originales
        - Mapeo de headers normalizados a originales
        """
        try:
            content_str = content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(content_str))
            
            # Guardar headers originales y crear mapeo
            headers_originales = list(reader.fieldnames) if reader.fieldnames else []
            mapeo_headers = {}  # {header_normalizado: header_original}
            
            for header_original in headers_originales:
                header_normalizado = header_original.lower().strip()
                mapeo_headers[header_normalizado] = header_original
            
            filas = []
            for row in reader:
                # Normalizar nombres de columnas para búsqueda
                fila_normalizada = {}
                for key, value in row.items():
                    key_normalizada = key.lower().strip()
                    fila_normalizada[key_normalizada] = value.strip() if value else ''
                filas.append(fila_normalizada)
            
            return filas, headers_originales, mapeo_headers
        except Exception as e:
            logger.error(f"Error parseando CSV: {e}")
            raise ValueError(f"Error parseando CSV: {str(e)}")
    
    def contar_filas(self, content: bytes) -> int:
        """Cuenta el número total de filas en el CSV (sin contar header)"""
        try:
            filas, _, _ = self.parsear_csv(content)
            return len(filas)
        except Exception as e:
            logger.error(f"Error contando filas: {e}")
            return 0
    
    def normalizar_nombre(self, nombre: str) -> str:
        """Normaliza un nombre para comparación: lowercase y sin espacios"""
        if not nombre:
            return ""
        return re.sub(r'\s+', '', nombre.lower().strip())
    
    def procesar_fila(self, fila: Dict[str, str], callback_progreso=None) -> Dict[str, any]:
        """
        Procesa una fila del CSV y retorna el resultado
        Retorna: {'status': 'creado'|'actualizado'|'rechazado'|'error', 'mensaje': str, 'fila': dict}
        """
        try:
            # Extraer datos de la fila
            nombre = fila.get('nombre', '').strip()
            descripcion = fila.get('descripcion', '').strip()
            precio_str = fila.get('precio', '').strip()
            stock_str = fila.get('stock', '').strip()
            fecha_vencimiento = fila.get('fecha_vencimiento', '').strip()
            categoria_nombre = fila.get('categoria', '').strip()
            proveedor_nombre = fila.get('proveedor', '').strip()
            
            # Validaciones básicas
            if not nombre:
                return {'status': 'error', 'mensaje': 'Nombre es requerido', 'fila': fila}
            
            try:
                precio = float(precio_str)
            except (ValueError, TypeError):
                return {'status': 'error', 'mensaje': f'Precio inválido: {precio_str}', 'fila': fila}
            
            try:
                stock = int(stock_str)
            except (ValueError, TypeError):
                return {'status': 'error', 'mensaje': f'Stock inválido: {stock_str}', 'fila': fila}
            
            # 1. Buscar o crear categoría
            categoria = self.repositorio_categoria.obtener_por_nombre(categoria_nombre)
            if not categoria:
                # Crear categoría
                try:
                    comando_categoria = CrearCategoria(
                        nombre=categoria_nombre,
                        descripcion=f"Categoría creada automáticamente: {categoria_nombre}"
                    )
                    categoria = ejecutar_comando(comando_categoria)
                    logger.info(f"Categoría creada: {categoria_nombre}")
                except Exception as e:
                    return {'status': 'error', 'mensaje': f'Error creando categoría: {str(e)}', 'fila': fila}
            categoria_id = str(categoria.id)
            
            # 2. Buscar proveedor por nombre
            proveedor = self.servicio_proveedores.obtener_proveedor_por_nombre(proveedor_nombre)
            if not proveedor:
                return {'status': 'rechazado', 'mensaje': f'Proveedor no encontrado: {proveedor_nombre}', 'fila': fila}
            proveedor_id = proveedor.get('id')
            
            # 3. Buscar producto por nombre
            producto_existente = self.repositorio_producto.obtener_por_nombre(nombre)
            
            if producto_existente:
                # Actualizar producto existente
                try:
                    comando = ActualizarProductoConInventario(
                        producto_id=str(producto_existente.id),
                        nombre=nombre,
                        descripcion=descripcion,
                        precio=precio,
                        stock=stock,
                        fecha_vencimiento=fecha_vencimiento,
                        categoria=categoria_nombre,
                        categoria_id=categoria_id,
                        proveedor_id=proveedor_id
                    )
                    ejecutar_comando(comando)
                    logger.info(f"Producto actualizado: {nombre}")
                    return {'status': 'actualizado', 'mensaje': 'Producto actualizado exitosamente', 'fila': fila}
                except Exception as e:
                    logger.error(f"Error actualizando producto {nombre}: {e}")
                    return {'status': 'error', 'mensaje': f'Error actualizando producto: {str(e)}', 'fila': fila}
            else:
                # Crear nuevo producto
                try:
                    comando = CrearProductoConInventario(
                        nombre=nombre,
                        descripcion=descripcion,
                        precio=precio,
                        stock=stock,
                        fecha_vencimiento=fecha_vencimiento,
                        categoria=categoria_nombre,
                        categoria_id=categoria_id,
                        proveedor_id=proveedor_id
                    )
                    ejecutar_comando(comando)
                    logger.info(f"Producto creado: {nombre}")
                    return {'status': 'creado', 'mensaje': 'Producto creado exitosamente', 'fila': fila}
                except Exception as e:
                    logger.error(f"Error creando producto {nombre}: {e}")
                    return {'status': 'error', 'mensaje': f'Error creando producto: {str(e)}', 'fila': fila}
            
        except Exception as e:
            logger.error(f"Error procesando fila: {e}")
            return {'status': 'error', 'mensaje': f'Error inesperado: {str(e)}', 'fila': fila}
    
    def procesar_csv(self, content: bytes, callback_progreso=None) -> Tuple[List[Dict[str, any]], List[Dict[str, str]], List[str], Dict[str, str]]:
        """
        Procesa todo el CSV y retorna lista de resultados, filas, headers originales y mapeo
        callback_progreso: función(filas_procesadas, total_filas) que se llama periódicamente
        """
        filas, headers_originales, mapeo_headers = self.parsear_csv(content)
        resultados = []
        total_filas = len(filas)
        
        for i, fila in enumerate(filas):
            resultado = self.procesar_fila(fila, callback_progreso)
            resultados.append(resultado)
            
            # Llamar callback de progreso si está disponible
            if callback_progreso:
                callback_progreso(i + 1, total_filas)
        
        return resultados, filas, headers_originales, mapeo_headers
    
    def generar_csv_resultado(self, filas_normalizadas: List[Dict[str, str]], resultados: List[Dict[str, any]], 
                              headers_originales: List[str], mapeo_headers: Dict[str, str]) -> bytes:
        """Genera un CSV con las filas originales más columnas 'status' y 'mensaje'"""
        try:
            output = io.StringIO()
            
            # Usar headers originales y agregar status y mensaje al final
            headers = headers_originales.copy() if headers_originales else []
            if 'status' not in headers:
                headers.append('status')
            if 'mensaje' not in headers:
                headers.append('mensaje')
            
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            
            # Escribir filas con status y mensaje
            for fila_normalizada, resultado in zip(filas_normalizadas, resultados):
                # Construir fila con headers originales
                fila_resultado = {}
                for header_original in headers:
                    if header_original == 'status':
                        fila_resultado[header_original] = resultado.get('status', 'error')
                    elif header_original == 'mensaje':
                        # Mostrar mensaje solo si hay error o rechazo, o si es exitoso mostrar un mensaje breve
                        status = resultado.get('status', 'error')
                        mensaje = resultado.get('mensaje', '')
                        
                        # Si no hay mensaje pero el status es exitoso, poner mensaje vacío o un mensaje genérico
                        if status in ['creado', 'actualizado']:
                            # Para casos exitosos, podemos poner el mensaje o dejarlo vacío
                            # El mensaje ya viene en el resultado, así que lo usamos
                            fila_resultado[header_original] = mensaje if mensaje else 'OK'
                        else:
                            # Para errores y rechazos, siempre mostrar el mensaje
                            fila_resultado[header_original] = mensaje if mensaje else f'Error: {status}'
                    else:
                        # Buscar el valor usando el header normalizado
                        header_normalizado = header_original.lower().strip()
                        fila_resultado[header_original] = fila_normalizada.get(header_normalizado, '')
                
                writer.writerow(fila_resultado)
            
            csv_bytes = output.getvalue().encode('utf-8')
            output.close()
            return csv_bytes
            
        except Exception as e:
            logger.error(f"Error generando CSV resultado: {e}")
            raise ValueError(f"Error generando CSV resultado: {str(e)}")

