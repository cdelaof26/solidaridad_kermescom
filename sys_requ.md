# Requerimientos del Proyecto para el Sistema KermESCOM

### Objetivo

Desarrollar un sistema web que facilite la interacción entre vendedores y compradores en la KermESCOM, permitiendo visualización de productos a través de un sitio alojado en Azure. El sistema deberá administrar cuentas de vendedores, validar donaciones, y facilitar la interacción de compradores y vendedores sin necesidad de registro para los compradores.

### Requerimientos Funcionales

1. Registro de Vendedores

- **Creación de Cuenta**: Los vendedores deberán registrarse con un formulario que incluya campos como nombre, correo electrónico y contraseña.
- **Donación**: Validación manual de una donación de $20 realizada mediante transferencia bancaria, con un sistema para comprobar y aprobar la donación antes de habilitar la cuenta.

2. Gestión de Productos

- **Creación de Artículos**: Los vendedores podrán agregar productos con la siguiente información:
  - Fotografía del producto.
  - Precio.
  - Detalles de pago (efectivo y/o transferencia).
  - Cantidad disponible.
- **Instrucciones Adicionales**:
- Posibilidad de agregar instrucciones sobre acciones altruistas que los compradores pueden realizar para obtener descuentos.

3. Interacción de Compradores

- **Acceso sin Registro**: Los compradores podrán navegar por el sitio y ver todos los productos disponibles sin necesidad de crear una cuenta.
- **Página de Producto**: Los compradores podrán acceder a una página detallada del producto que incluya la descripción, precio y fotografías.
- **Apertura de Tickets**: Los compradores podrán abrir un ticket especificando:
  - Opción de recogida en el puesto o envío a un aula.
  - Nombre completo.
  - Número telefónico de contacto.
  Cantidad de productos (de 1 a 5).

4. Notificaciones y Comunicación

**Notificación al Vendedor**: Cuando se emita un ticket, el vendedor recibirá una notificación en su navegador.

### Requerimientos No Funcionales

1. Alojamiento

**Infraestructura**: El sitio web debe estar alojado en una plataforma en la nube, como Azure, asegurando disponibilidad, escalabilidad y seguridad.

2. Usabilidad

**Interfaz Amigable**: El diseño de la interfaz debe ser intuitivo tanto para vendedores como para compradores, facilitando la navegación y el uso del sistema.

3. Seguridad

**Protección de Datos**: Implementar medidas de seguridad para proteger la información sensible de vendedores y compradores.

4. Rendimiento

**Tiempo de Carga**: El sistema debe garantizar tiempos de carga rápidos para una experiencia de usuario óptima.

### Consideraciones Técnicas

**Tecnologías**:

Desarrollo web utilizando lenguajes y frameworks adecuados como HTML, TailwindCSS, JavaScript, y un backend que podría ser desarrollado con Python (Flask).

**Base de Datos**: Implementar un sistema de base de datos (como SQL) para almacenar la información de usuarios, productos y tickets.

